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
    topics: tuple[str, ...] = ()  # word demo: combobox choices; empty = free text only


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
                "Demo 1: Japanese small house set",
                "Scripted metric plan (rooms, labels, dims) + south elevation: "
                "DXF, PNG, PDF, SVG. 2D engine: no true isometric.",
                "List rooms of a small Japanese house plan (genkan, washitsu, "
                "engawa, LD, bath) as JSON list of {room, note}. No prose.",
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
                "Demo 1: 5-slide democraft pitch deck",
                "Render the sample deck to PNGs, then outline the 5 slides from the slide count.",
                "Outline a 5-slide pitch deck for 'democraft-mcp' as JSON "
                "list of {slide, bullets}. No prose.",
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
                "Demo 1: print spread of pelican + house plan",
                "Sample magazine render to PNGs + AI spread reading.",
                "Describe a 2-page spread (house plan + pelican) as JSON "
                "{left, right, palette}. No prose.",
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
                "Demo 1: title-card still",
                "Engine capability map, then a still render attempt.",
                "Write a title-card spec (text, palette, timing) as JSON. No prose.",
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
                "Demo 1: democraft landing page",
                "Landing-page template built headless + PNG render.",
                "List landing-page sections for a demo site as JSON list of "
                "{section, purpose}. No prose.",
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
                "Demo 1: 3-shot pelican storyboard",
                "Project inspect + AI 3-shot board; sequence assembly is gated on a project file.",
                "Board a 3-shot storyboard (pelican, bike, reveal) as JSON "
                "list of {shot, lens, action}. No prose.",
            ),
        ),
    ),
    CraftApp(
        "grid",
        "GridCraft",
        "gridcraft-cli.exe",
        "Spreadsheets: convert, eval, round-trip.",
        (
            Demo(
                "homepage-grid",
                "Demo 1: democraft homepage grid",
                "CSV lineup written, converted to XLSX, read back. AI summaries the sheet.",
                "Given rows [app, demo, status], write a one-line summary. "
                "Rows: cad/house-plan/ok, deck/pitch-deck/ok, fig/landing-page/ok.",
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
                "Demo 1: demo-outputs portfolio PDF",
                "Combine demo PDFs into one portfolio + thumbnail render.",
                "Name 4 portfolio sections for craft demo outputs as JSON list. No prose.",
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
                "Demo 1: grade the pelican photo",
                "Grade pass over the demo PNG + AI grade reading.",
                "Suggest exposure/contrast/saturation tweaks for a flat PNG "
                "as JSON {exposure, contrast, saturation, note}. No prose.",
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
                "Demo 1: pelican riding a bike (photo)",
                "AI SVG concept rendered through the convert/info pipeline. "
                "No generative verbs exist in this build.",
                "Draw a flat side-view pictogram on an 800x600 canvas: "
                "pelican body (ellipse), head (circle), long beak (polygon), "
                "eye (small circle), wing (ellipse), two bike wheels (circles "
                "with spoke lines), frame lines, ground line. 12-20 shapes. "
                "Raw SVG only.",
                "cli",
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
                "Demo 1: pelican riding a bike (vector)",
                "AI SVG concept run through the run/export pipeline. Same "
                "prompt as photo: compare the two.",
                "Draw a flat side-view pictogram on an 800x600 canvas: "
                "pelican body (ellipse), head (circle), long beak (polygon), "
                "eye (small circle), wing (ellipse), two bike wheels (circles "
                "with spoke lines), frame lines, ground line. 12-20 shapes. "
                "Raw SVG only.",
                "cli",
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
        else (
            f"Write a one-page report on '{topic}' as markdown: a # title line, "
            "then 4-6 short paragraphs. No preamble."
        ),
        model,
    )
    steps: list[dict] = []
    artifacts: list[str] = []

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
        script = run_dir / "landing.jsonl"
        script.write_text(
            '{"command": "file.newFromTemplate", "params": {"template": "landing-page"}}\n',
            encoding="utf-8",
        )
        do(["run", str(script), "--out", "landing.figcraft"])
        if (run_dir / "landing.figcraft").is_file():
            do(["render", str(run_dir / "landing.figcraft"), "-o", "landing.png"])
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
        (run_dir / "lineup.csv").write_text(
            "app,demo,status\ncad,house-plan,ok\ndeck,pitch-deck,ok\nfig,landing-page,ok\n",
            encoding="utf-8",
        )
        do(["convert", "lineup.csv", "lineup.xlsx"])
        do(["cat", "lineup.xlsx", "--csv"])
        do(["eval", "6*7"])
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
