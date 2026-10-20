# democraft-mcp

Demo fleet for the ArtCraft family. One page per Craft app, every demo a real
headless CLI/MCP run plus a real local-LLM step. No fake pixels: account-gated
engine features return `needs_account`, missing wrappees return `wrappee_missing`.

![FastMCP 3.4.4+](https://img.shields.io/badge/FastMCP-3.4.4%2B-blue) ![MCPB](https://img.shields.io/badge/packaging-MCPB-green) ![Windows CI](https://img.shields.io/badge/CI-Windows-lightgrey) ![beta](https://img.shields.io/badge/status-0.2%20beta-orange)

## Before you start - install the Craft apps

**This repo ships no engines.** Every demo shells to an installed
`<Craft>\*-cli.exe`; without the apps the API returns `wrappee_missing` and the
page tells you to install. Thirteen apps: CAD, Deck, Design, Effect, Fig, Film,
Grid, Light, PDF, Photo, Sound, Vector, Word.

- **Get the apps:** <https://getartcraft.com> (official site / installer)
- **Per-app install notes, licences and sanity checks:** `docs/ONBOARDING.md`
- The vault is not bundled: demos work in `outbox/` and never modify your
  Craft documents.

## Preview

Real engine output, not mockups. PhotoCraft grades a public-domain plate through
Black & White, Curves and Gradient Map adjustment layers; DeckCraft renders a
real wipe-transition frame between two AI plates.

| PhotoCraft plate grade | DeckCraft wipe (t = 0.4) | PhotoCraft lighthouse (stroke demo) |
|---|---|---|
| ![plate grade](docs/screenshots/plate-grade.jpg) | ![wipe](docs/screenshots/transition-wipe.jpg) | ![lighthouse](docs/screenshots/lighthouse-live.jpg) |

The lighthouse is drawn stroke by stroke in PhotoCraft (13 stages, no AI), the
way hands-in playback shows it. The pelican-on-a-bike prompt is kept separately
as Simon Willison's benchmark: deliberately awkward to draw, easy to compare
across models - not a showcase.

Shapes are AI-drawn, pixels are engine-rendered - the compare page shows both
engine logs side by side.

## How it runs

Headless by default: each demo shells to the installed `<Craft>\*-cli.exe`
(`C:\Program Files\...`) and renders artifacts into `outbox/<app>/<demo>/`.
With an app open on its control port, the same demos can drive the live app
(`--connect`); the API reports which path ran. Hands-in: run any demo from the
webapp or chat and inspect real outputs. Hands-out: demos never modify your
Craft documents - they work in `outbox/` only.

## Quickstart

1. Install the Craft apps from <https://getartcraft.com> (see `docs/ONBOARDING.md` - wrappees are the product).
2. Double-click `start.bat` (backend :11246, frontend :11245).
3. Open the Dashboard, pick a Craft page, run demo #1.

## Free VST3 set

SoundCraft (and Reaper, once its path is set) can use a curated free set:
Surge XT, Surge XT Effects, Dexed, the four Dragonfly reverbs, Valhalla
Supermassive, and Cardinal (modular). Details, licences and re-scan steps:
`docs/FREE_VST3_SET.md`.

## What 0.2 adds

- **Job engine**: `POST /api/jobs`, per-run provenance (`job.json`,
  `events.jsonl`), SSE event stream, cancel at the step boundary, retry as a new
  job.
- **Depot** (was Inbox): every run kept, cards/list toggle, source and artifact
  links, history browsing.
- **Hands-in**: a dedicated page and taped playback with Play / Pause / Stop /
  Rewind and a 0.25x-4x speed slider.
- **New demos**: PhotoCraft plate grade and batch treatment, DeckCraft
  transition reel with real transition frames, a lighthouse drawn stroke by
  stroke, and a SoundCraft melody bounced dry and through a VST3 reverb.

## Flows

`/flows` ships twelve readymade multi-app chains - cover factory, photo book,
data deck, CAD board, poster lab, data report, brand kit, storyboard, lyric
sheet, audiobook art, title sequence, score-driven cut. Each is an ordered list
of real demos across apps; the runner executes them sequentially and bundles the
artifacts under `outbox/_flows/<run>/`. Create, edit, reorder and delete flows in
the UI (`/flows/new`). Blocked flows say why (FilmCraft timeline, SoundCraft VST3
instruments). Seed catalog: `src/democraft_mcp/flows.py`; design notes:
`mcp-central-docs/patterns/CRAFT_MULTI_APP_FLOWS.md`.

## Stack

Python 3.11+ (uv) - FastMCP 3.4.4+ - FastAPI + Pydantic v2 - Uvicorn -
prefab-ui. Webapp: React 19 - Vite 6 - TailwindCSS 4 - Lucide - Framer Motion -
Zustand - React Router - TypeScript - Biome - Playwright. Package managers:
uv (Python) + Bun (JS). Gates: `just ci` (ruff, pytest, pyright, tsc, biome, build).

## Tools

| Tool | Pattern | What |
|------|---------|------|
| `craft` | portmanteau (8 ops) | list_apps, app_status, run_demo, craft_commands, ollama_models, ai_flow, help, shutdown |
| `show_apps_prefab_card` | Prefab | Installed-apps card |
| `show_demo_prefab_card` | Prefab | Single-demo card |
| prompt `democraft_demo_guide` | prompt | Per-app demo instructions |
| resource `democraft://apps` | resource | Live registry JSON |

Full reference: `docs/TOOLS.md`.

## Env vars

| Var | Default |
|-----|---------|
| `DEMOCRAFT_PORT` | `11246` (frontend :11245) |
| `DEMOCRAFT_MODEL` | `gemma4:e4b` |
| `DEMOCRAFT_OLLAMA_URL` | `http://127.0.0.1:11434` |
| `DEMOCRAFT_OUTBOX` | `<repo>/outbox` |
| `DEMOCRAFT_PROGRAM_FILES` | `C:\Program Files` |
| `DEMOCRAFT_PREFAB_APPS` | `1` (0 skips Prefab tools) |

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

## Install (Claude Desktop on Windows)

Open **Windows PowerShell** and run (labels per MCPB_PACKAGING_STANDARDS.md 2.2b):

```powershell
irm https://github.com/sandraschi/democraft-mcp/releases/latest/download/install.ps1 | iex
```

Then quit Claude Desktop completely (tray > Quit) and relaunch - democraft appears
under Settings > Extensions. The `.mcpb` bundle is a Claude Desktop format; other
clients (Cursor, VS Code, Claude Code) use the `uv` MCP config above instead -
`uvx` has no published package to install from (local-only distribution).
