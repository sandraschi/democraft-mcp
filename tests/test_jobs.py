"""Job engine: lifecycle, provenance, cancellation, event replay."""

from __future__ import annotations

import time
from pathlib import Path

from democraft_mcp.jobs import JobEngine


def wait(engine: JobEngine, job_id: str, timeout: float = 10.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        job = engine.get(job_id)
        if job and job.status in ("succeeded", "failed", "cancelled"):
            return job
        time.sleep(0.05)
    raise AssertionError(f"job {job_id} did not finish in {timeout}s")


def fake_runner(app, demo, run_dir, topic, model, on_step, should_cancel):
    on_step({"kind": "ai", "success": True, "model": "fake", "ms": 1})
    for index in range(3):
        if should_cancel():
            return {"success": False, "message": "cancelled"}
        (run_dir / f"step{index}.txt").write_text("x", encoding="utf-8")
        on_step(
            {
                "kind": "step",
                "argv": ["fake", str(index)],
                "returncode": 0,
                "ms": 1,
                "artifacts": [f"step{index}.txt"],
            }
        )
    return {"success": True, "message": "ok", "artifacts": ["step0.txt"]}


def test_job_lifecycle_writes_provenance(tmp_path: Path) -> None:
    engine = JobEngine(tmp_path, runner=fake_runner, workers=1)
    job = engine.submit("app", "demo", "topic")
    done = wait(engine, job.id)

    assert done.status == "succeeded"
    assert done.result and done.result["success"] is True
    assert (done.run_dir / "job.json").is_file()
    assert (done.run_dir / "events.jsonl").is_file()
    assert (done.run_dir / "step0.txt").is_file()

    kinds = [event["kind"] for event in done.events]
    assert kinds[0] == "queued"
    assert "start" in kinds and "step" in kinds
    assert kinds[-1] == "done"

    # replay: a finished job's stream returns its tape and stops at done
    replay = list(engine.stream(job.id))
    assert replay[-1]["kind"] == "done"


def test_cancel_queued_job(tmp_path: Path) -> None:
    def slow_runner(app, demo, run_dir, topic, model, on_step, should_cancel):
        time.sleep(0.5)
        return {"success": True, "message": "slow"}

    engine = JobEngine(tmp_path, runner=slow_runner, workers=1)
    first = engine.submit("app", "demo")
    second = engine.submit("app", "demo")
    assert engine.cancel(second.id) is True
    assert engine.get(second.id).status == "cancelled"
    assert wait(engine, first.id).status == "succeeded"


def test_retry_creates_new_job(tmp_path: Path) -> None:
    engine = JobEngine(tmp_path, runner=fake_runner, workers=1)
    job = engine.submit("app", "demo")
    wait(engine, job.id)
    retried = engine.retry(job.id)
    assert retried is not None
    assert retried.id != job.id
    assert retried.attempts == 2
    assert wait(engine, retried.id).status == "succeeded"
