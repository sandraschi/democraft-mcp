# DemoCraft Expert

Domain skill for working with democraft-mcp (repo `democraft-mcp`, backend :11246).

## For agents

Use the `craft` portmanteau - one tool, `operation` enum is the catalog:
`craft(operation="list_apps")` (14 apps + install flags), `craft(operation="app_status")`
(CLI paths + missing list), `craft(operation="run_demo", app="<key>", demo="<id>")`
(real headless CLI + local-LLM step, artifacts in `outbox/<app>/<demo>/`),
`craft(operation="craft_commands", app="<key>")` (live command discovery),
`craft(operation="ollama_models")`, `craft(operation="ai_flow", prompt="...")`,
`craft(operation="help")`, `craft(operation="shutdown", confirm=True)`.
Prefab: `show_apps_prefab_card()`, `show_demo_prefab_card(app, demo)`.
Prompt: `democraft_demo_guide(app)`. Resource: `democraft://apps` (live registry JSON).
REST mirrors everything under `/api/*` (MCP mounted at `/mcp`).

## For humans

Open the webapp (:11245), pick a Craft page in the sidebar, press Run demo #1.
Every attempt lands in the Inbox with artifacts and engine logs. MOCK badges
mean a missing wrappee or an account-gated feature - onboarding clears them
by successful runs, never by hand.

## Workflow 1: run and verify a demo

1. `app_status` (is the wrappee installed?).
2. `run_demo` (note `all_cli_ok`, `ai_step.skipped`, artifact bytes).
3. Open the PNG/PDF/DXF/WAV from `run_dir`; compare against the demo's
   verify checklist in `assets/prompts/user.md` (per-demo section).
4. Mismatch? Read `cli_steps[].stderr` first - it is the engine talking.

## Workflow 2: add a demo

1. Map command ids via `craft_commands` (never assume ids).
2. Add the `Demo` + argv wiring in `src/democraft_mcp/crafts.py`.
3. Run it headless twice (fresh outbox the second time).
4. Add an `examples.json` entry and a worked session in `assets/prompts/user.md`.

## Troubleshooting

`wrappee_missing` -> install the Craft app (docs/ONBOARDING.md).
`needs_account` -> generative features need tokens; demo #1s never do.
`needs_input` -> follow the recovery path (e.g. copy landing.png as grade-in).
Non-zero returncode -> quote stderr, fix params, retry. Ollama down ->
AI step skipped, CLI part still runs. Ports busy -> start.ps1 clears first.
