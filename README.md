# democraft-mcp

Demo fleet for the ArtCraft family. One page per Craft app, every demo a real
headless CLI/MCP run plus a real local-LLM step. No fake pixels: account-gated
engine features return `needs_account`, missing wrappees return `wrappee_missing`.

![FastMCP 3.4.4+](https://img.shields.io/badge/FastMCP-3.4.4%2B-blue) ![MCPB](https://img.shields.io/badge/packaging-MCPB-green) ![Windows CI](https://img.shields.io/badge/CI-Windows-lightgrey)

## How it runs

Headless by default: each demo shells to the installed `<Craft>\*-cli.exe`
(`C:\Program Files\...`) and renders artifacts into `outbox/<app>/<demo>/`.
With an app open on its control port, the same demos can drive the live app
(`--connect`); the API reports which path ran. Hands-in: run any demo from the
webapp or chat and inspect real outputs. Hands-out: demos never modify your
Craft documents - they work in `outbox/` only.

## Quickstart

1. Install the Craft apps (see `docs/ONBOARDING.md` - wrappees are the product).
2. Double-click `start.bat` (backend :11246, frontend :11245).
3. Open the Dashboard, pick a Craft page, run demo #1.

## Documentation

| Doc | What |
|-----|------|
| `docs/ONBOARDING.md` | Wrappee install, AI model setup, first demo |
| `docs/CONFIGURATION.md` | Env vars, ports |
| `docs/DEVELOPMENT.md` | Dev loop, tests, CI |
| `docs/TOOLS.md` | `craft` operations reference |
| `docs/TROUBLESHOOTING.md` | Engine errors, Ollama down, missing wrappees |
| `INSTALL.md` | Naked-PC install |
| `CHANGELOG.md` | Releases |

## MCP config

```json
{ "mcpServers": { "democraft": { "command": "uv", "args": ["run", "python", "-m", "democraft_mcp.mcp_stdio"], "cwd": "D:\\Dev\\repos\\democraft-mcp" } } }
```
