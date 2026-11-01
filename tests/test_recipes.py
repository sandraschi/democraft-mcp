"""Recipes added for the Oct 31 ArtCraft releases and SolidCraft. Real CLIs, no mocks.

The pure helpers are tested directly; each recipe also runs end to end against the
installed engine (skipped when that app is missing) and its report is checked
against what the engine actually produced.
"""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET

import pytest
from fastapi.testclient import TestClient

from democraft_mcp import recipes
from democraft_mcp.api import create_app
from democraft_mcp.crafts import BY_KEY, run_demo


def _needs(*keys: str):
    missing = [k for k in keys if not BY_KEY[k].installed()]
    return pytest.mark.skipif(bool(missing), reason=f"not installed: {missing}")


def test_every_recipe_is_a_registered_demo():
    for app_key, demo_id in recipes.RECIPES:
        assert app_key in BY_KEY, app_key
        assert demo_id in {d.id for d in BY_KEY[app_key].demos}, (app_key, demo_id)


def test_new_demos_carry_an_added_date():
    for app_key, demo_id in recipes.RECIPES:
        demo = next(d for d in BY_KEY[app_key].demos if d.id == demo_id)
        assert demo.added == "2026-11-01"


def test_solidcraft_is_a_community_member():
    solid = BY_KEY["solid"]
    assert solid.family == "community"
    assert solid.maker == "Tangency Labs"
    assert solid.clone_of == "Autodesk Fusion"


def test_traced_sample_is_valid_svg_with_planted_defects():
    root = ET.fromstring(recipes.traced_sample_svg())
    ids = {el.get("id") for el in root.iter() if el.get("id")}
    assert {"rose", "gear", "hub", "wave"} <= ids
    assert len([i for i in ids if i.startswith("planted-")]) == 5  # + the doubled hub anchor


@pytest.mark.parametrize(
    ("topic", "expect"),
    [
        ("Raspberry Pi Zero 2 W (65 x 30 mm, holes 3.5 mm in)", {"board_w": "65 mm"}),
        ("my board 72.5 x 41 inset 3", {"board_w": "72.5 mm", "hole_inset": "3 mm"}),
        ("70x50", {"board_w": "70 mm", "board_d": "50 mm"}),
        ("", {}),
        ("no numbers here", {}),
    ],
)
def test_board_params(topic, expect):
    _, params = recipes.board_params(topic)
    for k, v in expect.items():
        assert params[k] == v
    if not expect:
        assert params == {}


def test_flatten_keeps_depth_and_order():
    tree = [{"title": "A", "children": [{"title": " B  c ", "children": []}]}, {"title": "D"}]
    assert recipes._flatten(tree) == [(0, "A"), (1, "B c"), (0, "D")]


@_needs("vector")
def test_vector_cleanup_pass_measures_real_reduction(tmp_path):
    res = run_demo("vector", "cleanup-pass", tmp_path, model="none")
    assert res["success"] and res["all_cli_ok"], res["message"]
    rep = json.loads((tmp_path / "vector" / "cleanup-pass" / "cleanup-report.json").read_text())
    assert rep["issues_before"] > 0
    assert rep["issues_after"] == 0
    assert rep["anchors_after"] < rep["anchors_before"]
    assert rep["pixels"]["pixels_changed_pct"] < 5
    assert set(rep["planted_flagged"]) | set(rep["planted_not_flagged"]) == set(recipes.PLANTED)


@_needs("pdf", "word")
def test_pdf_auto_bookmarks_recovers_the_outline(tmp_path):
    res = run_demo("pdf", "auto-bookmarks", tmp_path, model="none")
    assert res["success"] and res["all_cli_ok"], res["message"]
    out = tmp_path / "pdf" / "auto-bookmarks"
    rep = json.loads((out / "bookmarks-report.json").read_text())
    score = rep["score"]
    assert score["bookmarks_left_after_strip"] == 0
    assert score["titles_recovered"] == score["headings_in_original_outline"] == 8
    assert score["same_titles_and_nesting"] is True
    assert (out / "rebuilt.pdf").is_file()


@_needs("grid")
def test_grid_macro_replay_refuses_then_runs(tmp_path):
    res = run_demo("grid", "macro-replay", tmp_path, model="none")
    assert res["success"] and res["all_cli_ok"], res["message"]
    out = tmp_path / "grid" / "macro-replay"
    md = (out / "macro-report.md").read_text(encoding="utf-8")
    assert "Table E1:G3: refused" in md and "G3 holds text" in md
    rows = (out / "result.csv").read_text(encoding="utf-8").splitlines()
    assert "Total,4160,1002" in rows[-1]
    assert any("Total,2339,2230" in r for r in rows)


@_needs("solid")
def test_solid_parametric_bracket_rebuilds_three_variants(tmp_path):
    res = run_demo("solid", "parametric-bracket", tmp_path, model="none")
    assert res["success"] and res["all_cli_ok"], res["message"]
    out = tmp_path / "solid" / "parametric-bracket"
    rows = (out / "variants.csv").read_text(encoding="utf-8").splitlines()
    assert len(rows) == 4
    for name in ("compact", "long", "heavy"):
        assert (out / f"bracket-{name}.step").stat().st_size > 1000
        ev = json.loads((out / f"bracket-{name}.eval.json").read_text(encoding="utf-8-sig"))
        assert ev["bodies"][0]["closed"] is True
        assert not any(t.get("error") for t in ev["timeline"])
    masses = [float(r.split(",")[6]) for r in rows[1:]]
    assert len(set(masses)) == 3  # each parameter set really changed the part


@_needs("solid")
def test_solid_enclosure_fits_a_custom_board(tmp_path):
    res = run_demo("solid", "enclosure-fit", tmp_path, model="none", topic="70 x 50 inset 4")
    assert res["success"] and res["all_cli_ok"], res["message"]
    out = tmp_path / "solid" / "enclosure-fit"
    ev = json.loads((out / "enclosure.eval.json").read_text(encoding="utf-8-sig"))
    params = {p["name"]: p["expression"] for p in ev["params"]}
    assert params["board_w"] == "70 mm" and params["hole_inset"] == "4 mm"
    assert {b["name"] for b in ev["bodies"]} == {"Case", "Lid"}
    for png in ("enclosure-iso.png", "enclosure-section.png", "enclosure-xray.png"):
        assert (out / png).stat().st_size > 10_000


def test_gallery_endpoint_shape(tmp_path):
    run_dir = tmp_path / "cad" / "house-plan"
    run_dir.mkdir(parents=True)
    from PIL import Image

    Image.effect_noise((200, 150), 60).convert("RGB").save(run_dir / "plan.png")
    (run_dir / "tiny.png").write_bytes(b"x" * 10)
    client = TestClient(create_app(outbox=tmp_path))
    tiles = client.get("/api/gallery").json()["tiles"]
    assert [(t["app"], t["demo"], t["file"]) for t in tiles] == [("cad", "house-plan", "plan.png")]
