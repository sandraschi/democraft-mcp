# INSTALL.md

> New here? Read `docs/ONBOARDING.md` first (wrappees + AI setup). This file is the mechanical install.

## Prerequisites (winget, naked-PC safe)

```powershell
winget install --id Astral.UV -e
winget install --id OpenJS.NodeJS.LTS -e
winget install --id Casey.Just -e
winget install --id Ollama.Ollama -e
```

`start.bat` also bootstraps via `Require-Command`. Python comes from uv
(`requires-python >=3.11`); never install system Python for this repo.

## Option A - run it

Double-click `start.bat`. Backend http://127.0.0.1:11246, frontend http://127.0.0.1:11245.

## Option B - MCP in your client

```json
{ "mcpServers": { "democraft": { "command": "uv", "args": ["run", "python", "-m", "democraft_mcp.mcp_stdio"], "cwd": "D:\\Dev\\repos\\democraft-mcp" } } }
```

## Validate

```powershell
Invoke-WebRequest http://127.0.0.1:11246/api/health -UseBasicParsing
C:\Users\sandr\.local\bin\uv.exe run pytest -q
```

## Craft apps + Ollama model

See `docs/ONBOARDING.md` §3-4. Without them, demos report `wrappee_missing`
/ skipped AI steps - by design, never silently.
