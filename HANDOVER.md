# HANDOVER - democraft-mcp

**As of:** 2026-11-02. **Version:** 0.3.0.
**Assess score:** not re-scored this session; the 91 from 2026-10-21 was self-assessed.

## What this repo is

The demo bench for the Craft family: one page per app, every demo a real headless
`<app>-cli.exe` run plus an optional local-LLM step. 15 apps: 13 Storytold ArtCraft (`core`)
plus 2 community members (SolidCraft by Tangency Labs, Craft Anything by Storytold). One registry
(`src/democraft_mcp/crafts.py`), demos since 2026-11-01 in `recipes.py`, one portmanteau MCP
tool (`craft`), one webapp. 35 demos plus capability maps.

Ports: **11245** frontend, **11246** backend. Gates: `just ci`.

## Last concrete action (2026-11-02)

1. **Craft Anything integrated** as 15th craft app: added `anything/study-and-spec` and
   `anything/oracle-check` clean-room recipes to `recipes.py`.
2. **SolidCraft & TextureCraft verified**: parametric bracket & enclosure fitting, ORM maps
   export and headless Godot import.
3. **Release v0.3.0 tagged and pushed.**

1. **Oct 31 builds.** All 13 core CLIs bumped; drift additive only (104 verbs). Every existing
   demo re-run green on the new builds, baselines accepted for all 14 apps
   (`data/craft_compat.json`, gitignored).
2. **`_upstream/` refreshed** to 2026-11-01 for the 15 Craft clones. The local changes found
   there were formatter output (Biome style) and CRLF churn, no real work; stashed, inspected,
   dropped. Mirrors now pin `core.autocrlf false`, `_upstream\AGENTS.md` + `CLAUDE.md` tell
   agents the folder is read-only, and refreshes go through
   `mcp-central-docs\scripts\refresh-upstream-mirrors.ps1` (hard reset to remote, logged).
   Non-Craft clones (buzz, immich, gods-eye-view, photoprism, Strata, VoiceStudio,
   token-factory-cookbook) were fetched only; run the script with `-All` to clean them too.
3. **SolidCraft** registered (`family="community"`, `maker`); `/api/crafts` carries both.
4. **Recipes** (`recipes.py`, dispatched in `run_demo` before the legacy chain via
   `RECIPES[(app, demo)]` and a `RunCtx` with `do_with(exe, argv)` for cross-app steps):
   grid/macro-replay, pdf/auto-bookmarks, vector/cleanup-pass, solid/parametric-bracket,
   solid/enclosure-fit. Each writes a `*-report.md` with measured numbers.
5. **Webapp redesign**: contact-sheet dashboard (`GET /api/gallery`), family grouping, inline
   last-run outputs, Ctrl+K palette, bench tokens in `index.css`, `lib/appMeta.ts` (hue/icon per
   app), `components/ContactSheet.tsx`, `components/ArtifactGrid.tsx`. Companion button removed
   (it opened nothing). Biome now parses Tailwind directives (`biome.json`).

## Next step

1. EffectCraft camera track to Blender: chain works, solve does not (see `docs/apps/effect.md`).
   Retry with filmed footage or a textured SolidCraft render (appearances exist).
2. Phase 1 of `docs/PLAN.md` continues: port legacy branches of `run_demo` into `recipes.py`
   one app at a time; the recipe pattern is the typed-adapter seam.
3. Regenerate README screenshots after UI changes: start the app, then
   `node webapp/scripts/shots.mjs docs/screenshots` (Node, not Bun: Playwright hangs under
   Bun on Windows).

## Blockers / open items

- **Directory standard**: the frontend dir was `web_sota/` and is now `webapp/` (fleet standard).
  Start script config, justfile, CI, ignore files and docs follow it; old reports and the
  0.3.0b1 changelog keep the old name as history. Restart the dev server from `webapp/`.
- **Goliath has hundreds of stale `python.exe` processes** dating from Oct 30-31 (likely leaked
  MCP server instances). Not touched; worth a look outside this repo.
- **Streaming chat endpoint** and **vendored MCPB pack script** - still open from 2026-10-21.
- **Dashboard KPI "demo runs"** vs `/api/runs` count - still undecided.

## Deliberately not done

- No AI in SolidCraft demos: a model guessing board dimensions would be fabrication.
- Board presets limited to symmetric hole patterns (the script has one `hole_inset`).
- No light theme (fleet standard: dark permanent).

## How to pick it up

1. `just ci`.
2. `src/democraft_mcp/recipes.py` for the new demo pattern; `crafts.py` for the registry.
3. `webapp/src/lib/appMeta.ts` when adding an app (hue + icon), `HERO` in `crafts.py` for facts.
4. `outbox/<app>/<demo>/` - every artifact with `run.json` and the report.
