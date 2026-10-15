# docs/DEVELOPMENT.md

Onboarding is required for this repo (wrappees = the 13 Craft apps), so no
N/A rationale applies.

## Loop

```powershell
C:\Users\sandr\.local\bin\uv.exe sync --extra dev
C:\Users\sandr\.local\bin\uv.exe run pytest -q
C:\Users\sandr\.local\bin\uv.exe run ruff check .; C:\Users\sandr\.local\bin\uv.exe run ruff format --check .
cd web_sota; C:\Users\sandr\.bun\bin\bun.exe install; C:\Users\sandr\.bun\bin\bun.exe run check; C:\Users\sandr\.bun\bin\bun.exe run build
```

Or `just ci` (lint + test + web-check + web-build).

## Adding a demo

Add a `Demo` to the app in `src/democraft_mcp/crafts.py`, wire its CLI argv in
`run_demo`, add an example object to `assets/prompts/examples.json`. Demos must
execute a real CLI - dry-run short-circuit only for account-gated features,
declared via `requires: artcraft-account`.

## Test doubles

Declared only: `run_demo` accepts any `outbox` dir (tests use tmp). No mocks
of CLI results - tests run the real headless CLIs.
