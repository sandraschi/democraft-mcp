"""Registry contract: every app carries hero metadata and more than one demo."""

from democraft_mcp.crafts import APPS


def test_every_app_has_hero_and_two_demos() -> None:
    assert APPS, "registry is empty"
    for app in APPS:
        assert app.clone_of, f"{app.key}: clone_of missing"
        assert app.description, f"{app.key}: description missing"
        assert len(app.gaps) >= 2, f"{app.key}: needs at least two observed gaps"
        assert len(app.demos) >= 2, f"{app.key}: needs more than one demo"
        assert any(d.id == "capability-map" for d in app.demos), (
            f"{app.key}: capability-map demo missing"
        )


def test_capability_demo_has_no_ai_prompt() -> None:
    for app in APPS:
        cap = next(d for d in app.demos if d.id == "capability-map")
        assert cap.ai_prompt == "", f"{app.key}: capability map must not call the LLM"
