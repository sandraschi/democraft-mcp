# PLAN — building out democraft-mcp

**Status:** v0.1.1, thirteen apps, real demos, score 91. This plan turns the demo
fleet into the operational hub for the ArtCraft family. Each phase ships
independently and has an acceptance test that can be run, not argued.

**Non-goals (standing):** no thirteen sibling repos, no fake artifacts, no
generative verbs in the CLIs, no silent installs, no demos that succeed when the
engine failed.

## Phase 1 — Adapter contract (next)

Today each app is a registry entry with ad-hoc branches. Make the adapter an
interface every surface consumes.

- `CraftAdapter`: `detect()`, `version()`, `commands()`, `run(op, params)`,
  `script(lines)`, `capabilities()`, `roots()`.
- Error taxonomy, stable across apps: `wrappee_missing`, `needs_account`,
  `engine_error` (stderr attached), `timeout`, `bad_params`.
- One timeout policy per operation class; no per-app magic numbers.
- Contract tests: every adapter answers `detect`/`version`/`commands` even when
  the app is missing (structured error, not an exception).

**Acceptance:** a new app can be added by declaring a table row plus one demo,
with no `if app == ...` in the API, webapp or MCP layers; contract tests pass
with all apps absent.

## Phase 2 — Job engine

Demos are synchronous subprocess calls. Real work needs a queue.

- Job manifest: id, app, operation, params, started/finished, exit code,
  artifact paths, engine log path, AI step (model + prompt + output), provenance.
- Queue with bounded concurrency; cancel; retry only for `timeout`/`engine_error`.
- Progress over SSE (`GET /api/jobs/{id}/events`); polling stays as fallback.
- Artifacts under `outbox/<app>/<demo>/<job-id>/`; never overwrite a previous run.

**Acceptance:** two long demos run concurrently without blocking the API; a
cancelled job leaves no partial artifact claimed as complete; every manifest
reconstructs which CLI, params and model produced the output.

## Phase 3 — Webapp surfaces

- Per-app pages generated from `commands()` (the CLIs already publish their
  catalogs): a form per operation, validation, real run, artifact preview.
- Asset library: every artifact, filterable by app/job/date, with its log.
- Job history and compare: two runs of the same demo side by side, logs aligned.
- Status page: app detected / version / account-gated / roots, one row per app.

**Acceptance:** a user can run any published CLI command from the browser
without the page knowing app-specific code; every displayed number traces to a
manifest.

## Phase 4 — The book pipeline (first product)

The on-hyperart print build is the proof case: pandoc → styled DOCX →
DesignCraft `file.place` (autoflow) → heads/folios/TOC/plates → PDF.

- Presets: A4 and 6x9, margins, bleed, body/leading, chapter-open recto.
- Plate handling: local archive with credits, PD check, per-chapter placement.
- Known edge: imported table columns are even; solve with a caret-in-cell pass
  or a table pre-pass.
- A `Book` page in the webapp: choose source repo, preset, output, run as a job.

**Acceptance:** rebuilding on-hyperart from the webapp reproduces the CLI build
page-for-page; the job manifest names every source chapter and plate.

## Phase 5 — Fleet handoffs

Hands-in: Calibre covers/metadata, Google Docs exports, arXiv papers, search
results. Hands-out: deliverables into a repo, Calibre `add`/`add_format`, Drive.
Every handoff writes a provenance record; no silent mutation of a library.

**Acceptance:** a book built in Phase 4 lands in Calibre with both formats and a
manifest linking chapters to the PDF pages they became.

## Phase 6 — Packaging and ops

- MCPB audit clean; prompts 3-4-100 parity; shim migration for the pack script.
- Ports registered (done 2026-10-19); `just ci` green on a clean clone.
- Per-app onboarding: install link, licence note, first-demo sanity check.
- Screenshots per app page; README preview matches the live webapp.

**Acceptance:** a naked Windows VM reaches a first successful demo using only
`INSTALL.md` + `docs/ONBOARDING.md`; no step requires the author's machine.

## Order and cost

Phases 1–3 are the hub. Phase 4 is the first product and the reason the hub
exists. Phase 5 is what makes it a fleet citizen. Phase 6 is packaging debt that
should not block 1–3.

Deliberately last: a plugin marketplace, per-app auth, and any feature that
turns the hub into an editor. The apps are the editors. The hub schedules,
records, and hands off.
