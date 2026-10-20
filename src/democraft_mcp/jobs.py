"""Job engine: queue, provenance, cancellation and event streams.

Phase 2 of docs/PLAN.md. Jobs are additive to the synchronous demo path: the
engine owns the queue, the run directory, the event tape and the status, while
`run_demo` stays the thing that actually drives the CLIs.

Durability is file-based on purpose (no DB): every job writes `job.json` and
`events.jsonl` beside its artifacts, so a restart loses the queue but not the
record. A real queue with crash recovery is a later phase.
"""

from __future__ import annotations

import json
import queue
import threading
import time
import uuid
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from .crafts import DEFAULT_MODEL, DemoCancelled


def _now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


@dataclass
class Job:
    id: str
    app: str
    demo: str
    topic: str
    model: str
    run_dir: Path
    focus: bool = False
    status: str = "queued"
    created: str = field(default_factory=_now)
    started: str | None = None
    finished: str | None = None
    error: str | None = None
    attempts: int = 1
    cancel_requested: bool = False
    events: list[dict] = field(default_factory=list)
    subscribers: list[queue.Queue] = field(default_factory=list)
    result: dict | None = None

    def public(self) -> dict:
        files = []
        if self.run_dir.is_dir():
            files = sorted(
                str(p.relative_to(self.run_dir)).replace("\\", "/")
                for p in self.run_dir.rglob("*")
                if p.is_file() and p.name not in ("job.json", "events.jsonl", "run.json")
            )
        return {
            "id": self.id,
            "app": self.app,
            "demo": self.demo,
            "topic": self.topic,
            "model": self.model,
            "focus": self.focus,
            "status": self.status,
            "created": self.created,
            "started": self.started,
            "finished": self.finished,
            "error": self.error,
            "attempts": self.attempts,
            "artifacts": files,
            "event_count": len(self.events),
            "run_dir": str(self.run_dir),
        }


class JobEngine:
    """Bounded worker pool over demo runs, with an event tape per job."""

    def __init__(self, outbox: Path, runner: Callable | None = None, workers: int = 2):
        self.outbox = outbox
        self.runner = runner
        self.lock = threading.Lock()
        self.jobs: dict[str, Job] = {}
        self.pool = ThreadPoolExecutor(max_workers=workers, thread_name_prefix="democraft-job")

    # -- lifecycle ---------------------------------------------------------
    def submit(
        self, app: str, demo: str, topic: str = "", model: str = "", focus: bool = False
    ) -> Job:
        job_id = time.strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:6]
        run_dir = self.outbox / app / demo / "jobs" / job_id
        run_dir.mkdir(parents=True, exist_ok=True)
        job = Job(
            id=job_id,
            app=app,
            demo=demo,
            topic=topic,
            model=model,
            run_dir=run_dir,
            focus=focus,
        )
        with self.lock:
            self.jobs[job_id] = job
        self._emit(job, {"kind": "queued", "job": job_id, "app": app, "demo": demo})
        self.pool.submit(self._run, job)
        return job

    def get(self, job_id: str) -> Job | None:
        with self.lock:
            return self.jobs.get(job_id)

    def list(self) -> list[dict]:
        with self.lock:
            jobs = list(self.jobs.values())
        return [j.public() for j in sorted(jobs, key=lambda j: j.created, reverse=True)]

    def cancel(self, job_id: str) -> bool:
        job = self.get(job_id)
        if job is None or job.status in ("succeeded", "failed", "cancelled"):
            return False
        job.cancel_requested = True
        if job.status == "queued":
            job.status = "cancelled"
            job.finished = _now()
            self._emit(job, {"kind": "done", "status": "cancelled"})
        return True

    def retry(self, job_id: str) -> Job | None:
        old = self.get(job_id)
        if old is None:
            return None
        job = self.submit(old.app, old.demo, old.topic, old.model, old.focus)
        job.attempts = old.attempts + 1
        return job

    # -- execution ---------------------------------------------------------
    def _run(self, job: Job) -> None:
        job.status = "running"
        job.started = _now()
        self._emit(
            job,
            {"kind": "start", "job": job.id, "app": job.app, "demo": job.demo, "model": job.model},
        )

        def on_step(event: dict) -> None:
            self._emit(job, event)

        def should_cancel() -> bool:
            return job.cancel_requested

        try:
            if self.runner is None:
                from .crafts import run_demo

                result = run_demo(
                    job.app,
                    job.demo,
                    job.run_dir.parents[3],
                    model=job.model or DEFAULT_MODEL,
                    topic=job.topic,
                    on_step=on_step,
                    should_cancel=should_cancel,
                    run_dir=job.run_dir,
                    focus=job.focus,
                )
            else:
                result = self.runner(
                    job.app,
                    job.demo,
                    job.run_dir,
                    job.topic,
                    job.model,
                    on_step,
                    should_cancel,
                )
            job.result = result
            if job.cancel_requested:
                job.status = "cancelled"
            else:
                job.status = "succeeded" if result.get("success") else "failed"
                job.error = None if result.get("success") else result.get("message")
        except DemoCancelled:
            job.status = "cancelled"
        except Exception as exc:  # noqa: BLE001 - job boundary
            job.status = "failed"
            job.error = f"{type(exc).__name__}: {exc}"
        finally:
            job.finished = _now()
            self._write_job(job)
            self._emit(
                job,
                {
                    "kind": "done",
                    "job": job.id,
                    "status": job.status,
                    "error": job.error,
                    "result": job.result,
                },
            )

    # -- events ------------------------------------------------------------
    def _emit(self, job: Job, event: dict) -> None:
        with self.lock:
            event = dict(event, seq=len(job.events), ts=_now())
            job.events.append(event)
            subscribers = list(job.subscribers)
        with open(job.run_dir / "events.jsonl", "a", encoding="utf-8") as fh:
            fh.write(json.dumps(event, ensure_ascii=False) + "\n")
        for subscriber in subscribers:
            subscriber.put(event)

    def stream(self, job_id: str):
        """Yield events: replay what happened, then follow until done."""
        job = self.get(job_id)
        if job is None:
            yield {"kind": "error", "error": f"unknown job '{job_id}'"}
            return
        subscriber: queue.Queue = queue.Queue()
        with self.lock:
            replay = list(job.events)
            job.subscribers.append(subscriber)
        try:
            for event in replay:
                yield event
                if event.get("kind") == "done":
                    return
            while True:
                event = subscriber.get()
                yield event
                if event.get("kind") == "done":
                    return
        finally:
            with self.lock:
                if subscriber in job.subscribers:
                    job.subscribers.remove(subscriber)

    def _write_job(self, job: Job) -> None:
        payload = job.public()
        payload["result"] = job.result
        (job.run_dir / "job.json").write_text(
            json.dumps(payload, indent=1, ensure_ascii=False), encoding="utf-8"
        )
