"""FastAPI backend: health, registry, demos, runs, tools, skills, logs, LLM, dashboard.

[RATIONALE] The webapp never shells out and never hardcodes the app list -
every route reads the same registry the MCP tool reads.
"""

from __future__ import annotations

import collections
import time
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from . import __version__
from .crafts import APPS, BY_KEY, DEFAULT_MODEL, run_demo

LOGS: collections.deque[dict] = collections.deque(maxlen=300)


def log(source: str, message: str) -> None:
    LOGS.append({"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "source": source, "message": message})


class DemoRequest(BaseModel):
    app: str
    demo: str = ""
    model: str = DEFAULT_MODEL


class ChatRequest(BaseModel):
    prompt: str
    model: str = DEFAULT_MODEL


def create_app(outbox: Path | None = None) -> FastAPI:
    from .server import OUTBOX as DEFAULT_OUTBOX

    box = outbox or DEFAULT_OUTBOX

    api = FastAPI(title="democraft-mcp", version=__version__)

    api.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://127.0.0.1:11245",
            "http://localhost:11245",
            "tauri://localhost",
            "http://tauri.localhost",
        ],
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )

    @api.get("/api/health")
    def health() -> dict:
        installed = sum(1 for a in APPS if a.installed())
        return {"status": "ok", "version": __version__, "apps": len(APPS), "installed": installed}

    @api.get("/api/crafts")
    def crafts() -> dict:
        return {
            "success": True,
            "apps": [
                {
                    "key": a.key,
                    "name": a.name,
                    "installed": a.installed(),
                    "tagline": a.tagline,
                    "demos": [
                        {"id": d.id, "title": d.title, "blurb": d.blurb, "requires": d.requires}
                        for d in a.demos
                    ],
                }
                for a in APPS
            ],
        }

    @api.post("/api/demos/run")
    def demos_run(req: DemoRequest) -> dict:
        a = BY_KEY.get(req.app)
        demo_id = req.demo or (a.demos[0].id if a and a.demos else "")
        res = run_demo(req.app, demo_id, box, req.model)
        log("demo", f"{req.app}/{demo_id} success={res.get('success')}")
        return res

    @api.get("/api/runs")
    def runs() -> dict:
        items = []
        if box.is_dir():
            for app_dir in sorted(box.iterdir()):
                if not app_dir.is_dir():
                    continue
                for run_dir in sorted(app_dir.iterdir()):
                    if not run_dir.is_dir():
                        continue
                    files = sorted(
                        str(f.relative_to(run_dir)) for f in run_dir.rglob("*") if f.is_file()
                    )
                    items.append(
                        {
                            "app": app_dir.name,
                            "demo": run_dir.name,
                            "artifacts": len(files),
                            "files": files[:20],
                        }
                    )
        return {"success": True, "runs": items}

    @api.get("/api/tools")
    def tools() -> dict:
        return {
            "success": True,
            "tools": [
                {
                    "name": "craft",
                    "pattern": "portmanteau",
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
                },
                {"name": "show_apps_prefab_card", "pattern": "prefab"},
                {"name": "show_demo_prefab_card", "pattern": "prefab"},
            ],
        }

    @api.get("/api/skills")
    def skills() -> dict:
        from .server import REPO_ROOT

        out = []
        for f in sorted((REPO_ROOT / "skills").glob("*/SKILL.md")):
            out.append(
                {
                    "name": f.parent.name,
                    "path": f"skill://democraft/{f.parent.name}",
                    "preview": f.read_text(encoding="utf-8")[:2000],
                }
            )
        return {"success": True, "skills": out}

    @api.get("/api/logs")
    def logs(limit: int = 100) -> dict:
        return {"success": True, "logs": list(LOGS)[-limit:]}

    @api.get("/api/llm/providers")
    def llm_providers() -> dict:
        import httpx

        try:
            r = httpx.get("http://127.0.0.1:11434/api/tags", timeout=10)
            r.raise_for_status()
            return {
                "success": True,
                "providers": [
                    {
                        "id": "ollama",
                        "ok": True,
                        "models": [m.get("name") for m in r.json().get("models", [])],
                        "default_model": DEFAULT_MODEL,
                    }
                ],
            }
        except Exception as e:
            return {"success": False, "providers": [{"id": "ollama", "ok": False, "error": str(e)}]}

    @api.post("/api/llm/chat")
    def llm_chat(req: ChatRequest) -> dict:
        from .crafts import ai_step

        step = ai_step(req.prompt, req.model)
        log("chat", f"model={req.model} ok={step.get('success')}")
        return step

    @api.get("/api/dashboard")
    def dashboard() -> dict:
        installed = [a for a in APPS if a.installed()]
        runs_count = 0
        if box.is_dir():
            runs_count = sum(
                1
                for a in box.iterdir()
                if a.is_dir()
                for _ in (x for x in a.iterdir() if x.is_dir())
            )
        return {
            "success": True,
            "kpis": [
                {"label": "Craft apps", "value": len(APPS)},
                {"label": "Installed", "value": len(installed)},
                {"label": "Demos defined", "value": sum(len(a.demos) for a in APPS)},
                {"label": "Demo runs", "value": runs_count},
            ],
        }

    try:
        from .server import mcp

        api.mount("/mcp", mcp.http_app())
    except Exception as e:
        log("mcp-mount", f"mount failed: {e}")

    return api
