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
from dataclasses import dataclass, field
from pathlib import Path

PROGRAM_FILES = Path(os.getenv("DEMOCRAFT_PROGRAM_FILES", r"C:\Program Files"))
OLLAMA_URL = os.getenv("DEMOCRAFT_OLLAMA_URL", "http://127.0.0.1:11434")
DEFAULT_MODEL = os.getenv("DEMOCRAFT_MODEL", "gemma4:12b")
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


@dataclass(frozen=True)
class CraftApp:
    key: str
    name: str
    cli: str  # exe name under C:\Program Files\<Name>\
    tagline: str
    demos: tuple[Demo, ...] = field(default_factory=tuple)

    @property
    def cli_path(self) -> Path:
        return PROGRAM_FILES / self.name / self.cli

    def installed(self) -> bool:
        return self.cli_path.is_file()


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
                "Landing-page template built headless; your topic's headline "
                "and subline are set into the hero before render + PNG.",
                "Write a landing-page copy brief as markdown: # headline, "
                "3 sections with one line each, one call to action.",
                topics=FIG_TOPICS,
                topic_prompt="Return JSON only for a landing page about '{topic}': "
                '{{"headline": str (<=40 chars), "sub": str (<=90 chars), '
                '"brief": str (3 sections + CTA as markdown)}}. No preamble.',
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
        "Photo: convert + info pipeline.",
        (
            Demo(
                "pelican-photo",
                "Demo 1: SVG subject (pick one)",
                "AI draws your subject as SVG; the convert/info pipeline "
                "renders it. No generative verbs exist in this build.",
                "Draw a flat side-view pictogram on an 800x600 canvas: "
                "pelican body (ellipse), head (circle), long beak (polygon), "
                "eye (small circle), wing (ellipse), two bike wheels (circles "
                "with spoke lines), frame lines, ground line. 12-20 shapes. "
                "Raw SVG only.",
                "cli",
                topics=PHOTO_TOPICS,
                topic_prompt="Draw '{topic}' as a flat pictogram SVG on an 800x600 "
                "canvas, 12-20 shapes (ellipse/circle/rect/polygon/line). Raw SVG only.",
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
                "Demo 1: SVG subject (pick one)",
                "AI draws your subject as SVG; the run/export pipeline "
                "renders it. Same prompt as photo: compare the two.",
                "Draw a flat side-view pictogram on an 800x600 canvas: "
                "pelican body (ellipse), head (circle), long beak (polygon), "
                "eye (small circle), wing (ellipse), two bike wheels (circles "
                "with spoke lines), frame lines, ground line. 12-20 shapes. "
                "Raw SVG only.",
                "cli",
                topics=VECTOR_TOPICS,
                topic_prompt="Draw '{topic}' as a flat pictogram SVG on an 800x600 "
                "canvas, 12-20 shapes (ellipse/circle/rect/polygon/line). Raw SVG only.",
            ),
        ),
    ),
)

BY_KEY = {a.key: a for a in APPS}

_FALLBACK_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300">'
    '<ellipse cx="200" cy="120" rx="90" ry="60"/>'
    '<circle cx="280" cy="80" r="28"/>'
    '<rect x="60" y="200" width="280" height="12" rx="6"/>'
    '<circle cx="120" cy="240" r="34"/><circle cx="280" cy="240" r="34"/></svg>'
)


def ai_step(prompt: str, model: str = DEFAULT_MODEL) -> dict:
    """One local-LLM call. Never raises: failure is a declared skip."""
    import httpx

    started = time.time()
    try:
        r = httpx.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=90,
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
            [str(exe), *argv], cwd=str(cwd), capture_output=True, text=True, timeout=timeout_s
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
    if not app.installed():
        return {
            "success": False,
            "message": f"{app.name} not installed at {app.cli_path}",
            "error_type": "wrappee_missing",
            "recovery": f"Install {app.name}, then retry. See docs/ONBOARDING.md.",
        }
    outbox.mkdir(parents=True, exist_ok=True)
    run_dir = outbox / app_key / demo_id
    run_dir.mkdir(parents=True, exist_ok=True)

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
            ["rectang", '{"p1": [0, 0], "p2": [7.28, 5.46]}'],
            ["line", '{"points": [[1.82, 0], [1.82, 1.82]]}'],
            ["line", '{"points": [[0, 1.82], [7.28, 1.82]]}'],
            ["line", '{"points": [[3.64, 1.82], [3.64, 5.46]]}'],
            ["line", '{"points": [[5.46, 0], [5.46, 1.82]]}'],
            ["text", '{"at": [0.91, 0.91], "text": "genkan", "height": 0.18}'],
            ["text", '{"at": [3.64, 0.91], "text": "hall", "height": 0.18}'],
            ["text", '{"at": [1.82, 3.64], "text": "washitsu", "height": 0.18}'],
            ["text", '{"at": [5.46, 3.64], "text": "LD", "height": 0.18}'],
            ["text", '{"at": [6.37, 0.91], "text": "bath", "height": 0.18}'],
            ["dimlinear", '{"p1": [0, 0], "p2": [7.28, 0], "at": [3.64, -0.6]}'],
            ["dimlinear", '{"p1": [0, 0], "p2": [0, 5.46], "at": [-0.6, 2.73]}'],
        ]
        if topic:
            import json as _json

            plan.insert(
                0, ["text", _json.dumps({"at": [0, 6.1], "text": topic[:40], "height": 0.3})]
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

        headline, sub, brief_text = topic or "democraft", "", ""
        if ai.get("success") and ai.get("text"):
            txt = ai["text"]
            start, end = txt.find("{"), txt.rfind("}")
            if start >= 0 and end > start:
                try:
                    obj = _json.loads(txt[start : end + 1])
                    headline = str(obj.get("headline", headline))[:60] or headline
                    sub = str(obj.get("sub", ""))[:120]
                    brief_text = str(obj.get("brief", txt))[:4000]
                except Exception:
                    brief_text = txt[:4000]
            else:
                brief_text = txt[:4000]
        lines = ['{"command": "file.newFromTemplate", "params": {"template": "landing-page"}}']
        customized = bool(topic)
        if customized:
            lines.append(
                '{"command": "text.set", "params": {"id": 24, "characters": '
                + _json.dumps(headline)
                + "}}"
            )
            lines.append(
                '{"command": "text.set", "params": {"id": 25, "characters": '
                + _json.dumps(sub or headline)
                + "}}"
            )
        script = run_dir / "landing.jsonl"
        script.write_text("\n".join(lines) + "\n", encoding="utf-8")
        built = do(["run", str(script), "--out", "landing.figcraft"])
        if customized and not built.get("success"):
            steps[-1].setdefault("note", "hero text.set failed - template render is the demo")
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
    elif k in ("photo", "vector"):
        svg = run_dir / "pelican.svg"
        txt = ai.get("text", "") if ai.get("success") else ""
        start = txt.find("<svg")
        end = txt.find("</svg>")
        if start >= 0 and end > start:
            svg.write_text(txt[start : end + len("</svg>")], encoding="utf-8")
        elif start >= 0:
            svg.write_text(txt[start:], encoding="utf-8")
        else:
            svg.write_text(_FALLBACK_SVG, encoding="utf-8")
        if k == "photo":
            do(["convert", "pelican.svg", "pelican.png"])
            do(["info", "pelican.png"])
        else:
            do(["run", "--in", "pelican.svg", "--export", "pelican.png"])

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
