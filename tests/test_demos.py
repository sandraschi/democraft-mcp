"""democraft-mcp tests: registry integrity, runners, API. All green, no mocks."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from democraft_mcp.crafts import APPS, BY_KEY, run_demo
from democraft_mcp.server import build_api


def _needs(app_key: str):
    return pytest.mark.skipif(
        not BY_KEY[app_key].installed(), reason=f"{app_key} wrappee not installed"
    )


def test_registry_has_13_apps():
    assert len(APPS) == 13
    assert len(BY_KEY) == 13
    for a in APPS:
        assert a.demos, f"{a.key} has no demo"


def test_demo_ids_unique_per_app():
    for a in APPS:
        ids = [d.id for d in a.demos]
        assert len(ids) == len(set(ids))


def test_installed_flags_are_bool():
    for a in APPS:
        assert isinstance(a.installed(), bool)


def test_run_demo_unknown_app(tmp_path):
    res = run_demo("nope", "x", tmp_path)
    assert res["success"] is False
    assert res["error_type"] == "unknown_app"


def test_craft_tool_unknown_app_is_structured():
    """An unknown app key must not raise KeyError out of the MCP tool."""
    from democraft_mcp.server import craft

    res = craft(operation="run_demo", app="nope")
    assert res["success"] is False
    assert res["known_apps"]


@_needs("cad")
def test_focus_is_reported_in_result_and_manifest(tmp_path, monkeypatch):
    from democraft_mcp import crafts

    monkeypatch.setattr(
        crafts, "ensure_foreground", lambda cli: {"ok": True, "window": "CADCraft", "fake": True}
    )
    res = run_demo("cad", "capability-map", tmp_path, focus=True)
    assert res["success"] is True
    assert res["focus"]["window"] == "CADCraft"
    manifest = json.loads((tmp_path / "cad" / "capability-map" / "run.json").read_text("utf-8"))
    assert manifest["focus"]["ok"] is True


@_needs("cad")
def test_focus_is_off_by_default(tmp_path, monkeypatch):
    from democraft_mcp import crafts

    called = []
    monkeypatch.setattr(crafts, "ensure_foreground", lambda cli: called.append(cli))
    res = run_demo("cad", "capability-map", tmp_path)
    assert res["focus"] is None
    assert called == []


@_needs("cad")
def test_cad_demo_runs_headless(tmp_path):
    res = run_demo("cad", "house-plan", tmp_path)
    assert res["success"] is True
    assert res["cli_steps"], "demo must execute CLI steps"
    assert res["artifacts"], "cad demo must produce artifacts"


@_needs("grid")
def test_grid_round_trip(tmp_path):
    res = run_demo("grid", "homepage-grid", tmp_path)
    assert res["success"] is True
    names = [Path(p).name for p in res["artifacts"]]
    assert "report.xlsx" in names and "report.pdf" in names


@_needs("word")
def test_word_round_trip(tmp_path):
    res = run_demo("word", "demo-report", tmp_path)
    assert res["success"] is True
    names = [Path(p).name for p in res["artifacts"]]
    assert "brief.docx" in names and "brief.pdf" in names


@_needs("film")
def test_film_timeline_cut_persists_transition(tmp_path):
    """A dissolve that only lives in the export process is lost by the next render."""
    res = run_demo("film", "timeline-cut", tmp_path)
    assert res["success"] is True
    assert res["all_cli_ok"] is True
    assert any(
        "sequence.applyVideoTransition" in " ".join(step.get("argv") or [])
        for step in res["cli_steps"]
    ), "the transition must be a real CLI step, not a note"
    project = tmp_path / "film" / "timeline-cut" / "cut.fcproj"
    assert "cross_dissolve" in project.read_text(encoding="utf-8"), (
        "the saved project must carry the transition; otherwise poster.png and "
        "transition.png (rendered in later processes) show a hard cut"
    )
    names = [Path(p).name for p in res["artifacts"]]
    assert {"cut.mp4", "poster.png", "transition.png"} <= set(names)


def test_api_health():
    client = TestClient(build_api())
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_api_crafts_lists_13():
    client = TestClient(build_api())
    r = client.get("/api/crafts")
    assert r.status_code == 200
    assert len(r.json()["apps"]) == 13


def test_prompts_meet_3_4_100():
    root = Path(__file__).resolve().parents[1]
    system = (root / "assets" / "prompts" / "system.md").read_text(encoding="utf-8")
    user = (root / "assets" / "prompts" / "user.md").read_text(encoding="utf-8")
    examples = json.loads(
        (root / "assets" / "prompts" / "examples.json").read_text(encoding="utf-8")
    )
    assert len(system.split()) >= 3000, len(system.split())
    assert len(user.split()) >= 4000, len(user.split())
    assert len(examples) >= 100, len(examples)


def test_grid_pivot_report_is_registered_and_deterministic():
    from democraft_mcp import crafts

    grid = next(a for a in crafts.APPS if a.key == "grid")
    demo = next(d for d in grid.demos if d.id == "pivot-report")
    assert demo.ai_prompt == ""
    assert not demo.topics


def test_new_deterministic_demos_are_registered():
    from democraft_mcp import crafts

    wanted = {"grid": "pivot-report", "fig": "retro-board", "word": "scale-fonts"}
    for key, demo_id in wanted.items():
        app = next(a for a in crafts.APPS if a.key == key)
        demo = next(d for d in app.demos if d.id == demo_id)
        assert demo.ai_prompt == ""
        assert not demo.topics
