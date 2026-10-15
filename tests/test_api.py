"""API + tool-op tests: every new endpoint, no CLI side effects except one chat call."""

from __future__ import annotations

from fastapi.testclient import TestClient

from democraft_mcp.server import build_api, craft


def _client() -> TestClient:
    return TestClient(build_api())


def test_status_shape():
    r = _client().get("/api/status")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["apps"] == 13
    assert "uptime_seconds" in body


def test_capabilities_shape():
    r = _client().get("/api/capabilities")
    assert r.status_code == 200
    body = r.json()
    assert "run_demo" in body["operations"]
    assert len(body["apps"]) == 13


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
    assert len(res["apps"]) == 13


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


def test_craft_commands_cad():
    res = craft(operation="craft_commands", app="cad")
    assert res["success"] is True
    assert "result" in res


def test_craft_ollama_models():
    res = craft(operation="ollama_models")
    assert "models" in res or "error_type" in res


def test_prefab_cards_have_content():
    from democraft_mcp.server import show_apps_prefab_card, show_demo_prefab_card

    a = show_apps_prefab_card()
    assert a["success"] is True and a["content"]
    d = show_demo_prefab_card(app="fig")
    assert d["success"] is True and "landing" in d["content"].lower()
