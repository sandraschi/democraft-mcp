"""API + tool-op tests: every new endpoint, no CLI side effects except one chat call."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from democraft_mcp.crafts import BY_KEY
from democraft_mcp.server import build_api, craft


def _needs(app_key: str):
    return pytest.mark.skipif(
        not BY_KEY[app_key].installed(), reason=f"{app_key} wrappee not installed"
    )


def _client() -> TestClient:
    return TestClient(build_api())


def test_status_shape():
    r = _client().get("/api/status")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["apps"] == 14
    assert "uptime_seconds" in body


def test_capabilities_shape():
    r = _client().get("/api/capabilities")
    assert r.status_code == 200
    body = r.json()
    assert "run_demo" in body["operations"]
    assert len(body["apps"]) == 14


def test_chat_alias():
    r = _client().post("/api/chat", json={"prompt": "say ok"})
    assert r.status_code == 200
    assert "ai_step" in r.json() or "skipped" in r.json() or "text" in r.json()


def test_shutdown_needs_confirm():
    r = _client().post("/api/shutdown", json={"confirm": False})
    assert r.status_code == 200
    assert r.json()["needs_confirm"] is True


def test_llm_discover_shape():
    r = _client().get("/api/llm/discover")
    assert r.status_code == 200
    body = r.json()
    assert "ollama" in body["providers"]
    assert "gpu" in body


def test_llm_models_live_or_fallback():
    r = _client().get("/api/llm/models")
    assert r.status_code == 200
    assert len(r.json()["models"]) > 0


def test_llm_onboarding_path():
    r = _client().get("/api/llm/onboarding")
    assert r.status_code == 200
    assert r.json()["path"] in ("ready", "install-ollama")


def test_tools_lists_ops():
    r = _client().get("/api/tools")
    assert "shutdown" in r.json()["tools"][0]["operations"]


def test_runs_lists_outbox():
    r = _client().get("/api/runs")
    assert r.status_code == 200
    assert isinstance(r.json()["runs"], list)


def test_demo_invalid_app_fast():
    r = _client().post("/api/demos/run", json={"app": "nope"})
    assert r.status_code == 200
    assert r.json()["error_type"] == "unknown_app"


def test_craft_list_apps():
    res = craft(operation="list_apps")
    assert res["success"] is True
    assert len(res["apps"]) == 14


def test_craft_app_status():
    res = craft(operation="app_status")
    assert "missing" in res


def test_craft_help():
    res = craft(operation="help")
    assert "run_demo" in res["operations"]


def test_craft_unknown_op():
    res = craft(operation="bogus")  # type: ignore[arg-type]
    assert res["success"] is False


def test_craft_shutdown_needs_confirm():
    res = craft(operation="shutdown")
    assert res["needs_confirm"] is True


@_needs("cad")
def test_craft_commands_cad():
    res = craft(operation="craft_commands", app="cad")
    assert res["success"] is True
    assert "result" in res


def test_craft_ollama_models():
    res = craft(operation="ollama_models")
    assert "models" in res or "error_type" in res


def test_word_topics_exposed():
    r = _client().get("/api/crafts")
    word = next(a for a in r.json()["apps"] if a["key"] == "word")
    assert len(word["demos"][0]["topics"]) == 20


def test_grid_fig_topics_exposed():
    r = _client().get("/api/crafts")
    apps = {a["key"]: a for a in r.json()["apps"]}
    assert len(apps["grid"]["demos"][0]["topics"]) == 12
    assert len(apps["fig"]["demos"][0]["topics"]) == 12


def test_each_app_has_a_topic_driven_demo():
    from democraft_mcp.crafts import APPS as _APPS

    # Deterministic demos (plate-grade, capability-map) carry no topics by
    # design; every app must still offer at least one topic-driven demo.
    for a in _APPS:
        topic_demos = [d for d in a.demos if d.topics]
        assert topic_demos, a.key
        for d in topic_demos:
            assert len(d.topics) >= 8, (a.key, d.id)
            assert d.topic_prompt, (a.key, d.id)


def test_inca_wall_runs_headless(tmp_path):
    from democraft_mcp.crafts import BY_KEY as _BY
    from democraft_mcp.crafts import run_demo

    if not _BY["inca"].runnable():
        pytest.skip("freecadcmd not installed")
    res = run_demo("inca", "dry-stone-wall", tmp_path, topic="Garden dry-stone wall")
    assert res["success"] is True
    names = [__import__("pathlib").Path(p).name for p in res["artifacts"]]
    assert "wall-iso.svg" in names


@_needs("grid")
def test_grid_demo_with_topic(tmp_path):
    from pathlib import Path as _P

    from democraft_mcp.crafts import run_demo

    res = run_demo(
        "grid", "homepage-grid", tmp_path, topic="Sales report 2025 (monthly revenue + units)"
    )
    assert res["success"] is True
    names = [_P(p).name for p in res["artifacts"]]
    assert "report.xlsx" in names and "report.pdf" in names


@_needs("fig")
def test_fig_demo_topic_reaches_canvas(tmp_path):
    from democraft_mcp.crafts import run_demo

    res = run_demo("fig", "landing-page", tmp_path, topic="Pelican bike shop")
    assert res["success"] is True
    script = (tmp_path / "fig" / "landing-page" / "landing.jsonl").read_text(encoding="utf-8")
    assert "text.set" in script
    assert '"id": 8' in script  # brand always set when a topic is picked
    assert (tmp_path / "fig" / "landing-page" / "landing.png").is_file()


@_needs("word")
def test_word_demo_with_topic(tmp_path):
    from democraft_mcp.crafts import run_demo

    res = run_demo("word", "demo-report", tmp_path, topic="Pelicans: a short natural history")
    assert res["success"] is True
    names = [__import__("pathlib").Path(p).name for p in res["artifacts"]]
    assert "report.docx" in names and "report.pdf" in names


@_needs("grid")
def test_artifact_served_and_guarded(tmp_path):
    from democraft_mcp.crafts import run_demo
    from democraft_mcp.server import build_api as _build

    run_demo("grid", "homepage-grid", tmp_path)
    import democraft_mcp.server as srv

    old = srv.OUTBOX
    srv.OUTBOX = tmp_path
    try:
        client = TestClient(_build())
        ok = client.get("/api/artifacts/grid/homepage-grid/lineup.xlsx")
        assert ok.status_code == 200
    finally:
        srv.OUTBOX = old


def test_artifact_guard_no_wrappee(tmp_path):
    import democraft_mcp.server as srv
    from democraft_mcp.server import build_api as _build

    seed = tmp_path / "grid" / "homepage-grid"
    seed.mkdir(parents=True)
    (seed / "x.txt").write_text("hi", encoding="utf-8")
    old = srv.OUTBOX
    srv.OUTBOX = tmp_path
    try:
        client = TestClient(_build())
        bad = client.get("/api/artifacts/grid/homepage-grid/../../secret")
        # httpx may normalize dot-segments before sending; either the guard
        # fires or the route 404s - both prove no file escapes.
        if bad.status_code == 200:
            assert bad.json()["error_type"] == "bad_path"
        else:
            assert bad.status_code == 404
        missing = client.get("/api/artifacts/grid/homepage-grid/nope.txt")
        assert missing.json()["success"] is False
    finally:
        srv.OUTBOX = old


def test_prefab_cards_have_content():
    from democraft_mcp.server import show_apps_prefab_card, show_demo_prefab_card

    a = show_apps_prefab_card()
    assert a["success"] is True and a["content"]
    d = show_demo_prefab_card(app="fig")
    assert d["success"] is True and "landing" in d["content"].lower()
