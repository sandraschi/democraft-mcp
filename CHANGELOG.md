# CHANGELOG.md

## 0.1.2b1 - 0.1 beta (2026-10-20)

First beta of the demo hub. 13 Craft apps, real headless runs, a job engine with
provenance and cancellation, a Depot that keeps every run, and hands-in playback
with speed control. Ships no engines: install the apps from
<https://getartcraft.com> first (`docs/ONBOARDING.md`).

Highlights since 0.1.1: PhotoCraft plate-grade and batch demos; DeckCraft
transition reel (real intro/outro frames); Grid data-to-chart with streaming;
job engine (`/api/jobs`, SSE events, cancel, retry); Depot cards/list with
history and source links; Hands-in page with taped playback; IncaCraft removed.

## Unreleased (2026-10-20, lighthouse hands-in demo)

`photo/lighthouse-live`: thirteen stroke stages on a blank 1200x800 canvas, drawn
with `paint.stroke` point streams (sea, haze, tower, bands, gallery, lantern,
roof, beam, glow, door, rocks, waves, rain). Each stage saves a `.pcraft` and
exports a frame, so hands-in playback is the drawing itself - 27 CLI steps, no
AI. Pelican benchmark restored (photo + vector) with the Willison credit: it is
a measurement, not a showcase; changing the prompt would have broken
comparability.

## Unreleased (2026-10-20, Phase 2 job engine)

`src/democraft_mcp/jobs.py`: bounded two-worker queue, per-job run directory
(`outbox/<app>/<demo>/jobs/<id>/`), `job.json` + `events.jsonl`, SSE
replay-then-follow, cancel at the step boundary, retry as a new job, artifact
serving per job. API: `POST/GET /api/jobs`, `GET /api/jobs/{id}`,
`GET /api/jobs/{id}/events`, `POST /api/jobs/{id}/cancel|retry`,
`GET /api/jobs/{id}/artifacts/...`. The hands-in player now runs a job and can
Cancel it; its tape includes queued/start/step/done. Tests: lifecycle +
provenance, cancel-while-queued, retry. Verified end to end through TestClient:
create -> running -> succeeded, capabilities.txt served. Caveats recorded in
`docs/PLAN.md`: in-memory queue (no crash recovery), cancel lands at the step
boundary, Depot not yet listing jobs.

## Unreleased (2026-10-20, hands-in playback controls)

The hands-in stream now tapes the run and plays it back under user control:
Play / Pause / Stop / Rewind, a 0.25x-4x speed slider, and a step counter.
Default pace is 1.5 s per step at 1x, so a four-step GridCraft build takes six
seconds instead of flashing past. The final artifacts stay hidden until the tape
is played out; Stop rewinds to the first step. Live streaming still runs at real
speed underneath - the controls govern the viewing, not the engine.

## Unreleased (2026-10-19, IncaCraft removed)

IncaCraft was a joke app, not a wrappee. Removed the registry entry, its
dry-stone demo branch, its hero metadata, its topic list, the test that drove it,
and the one-line mentions in onboarding and llms.txt. The fleet is the 13 real
ArtCraft apps (CAD through Word); FreeCAD helpers stay because CADCraft's
optional isometric path still uses them.

## Unreleased (2026-10-19, transitions + hands-in streaming)

- **Deck transition reel** (`deck/transition-reel`): three AI plates, three real
  transitions (push, wipe, split). DeckCraft exports the deck, a slide GIF,
  per-slide PNGs and renders actual transition frames; a 12-frame GIF is
  assembled from them. Verified: 5 CLI steps, 22 artifacts, mid-wipe frame shows
  the incoming slide over the outgoing one.
- **Hands-in streaming**: `POST /api/demos/stream` runs a demo in a thread and
  emits SSE events (`ai`, `step`, `done`, `error`) as each CLI step finishes,
  with artifacts so far. Webapp gets a "Watch it build" checkbox that reads the
  stream and lists steps plus artifact links live. Verified against GridCraft:
  6 events, 4 steps.
- **Pelican brief replaced**: the photo/vector benchmark now asks for a
  three-colour lighthouse poster instead of the bicycle pelican; titles say
  "poster benchmark". IDs unchanged so outbox paths stay stable.

## Unreleased (2026-10-19, PhotoCraft batch demo)

`photo/batch-treatment`: PhotoCraft's batch/actions engine applied one recorded
action (Black & White, Curves, Gaussian grain in `assets/photo/batch-actions.json`)
to three 2024 AI generations from the local archive, re-encoded as JPEG. Proves
the batch path that plate-grade does not: three inputs, one action, three outputs,
per-file warnings surfaced. Inputs and provenance in `assets/ai-art/CREDITS.md`
(model/seed/prompt were not recorded with the files).

## Unreleased (2026-10-19, PhotoCraft flagship demo)

`photo/plate-grade`: a real public-domain plate (Böcklin, *Isle of the Dead*,
1880) through PhotoCraft's non-destructive stack — Black & White, Curves and
Gradient Map adjustment layers — saved as `.pcraft` with the layer tree intact,
then flattened to PNG and JPG. Deterministic recipe; the AI step only writes the
restoration note. Asset bundled at `assets/photo/isle-of-the-dead.jpg` (247 KB,
PD). Verified end to end: 4 CLI steps, 4 artifacts, four layers in the `.pcraft`.
Topic-test relaxed to "every app has at least one topic-driven demo"; deterministic
demos (plate-grade, capability map) are allowed.

## Unreleased (2026-10-19, craft pages hero)

Per-app pages now open with a hero: the app, the tool it is a local alternative
to, a short description, and **observed gaps** (chips, explicitly not a roadmap).
Below it, a demo selector; every app has at least two demos. Demo 2 for every
app is a real capability map: `commands` (or `--help` fallback for PdfCraft)
dumped to `capabilities.txt`, no AI step. Also fixed CLI output decoding on
Windows (UTF-8 with replacement; cp1252 was crashing on non-ASCII catalogs).
Tests: registry contract (hero + >=2 demos + no-AI capability map), 39 passing.

## Unreleased (2026-10-19, tight assfix + plan)

Tight verification, not a full re-audit: gates green (ruff, 37 tests at 72.75%,
tsc+biome). Closed the open HIGH by registering ports 11245/11246 in
`mcp-central-docs/operations/WEBAPP_PORTS.md` (verified free across the fleet).
Score 83 -> 91, self-assessed. Added `HANDOVER.md` and `docs/PLAN.md` (six
phases: adapter contract, job engine, webapp surfaces, book pipeline, fleet
handoffs, packaging). Open: streaming chat, vendored pack-script migration,
Discord channel.

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
