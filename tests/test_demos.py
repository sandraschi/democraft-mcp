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
    assert "lineup.xlsx" in names


@_needs("word")
def test_word_round_trip(tmp_path):
    res = run_demo("word", "demo-report", tmp_path)
    assert res["success"] is True
    names = [Path(p).name for p in res["artifacts"]]
    assert "brief.docx" in names and "brief.pdf" in names


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
