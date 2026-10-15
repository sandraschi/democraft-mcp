# docs/TOOLS.md

## `craft` (portmanteau)

[RATIONALE] 13 apps, one entry. The `operation` enum is the catalog.

| Operation | Params | Returns |
|-----------|--------|---------|
| `list_apps` | - | 13 apps, installed flags, demo ids |
| `app_status` | - | per-app CLI paths + missing list |
| `run_demo` | `app`, `demo` (=#1 default), `model` | `ai_step`, `cli_steps`, `artifacts`, `run_dir` |
| `craft_commands` | `app` | live `commands --json` from the CLI |
| `ollama_models` | - | local models via `/api/tags` |
| `ai_flow` | `prompt`, `model` | one local-LLM call (declared skip when down) |
| `help` | - | op catalog + usage |
| `shutdown` | `confirm=True` | exits ~500ms after responding |

## Prefab

`show_apps_prefab_card`, `show_demo_prefab_card(app, demo)` - always include a
plain-text `content` fallback.

## Prompts

`democraft_demo_guide(app)` - per-app demo instructions.

## REST

`GET /api/health|crafts|runs|tools|skills|logs|dashboard`, `POST /api/demos/run|llm/chat`.
MCP mounted at `/mcp`. CORS: explicit localhost origins only.
