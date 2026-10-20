"""Flow store: seed catalog, validation, CRUD, and API wiring."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from democraft_mcp.api import create_app
from democraft_mcp.flows import SEED_FLOWS, FlowError, FlowStore, validate_flow


def test_seed_catalog_loads(tmp_path: Path) -> None:
    store = FlowStore(tmp_path / "flows.json")
    flows = store.list()
    assert len(flows) == len(SEED_FLOWS)
    assert store.get("cover-factory") is not None
    assert store.get("title-sequence")["status"] == "exploratory"


def test_create_update_delete(tmp_path: Path) -> None:
    store = FlowStore(tmp_path / "flows.json")
    flow = {
        "id": "test-flow",
        "name": "Test flow",
        "description": "two steps",
        "steps": [
            {"app": "design", "demo": "capability-map", "note": "one"},
            {"app": "photo", "demo": "capability-map"},
        ],
    }
    created = store.create(flow)
    assert created["id"] == "test-flow"
    with pytest.raises(FlowError):
        store.create(flow)

    updated = store.update("test-flow", {**flow, "name": "Renamed"})
    assert updated["name"] == "Renamed"
    assert store.delete("test-flow") is True
    assert store.get("test-flow") is None


def test_validation_rejects_unknown_app_and_demo() -> None:
    with pytest.raises(FlowError):
        validate_flow({"id": "x-flow", "name": "X", "steps": [{"app": "nope", "demo": "d"}]})
    with pytest.raises(FlowError):
        validate_flow({"id": "x-flow", "name": "X", "steps": [{"app": "photo", "demo": "nope"}]})
    with pytest.raises(FlowError):
        validate_flow({"id": "Bad ID", "name": "X", "steps": []})


def test_api_crud_and_blocked_run(tmp_path: Path) -> None:
    client = TestClient(create_app(tmp_path / "outbox"))
    listed = client.get("/api/flows").json()
    assert listed["success"] is True
    assert len(listed["flows"]) == len(SEED_FLOWS)

    new = {
        "id": "api-flow",
        "name": "API flow",
        "steps": [{"app": "design", "demo": "capability-map"}],
    }
    created = client.post("/api/flows", json=new).json()
    assert created["success"] is True
    assert created["flow"]["id"] == "api-flow"
    assert (
        client.put("/api/flows/api-flow", json={**new, "name": "Renamed"}).json()["flow"]["name"]
        == "Renamed"
    )
    assert client.delete("/api/flows/api-flow").json()["success"] is True

    blocked_flow = {
        "id": "blocked-flow",
        "name": "Blocked flow",
        "status": "blocked",
        "blocked_reason": "test",
        "steps": [{"app": "design", "demo": "capability-map"}],
    }
    assert client.post("/api/flows", json=blocked_flow).json()["success"] is True
    blocked = client.post("/api/flows/blocked-flow/run").json()
    assert blocked["success"] is False
    assert "blocked" in blocked["message"]


def test_new_seeds_reach_an_existing_store(tmp_path: Path) -> None:
    path = tmp_path / "flows.json"
    path.write_text(
        '{"flows": [{"id": "mine", "name": "Mine", "status": "ready", '
        '"description": "", "steps": [{"app": "pdf", "demo": "portfolio"}]}]}',
        encoding="utf-8",
    )
    store = FlowStore(path)
    flows = store.list()
    assert store.get("mine") is not None
    assert store.get("video-delivery") is not None
    assert len(flows) == len(SEED_FLOWS) + 1
