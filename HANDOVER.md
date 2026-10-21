# HANDOVER — democraft-mcp

**As of:** 2026-10-21. **Version:** 0.2.0b2.
**Assess score:** 91 self-assessed; cold rescore still preferred.

## What this repo is

The demo fleet for the ArtCraft family: one page per Craft app, every demo a
real headless `<app>-cli.exe` run plus an optional local-LLM step. Thirteen
apps, one registry (`src/democraft_mcp/crafts.py`), one portmanteau MCP tool
(`craft`, 8 ops), one webapp. 32 demos, 6 of them streamable ("hands-in"),
12 multi-app flows.

Ports: **11245** frontend, **11246** backend (registered in `WEBAPP_PORTS.md`).
Gates: `just ci` (ruff check + format, pytest with coverage,
tsc, biome, vite build). Last measured: 73 tests, 61.67% coverage, README
structure check strict pass.

## Last concrete action

2026-10-21:
1. **ArtCraft October 21 release drift resolved (wave 1 & 2)**: All 13 installed binaries
   bumped in `C:\Program Files` across two waves (CADCraft 0.10.0, DeckCraft 0.9.0, DesignCraft 0.11.0,
   EffectCraft 0.14.0, FigCraft 0.9.0, FilmCraft 0.10.0, GridCraft 0.10.0, LightCraft 0.11.0,
   PdfCraft 0.10.1, PhotoCraft 0.12.0, SoundCraft 0.11.0, VectorCraft 0.14.0, WordCraft 0.9.0).
   Tripwire drift tested, accepted with `force=True`, and baseline state locked in `data/craft_compat.json`.
2. **Upstream tracking synchronization**: all 14 clones in `_upstream/` fetched and
   fast-forwarded to `upstream/main`.
3. **Docs update**: `docs/WRAPPEE.md` and all 13 per-app pages in `docs/apps/` updated with verified
   latest builds, documented new verbs, and patched gaps.

2026-10-20, two pieces of work:

1. **FilmCraft NLE demo** (`film/timeline-cut`): real cut, cross dissolve,
   H.264 export, two rendered frames; the two film flows now point at it.
   Fixed while verifying: the dissolve was applied inside the export process
   without `--save`, so `cut.fcproj` and the later `transition.png` had no
   transition. It is now a real `exec --save` step, with regression test
   `test_film_timeline_cut_persists_transition`.
2. **Docs pass**: README rebuilt to the fleet wrapper/webapp structure,
   INSTALL rewritten with Options A/A2/B/C/D, new `docs/WRAPPEE.md`,
   `docs/apps/` (13 per-app pages + index), `docs/screenshots/README.md`,
   real Playwright captures (dashboard, hands-in, depot), 16 GitHub topics and
   a new repo description. `effect-still.png` (614 KB) replaced by a 63 KB
   JPEG. `docs/TOOLS.md` corrected from 14 to 13 apps.

## Next step

Phase 1 of `docs/PLAN.md`: harden the adapter contract. The demos work; the
adapter is still a registry of special cases. Extract a typed adapter
(detect / version / commands / run / script / error taxonomy) and make each app
declare capability, not code.

## Blockers / open items

- **Streaming chat endpoint** (`POST /api/chat/stream`) — MEDIUM, open.
- **Vendored MCPB pack script** — MEDIUM, open (manifest relocation + 3-4-100
  prompt parity before the shim migration).
- **`needs_account` is taxonomy only** — no engine currently gates a feature
  through it; `crafts.py` says so in its header. Do not advertise it as live.
- **Dashboard KPI "demo runs" counts only runs with a `started` timestamp**
  (5 today) while `/api/runs` lists 29; older folders predate manifests. If the
  KPI is meant to match the Depot, decide which number is authoritative.
- **Project page** `mcp-central-docs/projects/democraft-mcp/` does not exist
  yet (project-page standard).
- **Cold-context rescore** — recommended; the 91 is self-assessed.

## Deliberately not done

- **Thirteen repos.** No `designcraft-mcp`, `photocraft-mcp`, etc. One hub,
  many adapters.
- **Fake artifacts.** No placeholder renders, no "demo mode" that draws a
  rectangle and calls it a photo.
- **Generative verbs.** The CLIs are editors, not generators. The AI step
  drafts parameters or prose, not pixels.
- **Auto-install.** Wrappees are the product; `docs/ONBOARDING.md` instructs,
  the demo does not silently download paid software.
- **NSIS installer.** The webapp is source-run (`start.bat`); README and
  INSTALL say so instead of implying a one-click app.
- **Cloud LLM.** `ai_step` posts to Ollama's `/api/generate`; an
  OpenAI-compatible provider is not wired in. INSTALL says so.

## How to pick it up

1. `just ci` — confirm the gates are still green.
2. `docs/PLAN.md` — phases and acceptance criteria; start at Phase 1.
3. `src/democraft_mcp/crafts.py` — the registry is the truth for apps and demos.
4. `web_sota/src` — one page per app, generated from the same registry.
5. `outbox/<app>/<demo>/` — every artifact, with `run.json` and engine output.
