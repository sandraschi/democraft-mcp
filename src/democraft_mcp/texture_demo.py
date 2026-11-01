"""TextureCraft demo: a textured prop for Godot, proven by importing it.

TextureCraft (Storytold) puts a smart material on a built-in mesh and exports PBR
maps with a Godot 4 (ORM) preset plus a glTF mesh. This recipe does exactly that
and then lets a local Godot (headless) import the result and report what it
found: surfaces, texture sizes, which material slots are filled. Nothing is
drawn or estimated here; every number in the report comes from TextureCraft's
output files or from Godot's own import.
"""

from __future__ import annotations

import json
import os
import re
import shutil
from pathlib import Path

# prop label -> (builtin mesh, smart material name as listed by `material.list`)
PROPS: dict[str, tuple[str, str]] = {
    "Weathered wooden crate": ("crate", "Wood Weathered"),
    "Mossy stone ball": ("sphere", "Stone Mossy"),
    "Red brick block": ("rounded_cube", "Brick Red"),
    "Granite pillar": ("cylinder", "Granite"),
    "Asphalt slab": ("plane", "Asphalt"),
}
PROP_TOPICS = tuple(PROPS)
# The AI demo may only choose from combinations measured to export cleanly.
AI_MESHES = ("crate", "sphere", "rounded_cube", "cylinder", "plane")
AI_MATERIALS = (
    "Wood Weathered",
    "Stone Mossy",
    "Brick Red",
    "Granite",
    "Asphalt",
    "Concrete",
    "Brick Mossy",
    "Sandstone",
)
AI_TOPICS = (
    "A ruined castle wall",
    "An abandoned warehouse crate",
    "A mossy garden boulder",
    "A fresh asphalt road patch",
    "A brick chimney stack",
    "A granite monument pillar",
    "A sandstone desert block",
    "A concrete bunker slab",
)
AI_PROMPT = (
    "Prop: '{topic}'. Pick the mesh and material that fit it best. Mesh must be one of "
    + ", ".join(AI_MESHES)
    + ". Material must be one of "
    + ", ".join(AI_MATERIALS)
    + '. Return JSON only: {{"mesh": str, "material": str, "why": str}}. No prose.'
)
GODOT = Path(os.getenv("DEMOCRAFT_GODOT", r"C:\Users\sandr\.local\bin\godot.exe"))
TEX_SIZE = 1024

PROJECT_GODOT = """config_version=5

[application]
config/name="democraft_texturecraft"

[rendering]
renderer/rendering_method="gl_compatibility"
"""

# Prints one `DC {json}` line per mesh surface; the recipe parses only those.
CHECK_GD = """extends SceneTree

func _tex(t) -> Variant:
\treturn null if t == null else [t.get_width(), t.get_height()]

func _init():
\tvar ps = load("res://prop.glb")
\tif ps == null:
\t\tprint("DC ", JSON.stringify({"error": "prop.glb did not import"}))
\t\tquit(1)
\t\treturn
\tvar root = ps.instantiate()
\tvar stack = [root]
\twhile stack.size() > 0:
\t\tvar n = stack.pop_back()
\t\tfor c in n.get_children():
\t\t\tstack.append(c)
\t\tif n is MeshInstance3D and n.mesh != null:
\t\t\tvar m: Mesh = n.mesh
\t\t\tfor i in m.get_surface_count():
\t\t\t\tvar mat = m.surface_get_material(i)
\t\t\t\tvar sz = m.get_aabb().size
\t\t\t\tvar row = {"node": str(n.name), "surface": i, "aabb": [sz.x, sz.y, sz.z]}
\t\t\t\tif mat is BaseMaterial3D:
\t\t\t\t\trow["material"] = mat.resource_name
\t\t\t\t\trow["albedo"] = _tex(mat.albedo_texture)
\t\t\t\t\trow["metallic_tex"] = _tex(mat.metallic_texture)
\t\t\t\t\trow["roughness_tex"] = _tex(mat.roughness_texture)
\t\t\t\t\trow["ao_tex"] = _tex(mat.ao_texture)
\t\t\t\t\trow["normal"] = _tex(mat.normal_texture)
\t\t\t\tprint("DC ", JSON.stringify(row))
\tquit()
"""


def pick(topic: str) -> tuple[str, str, str]:
    """(label, mesh, material) for a topic; unknown or empty topics use the first prop."""
    want = (topic or "").strip().lower()
    for label, (mesh, material) in PROPS.items():
        if label.lower() == want:
            return label, mesh, material
    label = next(iter(PROPS))
    return label, *PROPS[label]


def godot_rows(stdout: str) -> list[dict]:
    rows = []
    for line in stdout.splitlines():
        m = re.match(r"\s*DC\s+(\{.*\})\s*$", line)
        if m:
            try:
                rows.append(json.loads(m.group(1)))
            except ValueError:
                continue
    return rows


def _fmt_tex(v: object) -> str:
    return f"{v[0]}x{v[1]}" if isinstance(v, list) and len(v) == 2 else "none"


def pick_ai(ai: dict) -> tuple[str, str, str] | None:
    """(mesh, material, why) from the model's JSON, only if both names are allowed."""
    m = re.search(r"\{.*\}", str((ai or {}).get("text") or ""), re.S)
    if not m:
        return None
    try:
        obj = json.loads(m.group(0))
    except ValueError:
        return None
    mesh, material = str(obj.get("mesh", "")).strip(), str(obj.get("material", "")).strip()
    by_lower = {x.lower(): x for x in AI_MATERIALS}
    if mesh not in AI_MESHES or material.lower() not in by_lower:
        return None
    return mesh, by_lower[material.lower()], str(obj.get("why", "")).strip()[:300]


def godot_prop(ctx) -> dict | None:  # noqa: ANN001 - RunCtx lives in recipes.py
    label, mesh, material = pick(ctx.topic)
    return _build(ctx, label, mesh, material, "")


def godot_prop_ai(ctx) -> dict | None:  # noqa: ANN001
    label = (ctx.topic or AI_TOPICS[0]).strip()
    chosen = pick_ai(ctx.ai)
    if chosen is None:
        mesh, material = "crate", "Wood Weathered"
        note = (
            "The model's answer was missing or named a mesh or material outside the "
            f"allowed lists, so the fallback ({mesh}, {material}) was used."
        )
    else:
        mesh, material, why = chosen
        note = (
            f"The local model chose `{mesh}` + `{material}`: {why}"
            if why
            else (f"The local model chose `{mesh}` + `{material}`.")
        )
    return _build(ctx, label, mesh, material, note)


def _build(ctx, label: str, mesh: str, material: str, note: str) -> dict | None:  # noqa: ANN001
    proj = ctx.run_dir / "godot"
    tex = proj / "textures"
    tex.mkdir(parents=True, exist_ok=True)

    def posix(p: Path) -> str:
        return str(p).replace("\\", "/")

    steps = [
        {"id": "material.apply", "params": {"material": material}},
        {
            "id": "file.exportTextures",
            "params": {
                "dir": posix(tex),
                "preset": "Godot 4 (ORM)",
                "size": TEX_SIZE,
                "format": "png",
            },
        },
        {"id": "file.exportMesh", "params": {"path": posix(proj / "prop.glb")}},
    ]
    doc = {"open": f"builtin:{mesh}", "steps": steps, "save": "prop.tcraft"}
    batch = ctx.write("prop.batch.json", doc)
    res = ctx.do(["batch", str(batch)], timeout_s=240)
    ctx.do(
        ["render", "prop.tcraft", "prop.png", "--size", "960x640", "--samples", "32"],
        timeout_s=240,
    )

    maps = sorted(p.name for p in tex.glob("*.png"))
    glb = proj / "prop.glb"
    lines = [
        f"# TextureCraft to Godot: {label}",
        "",
        f"Built-in mesh `{mesh}`, smart material `{material}`, exported with the "
        f"Godot 4 (ORM) preset at {TEX_SIZE} px plus a glTF mesh.",
        "",
        *([note, ""] if note else []),
        "## TextureCraft output",
        "",
        f"- batch exit: {res.get('returncode')}",
        f"- texture maps written: {len(maps)}" + (f" ({', '.join(maps)})" if maps else ""),
        f"- prop.glb: {glb.stat().st_size} bytes" if glb.is_file() else "- prop.glb: not written",
        "",
    ]

    if not glb.is_file() or not maps:
        lines += ["TextureCraft did not produce the export, so Godot was not run.", ""]
        ctx.write("godot-report.md", "\n".join(lines))
        return None

    if not GODOT.is_file():
        lines += [
            "## Godot import",
            "",
            f"Godot was not found at `{GODOT}` (set DEMOCRAFT_GODOT), so the import "
            "check was skipped. Nothing is claimed about how Godot reads these files.",
            "",
        ]
        ctx.write("godot-report.md", "\n".join(lines))
        return None

    (proj / "project.godot").write_text(PROJECT_GODOT, encoding="utf-8")
    (proj / "check.gd").write_text(CHECK_GD, encoding="utf-8")
    imp = ctx.do_with(GODOT, ["--headless", "--path", str(proj), "--import"], timeout_s=240)
    chk = ctx.do_with(
        GODOT,
        ["--headless", "--path", str(proj), "--script", "res://check.gd"],
        timeout_s=120,
        keep_stdout=200_000,
    )
    rows = godot_rows(chk.get("stdout", ""))
    shutil.rmtree(proj / ".godot", ignore_errors=True)  # import cache, not an artifact
    chk["stdout"] = chk.get("stdout", "")[-3000:]

    lines += ["## Godot import (headless, real import)", ""]
    lines.append(f"- import exit: {imp.get('returncode')}, check exit: {chk.get('returncode')}")
    if not rows or rows[0].get("error"):
        lines += ["- Godot reported no surfaces; the import failed or the check did not run.", ""]
    else:
        lines += [f"- surfaces found: {len(rows)}", ""]
        lines += [
            "| node | surface | albedo | normal | other slots |",
            "|---|---|---|---|---|",
        ]
        for r in rows:
            other = [
                k.replace("_tex", "")
                for k in ("metallic_tex", "roughness_tex", "ao_tex")
                if r.get(k)
            ]
            lines.append(
                f"| {r.get('node')} | {r.get('surface')} | {_fmt_tex(r.get('albedo'))} | "
                f"{_fmt_tex(r.get('normal'))} | {', '.join(other) or 'none'} |"
            )
        lines.append("")
    lines += [
        "`prop.glb` embeds the maps; `godot/textures/` holds the same maps as files. Open "
        "`godot/` as a Godot project to see the prop. Slots shown above are what Godot "
        "filled on import, not what TextureCraft intended.",
        "",
    ]
    ctx.write("godot-report.md", "\n".join(lines))
    return None
