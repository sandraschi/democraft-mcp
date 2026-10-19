# HANDOVER — democraft-mcp

**As of:** 2026-10-19. **Version:** 0.1.1. **Assess score:** 83 → 91 (ports HIGH
closed; self-assessed, cold rescore still preferred).

## What this repo is

The demo fleet for the ArtCraft family: one page per Craft app, every demo a
real headless `<app>-cli.exe` run plus a real local-LLM step. No fake pixels.
Account-gated engine features return `needs_account`; missing wrappees return
`wrappee_missing`. Thirteen apps, one registry (`src/democraft_mcp/crafts.py`),
one portmanteau MCP tool (`craft`, 8 ops), one webapp.

Ports: **11245** frontend, **11246** backend (now in `WEBAPP_PORTS.md`).
Gates: `just ci` (ruff, pytest, pyright, tsc, biome, build). Last measured:
37 tests, 72.75% coverage.

## Last concrete action

Tight assfix, 2026-10-19: re-ran gates (green), registered 11245/11246 in
`mcp-central-docs/operations/WEBAPP_PORTS.md` (the open HIGH from the 2026-10-18
run). Full report: `docs/assess-reports/2026-10-19.md`.

## Next step

Phase 1 of `docs/PLAN.md`: harden the adapter contract. The demos work; the
adapter is still a registry of special cases. Extract a typed adapter
(detect / version / commands / run / script / error taxonomy) and make each app
declare capability, not code.

## Blockers / open items

- **Streaming chat endpoint** (`POST /api/chat/stream`) — MEDIUM, open. The
  non-streaming chat works; token streaming is not implemented.
- **Vendored MCPB pack script** — MEDIUM, open. Shim migration needs the
  manifest relocation and 3-4-100 prompt parity checked first.
- **Discord fleet-democraft channel** — LOW, open (no Discord tool in session).
- **Cold-context rescore** — recommended; the 91 is self-assessed.

## Deliberately not done

- **Thirteen repos.** No `designcraft-mcp`, `photocraft-mcp`, etc. The apps ship
  MCP; a wrapper repo each would be thirteen CI pipelines and thirteen tool
  surfaces. One hub, many adapters.
- **Fake artifacts.** No placeholder renders, no "demo mode" that draws a
  rectangle and calls it a photo. If the engine does not run, the demo fails
  loudly with stderr.
- **Generative verbs.** The CLIs are editors, not generators (verified
  2026-10-15). The AI step drafts parameters, not pixels.
- **Auto-install.** Wrappees are the product; `docs/ONBOARDING.md` instructs,
  the demo does not silently download paid software.

## How to pick it up

1. `just ci` — confirm the gates are still green.
2. `docs/PLAN.md` — phases and acceptance criteria; start at Phase 1.
3. `src/democraft_mcp/crafts.py` — the registry is the truth for apps and demos.
4. `web_sota/src` — one page per app, generated from the same registry.
5. `outbox/<app>/<demo>/` — every artifact, with the engine log beside it.
