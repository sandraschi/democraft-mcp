"""Seed assets/prompts/examples.json: 13 apps x 8 ops = 104 real tool-call examples.

Committed generator: re-run after adding demos. Output is data, reviewed like code.
"""

import json
from pathlib import Path

APPS = [
    "cad",
    "deck",
    "design",
    "effect",
    "fig",
    "film",
    "grid",
    "sound",
    "word",
    "pdf",
    "light",
    "photo",
    "vector",
]
DEMOS = {
    "cad": "house-plan",
    "deck": "pitch-deck",
    "design": "print-spread",
    "effect": "title-card",
    "fig": "landing-page",
    "film": "storyboard",
    "grid": "homepage-grid",
    "sound": "ident-jingle",
    "word": "demo-report",
    "pdf": "portfolio",
    "light": "grade-pelican",
    "photo": "pelican-photo",
    "vector": "pelican-vector",
}

OPS = [
    ("list_apps", {}, "inventory before anything else"),
    ("app_status", {}, "which wrappees are installed"),
    ("run_demo", None, "execute the app demo #1"),
    ("craft_commands", None, "live command discovery from the CLI"),
    ("ollama_models", {}, "local models available"),
    ("ai_flow", {"prompt": "caption this demo output"}, "single local-LLM step"),
    ("help", {}, "operation catalog"),
    ("shutdown", {"confirm": True}, "graceful exit"),
]

examples = []
for app in APPS:
    for op, params, note in OPS:
        p = dict(params or {})
        if op in ("run_demo", "craft_commands"):
            p = {"app": app, **p}
        if op == "run_demo":
            p["demo"] = DEMOS[app]
        examples.append({"tool": "craft", "operation": op, "input": p, "note": f"{app}: {note}"})

out = Path(__file__).resolve().parents[1] / "assets" / "prompts" / "examples.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(examples, indent=1), encoding="utf-8")
print(f"wrote {len(examples)} examples")
