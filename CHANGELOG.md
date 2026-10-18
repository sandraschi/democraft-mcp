# CHANGELOG.md

## Unreleased (2026-10-18, assfix reassess)

Cold-context reassess (score 49): fixed mcpb-pack staging (package dir, not src
dir - bundle imports itself again; pyc/bak purge; stable-name copy), README
Claude Desktop one-liner, skill Configuration section (S1 gate), Tools
tools-count testid, pytest --cov gate (fail-under 55, measured 73%),
.env.example FREECADCMD guard lines. Deferred: WEBAPP_PORTS.md registration
(mcd-side), shim migration (needs manifest relocation + 3-4-100 parity),
streaming chat, Discord channel.

## 0.1.1 (2026-10-15, assfix pass)

First assfix (score -215): fixed all 22 HIGH + most MEDIUM. REST: capabilities,
status, /health alias, chat alias, shutdown, llm/discover+models+onboarding.
MCP mount fixed (path=/ + lifespan + /mcp rewrite, proven over HTTP).
CORS regex + Tauri-gated absolute URLs. Demos: CAD architect set
(plan + south elevation, DXF/PNG/PDF/SVG), full-groove SoundCloud bounce (~56s),
richer pelican prompts with SVG end-tag parsing. Webapp: LLM elicitation
full (discover/dots/selects/persist/disabled), Chat upgrade (personalities,
examples, skill-first, export, clear, 100-cap), Dashboard status strip,
loading/error states, Inbox search+count, font/contrast pass, backoff.
Repo: session channels, pre-commit + hook, gitattributes, bootstrap,
FleetStartMode vendored, starts template, pyright+T20+coverage, justfile fixes.

## 0.1.0 (2026-10-15)

Initial assfix-zero build: `craft` portmanteau (8 ops, 13 apps), Prefab cards,
demo prompt, FastAPI backend (health/crafts/demos/runs/tools/skills/logs/LLM/
dashboard, MCP at /mcp), webapp (catch-them-all + 13 craft pages, onboarding
CTA, MOCK-until-onboarded), docs stack, pytest + ruff + tsc/biome green,
Windows CI, MCPB (3-4-100 prompts), ports 11246/11245 claimed.
