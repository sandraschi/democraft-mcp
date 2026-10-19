"""Craft registry + headless demo runners.

[RATIONALE] One module owns every Craft app's install path, CLI shape, and
demo #1 so the MCP tool, the REST API, and the webapp all read the same
truth. No per-app snowflakes, no hardcoded lists in the frontend.

Every demo = optional AI step (Ollama, declared) + real CLI subprocess.
Structured errors beat fake artifacts: engine failures return the real
stderr; `needs_account` exists for the day an engine gates a feature.
Verified 2026-10-15: no generative verbs in any of the 13 CLIs.
"""

from __future__ import annotations

import os
import subprocess
import time
from dataclasses import dataclass, field, replace
from pathlib import Path

PROGRAM_FILES = Path(os.getenv("DEMOCRAFT_PROGRAM_FILES", r"C:\Program Files"))
OLLAMA_URL = os.getenv("DEMOCRAFT_OLLAMA_URL", "http://127.0.0.1:11434")
DEFAULT_MODEL = os.getenv("DEMOCRAFT_MODEL", "gemma4:e4b")
CLI_TIMEOUT_S = 120


@dataclass(frozen=True)
class Demo:
    id: str
    title: str
    blurb: str
    ai_prompt: str
    requires: str = "cli"  # cli | artcraft-account
    topics: tuple[str, ...] = ()  # combobox choices; empty = free text only
    topic_prompt: str = ""  # {topic} template used when a topic is picked; else ai_prompt


def _grid_data(ai: dict, topic: str) -> dict:
    """Parse the AI JSON table or fall back to a real sales mini-table (declared)."""
    import json as _json

    fallback = {
        "title": topic or "Sales report 2025",
        "headers": ["Month", "Revenue", "Units"],
        "rows": [
            ["Jan", "12400", "312"],
            ["Feb", "11800", "298"],
            ["Mar", "14200", "351"],
            ["Apr", "13900", "340"],
            ["May", "15100", "377"],
            ["Jun", "14800", "365"],
        ],
    }
    txt = ai.get("text", "") if ai.get("success") else ""
    start, end = txt.find("{"), txt.rfind("}")
    if start >= 0 and end > start:
        try:
            obj = _json.loads(txt[start : end + 1])
            headers = [str(h)[:40] for h in obj.get("headers", [])][:8]
            rows = [[str(v)[:40] for v in row][:8] for row in obj.get("rows", [])][:20]
            if headers and rows and all(rows):
                return {
                    "title": str(obj.get("title", topic or "Report"))[:80],
                    "headers": headers,
                    "rows": rows,
                }
        except Exception:
            pass
    fallback["title"] = topic or fallback["title"]
    return fallback


def _ai_json(text: str) -> dict:
    """Brace-slice + parse one JSON object from model chatter. Returns {} on failure."""
    import json as _json

    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end <= start:
        return {}
    try:
        obj = _json.loads(text[start : end + 1])
        return obj if isinstance(obj, dict) else {}
    except Exception:
        return {}


def _labeled_lines(text: str, labels: dict[str, str]) -> dict[str, str]:
    """Parse 'Label: value' lines. Values capped; missing labels stay absent."""
    out: dict[str, str] = {}
    lowered = {k: v.lower() for k, v in labels.items()}
    for line in text.splitlines():
        s = line.strip().lstrip("#*- ").strip()
        if ":" not in s:
            continue
        head, _, tail = s.partition(":")
        head = head.strip().lower()
        for key, label in lowered.items():
            if head == label.rstrip(":").lower() and tail.strip():
                out.setdefault(key, tail.strip()[:160])
                break
    return out


BENCH_MODELS: tuple[str, ...] = ("qwen3.8-tools", "mistral-nemo:12b")


def _save_svg(text: str, path) -> bool:
    """Slice <svg>...</svg> out of model chatter. False when there is no SVG."""
    start, end = text.find("<svg"), text.find("</svg>")
    if start >= 0 and end > start:
        path.write_text(text[start : end + len("</svg>")], encoding="utf-8")
        return True
    if start >= 0:
        path.write_text(text[start:], encoding="utf-8")
        return True
    return False


def _model_tag(model: str) -> str:
    return "".join(c if c.isalnum() else "-" for c in model).strip("-")[:40]


FREECADCMD = Path(
    os.getenv(
        "DEMOCRAFT_FREECADCMD",
        r"D:\Dev\repos\FreeCAD\FreeCAD_1.1.1-Windows-x86_64-py311\bin\freecadcmd.exe",
    )
)
FREECAD_REST = os.getenv("DEMOCRAFT_FREECAD_REST", "http://127.0.0.1:10944/api/v1/control/tool")


def _freecad_bridge_probe(steps: list[dict]) -> None:
    """Record freecad-mcp REST reachability (read-only, 5s). Never fails the demo."""
    import httpx

    try:
        r = httpx.post(FREECAD_REST, json={"tool": "bim_status", "arguments": {}}, timeout=5)
        bridge = f"freecad-mcp reachable ({r.status_code})" if r.status_code == 200 else "down"
    except Exception as e:
        bridge = f"unreachable ({type(e).__name__})"
    steps.append(
        {
            "argv": ["freecad-mcp", "bim_status"],
            "returncode": 0,
            "stdout": bridge,
            "stderr": "",
            "ms": 0,
            "success": True,
            "note": "bridge probe - model build below is direct freecadcmd",
        }
    )


def _freecad_iso_boxes(
    run_dir: Path,
    steps: list[dict],
    name: str,
    boxes: list[tuple[tuple, tuple]],
    scale: float = 12.0,
) -> bool:
    """Build boxes in FreeCAD, fuse, TechDraw ISO view. True on real SVG output."""
    if not FREECADCMD.is_file():
        steps.append(
            {
                "argv": ["freecadcmd"],
                "returncode": 1,
                "stdout": "",
                "stderr": "freecadcmd not found - set DEMOCRAFT_FREECADCMD",
                "ms": 0,
                "success": False,
                "error_type": "wrappee_missing",
            }
        )
        return False
    out_svg = run_dir / f"{name}-fragments.svg"
    script = run_dir / f"{name}_fc.py"
    lines = [
        "import FreeCAD, Part, TechDraw",
        f'doc = FreeCAD.newDocument("{name}")',
        "objs = []",
        "i = 0",
    ]
    for n, (p, d) in enumerate(boxes):
        lines += [
            f"p{n} = {p!r}",
            f"d{n} = {d!r}",
            f"b = doc.addObject('Part::Box', 'Block{n}')",
            f"b.Placement.Base = FreeCAD.Vector(*p{n})",
            f"b.Length, b.Width, b.Height = d{n}",
            "objs.append(b)",
        ]
    lines += [
        "doc.recompute()",
        "fused = doc.addObject('Part::MultiFuse','Solid')",
        "fused.Shapes = objs",
        "doc.recompute()",
        "page = doc.addObject('TechDraw::DrawPage','Page')",
        "template = doc.addObject('TechDraw::DrawTemplate','Template')",
        "template.Width = 297.0",
        "template.Height = 210.0",
        "template.Orientation = 'Landscape'",
        "page.Template = template",
        "iso = doc.addObject('TechDraw::DrawViewPart','ViewIso')",
        "iso.Source = [fused]",
        "iso.Direction = (1,-1,1)",
        f"iso.Scale = {scale}",
        "page.addView(iso)",
        "doc.recompute()",
        f"open(r'{out_svg}', 'w').write(TechDraw.viewPartAsSvg(iso))",
        "print('ISO-OK')",
    ]
    script.write_text("\n".join(lines) + "\n", encoding="utf-8")
    res = cli_run(FREECADCMD, [str(script)], run_dir, timeout_s=300)
    res["argv"] = ["freecadcmd", f"{name}_fc.py"]
    steps.append(res)
    if not res.get("success") or not out_svg.is_file():
        res.setdefault("note", "FreeCAD iso failed - 2D set above is the demo")
        return False
    frag = out_svg.read_text(encoding="utf-8")
    (run_dir / f"{name}.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="-6 -4.5 12 9" width="720" height="540">'
        '<rect x="-6" y="-4.5" width="12" height="9" fill="white"/>'
        '<g fill="none" stroke="#111" stroke-width="0.08">' + frag + "</g></svg>",
        encoding="utf-8",
    )
    return True


def _freecad_iso(run_dir: Path, steps: list[dict]) -> dict:
    """True isometric via FreeCAD: wall shell + slab, TechDraw ISO view.

    Crossconnect (1-hop, soft degradation): probes the freecad-mcp REST bridge
    first and records reachability; the model build itself runs headless
    freecadcmd (verified, no server dependency). BIM round-trip
    (wall JSON -> bim_create_wall -> IFC) is demo #2 once verified live.
    """
    _freecad_bridge_probe(steps)
    boxes = [
        ((0, 0, -0.15), (7.28, 5.46, 0.15)),
        ((0, 0, 0), (7.28, 0.24, 2.6)),
        ((0, 5.22, 0), (7.28, 0.24, 2.6)),
        ((0, 0.24, 0), (0.24, 4.98, 2.6)),
        ((7.04, 0.24, 0), (0.24, 4.98, 2.6)),
    ]
    ok = _freecad_iso_boxes(run_dir, steps, "iso", boxes)
    if not ok:
        return {"success": False, "message": "FreeCAD iso failed - 2D set above is the demo"}
    return {"success": True, "message": "true isometric rendered"}


def _fit_viewbox(svg_path, frag_path) -> None:
    """Tighten an iso SVG viewBox to its drawn bounds (else tiny models blow up strokes).

    Bounds come from the raw fragment file so header/rect numbers cannot pollute them.
    """
    import re as _re

    frag = frag_path.read_text(encoding="utf-8")
    ds = _re.findall(r'd="([^"]+)"', frag)
    nums: list[float] = []
    for d in ds:
        nums += [float(n) for n in _re.findall(r"-?\d+(?:\.\d+)?", d)]
    pairs = list(zip(nums[::2], nums[1::2], strict=False))
    if not pairs:
        return
    xs = [p[0] for p in pairs]
    ys = [p[1] for p in pairs]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    pad = max((x1 - x0), (y1 - y0), 0.1) * 0.08
    w, h = (x1 - x0) + pad * 2, (y1 - y0) + pad * 2
    stroke = max(min(w, h) / 120.0, 0.005)
    head = (
        '<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="{x0 - pad:.3f} {y0 - pad:.3f} {w:.3f} {h:.3f}" width="720" height="540">'
        f'<rect x="{x0 - pad:.3f}" y="{y0 - pad:.3f}" width="{w:.3f}" '
        f'height="{h:.3f}" fill="white"/>'
        f'<g fill="none" stroke="#111" stroke-width="{stroke:.3f}">'
    )
    svg_path.write_text(head + frag + "</g></svg>", encoding="utf-8")


def _first_numeric_col(rows: list[list[str]], ncols: int) -> int:
    for c in range(ncols):
        try:
            [float(r[c].replace(",", "")) for r in rows if len(r) > c]
            return c
        except (ValueError, IndexError):
            continue
    return -1


FIG_TOPICS: tuple[str, ...] = (
    "Pelican bike shop",
    "Vienna coffee map",
    "Sourdough bakery",
    "Danube cycling guide",
    "Watch repair atelier",
    "Community tool library",
    "Night tram photography",
    "Small-house architects",
    "Secondhand bookshop",
    "Urban beekeeping co-op",
    "Kids bike school",
    "Lake swimming guide",
)


GRID_TOPICS: tuple[str, ...] = (
    "Sales report 2025 (monthly revenue + units)",
    "Pelican census (Danube counts by month)",
    "Bike shop inventory (models, stock, price)",
    "Household energy 2025 (kWh by month)",
    "Reading log 2025 (books, pages, rating)",
    "Marathon training (week, km, long run)",
    "Sourdough log (bake, hydration, score)",
    "Vienna rents (district, sqm, euros)",
    "Coffee spending 2025 (month, cups, euros)",
    "Fleet demo runs (app, seconds, artifacts)",
    "Garden harvest (crop, kg, week)",
    "Rainy days 2025 (month, days, mm)",
)


WORD_TOPICS: tuple[str, ...] = (
    "Why headless demos beat screenshots",
    "A field guide to DXF",
    "The quiet craft of release notes",
    "What EDLs remember",
    "Danube floodplains: a cyclist's notes",
    "Vienna's coffee-house WiFi, ranked",
    "How spreadsheets lie",
    "The 56-second ident",
    "Pelicans: a short natural history",
    "Bike lanes I have loved",
    "What print still does better",
    "Fonts that survive fax",
    "A defense of plain text",
    "The backup that saved October",
    "Reading a floorplan",
    "Why every demo needs a failure mode",
    "The care and feeding of local LLMs",
    "Small houses, big ideas",
    "What I learned bouncing stems",
    "Port registries and other love letters",
)


CAD_TOPICS: tuple[str, ...] = (
    "Machiya townhouse",
    "Alpine hut",
    "Danube houseboat",
    "Courtyard house",
    "Tiny cabin",
    "Corner bakery",
    "Bike workshop",
    "Lakeside sauna",
)


DECK_TOPICS: tuple[str, ...] = (
    "Democraft pitch",
    "Pelican bike shop launch",
    "Sourdough bakery plan",
    "Vienna coffee map",
    "Night tram photo show",
    "Urban beekeeping",
    "Kids bike school",
    "Tool library opening",
)


DESIGN_TOPICS: tuple[str, ...] = (
    "Pelican + house spread",
    "Bakery menu spread",
    "Bike catalog spread",
    "Photo essay spread",
    "Coffee map spread",
    "Garden year spread",
    "Lake guide spread",
    "Workshop manual spread",
)


EFFECT_TOPICS: tuple[str, ...] = (
    "Democraft title",
    "Pelican reveal",
    "Bakery morning",
    "Night tram",
    "Lake dawn",
    "Bike race",
    "Bread oven",
    "Rain window",
)


FILM_TOPICS: tuple[str, ...] = (
    "Pelican storyboard",
    "Bakery morning",
    "Night tram",
    "Danube crossing",
    "Market day",
    "Lake swim",
    "Bike commute",
    "Storm front",
)


SOUND_TOPICS: tuple[str, ...] = (
    "Groove analysis",
    "Mix balance",
    "Drum sound",
    "Bass line",
    "Hat patterns",
    "Stereo image",
    "Dynamics",
    "Arrangement",
)


PDF_TOPICS: tuple[str, ...] = (
    "Demo outputs portfolio",
    "Bakery docs",
    "Bike catalog",
    "Photo set",
    "Coffee map pack",
    "Garden year",
    "Lake guide",
    "Workshop manual",
)


LIGHT_TOPICS: tuple[str, ...] = (
    "Punchy daylight",
    "Moody evening",
    "Warm print",
    "Cool screen",
    "High contrast",
    "Soft pastel",
    "B&W conversion",
    "Vivid color",
)


PHOTO_TOPICS: tuple[str, ...] = (
    "Pelican on a bike",
    "House by the Danube",
    "Coffee cup steaming",
    "Bike leaning on a wall",
    "Sailboat at dawn",
    "Cat on a windowsill",
    "Sourdough loaf",
    "Tram at night",
    "Mountain hut",
    "Lighthouse",
)


VECTOR_TOPICS: tuple[str, ...] = PHOTO_TOPICS


INCA_TOPICS: tuple[str, ...] = (
    "Sacsayhuaman course",
    "Terrace retaining wall",
    "Garden dry-stone wall",
    "Fire pit ring",
    "Stair cheek walls",
    "Well head",
    "Field gate posts",
    "Sun temple plinth",
)


@dataclass(frozen=True)
class CraftApp:
    key: str
    name: str
    cli: str  # exe name under C:\Program Files\<Name>\
    tagline: str
    demos: tuple[Demo, ...] = field(default_factory=tuple)
    clone_of: str = ""
    description: str = ""
    gaps: tuple[str, ...] = ()

    @property
    def cli_path(self) -> Path:
        return PROGRAM_FILES / self.name / self.cli

    def installed(self) -> bool:
        return self.cli_path.is_file()

    def runnable(self) -> bool:
        """A demo can run without its wrappee when a fallback engine exists."""
        if self.key == "inca":
            return FREECADCMD.is_file()
        return self.installed()


APPS: tuple[CraftApp, ...] = (
    CraftApp(
        "cad",
        "CADCraft",
        "cadcraft-cli.exe",
        "CAD: DXF/DWG plans, headless sample + script runs.",
        (
            Demo(
                "house-plan",
                "Demo 1: small house set (pick a type)",
                "Scripted metric plan (rooms, labels, dims) + south elevation: "
                "DXF, PNG, PDF, SVG. Topic titles the sheet. 2D engine: no true isometric.",
                "List rooms of a small Japanese house plan (genkan, washitsu, "
                "engawa, LD, bath) as JSON list of {room, note}. No prose.",
                topics=CAD_TOPICS,
                topic_prompt="Return JSON for a '{topic}' small house: {{\"title\": str, "
                '"rooms": [{{name, note}} x5]}}. No prose.',
            ),
        ),
    ),
    CraftApp(
        "deck",
        "DeckCraft",
        "deckcraft-cli.exe",
        "Slides: sample render + scripted runs.",
        (
            Demo(
                "pitch-deck",
                "Demo 1: pitch deck (pick a subject)",
                "Render the sample deck to PNGs; local AI outlines 5 slides "
                "for your subject, saved as outline.md.",
                "Outline a 5-slide pitch deck for 'democraft-mcp' as JSON "
                "list of {slide, bullets}. No prose.",
                topics=DECK_TOPICS,
                topic_prompt="Outline a 5-slide pitch deck for '{topic}' as JSON "
                "list of {{slide, bullets}}. No prose.",
            ),
        ),
    ),
    CraftApp(
        "design",
        "DesignCraft",
        "designcraft-cli.exe",
        "Page layout: threaded stories, PDF/X-4 + EPUB.",
        (
            Demo(
                "print-spread",
                "Demo 1: print spread (pick a subject)",
                "Sample magazine render to PNGs; local AI describes the "
                "spread for your subject, saved as brief.md.",
                "Describe a 2-page spread (house plan + pelican) as JSON "
                "{left, right, palette}. No prose.",
                topics=DESIGN_TOPICS,
                topic_prompt="Describe a 2-page print spread about '{topic}' as JSON "
                "{{left, right, palette}}. No prose.",
            ),
        ),
    ),
    CraftApp(
        "effect",
        "EffectCraft",
        "effectcraft-cli.exe",
        "Motion graphics: engine info + still renders.",
        (
            Demo(
                "title-card",
                "Demo 1: title-card still (pick a subject)",
                "Demo project still render; local AI writes the title spec "
                "for your subject, saved as brief.md.",
                "Write a title-card spec (text, palette, timing) as JSON. No prose.",
                topics=EFFECT_TOPICS,
                topic_prompt="Write a title-card spec for '{topic}' (text, palette, "
                "timing) as JSON. No prose.",
            ),
        ),
    ),
    CraftApp(
        "fig",
        "FigCraft",
        "figcraft-cli.exe",
        "Interface design: templates headless.",
        (
            Demo(
                "landing-page",
                "Demo 1: landing page + copy brief (pick a topic)",
                "Landing-page template built headless; 14 text nodes (brand, "
                "hero, features, cards, quote, CTA) set from your topic "
                "before render + PNG. Stats/person/buttons stay template.",
                "Write a landing-page copy brief as markdown: # headline, "
                "3 sections with one line each, one call to action.",
                topics=FIG_TOPICS,
                topic_prompt="Write landing-page copy for '{topic}' as labeled lines, "
                "one per line, no extra text: Headline: ... / Sub: ... / Features title: ... / "
                "Features sub: ... / F1 title: ... / F1 text: ... / F2 title: ... / F2 text: ... / "
                "F3 title: ... / F3 text: ... / Quote: ... (illustrative) / CTA title: ... / "
                "CTA sub: ... Keep every line under 25 words.",
            ),
        ),
    ),
    CraftApp(
        "film",
        "FilmCraft",
        "filmcraft-cli.exe",
        "Video: project inspect + scripted runs.",
        (
            Demo(
                "storyboard",
                "Demo 1: storyboard + AI board (pick a subject)",
                "Real EDL export; local AI boards 3 shots for your subject, "
                "saved as brief.md. Assembly stays project-gated.",
                "Board a 3-shot storyboard (pelican, bike, reveal) as JSON "
                "list of {shot, lens, action}. No prose.",
                topics=FILM_TOPICS,
                topic_prompt="Board a 3-shot storyboard about '{topic}' as JSON "
                "list of {{shot, lens, action}}. No prose.",
            ),
        ),
    ),
    CraftApp(
        "grid",
        "GridCraft",
        "gridcraft-cli.exe",
        "Spreadsheets: AI-filled data, formatting, charts, sparklines, PDF.",
        (
            Demo(
                "homepage-grid",
                "Demo 1: topic report sheet (try Sales report 2025)",
                "Pick a topic: local AI fills the data, the engine formats, "
                "charts, sparklines, and exports XLSX + PDF.",
                'Return JSON only: {"title": str, "headers": [3-5 short column '
                'names], "rows": [[6-10 rows of short plain values, numbers '
                "bare]]}. No prose.",
                topics=GRID_TOPICS,
                topic_prompt="Return JSON only about '{topic}': {{\"title\": str, "
                '"headers": [3-5 short column names], "rows": [[6-10 rows of '
                "short plain values, numbers bare]]}}. No prose.",
            ),
        ),
    ),
    CraftApp(
        "sound",
        "SoundCraft",
        "soundcraft-cli.exe",
        "Audio: demo project inspect + bounce.",
        (
            Demo(
                "ident-jingle",
                "Demo 1: Midnight Groove bounce (~56s)",
                "Bundled demo project rendered locally to WAV. No AI composes "
                "music; the AI step writes only the words describing it.",
                "Brief the bounced groove (tempo, key, layers heard) as JSON. No prose.",
                topics=SOUND_TOPICS,
                topic_prompt="Brief the bounced groove with focus on '{topic}' "
                "(tempo, key, layers) as JSON. No prose.",
            ),
        ),
    ),
    CraftApp(
        "word",
        "WordCraft",
        "wordcraft-cli.exe",
        "Documents: md/docx/pdf round-trips.",
        (
            Demo(
                "demo-report",
                "Demo 1: one-page report, your topic",
                "Pick a topic (or write your own): local AI drafts the report, "
                "WordCraft's Report template styles it to DOCX + PDF.",
                "Draft a one-page report as markdown: a # title line, then 4-6 short paragraphs.",
                topics=WORD_TOPICS,
                topic_prompt="Write a one-page report on '{topic}' as markdown: a # title "
                "line, then 4-6 short paragraphs. No preamble.",
            ),
        ),
    ),
    CraftApp(
        "pdf",
        "PdfCraft",
        "pdfcraft-cli.exe",
        "PDF: combine, render, anatomy.",
        (
            Demo(
                "portfolio",
                "Demo 1: portfolio PDF (pick a subject)",
                "Combine demo PDFs into one portfolio + thumbnail render; "
                "local AI names the sections for your subject, saved as brief.md.",
                "Name 4 portfolio sections for craft demo outputs as JSON list. No prose.",
                topics=PDF_TOPICS,
                topic_prompt="Name 4 portfolio sections for '{topic}' documents "
                "as JSON list. No prose.",
            ),
        ),
    ),
    CraftApp(
        "light",
        "LightCraft",
        "lightcraft-cli.exe",
        "Photo grade: headless develop runs.",
        (
            Demo(
                "grade-pelican",
                "Demo 1: grade with intent (pick one)",
                "Grade pass over the demo PNG; local AI suggests tweaks for "
                "your intent, saved as brief.md.",
                "Suggest exposure/contrast/saturation tweaks for a flat PNG "
                "as JSON {exposure, contrast, saturation, note}. No prose.",
                topics=LIGHT_TOPICS,
                topic_prompt="Suggest exposure/contrast/saturation tweaks for a flat "
                "PNG aiming at '{topic}' as JSON {{exposure, contrast, "
                "saturation, note}}. No prose.",
            ),
        ),
    ),
    CraftApp(
        "photo",
        "PhotoCraft",
        "photocraft-cli.exe",
        "Photo: non-destructive adjustment stacks, masks, filters, batch.",
        (
            Demo(
                "plate-grade",
                "Demo 1: plate restoration (Böcklin, 1880)",
                "A real public-domain plate through PhotoCraft's non-destructive "
                "stack: Black & White, Curves and Gradient Map adjustment layers, "
                "saved as .pcraft with the layer tree intact, then flattened to "
                "PNG/JPG. Deterministic recipe; the AI step only writes the note.",
                "Write a three-line restoration note for a 19th-century painting "
                "plate: tone, grain, contrast. No other text.",
                "cli",
            ),
            Demo(
                "pelican-photo",
                "Demo 2: pelican benchmark (pick a subject)",
                "Same plain prompt on every contender model, each rendered "
                "through convert/info. Quality deltas are the models'.",
                "Draw an SVG of a pelican riding a bicycle. Raw SVG only.",
                "cli",
                topics=PHOTO_TOPICS,
                topic_prompt="Draw an SVG of {topic}. Raw SVG only.",
            ),
        ),
    ),
    CraftApp(
        "vector",
        "VectorCraft",
        "vectorcraft-cli.exe",
        "Vector: run + export pipeline.",
        (
            Demo(
                "pelican-vector",
                "Demo 1: pelican benchmark (pick a subject)",
                "Same plain prompt on every contender model, each rendered "
                "through run/export. Compare with photo.",
                "Draw an SVG of a pelican riding a bicycle. Raw SVG only.",
                "cli",
                topics=VECTOR_TOPICS,
                topic_prompt="Draw an SVG of {topic}. Raw SVG only.",
            ),
        ),
    ),
    CraftApp(
        "inca",
        "IncaCraft",
        "incacraft-cli.exe",
        "3D dry-stone masonry (PROPOSED wrappee - FreeCAD engine until it exists).",
        (
            Demo(
                "dry-stone-wall",
                "Demo 1: dry-stone course (pick a wall)",
                "Ashlar courses generated as real FreeCAD solids, TechDraw "
                "isometric export. No mortar, no fakes.",
                "Describe a dry-stone wall program as JSON {title, courses, notes}. No prose.",
                "cli",
                topics=INCA_TOPICS,
                topic_prompt="Describe a dry-stone '{topic}' wall program as JSON "
                "{{title, courses, notes}}. No prose.",
            ),
        ),
    ),
)

HERO: dict[str, dict[str, object]] = {
    "cad": {
        "clone_of": "AutoCAD / BricsCAD",
        "description": "2D drafting with a scripted command surface: metric plans, "
        "elevations, room schedules, DXF/PDF/SVG export.",
        "gaps": (
            "No AutoLISP dialect (generic scripting only)",
            "2D engine: no true isometric or 3D solids",
            "No dynamic-block parametrics in the catalog",
        ),
    },
    "deck": {
        "clone_of": "Microsoft PowerPoint / Keynote",
        "description": "Slide decks rendered headless from the CLI, with an AI outline "
        "step that writes the brief before the engine draws.",
        "gaps": (
            "No Office round-trip verified (pptx import/export)",
            "No third-party template ecosystem",
        ),
    },
    "design": {
        "clone_of": "Adobe InDesign",
        "description": "Page layout with threaded stories, facing pages, styles, "
        "tables, footnotes, PDF and EPUB export.",
        "gaps": (
            "No master-page command surface (parent pages are script-level)",
            "No cloud collaboration or review",
            "Book sync is script-level, not a UI workflow",
        ),
    },
    "effect": {
        "clone_of": "Adobe After Effects",
        "description": "Motion-graphics projects rendered headless: keyframes, "
        "expressions, cameras, audio, export.",
        "gaps": (
            "No particle system in the command catalog",
            "No third-party plugin ecosystem",
        ),
    },
    "fig": {
        "clone_of": "Figma",
        "description": "Interface design with frames, auto layout, components, "
        "variants, styles and prototyping.",
        "gaps": (
            "No multiplayer editing",
            "No community/plugin marketplace",
            "No cloud file history",
        ),
    },
    "film": {
        "clone_of": "Adobe Premiere Pro",
        "description": "Timeline editing with keyframes, audio, transitions, color, "
        "subtitles and proxy workflows.",
        "gaps": (
            "No hardware-accelerated proxy pipeline verified",
            "No third-party plugin ecosystem",
        ),
    },
    "grid": {
        "clone_of": "Microsoft Excel",
        "description": "Workbook engine: formulas, charts, pivots, macros, import and export.",
        "gaps": (
            "No VBA/macro compatibility",
            "No xlsx round-trip verified",
        ),
    },
    "light": {
        "clone_of": "Blender / Cinema 4D (lighting)",
        "description": "Scene lighting and rendering from the command surface.",
        "gaps": (
            "No material or HDRI authoring in the catalog",
            "No bake pipeline",
        ),
    },
    "pdf": {
        "clone_of": "Adobe Acrobat Pro",
        "description": "PDF operations from the CLI: the working set the other "
        "crafts hand their exports to.",
        "gaps": (
            "No command catalog (the CLI has no `commands` verb)",
            "Verbs beyond the shipped set are not discoverable from the app",
        ),
    },
    "photo": {
        "clone_of": "Adobe Photoshop",
        "description": "Raster editing with layers, masks, filters, RAW handling and batch export.",
        "gaps": (
            "No generative fill (editor, not generator)",
            "No cloud asset sync",
        ),
    },
    "sound": {
        "clone_of": "Ableton Live / Pro Tools",
        "description": "Session audio: MIDI, mixing, effects, recording and export.",
        "gaps": (
            "No VST plugin hosting verified",
            "No cloud collaboration",
        ),
    },
    "vector": {
        "clone_of": "Adobe Illustrator",
        "description": "Vector paths, gradients, text and SVG/PDF export.",
        "gaps": (
            "No boolean path operations in the catalog",
            "No plugin ecosystem",
        ),
    },
    "word": {
        "clone_of": "Microsoft Word",
        "description": "Document editing with styles, tables and PDF export.",
        "gaps": (
            "No DOCX import/export in the catalog",
            "No image-placement verbs",
        ),
    },
    "inca": {
        "clone_of": "Autodesk Inventor / FreeCAD",
        "description": "Parametric CAD demos with a FreeCAD fallback when the "
        "IncaCraft wrappee is absent.",
        "gaps": (
            "Wrappee not installed on this machine (FreeCAD fallback)",
            "Parametric feature tree limited to the demo set",
        ),
    },
}

CAPABILITY_DEMO = Demo(
    "capability-map",
    "Capability map",
    "Dumps the app's real command catalog (or --help fallback) to capabilities.txt. "
    "No AI step: this is the surface the other demos choose from.",
    "",
)

APPS = tuple(
    replace(
        app,
        clone_of=str(HERO.get(app.key, {}).get("clone_of", "")),
        description=str(HERO.get(app.key, {}).get("description", app.tagline)),
        gaps=tuple(HERO.get(app.key, {}).get("gaps", ())),
        demos=(*app.demos, CAPABILITY_DEMO),
    )
    for app in APPS
)

BY_KEY = {a.key: a for a in APPS}

_FALLBACK_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300">'
    '<ellipse cx="200" cy="120" rx="90" ry="60"/>'
    '<circle cx="280" cy="80" r="28"/>'
    '<rect x="60" y="200" width="280" height="12" rx="6"/>'
    '<circle cx="120" cy="240" r="34"/><circle cx="280" cy="240" r="34"/></svg>'
)


def ai_step(prompt: str, model: str = DEFAULT_MODEL, timeout: int = 90) -> dict:
    """One local-LLM call. Never raises: failure is a declared skip."""
    import httpx

    started = time.time()
    try:
        r = httpx.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=timeout,
        )
        r.raise_for_status()
        return {
            "success": True,
            "model": model,
            "text": r.json().get("response", "")[:4000],
            "ms": int((time.time() - started) * 1000),
            "skipped": False,
        }
    except Exception as e:
        return {
            "success": False,
            "model": model,
            "skipped": True,
            "error": f"{type(e).__name__}: {e}",
            "ms": int((time.time() - started) * 1000),
        }


def cli_run(exe: Path, argv: list[str], cwd: Path, timeout_s: int = CLI_TIMEOUT_S) -> dict:
    """Run one CLI argv. Returns the real result, including real failures."""
    started = time.time()
    try:
        p = subprocess.run(
            [str(exe), *argv],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_s,
        )
        return {
            "success": p.returncode == 0,
            "argv": argv,
            "returncode": p.returncode,
            "stdout": p.stdout[-6000:],
            "stderr": p.stderr[-2000:],
            "ms": int((time.time() - started) * 1000),
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "argv": argv,
            "error_type": "timeout",
            "error": f"exceeded {timeout_s}s",
            "ms": timeout_s * 1000,
        }
    except Exception as e:
        return {
            "success": False,
            "argv": argv,
            "error_type": "spawn",
            "error": f"{type(e).__name__}: {e}",
        }


def run_demo(
    app_key: str, demo_id: str, outbox: Path, model: str = DEFAULT_MODEL, topic: str = ""
) -> dict:
    """Run a demo end to end. Returns dialogic {success, message, ...}."""
    app = BY_KEY.get(app_key)
    if app is None:
        return {
            "success": False,
            "message": f"unknown app '{app_key}'",
            "error_type": "unknown_app",
            "known_apps": sorted(BY_KEY),
        }
    demo = next((d for d in app.demos if d.id == demo_id), None)
    if demo is None:
        return {
            "success": False,
            "message": f"unknown demo '{demo_id}' for {app_key}",
            "known_demos": [d.id for d in app.demos],
        }
    if not app.runnable():
        return {
            "success": False,
            "message": f"{app.name} not installed at {app.cli_path}",
            "error_type": "wrappee_missing",
            "recovery": f"Install {app.name}, then retry. See docs/ONBOARDING.md.",
        }
    outbox.mkdir(parents=True, exist_ok=True)
    run_dir = outbox / app_key / demo_id
    run_dir.mkdir(parents=True, exist_ok=True)

    if demo.id == "capability-map":
        res = cli_run(app.cli_path, ["commands"], run_dir)
        text = (res.get("stdout") or "") + (res.get("stderr") or "")
        if not res.get("success") or not text.strip():
            res = cli_run(app.cli_path, ["--help"], run_dir)
            text = (res.get("stdout") or "") + (res.get("stderr") or "")
        (run_dir / "capabilities.txt").write_text(text[:200000] or "(no output)", encoding="utf-8")
        arts = [str(p) for p in sorted(run_dir.rglob("*")) if p.is_file()]
        return {
            "success": bool(res.get("success")),
            "message": f"{app.name} capability map written ({len(text)} chars).",
            "ai_step": {"skipped": True, "model": model, "reason": "no AI step"},
            "cli_steps": [res],
            "artifacts": arts,
            "all_cli_ok": bool(res.get("success")),
            "run_dir": str(run_dir),
        }

    ai = ai_step(
        demo.ai_prompt
        if not topic
        else (demo.topic_prompt.format(topic=topic) if demo.topic_prompt else demo.ai_prompt),
        model,
    )
    steps: list[dict] = []
    artifacts: list[str] = []

    if (
        demo.topics
        and ai.get("success")
        and ai.get("text")
        and app_key
        in (
            "cad",
            "deck",
            "design",
            "effect",
            "film",
            "sound",
            "pdf",
            "light",
            "inca",
        )
    ):
        (run_dir / "brief.md").write_text(ai["text"][:4000], encoding="utf-8")

    def do(argv: list[str]) -> dict:
        res = cli_run(app.cli_path, argv, run_dir)
        steps.append(res)
        for f in sorted(run_dir.rglob("*")):
            if f.is_file() and str(f) not in artifacts:
                artifacts.append(str(f))
        return res

    k = app_key
    if k == "cad":
        plan = [
            ["style", '{"name": "ArialTT", "font": "Arial"}'],
            [
                "dimstyle",
                '{"name": "ISO-25", "DIMTXT": 0.25, "arrowSize": 0.3, "DIMTXSTY": "ArialTT"}',
            ],
            ["rectang", '{"p1": [0, 0], "p2": [7.28, 0.24]}'],
            ["rectang", '{"p1": [0, 5.22], "p2": [7.28, 5.46]}'],
            ["rectang", '{"p1": [0, 0.24], "p2": [0.24, 5.22]}'],
            ["rectang", '{"p1": [7.04, 0.24], "p2": [7.28, 5.22]}'],
            ["rectang", '{"p1": [1.82, 0.24], "p2": [1.94, 2.06]}'],
            ["rectang", '{"p1": [0.24, 1.94], "p2": [7.04, 2.06]}'],
            ["rectang", '{"p1": [3.64, 2.06], "p2": [3.76, 5.22]}'],
            ["rectang", '{"p1": [5.46, 0.24], "p2": [5.58, 2.06]}'],
            ["hatch", '{"points": [[3.64, 0.12]], "pattern": "SOLID"}'],
            ["hatch", '{"points": [[3.64, 5.34]], "pattern": "SOLID"}'],
            ["hatch", '{"points": [[0.12, 2.7]], "pattern": "SOLID"}'],
            ["hatch", '{"points": [[7.16, 2.7]], "pattern": "SOLID"}'],
            ["hatch", '{"points": [[1.88, 1.0]], "pattern": "SOLID"}'],
            ["hatch", '{"points": [[3.0, 2.0]], "pattern": "SOLID"}'],
            ["hatch", '{"points": [[3.7, 3.6]], "pattern": "SOLID"}'],
            ["hatch", '{"points": [[5.52, 1.0]], "pattern": "SOLID"}'],
            [
                "mtext",
                '{"at": [1.03, 1.0], "text": "genkan", "height": 0.16, '
                '"style": "ArialTT", "align": "center"}',
            ],
            [
                "mtext",
                '{"at": [3.7, 1.0], "text": "hall", "height": 0.2, '
                '"style": "ArialTT", "align": "center"}',
            ],
            [
                "mtext",
                '{"at": [1.94, 3.64], "text": "washitsu", "height": 0.2, '
                '"style": "ArialTT", "align": "center"}',
            ],
            [
                "mtext",
                '{"at": [5.4, 3.64], "text": "LD", "height": 0.2, '
                '"style": "ArialTT", "align": "center"}',
            ],
            [
                "mtext",
                '{"at": [6.31, 1.0], "text": "bath", "height": 0.2, '
                '"style": "ArialTT", "align": "center"}',
            ],
            [
                "table",
                '{"at": [8.0, 5.4], "rows": 5, "cols": 2, "title": "Room schedule", '
                '"header": ["Room", "Finish"], "cells": [["genkan", "stone"], '
                '["hall", "wood"], ["washitsu", "tatami"], ["LD", "wood"], '
                '["bath", "tile"]]}',
            ],
            ["mleader", '{"points": [[5.0, 5.46], [5.0, 6.2]], "text": "window w1.5"}'],
            ["dimlinear", '{"p1": [0, 0], "p2": [7.28, 0], "at": [3.64, -1.2]}'],
            ["dimlinear", '{"p1": [0, 0], "p2": [0, 5.46], "at": [-0.6, 2.73]}'],
        ]
        if topic:
            import json as _json

            plan.insert(
                0,
                ["text", _json.dumps({"at": [0, 6.6], "text": topic[:40], "height": 0.3})],
            )
        argv: list[str] = ["run", "--metric"]
        for cid, params in plan:
            argv += ["--cmd", f"{cid} {params}"]
        do([*argv, "--save", "house.dxf", "--export", "house-plan.png"])
        do(["convert", "house.dxf", "house-plan.pdf"])
        do(["convert", "house.dxf", "house-plan.svg"])
        do(["info", "house.dxf"])
        elev = [
            ["line", '{"points": [[-1, 0], [8.28, 0]]}'],
            ["rectang", '{"p1": [0, 0], "p2": [7.28, 2.6]}'],
            ["line", '{"points": [[-0.5, 2.6], [3.64, 4.1]]}'],
            ["line", '{"points": [[3.64, 4.1], [7.78, 2.6]]}'],
            ["rectang", '{"p1": [1.0, 1.0], "p2": [2.5, 2.0]}'],
            ["rectang", '{"p1": [4.5, 0], "p2": [5.5, 2.1]}'],
            ["text", '{"at": [3.64, 4.5], "text": "SOUTH ELEVATION", "height": 0.25}'],
            ["dimlinear", '{"p1": [0, 0], "p2": [7.28, 0], "at": [3.64, -0.6]}'],
        ]
        argv = ["run", "--metric"]
        for cid, params in elev:
            argv += ["--cmd", f"{cid} {params}"]
        do([*argv, "--save", "elevation-south.dxf", "--export", "elevation-south.png"])
        do(["convert", "elevation-south.dxf", "elevation-south.pdf"])
        iso = _freecad_iso(run_dir, steps)
        if isinstance(iso, dict) and iso.get("success"):
            do(["convert", "iso.svg", "iso.png"])
    elif k == "deck":
        do(["render", "--sample", "--all", "slides"])
    elif k == "design":
        do(["run", "--sample", "--all-pages", "pages"])
    elif k == "effect":
        do(["exec", "file.openDemoProject"])
        still = do(["render-frame", "--out", "title-card.png"])
        if not still.get("success"):
            steps[-1]["note"] = "render needs an open project - capability map is the demo"
    elif k == "fig":
        import json as _json

        # Template text-node map (landing-page, verified by node.get walk):
        # 8 brand, 24 headline, 25 subline, 39/40 features title/sub,
        # 47/48, 54/55, 61/62 feature cards, 79 quote, 90/91 CTA.
        # Untouched template furniture (declared on the page): nav links,
        # hero picture, Figures stats, quote person, buttons, footer.
        copy: dict[str, str] = {}
        brief_text = ""
        if ai.get("success") and ai.get("text"):
            copy = _labeled_lines(
                ai["text"],
                {
                    "headline": "Headline:",
                    "sub": "Sub:",
                    "features_title": "Features title:",
                    "features_sub": "Features sub:",
                    "f1t": "F1 title:",
                    "f1b": "F1 text:",
                    "f2t": "F2 title:",
                    "f2b": "F2 text:",
                    "f3t": "F3 title:",
                    "f3b": "F3 text:",
                    "quote": "Quote:",
                    "cta_title": "CTA title:",
                    "cta_sub": "CTA sub:",
                },
            )
            brief_text = ai["text"][:4000]
            if len(copy) < 4:
                order = [
                    "headline",
                    "sub",
                    "features_title",
                    "features_sub",
                    "f1t",
                    "f1b",
                    "f2t",
                    "f2b",
                    "f3t",
                    "f3b",
                    "quote",
                    "cta_title",
                    "cta_sub",
                ]
                bare = [
                    ln.strip().lstrip("#*- ").strip()
                    for ln in ai["text"].splitlines()
                    if ln.strip()
                ]
                for key, line in zip(order, bare, strict=False):
                    copy.setdefault(key, line[:160])
        headline = copy.get("headline", "")[:60] or topic or "democraft"
        sub = copy.get("sub", "")[:120]
        sets = [
            (8, topic or "democraft"),
            (24, headline),
            (25, sub or headline),
            (39, copy.get("features_title", "")),
            (40, copy.get("features_sub", "")),
            (47, copy.get("f1t", "")),
            (48, copy.get("f1b", "")),
            (54, copy.get("f2t", "")),
            (55, copy.get("f2b", "")),
            (61, copy.get("f3t", "")),
            (62, copy.get("f3b", "")),
            (79, copy.get("quote", "")),
            (90, copy.get("cta_title", "")),
            (91, copy.get("cta_sub", "")),
        ]
        lines = ['{"command": "file.newFromTemplate", "params": {"template": "landing-page"}}']
        customized = bool(topic)
        if customized:
            for nid, text in sets:
                if text:
                    lines.append(
                        '{"command": "text.set", "params": {"id": '
                        + str(nid)
                        + ", "
                        + f'"characters": {_json.dumps(text)}'
                        + "}}"
                    )
        script = run_dir / "landing.jsonl"
        script.write_text("\n".join(lines) + "\n", encoding="utf-8")
        built = do(["run", str(script), "--out", "landing.figcraft"])
        if customized and not built.get("success"):
            steps[-1].setdefault("note", "copy text.set failed - template render is the demo")
        if (run_dir / "landing.figcraft").is_file():
            do(["render", str(run_dir / "landing.figcraft"), "-o", "landing.png"])
        brief = run_dir / "copy-brief.md"
        if brief_text:
            brief.write_text(brief_text, encoding="utf-8")
        else:
            brief.write_text(
                f"# Landing copy: {topic or 'democraft'}\n\n- Hero: one line.\n"
                "- Three sections.\n- One call to action.\n",
                encoding="utf-8",
            )
    elif k == "film":
        script = run_dir / "storyboard.jsonl"
        script.write_text(
            '{"id": "file.openDemoProject", "params": {}}\n'
            '{"id": "file.exportEdl", "params": {"path": "storyboard.edl"}}\n',
            encoding="utf-8",
        )
        do(["run", str(script)])
        # NOTE: inspect/project probes live in separate processes with no open
        # project, so the exported EDL above is the demo artifact, not the probe.
    elif k == "grid":
        import json as _json

        data = _grid_data(ai, topic)
        headers: list[str] = data["headers"]
        rows: list[list[str]] = data["rows"]
        title: str = data["title"]
        ncols = min(len(headers), 8)
        headers = headers[:ncols]
        col_letters = "ABCDEFGH"[:ncols]
        argv = ["run", "--cmd", f"cell.set={_json.dumps({'cell': 'A1', 'input': title})}"]
        for c, h in enumerate(headers):
            argv += ["--cmd", f"cell.set={_json.dumps({'cell': f'{col_letters[c]}2', 'input': h})}"]
        for r, row in enumerate(rows):
            for c in range(min(ncols, len(row))):
                cell = f"{col_letters[c]}{r + 3}"
                argv += ["--cmd", f"cell.set={_json.dumps({'cell': cell, 'input': row[c]})}"]
        last_row = len(rows) + 2
        head_range = f"A2:{col_letters[-1]}2"
        argv += [
            "--cmd",
            f"home.fillColor={_json.dumps({'range': head_range, 'color': '#F59E0B'})}",
        ]
        do([*argv, "--out", "report.xlsx"])
        data_range = f"A2:{col_letters[-1]}{last_row}"
        rec = cli_run(
            app.cli_path,
            [
                "run",
                "--in",
                "report.xlsx",
                "--cmd",
                "insert.chartRecommendations=" + _json.dumps({"range": data_range}),
            ],
            run_dir,
        )
        steps.append(rec)
        chart_type, chart_sub = "column", ""
        try:
            first = _json.loads(rec.get("stdout", "") or "{}")
            cands = first if isinstance(first, list) else []
            if isinstance(first, dict):
                for key in ("result", "recommendations", "charts"):
                    if isinstance(first.get(key), list) and first[key]:
                        cands = first[key]
                        break
            if cands:
                chart_type = cands[0].get("type", "column")
                chart_sub = cands[0].get("subtype", "")
        except Exception:
            pass
        chart_at = f"A{last_row + 3}"
        chart_params = {
            "range": data_range,
            "type": chart_type,
            "subtype": chart_sub,
            "title": title,
            "at": chart_at,
        }
        do(
            [
                "run",
                "--in",
                "report.xlsx",
                "--cmd",
                f"insert.chart={_json.dumps(chart_params)}",
                "--cmd",
                f"file.saveAs={_json.dumps({'path': 'report.pdf'})}",
                "--out",
                "report-chart.xlsx",
            ]
        )
        num_col = _first_numeric_col(rows, ncols)
        if num_col >= 0 and ncols < 8:
            num_letter = col_letters[num_col]
            free_letter = "ABCDEFGH"[ncols]
            spark_params = {
                "range": f"{num_letter}3:{num_letter}{last_row}",
                "location": f"{free_letter}3",
                "type": "line",
            }
            do(
                [
                    "run",
                    "--in",
                    "report-chart.xlsx",
                    "--cmd",
                    f"insert.sparkline={_json.dumps(spark_params)}",
                    "--out",
                    "report-final.xlsx",
                ]
            )
            final = "report-final.xlsx"
        else:
            final = "report-chart.xlsx"
        do(["cat", final, "--csv"])
    elif k == "sound":
        do(["run", "--demo", "--inspect"])
        bounced = dict(
            cli_run(
                app.cli_path, ["run", "--demo", "--bounce", "ident.wav"], run_dir, timeout_s=300
            )
        )
        steps.append(bounced)
        if bounced.get("success") and (run_dir / "ident.wav").is_file():
            do(["info", "ident.wav"])
        else:
            steps[-1]["note"] = "bounce produced no file - inspect JSON is the demo"
    elif k == "word":
        brief = run_dir / "brief.md"
        if ai.get("success") and ai.get("text"):
            brief.write_text(ai["text"], encoding="utf-8")
        else:
            brief.write_text(
                f"# {topic or 'democraft demo report'}\n\n- Headless demos execute.\n"
                "- Structured errors beat fake artifacts.\n"
                "- Declared gates beat silent mocks.\n",
                encoding="utf-8",
            )
        do(["convert", "brief.md", "brief.docx"])
        do(["convert", "brief.md", "brief.pdf"])
        do(["info", "brief.docx"])
        paras = [p.strip() for p in brief.read_text(encoding="utf-8").split("\n\n") if p.strip()]
        if paras:
            import json as _json

            argv = ["run", "--template", "Report"]
            for para in paras[:12]:
                argv += ["--cmd", f"text.insert={_json.dumps({'text': para[:2000]})}"]
                argv += ["--cmd", "text.newParagraph={}"]
            styled = do([*argv, "--save", "report.docx"])
            if styled.get("success") and (run_dir / "report.docx").is_file():
                do(["convert", "report.docx", "report.pdf"])
                do(["info", "report.docx"])
            else:
                steps[-1].setdefault(
                    "note", "template styling failed - plain brief.* remain the demo"
                )
    elif k == "pdf":
        src = run_dir / "brief.pdf"
        if not src.is_file():
            (run_dir / "seed.md").write_text(
                "# portfolio seed\n\nBuilt for the combine demo.\n", encoding="utf-8"
            )
            wc = PROGRAM_FILES / "WordCraft" / "wordcraft-cli.exe"
            if wc.is_file():
                steps.append(cli_run(wc, ["convert", "seed.md", "brief.pdf"], run_dir))
            else:
                return {
                    "success": False,
                    "message": "needs WordCraft seed PDF",
                    "error_type": "wrappee_missing",
                }
        do(["combine", "brief.pdf", "brief.pdf", "--out", "portfolio.pdf"])
        if (run_dir / "portfolio.pdf").is_file():
            do(["render", "portfolio.pdf", "--page", "1", "--out", "thumb.png"])
            do(["info", "portfolio.pdf"])
    elif k == "light":
        src = run_dir / "grade-in.png"
        if not src.is_file():
            return {
                "success": False,
                "message": "light demo needs an input PNG in the run dir",
                "error_type": "needs_input",
                "recovery": "Run the fig demo, copy landing.png here as grade-in.png, retry.",
            }
        cmds = cli_run(app.cli_path, ["commands", "--json"], run_dir)
        if not cmds.get("success"):
            cmds = cli_run(app.cli_path, ["commands"], run_dir)
        steps.append(cmds)
        do(["run", "--import", "grade-in.png", "develop.auto", "app.export", "path=grade-out.png"])
    elif k == "photo" and demo.id == "plate-grade":
        src = Path(__file__).resolve().parents[2] / "assets" / "photo" / "isle-of-the-dead.jpg"
        if not src.is_file():
            return {
                "success": False,
                "message": f"demo asset missing at {src}",
                "error_type": "asset_missing",
                "recovery": (
                    "Restore assets/photo/isle-of-the-dead.jpg (public domain, Böcklin 1880)."
                ),
            }
        if ai.get("success") and ai.get("text"):
            (run_dir / "brief.md").write_text(ai["text"][:2000], encoding="utf-8")
        do(
            [
                "run",
                str(src),
                "--cmd",
                "layer.newAdjustmentLayer.blackWhite",
                "--params",
                '{"reds":45,"yellows":70,"greens":35,"cyans":55,"blues":10,"magentas":60}',
                "--cmd",
                "layer.newAdjustmentLayer.curves",
                "--params",
                '{"points":[[0,10],[64,52],[128,128],[192,202],[255,242]]}',
                "--cmd",
                "layer.newAdjustmentLayer.gradientMap",
                "--params",
                '{"stops":[[0,"#0b1020"],[0.5,"#8a7656"],[1,"#f4e8d0"]]}',
                "--out",
                "plate-grade.pcraft",
            ]
        )
        do(["convert", "plate-grade.pcraft", "plate-grade.png"])
        do(["convert", "plate-grade.pcraft", "plate-grade.jpg", "--quality", "88"])
        do(["info", "plate-grade.pcraft"])
    elif k in ("photo", "vector"):
        # Pelican benchmark: the SAME plain prompt on every contender model,
        # each rendered through the real engine pipeline. Quality deltas are
        # the models', not the prompt's - no scaffolding, no retries.
        bench_prompt = demo.topic_prompt.format(topic=topic) if topic else demo.ai_prompt
        rendered: list[str] = []
        seen: set[str] = set()
        for m in (model, *BENCH_MODELS):
            if m in seen:
                continue
            seen.add(m)
            tag = _model_tag(m)
            step = ai if m == model else ai_step(bench_prompt, m, timeout=240)
            if m != model:
                ok = bool(step.get("success") and step.get("text"))
                steps.append(
                    {
                        "argv": ["ollama", m],
                        "returncode": 0 if ok else 1,
                        "stdout": f"benchmark contender ({step.get('ms', 0)}ms)",
                        "stderr": "" if ok else str(step.get("error", "")),
                        "ms": step.get("ms", 0),
                        "success": True,
                        "note": "contender call - a miss only skips this model",
                    }
                )
            if step.get("success") and step.get("text"):
                svg_path = run_dir / f"pelican-{tag}.svg"
                if _save_svg(step["text"], svg_path):
                    png = f"pelican-{tag}.png"
                    if k == "photo":
                        do(["convert", svg_path.name, png])
                    else:
                        do(["run", "--in", svg_path.name, "--export", png])
                    if (run_dir / png).is_file():
                        rendered.append(png)
        if not rendered:
            (run_dir / "pelican-fallback.svg").write_text(_FALLBACK_SVG, encoding="utf-8")
            if k == "photo":
                do(["convert", "pelican-fallback.svg", "pelican-fallback.png"])
            else:
                do(["run", "--in", "pelican-fallback.svg", "--export", "pelican-fallback.png"])
            rendered = (
                ["pelican-fallback.png"] if (run_dir / "pelican-fallback.png").is_file() else []
            )
        if rendered:
            do(["info", rendered[0]])
    elif k == "inca":
        import hashlib
        import random as _random

        # Dry-stone wall: deterministic from the topic (same topic, same wall).
        # Courses of varied ashlar blocks, hairline joints, no mortar.
        rng = _random.Random(int(hashlib.sha256(topic.encode()).hexdigest(), 16) % (2**32))
        widths = [1.4, 1.1, 1.7, 0.9, 1.25, 1.55, 1.0, 1.85]
        heights = [0.7, 0.65, 0.6]
        boxes: list[tuple[tuple, tuple]] = []
        z = 0.0
        for course, h in enumerate(heights):
            x = -rng.uniform(0.0, 0.5) if course % 2 else 0.0
            while x < 6.0:
                w = rng.choice(widths)
                boxes.append(((round(x, 3), 0.0, round(z, 3)), (round(w - 0.02, 3), 0.6, h)))
                x += w
            z = round(z + h, 3)
        _freecad_bridge_probe(steps)
        ok = _freecad_iso_boxes(run_dir, steps, "wall", boxes, scale=40.0)
        if ok:
            _fit_viewbox(run_dir / "wall.svg", run_dir / "wall-fragments.svg")
        if ok:
            import shutil as _shutil

            _shutil.copy(run_dir / "wall.svg", run_dir / "wall-iso.svg")
            # CADCraft renders TechDraw fragments faithfully (PhotoCraft fills them black).
            cad = PROGRAM_FILES / "CADCraft" / "cadcraft-cli.exe"
            if cad.is_file():
                steps.append(cli_run(cad, ["convert", "wall-iso.svg", "wall-iso.png"], run_dir))
        else:
            steps[-1].setdefault("note", "FreeCAD wall failed - brief.md is the demo")

    artifacts = sorted({str(f) for f in run_dir.rglob("*") if f.is_file()})
    ok_cli = all(s.get("success") for s in steps) if steps else False
    msg = f"{app.name}/{demo.id}: {len(steps)} CLI steps, {len(artifacts)} artifacts"
    if not ok_cli:
        msg += " (a CLI step reported an engine error - see steps, nothing faked)"
    return {
        "success": True,
        "message": msg,
        "app": app_key,
        "demo": demo_id,
        "ai_step": ai,
        "cli_steps": steps,
        "artifacts": artifacts,
        "all_cli_ok": ok_cli,
        "run_dir": str(run_dir),
    }
