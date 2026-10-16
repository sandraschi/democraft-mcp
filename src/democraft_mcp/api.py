"""FastAPI backend: health, registry, demos, runs, tools, skills, logs, LLM, dashboard.

[RATIONALE] The webapp never shells out and never hardcodes the app list -
every route reads the same registry the MCP tool reads.
"""

from __future__ import annotations

import collections
import logging
import shutil
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from . import __version__
from .crafts import APPS, BY_KEY, DEFAULT_MODEL, run_demo

logger = logging.getLogger("democraft_mcp.api")

LOGS: collections.deque[dict] = collections.deque(maxlen=300)
STARTED = time.time()


def _error_response(source: str, message: str, error_type: str, recovery: str = "") -> dict:
    logger.exception("%s: %s", source, message)
    out: dict = {"success": False, "message": message, "error_type": error_type}
    if recovery:
        out["recovery"] = recovery
    return out


LOGS: collections.deque[dict] = collections.deque(maxlen=300)


def log(source: str, message: str) -> None:
    LOGS.append({"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "source": source, "message": message})


class DemoRequest(BaseModel):
    app: str
    demo: str = ""
    model: str = DEFAULT_MODEL
    topic: str = ""


class ChatRequest(BaseModel):
    prompt: str
    model: str = DEFAULT_MODEL


class ShutdownRequest(BaseModel):
    confirm: bool = False


def _probe_http(url: str, timeout: float = 3) -> bool:
    import httpx

    try:
        r = httpx.get(url, timeout=timeout)
        return r.status_code < 500
    except Exception:
        return False


def _gpu_present() -> bool:
    if shutil.which("nvidia-smi") is None:
        return False
    import subprocess

    try:
        p = subprocess.run(["nvidia-smi", "-L"], capture_output=True, text=True, timeout=15)
        return p.returncode == 0 and bool(p.stdout.strip())
    except Exception:
        return False


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
            "https://tauri.localhost",
        ],
        allow_origin_regex=r"https?://(localhost|127\.0\.0\.1|\[::1\]|[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*)(:\d+)?",
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )

    @api.get("/api/health")
    def health() -> dict:
        installed = sum(1 for a in APPS if a.installed())
        return {"status": "ok", "version": __version__, "apps": len(APPS), "installed": installed}

    @api.get("/health")
    def health_alias() -> dict:
        return {"status": "ok", "version": __version__}

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
                        {
                            "id": d.id,
                            "title": d.title,
                            "blurb": d.blurb,
                            "requires": d.requires,
                            "topics": list(d.topics),
                        }
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
        res = run_demo(req.app, demo_id, box, req.model, topic=req.topic.strip()[:200])
        log("demo", f"{req.app}/{demo_id} success={res.get('success')}")
        return res

    @api.get("/api/artifacts/{app}/{demo}/{path:path}")
    def artifact(app: str, demo: str, path: str):
        """Serve a demo artifact for clickthrough (open in browser / Craft app).

        Path traversal is rejected: the resolved file must stay inside
        outbox/<app>/<demo>/. Correct MIME so PNG/PDF open inline and
        DOCX/XLSX/WAV download for their Craft app.
        """
        from fastapi.responses import FileResponse

        if app not in BY_KEY:
            return {"success": False, "message": f"unknown app '{app}'"}
        root = (box / app / demo).resolve()
        target = (root / path).resolve()
        if root != target and root not in target.parents:
            return {
                "success": False,
                "message": "path escapes the run dir",
                "error_type": "bad_path",
            }
        if not target.is_file():
            return {"success": False, "message": f"no such artifact '{path}'"}
        return FileResponse(str(target))

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
            logger.exception("llm/providers probe failed")
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

    @api.get("/api/status")
    def status() -> dict:
        import httpx

        tools = 3
        try:
            r = httpx.get("http://127.0.0.1:11434/api/tags", timeout=5)
            llm_ok = r.status_code == 200
        except Exception:
            llm_ok = False
        return {
            "success": True,
            "status": "ok",
            "version": __version__,
            "uptime_seconds": int(time.time() - STARTED),
            "tool_count": tools,
            "apps": len(APPS),
            "installed": sum(1 for a in APPS if a.installed()),
            "llm_ok": llm_ok,
        }

    @api.get("/api/capabilities")
    def capabilities() -> dict:
        return {
            "success": True,
            "name": "democraft-mcp",
            "version": __version__,
            "transports": ["stdio", "http"],
            "features": {
                "demos": True,
                "prefab": True,
                "skills": True,
                "streaming_chat": False,
                "webhooks": False,
            },
            "tools": ["craft", "show_apps_prefab_card", "show_demo_prefab_card"],
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
            "apps": [a.key for a in APPS],
        }

    @api.post("/api/chat")
    def chat(req: ChatRequest) -> dict:
        from .crafts import ai_step

        step = ai_step(req.prompt, req.model)
        log("chat", f"model={req.model} ok={step.get('success')}")
        return step

    @api.post("/api/shutdown")
    def shutdown(req: ShutdownRequest) -> dict:
        import os
        import threading

        if not req.confirm:
            return {
                "success": False,
                "message": "pass confirm=true to shut down",
                "needs_confirm": True,
            }
        threading.Timer(0.5, lambda: os._exit(0)).start()
        return {"success": True, "message": "shutting down in ~500ms"}

    @api.get("/api/llm/discover")
    def llm_discover() -> dict:
        probes = {
            "ollama": "http://127.0.0.1:11434/api/tags",
            "lmstudio": "http://127.0.0.1:1234/v1/models",
            "vllm": "http://127.0.0.1:8000/v1/models",
        }
        found = {k: _probe_http(v) for k, v in probes.items()}
        return {
            "success": True,
            "providers": found,
            "gpu": _gpu_present(),
            "default_model": DEFAULT_MODEL,
        }

    @api.get("/api/llm/models")
    def llm_models() -> dict:
        import httpx

        try:
            r = httpx.get("http://127.0.0.1:11434/api/tags", timeout=10)
            r.raise_for_status()
            models = [m.get("name") for m in r.json().get("models", [])]
            return {"success": True, "models": models, "live": True}
        except Exception as e:
            logger.exception("llm/models probe failed")
            fallback = ["gemma4:e4b", "qwen3.8-tools", "mistral-nemo:12b"]
            return {
                "success": True,
                "models": fallback,
                "live": False,
                "note": f"Ollama down ({e}); curated fallback",
            }

    @api.get("/api/llm/onboarding")
    def llm_onboarding() -> dict:
        import httpx

        try:
            r = httpx.get("http://127.0.0.1:11434/api/tags", timeout=5)
            if r.status_code == 200:
                models = [m.get("name") for m in r.json().get("models", [])]
            else:
                models = []
        except Exception:
            models = []
        if models:
            path = "ready"
            detail = f"{len(models)} local model(s); start with {DEFAULT_MODEL}."
        else:
            path = "install-ollama"
            detail = "Install Ollama and pull gemma4:e4b (8GB); demos run without it."
        return {"success": True, "path": path, "detail": detail, "recommended_model": DEFAULT_MODEL}

    from .server import mcp as _mcp

    mcp_app = _mcp.http_app(path="/")

    @asynccontextmanager
    async def _lifespan(app: FastAPI):
        async with mcp_app.lifespan(app):
            yield

    api.router.lifespan_context = _lifespan  # type: ignore[method-assign]

    class _McpSlashRewrite:
        def __init__(self, inner):
            self.inner = inner

        async def __call__(self, scope, receive, send):
            if scope.get("type") == "http" and scope.get("path") == "/mcp":
                scope = {**scope, "path": "/mcp/"}
            await self.inner(scope, receive, send)

    api.mount("/mcp", _McpSlashRewrite(mcp_app))

    return api
