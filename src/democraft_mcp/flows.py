"""Multi-app flows: a named sequence of demo steps across Craft apps.

A flow is data, not code: an ordered list of `{app, demo, note}` steps. The
runner executes them sequentially with the existing `run_demo`, copies each
step's artifacts into a per-run bundle, and records what happened. That keeps
the flow layer thin while the real work stays in the app adapters.

This is v1: steps reference demos, not arbitrary command lines, and handoff is
by convention (the next step reads the previous artifact path). Command-level
steps and true artifact piping are the next iteration.
"""

from __future__ import annotations

import json
import re
import shutil
import threading
import uuid
from datetime import UTC, datetime
from pathlib import Path

from .crafts import BY_KEY, run_demo

SLUG = re.compile(r"^[a-z0-9][a-z0-9-]{1,48}$")


def _now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


SEED_FLOWS: list[dict] = [
    {
        "id": "cover-factory",
        "name": "Cover factory",
        "description": "Grade a plate, lay it into a print spread, export a portfolio PDF.",
        "status": "ready",
        "steps": [
            {"app": "photo", "demo": "plate-grade", "note": "non-destructive grade + layered save"},
            {"app": "design", "demo": "print-spread", "note": "facing pages, styles, PDF"},
            {"app": "pdf", "demo": "portfolio", "note": "assemble the deliverable"},
        ],
    },
    {
        "id": "photo-book",
        "name": "Photo book",
        "description": "Batch-treat a set, lay out pages, export print-ready PDF.",
        "status": "ready",
        "steps": [
            {"app": "photo", "demo": "batch-treatment", "note": "one action over three plates"},
            {"app": "design", "demo": "print-spread", "note": "page architecture"},
            {"app": "pdf", "demo": "portfolio", "note": "print export"},
        ],
    },
    {
        "id": "data-deck",
        "name": "Data deck",
        "description": "Sheet + chart, slides, handout PDF.",
        "status": "ready",
        "steps": [
            {"app": "grid", "demo": "homepage-grid", "note": "data, formula, chart"},
            {"app": "deck", "demo": "pitch-deck", "note": "slides"},
            {"app": "pdf", "demo": "portfolio", "note": "handout"},
        ],
    },
    {
        "id": "cad-board",
        "name": "CAD board",
        "description": "Plan, presentation board, PDF.",
        "status": "ready",
        "steps": [
            {"app": "cad", "demo": "house-plan", "note": "2D plan set"},
            {"app": "design", "demo": "print-spread", "note": "board layout"},
            {"app": "pdf", "demo": "portfolio", "note": "export"},
        ],
    },
    {
        "id": "poster-lab",
        "name": "Poster lab",
        "description": "Vector source, texture pass, poster layout.",
        "status": "ready",
        "steps": [
            {"app": "vector", "demo": "pelican-vector", "note": "vector source"},
            {"app": "photo", "demo": "plate-grade", "note": "texture/grade pass"},
            {"app": "design", "demo": "print-spread", "note": "poster composition"},
        ],
    },
    {
        "id": "report",
        "name": "Data report",
        "description": "Charts, document, PDF.",
        "status": "ready",
        "steps": [
            {"app": "grid", "demo": "homepage-grid", "note": "charts"},
            {"app": "word", "demo": "demo-report", "note": "one-page report"},
            {"app": "pdf", "demo": "portfolio", "note": "deliverable"},
        ],
    },
    {
        "id": "brand-kit",
        "name": "Brand kit",
        "description": "Mark, specimens, motion reel.",
        "status": "exploratory",
        "steps": [
            {"app": "vector", "demo": "pelican-vector", "note": "mark"},
            {"app": "design", "demo": "print-spread", "note": "specimen sheet"},
            {"app": "deck", "demo": "transition-reel", "note": "animated brand beats"},
        ],
    },
    {
        "id": "storyboard",
        "name": "Storyboard",
        "description": "Wireframe, frames, board.",
        "status": "ready",
        "steps": [
            {"app": "fig", "demo": "landing-page", "note": "interface sketch"},
            {"app": "design", "demo": "print-spread", "note": "frame layout"},
            {"app": "film", "demo": "storyboard", "note": "board + AI panel"},
        ],
    },
    {
        "id": "video-delivery",
        "name": "Video delivery",
        "description": "Cut, caption, hand off: sequence, SRT round-trip, EDL and XML interchange.",
        "status": "ready",
        "steps": [
            {"app": "film", "demo": "timeline-cut", "note": "real NLE cut + H.264 export"},
            {
                "app": "film",
                "demo": "captions-roundtrip",
                "note": "SRT in, track read back, SRT out",
            },
            {
                "app": "film",
                "demo": "interchange-kit",
                "note": "EDL + FCP7 XML + FCPXML with reports",
            },
        ],
    },
    {
        "id": "animatic",
        "name": "Animatic",
        "description": "Graded stills and a shot board into a timed cut, plus poster frames.",
        "status": "ready",
        "steps": [
            {"app": "photo", "demo": "plate-grade", "note": "graded stills"},
            {"app": "film", "demo": "storyboard", "note": "EDL + AI shot board"},
            {"app": "film", "demo": "poster-strip", "note": "three frames for the depot"},
        ],
    },
    {
        "id": "lyric-sheet",
        "name": "Lyric sheet",
        "description": "Text, layout, PDF.",
        "status": "ready",
        "steps": [
            {"app": "word", "demo": "demo-report", "note": "text"},
            {"app": "design", "demo": "print-spread", "note": "typographic sheet"},
            {"app": "pdf", "demo": "portfolio", "note": "export"},
        ],
    },
    {
        "id": "audiobook-art",
        "name": "Audiobook art",
        "description": "Plate, typography, cover PDF.",
        "status": "ready",
        "steps": [
            {"app": "photo", "demo": "plate-grade", "note": "cover image"},
            {"app": "vector", "demo": "pelican-vector", "note": "title treatment"},
            {"app": "pdf", "demo": "portfolio", "note": "cover sheet"},
        ],
    },
    {
        "id": "title-sequence",
        "name": "Title sequence",
        "description": "Title card, motion pass, assembly.",
        "status": "exploratory",
        "blocked_reason": (
            "FilmCraft timeline exists and the film step is a real cut, but it "
            "builds its own demo footage instead of ingesting the motion still"
        ),
        "steps": [
            {"app": "design", "demo": "print-spread", "note": "title card"},
            {"app": "effect", "demo": "title-card", "note": "motion still"},
            {"app": "film", "demo": "timeline-cut", "note": "NLE cut (own footage)"},
        ],
    },
    {
        "id": "score-driven-cut",
        "name": "Score-driven cut",
        "description": "Music bed, cut to it.",
        "status": "exploratory",
        "blocked_reason": (
            "FilmCraft timeline exists; the cut step uses its own demo footage, "
            "not the music bed. SoundCraft VST3 instruments silent (BUG-082); "
            "built-in synth works."
        ),
        "steps": [
            {"app": "sound", "demo": "ident-jingle", "note": "music bed"},
            {"app": "film", "demo": "timeline-cut", "note": "NLE cut (own footage)"},
        ],
    },
]


class FlowError(ValueError):
    pass


def validate_flow(flow: dict) -> dict:
    fid = str(flow.get("id", "")).strip()
    if not SLUG.match(fid):
        raise FlowError("id must be a 2-49 char slug: lowercase letters, digits, hyphens")
    name = str(flow.get("name", "")).strip()
    if not name:
        raise FlowError("name is required")
    steps = flow.get("steps")
    if not isinstance(steps, list) or not steps:
        raise FlowError("a flow needs at least one step")
    clean_steps = []
    for index, step in enumerate(steps, 1):
        app_key = str(step.get("app", "")).strip()
        demo_id = str(step.get("demo", "")).strip()
        app = BY_KEY.get(app_key)
        if app is None:
            raise FlowError(f"step {index}: unknown app '{app_key}'")
        if not any(d.id == demo_id for d in app.demos):
            raise FlowError(f"step {index}: '{demo_id}' is not a demo of {app_key}")
        clean_steps.append(
            {
                "app": app_key,
                "demo": demo_id,
                "note": str(step.get("note", "")).strip()[:160],
                "topic": str(step.get("topic", "")).strip()[:200],
            }
        )
    status = str(flow.get("status", "ready"))
    if status not in ("ready", "exploratory", "blocked"):
        status = "ready"
    return {
        "id": fid,
        "name": name[:80],
        "description": str(flow.get("description", "")).strip()[:500],
        "status": status,
        "blocked_reason": str(flow.get("blocked_reason", "")).strip()[:300],
        "steps": clean_steps,
    }


class FlowStore:
    def __init__(self, path: Path):
        self.path = path
        self.lock = threading.Lock()
        self.flows = self._load()

    def _load(self) -> dict[str, dict]:
        if self.path.is_file():
            data = json.loads(self.path.read_text(encoding="utf-8"))
            flows = {flow["id"]: flow for flow in data.get("flows", [])}
            # Seeds added in a later release must reach installs that already
            # have a flows.json. Existing ids stay exactly as the user left them.
            missing = {s["id"]: s for s in SEED_FLOWS if s["id"] not in flows}
            if missing:
                flows.update(missing)
                self._write(flows)
            return flows
        seeded = {flow["id"]: flow for flow in SEED_FLOWS}
        self._write(seeded)
        return seeded

    def _write(self, flows: dict[str, dict]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"flows": [flows[k] for k in sorted(flows)]}
        self.path.write_text(json.dumps(payload, indent=1, ensure_ascii=False), encoding="utf-8")

    def list(self) -> list[dict]:
        with self.lock:
            return [self.flows[k] for k in sorted(self.flows)]

    def get(self, flow_id: str) -> dict | None:
        with self.lock:
            return self.flows.get(flow_id)

    def create(self, flow: dict) -> dict:
        clean = validate_flow(flow)
        with self.lock:
            if clean["id"] in self.flows:
                raise FlowError(f"flow '{clean['id']}' already exists")
            self.flows[clean["id"]] = clean
            self._write(self.flows)
        return clean

    def update(self, flow_id: str, flow: dict) -> dict:
        data = dict(flow)
        data["id"] = flow_id
        clean = validate_flow(data)
        with self.lock:
            if flow_id not in self.flows:
                raise FlowError(f"unknown flow '{flow_id}'")
            self.flows[flow_id] = clean
            self._write(self.flows)
        return clean

    def delete(self, flow_id: str) -> bool:
        with self.lock:
            if flow_id not in self.flows:
                return False
            del self.flows[flow_id]
            self._write(self.flows)
            return True


class FlowRunner:
    """Sequential demo runner with per-step artifacts copied into a bundle."""

    def __init__(self, outbox: Path):
        self.outbox = outbox
        self.runs: dict[str, dict] = {}
        self.lock = threading.Lock()

    def start(self, flow: dict) -> str:
        run_id = time_id()
        run_dir = self.outbox / "_flows" / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        state = {
            "id": run_id,
            "flow_id": flow["id"],
            "flow_name": flow["name"],
            "status": "running",
            "started": _now(),
            "finished": None,
            "steps": [],
            "artifacts": [],
            "error": None,
        }
        with self.lock:
            self.runs[run_id] = state
        threading.Thread(target=self._run, args=(state, flow, run_dir), daemon=True).start()
        return run_id

    def get(self, run_id: str) -> dict | None:
        with self.lock:
            return self.runs.get(run_id)

    def _run(self, state: dict, flow: dict, run_dir: Path) -> None:
        for index, step in enumerate(flow["steps"], 1):
            entry = {
                "index": index,
                "app": step["app"],
                "demo": step["demo"],
                "note": step.get("note", ""),
                "status": "running",
                "started": _now(),
                "finished": None,
                "artifacts": [],
                "error": None,
            }
            state["steps"].append(entry)
            try:
                result = run_demo(
                    step["app"],
                    step["demo"],
                    self.outbox,
                    topic=step.get("topic", ""),
                )
                copy_dir = run_dir / f"{index:02d}-{step['app']}-{step['demo']}"
                copy_dir.mkdir(parents=True, exist_ok=True)
                for artifact in result.get("artifacts", []):
                    source = Path(artifact)
                    if source.is_file():
                        shutil.copy2(source, copy_dir / source.name)
                        rel = str((copy_dir / source.name).relative_to(self.outbox)).replace(
                            "\\", "/"
                        )
                        entry["artifacts"].append(rel)
                        state["artifacts"].append(rel)
                entry["status"] = "succeeded" if result.get("success") else "failed"
                entry["error"] = None if result.get("success") else result.get("message")
            except Exception as exc:  # noqa: BLE001 - reported in the run state
                entry["status"] = "failed"
                entry["error"] = f"{type(exc).__name__}: {exc}"
            entry["finished"] = _now()
            if entry["status"] != "succeeded":
                state["status"] = "failed"
                break
        if state["status"] == "running":
            state["status"] = "succeeded"
        state["finished"] = _now()


def time_id() -> str:
    return datetime.now(UTC).strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:6]
