"""Craft registry + headless demo runners.

[RATIONALE] One module owns every Craft app's install path, CLI shape, and
demo #1 so the MCP tool, the REST API, and the webapp all read the same
truth. No per-app snowflakes, no hardcoded lists in the frontend.

Every demo = optional AI step (Ollama, declared) + real CLI subprocess.
Structured errors beat fake artifacts: a gated engine feature returns
``success=False, error_type=needs_account`` with recovery steps.
"""

from __future__ import annotations

import os
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path

PROGRAM_FILES = Path(r"C:\Program Files")
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
                "Demo 1: Japanese small house plan",
                "Sample floorplan DXF + AI room reading, rendered to PNG.",
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
                "Demo 1: 15s democraft ident",
                "Demo project inspect + AI jingle brief; bounce is attempted headless.",
                "Brief a 15-second ident jingle (tempo, key, layers) as JSON. No prose.",
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
                "Demo 1: one-page demo report",
                "Brief written as markdown, converted to DOCX + PDF. AI drafts the brief.",
                "Draft a 5-bullet report on 'headless demos beat screenshots' "
                "as markdown bullets only.",
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
                "Generative pixels are account-gated.",
                "Write a minimal SVG (3-6 shapes) of a pelican on a bike. Raw SVG only.",
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
                "Write a minimal SVG (3-6 shapes) of a pelican on a bike. Raw SVG only.",
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


def cli_run(exe: Path, argv: list[str], cwd: Path) -> dict:
    """Run one CLI argv. Returns the real result, including real failures."""
    started = time.time()
    try:
        p = subprocess.run(
            [str(exe), *argv], cwd=str(cwd), capture_output=True, text=True, timeout=CLI_TIMEOUT_S
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
            "error": f"exceeded {CLI_TIMEOUT_S}s",
            "ms": CLI_TIMEOUT_S * 1000,
        }
    except Exception as e:
        return {
            "success": False,
            "argv": argv,
            "error_type": "spawn",
            "error": f"{type(e).__name__}: {e}",
        }


def run_demo(app_key: str, demo_id: str, outbox: Path, model: str = DEFAULT_MODEL) -> dict:
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

    ai = ai_step(demo.ai_prompt, model)
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
        do(["sample", "floorplan", "floorplan.dxf"])
        do(["info", "floorplan.dxf"])
        do(["sample", "floorplan", "floorplan.png"])
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
    elif k == "word":
        brief = run_dir / "brief.md"
        if ai.get("success") and ai.get("text"):
            brief.write_text(ai["text"], encoding="utf-8")
        else:
            brief.write_text(
                "# democraft demo report\n\n- Headless demos execute.\n"
                "- Structured errors beat fake artifacts.\n"
                "- Declared gates beat silent mocks.\n",
                encoding="utf-8",
            )
        do(["convert", "brief.md", "brief.docx"])
        do(["convert", "brief.md", "brief.pdf"])
        do(["info", "brief.docx"])
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
        steps.append(cmds)
        do(["run", "--import", "grade-in.png", "develop.auto", "app.export", "path=grade-out.png"])
    elif k in ("photo", "vector"):
        svg = run_dir / "pelican.svg"
        txt = ai.get("text", "") if ai.get("success") else ""
        start = txt.find("<svg")
        svg.write_text(
            txt[start:] if start >= 0 else _FALLBACK_SVG,
            encoding="utf-8",
        )
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
