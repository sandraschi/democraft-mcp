"""democraft-mcp server: FastMCP portmanteau + FastAPI backend.

[RATIONALE] One `craft` tool fronts all 13 Craft apps so hosts see a single
entry instead of 13 toolsets; the `operation` enum is the catalog. The same
 Python functions back the REST API - one truth, two transports.
"""

from __future__ import annotations

import os
import threading
from pathlib import Path
from typing import Annotated, Literal

from fastmcp import FastMCP
from pydantic import Field

from .crafts import APPS, BY_KEY, DEFAULT_MODEL, ai_step, cli_run, run_demo

REPO_ROOT = Path(__file__).resolve().parents[2]
OUTBOX = Path(os.getenv("DEMOCRAFT_OUTBOX", str(REPO_ROOT / "outbox")))
BACKEND_PORT = int(os.getenv("DEMOCRAFT_PORT", "11246"))

mcp = FastMCP("democraft-mcp")

Operation = Literal[
    "list_apps",
    "app_status",
    "run_demo",
    "craft_commands",
    "ollama_models",
    "ai_flow",
    "help",
    "shutdown",
]


@mcp.tool()
def craft(
    operation: Annotated[
        Operation,
        Field(
            description="Operation: list_apps, app_status, run_demo, "
            "craft_commands, ollama_models, ai_flow, help, shutdown"
        ),
    ],
    app: Annotated[
        str,
        Field(
            description="Craft app key: cad, deck, design, effect, fig, "
            "film, grid, sound, word, pdf, light, photo, vector"
        ),
    ] = "",
    demo: Annotated[str, Field(description="Demo id (default: the app's demo #1)")] = "",
    model: Annotated[str, Field(description="Ollama model for the AI step")] = DEFAULT_MODEL,
    prompt: Annotated[str, Field(description="Prompt for ai_flow")] = "",
    confirm: Annotated[bool, Field(description=" confirm=True executes shutdown")] = False,
) -> dict:
    """Run Craft demos: list apps, check installs, execute headless CLI demos with a local-LLM step.

    ## Return Format
    `{"success": bool, "message": str, ...operation fields}` - `run_demo`
    adds `ai_step`, `cli_steps`, `artifacts`. Engine failures are reported,
    never hidden; account-gated features return `error_type: needs_account`.

    ## Examples
    `craft(operation="list_apps")`
    `craft(operation="run_demo", app="cad", demo="house-plan")`
    `craft(operation="ai_flow", prompt="caption this plan")`
    """
    if operation == "list_apps":
        return {
            "success": True,
            "message": f"{len(APPS)} Craft apps",
            "apps": [
                {
                    "key": a.key,
                    "name": a.name,
                    "installed": a.installed(),
                    "tagline": a.tagline,
                    "demos": [{"id": d.id, "title": d.title} for d in a.demos],
                }
                for a in APPS
            ],
        }
    if operation == "app_status":
        rows = [
            {"key": a.key, "name": a.name, "installed": a.installed(), "cli": str(a.cli_path)}
            for a in APPS
        ]
        missing = [r["name"] for r in rows if not r["installed"]]
        return {
            "success": True,
            "message": f"{len(rows) - len(missing)}/{len(rows)} installed",
            "apps": rows,
            "missing": missing,
        }
    if operation == "run_demo":
        if not app:
            return {"success": False, "message": "app is required", "known_apps": sorted(BY_KEY)}
        a = BY_KEY[app]
        demo_id = demo or (a.demos[0].id if a.demos else "")
        return run_demo(app, demo_id, OUTBOX, model)
    if operation == "craft_commands":
        if not app or app not in BY_KEY:
            return {"success": False, "message": "app is required", "known_apps": sorted(BY_KEY)}
        a = BY_KEY[app]
        if not a.installed():
            return {
                "success": False,
                "message": f"{a.name} not installed",
                "error_type": "wrappee_missing",
            }
        res = cli_run(a.cli_path, ["commands", "--json"], OUTBOX)
        return {
            "success": res.get("success", False),
            "message": f"commands for {a.name}",
            "app": app,
            "result": res,
        }
    if operation == "ollama_models":
        import httpx

        try:
            r = httpx.get("http://127.0.0.1:11434/api/tags", timeout=10)
            r.raise_for_status()
            names = [m.get("name") for m in r.json().get("models", [])]
            return {"success": True, "message": f"{len(names)} local models", "models": names}
        except Exception as e:
            return {
                "success": False,
                "message": f"Ollama unreachable: {type(e).__name__}: {e}",
                "error_type": "llm_down",
                "recovery": "Start Ollama, then retry.",
            }
    if operation == "ai_flow":
        if not prompt:
            return {"success": False, "message": "prompt is required"}
        step = ai_step(prompt, model)
        return {
            "success": step.get("success", False),
            "message": "ai step complete" if step.get("success") else "ai step skipped",
            "ai_step": step,
        }
    if operation == "help":
        return {
            "success": True,
            "message": "democraft-mcp: one tool, 8 ops, 13 apps",
            "operations": [
                "list_apps",
                "app_status",
                "run_demo",
                "craft_commands",
                "ollama_models",
                "ai_flow",
                "help",
                "shutdown",
            ],
            "usage": "craft(operation='run_demo', app='cad', demo='house-plan')",
        }
    if operation == "shutdown":
        if not confirm:
            return {
                "success": False,
                "message": "pass confirm=True to shut down",
                "needs_confirm": True,
            }
        threading.Timer(0.5, lambda: os._exit(0)).start()
        return {"success": True, "message": "shutting down in ~500ms"}
    return {"success": False, "message": f"unknown operation '{operation}'"}


@mcp.tool(app=True)
def show_apps_prefab_card() -> dict:
    """Show installed Craft apps as a rich Prefab card (plain-text fallback included)."""
    rows = [(a.name, "ready" if a.installed() else "missing") for a in APPS]
    text = "democraft apps: " + ", ".join(f"{n}={s}" for n, s in rows)
    return {
        "success": True,
        "message": text,
        "content": text,
        "apps": [{"key": a.key, "name": a.name, "installed": a.installed()} for a in APPS],
    }


@mcp.tool(app=True)
def show_demo_prefab_card(app: str = "cad", demo: str = "") -> dict:
    """Show one demo's definition as a Prefab card (run it with craft/run_demo)."""
    a = BY_KEY.get(app)
    if a is None:
        return {
            "success": False,
            "message": f"unknown app '{app}'",
            "content": f"unknown app '{app}'",
        }
    d = next((x for x in a.demos if x.id == (demo or (a.demos[0].id if a.demos else ""))), None)
    if d is None:
        return {"success": False, "message": "unknown demo", "content": "unknown demo"}
    text = f"{a.name} / {d.title}: {d.blurb} (requires: {d.requires})"
    return {
        "success": True,
        "message": text,
        "content": text,
        "app": app,
        "demo": d.id,
        "requires": d.requires,
    }


@mcp.prompt()
def democraft_demo_guide(app: str = "cad") -> str:
    a = BY_KEY.get(app)
    names = ", ".join(x.key for x in APPS)
    demo = a.demos[0].title if a and a.demos else "?"
    return (
        f"Democraft guide for {app} ({demo}). Apps: {names}. "
        "Every demo is a real headless CLI run plus a local-LLM step; "
        "account-gated engine features return needs_account, never fake pixels. "
        "Call craft(operation='run_demo', app=..., demo=...) and report artifacts honestly."
    )


def build_api():
    from .api import create_app

    return create_app()


app = build_api()


def main() -> None:
    import uvicorn

    uvicorn.run("democraft_mcp.server:app", host="127.0.0.1", port=BACKEND_PORT)


if __name__ == "__main__":
    main()
