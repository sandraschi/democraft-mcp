# democraft-mcp - AGENTS.md

Thin override; fleet rules in `D:\Dev\repos\mcp-central-docs\standards\AGENTS.md`.

- Python: `C:\Users\sandr\.local\bin\uv.exe run python` (never naked).
- Backend :11246 (`democraft_mcp.server:app`), frontend :11245. Never hardcode elsewhere.
- Demos run real Craft CLIs into `outbox/`; tests use tmp outbox. No CLI mocks.
- `just ci` before every commit. Max 5 files per commit.
- Upstream Craft repos (`_upstream/`) are read-only - never edit.
- Stateless server: no DB, no daemon/proxy split. stdio runs tools directly.
