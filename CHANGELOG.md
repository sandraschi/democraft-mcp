# CHANGELOG.md

## Unreleased (2026-10-28, ArtCraft 13-app release)

- **Modal handling for hands-in runs.** Probed all GUIs: no Win32 dialogs. The only modal found is SoundCraft's in-window Recover Unsaved Work prompt from a stale autosave; Escape does not dismiss it. windows.quarantine_recovery now moves stale `Autosave`/`Recovery` entries to `%LOCALAPPDATA%\democraft-mcp\recovery_quarantine` before launching a GUI that is not running (moved, never deleted); the result is reported as `recovery_quarantine` in the focus info. FigCraft was not probed (user instance running).
- **GridCraft demo pivot-report**: PivotTable, calculated field and bound PivotChart (insert.pivotTable, pivot.calculatedField, insert.pivotChart), XLSX + PDF. Verified on GridCraft 0.13.x, PDF values checked.
- Drift baselines NOT yet acknowledged: the tripwire still reports the new builds (CADCraft 0.14.0 etc.), which is why `test_craft_commands_cad` fails until acknowledged.

## Unreleased (2026-10-21, Craft apps wave 2 releases)

Second evening wave of ArtCraft releases updated in `C:\Program Files`, tripwire drift acknowledged and verified:

- **PhotoCraft** `0.12.0` (924 verbs, was 0.11.1): adds Mixer Brush commands (`brush.mixer.load`,
  `brush.mixer.clean`), History Brush state management (`history.setSource`, `stepForward`,
  `stepBackward`, `clear`), and Smart-Filter stack support.
- **DesignCraft** `0.11.0` (was 0.10.0): refactored placed-PDF rendering (`PDFR`).
- **FigCraft** `0.9.0` (was 0.8.0): component set and variants discoverability, SVG live text fixes.
- **GridCraft** `0.10.0` (was 0.9.0): MSI package upgrade, formula and calculation engine stability.
- **EffectCraft** `0.14.0` (was 0.13.0): color grading panel integration and rendering pipeline updates.
- **LightCraft** `0.11.0` (was 0.10.0): background asset reloading and paged catalog reading.
- **SoundCraft** `0.11.0` (was 0.10.0): audio-io and marker timing fixes; verified with `ident-jingle`.
- All 14 clones in `_upstream/` fast-forwarded to latest release tags.
- Full CI test suite passing (73 / 73 tests, 61.89% coverage).

## Unreleased (2026-10-21, Craft apps drift & upstream sync)

Eight ArtCraft apps updated in `C:\Program Files`, tripwire drift acknowledged and verified:

- **CADCraft** `0.10.0` (431 verbs, was 0.8.0): adds AutoCAD Express Tools (`breakline`,
  `burst`, `mocoro`, `txt2mtxt`).
- **FilmCraft** `0.10.0` (701 verbs, was 0.9.0): verified against `timeline-cut` and interchange flows;
  introduces animatable graphic properties and track color labels.
- **VectorCraft** `0.14.0` (792 verbs, was 0.13.1): adds `object.objectsOnPath.attach/expand/options`,
  `select.color`, and `path.moveAnchor`.
- **PdfCraft** `0.10.1` (148 verbs, was 0.9.0): adds `page.reverse`, annotation fills/borders, and local model weights.
- **WordCraft** `0.9.0` (633 verbs, was 0.8.0): adds `list.multilevelPreset` (headings 1.1 / article / outline) and `edit.spike`.
- **DeckCraft** `0.9.0`, **EffectCraft** `0.13.0`, and **LightCraft** `0.10.0` bumped and baselined.
- All 14 third-party clones in `_upstream/` synchronized with remote `upstream/main`.
- CI gate passes cleanly (73 tests, 61.67% coverage, Biome, TypeScript, Vite build).

## Unreleased (2026-10-20, film demos)

Three new FilmCraft demos, each verified against 0.9.0 on this machine:

- `interchange-kit` builds the two-clip cut, then exports EDL, FCP7 XML and FCPXML and keeps
  each exporter's own report (EDL: one video track only, Lumetri not representable; FCP7:
  generators written as FilmCraft effect ids, Lumetri curves unsupported; FCPXML: generators
  become gaps, transitions on V1 only).
- `captions-roundtrip` writes a two-cue SRT, imports it onto the built-in demo sequence in
  one process, exports SRT again and lists the track with style and timing. Text survives;
  times quantise to the sequence timebase (1,000 ms in, 1,001 ms out at 24 fps).
- `poster-strip` renders 0 s, 3 s and 6 s at half scale.

Two new flows: `video-delivery` (cut, caption, hand off) and `animatic` (graded stills, shot
board, poster frames). `tests/test_flows.py` now compares against `len(SEED_FLOWS)` instead
of a hard-coded 12, which is what broke when the catalog grew.

## Unreleased (2026-10-20, hands-in window)

Hands-in runs now put the Craft app itself on screen: `run_demo(focus=True)` starts the GUI if
needed (sibling `<app>.exe`, detached), waits for its **titled** main window (an untitled
startup window is a splash - maximising it leaves the real window normal-sized, which is what
the first implementation did), then restores, maximises and foregrounds it before the first
CLI step. The window work uses ctypes only, never raises, and reports `focus` in the result,
the SSE/job event stream and `run.json`: `ok`, `window`, `launched`, `maximized`, `foreground`
and `ms`. If Windows refuses the foreground handoff it tries the Alt-key unlock and records
`foreground: false` instead of pretending.

The webapp sets `focus` only for `live` demos (the hands-in set); MCP calls and multi-app flows
default to `focus=False`, so an agent never steals the foreground. Verified on 2026-10-20 with
FilmCraft launched from a cold start: `window: FilmCraft`, `maximized: true`,
`foreground: true`, 1.46 s, and the window measured at `-7,-7,1288,728` with `IsZoomed` true.
New `tests/test_windows.py` covers missing GUI, launch-then-find, splash rejection, no-window
timeout and exception paths without touching a real window.

## Unreleased (2026-10-20, build probes)

`craft_commands` and `/api/crafts` now read the version and command catalog
from the installed binary instead of assuming a release. The probe walks a
dialect ladder (`commands --json` / `tools --json` / `commands`), records a
baseline per CLI in `data/craft_compat.json` (gitignored), and reports a
changed version or verb set as drift. `craft_commands` refuses to look green
on an unacknowledged upgrade (`error_type: engine_drift`) until `force=True`
accepts the build. Measured 2026-10-20: 13/13 installed, PhotoCraft 0.11.1
against a 0.10.0 baseline (drift reported, then accepted); `/api/crafts`
takes 660 ms cold for 13 probes and is cached after that. New `/apps` page
lists version, build time and drift per app; the dashboard gained a build
strip. Also fixed: `craft(operation="run_demo", app=<unknown>)` raised
KeyError instead of returning a structured error (test added).

## Unreleased (2026-10-20, FilmCraft NLE demo)

`film/timeline-cut`: two demo clips imported (`OceanSunset`, `Aurora`), a 24 fps
1280x720 sequence built from them, a 12-frame cross dissolve on the cut, H.264
export (816 frames, 640x360) and two rendered frames (poster, transition).
Verified: 5 CLI steps, 7 artifacts, no failures. The dissolve is applied by a
real `exec` step with `--save` (not a note claiming success), so `cut.fcproj`
carries it and both rendered frames show it; regression test
`test_film_timeline_cut_persists_transition` fails if the transition survives
only inside the export process. The two film flows now use `timeline-cut`
instead of `storyboard`; they stay exploratory because the cut builds its own
footage rather than ingesting the previous step's artifact, and because
SoundCraft VST3 instruments are silent (BUG-082).

## Unreleased (2026-10-20, docs)

Fleet-standard documentation pass: `README.md` rebuilt to the wrapper + webapp
structure (What this wraps, Preview, What You Can Do with hands-in/out and the
headless callout, app index, install, companions, documentation, licence), and
`INSTALL.md` rewritten with Options A/A2/B/C/D, winget prerequisites and the
Ollama-only AI note. New `docs/WRAPPEE.md` (what ArtCraft is, app table,
disambiguation), `docs/apps/` with one page per Craft app (13), and
`docs/screenshots/README.md`. Preview images are real Playwright captures of
the running webapp (dashboard, hands-in, depot); the 614 KB effect still was
re-encoded to a 63 KB JPEG to meet the 300 KB rule. `docs/TOOLS.md` corrected
from 14 to 13 apps. `llms.txt` gained the execution/artifacts block.

## Unreleased (2026-10-20, Studio embedding)

`/studio` embeds GridCraft's **web build** in an iframe through the app's
same-origin `?host=parent` bridge: the page hands it a CSV, receives
`gridcraft:save` bytes, and tracks `dirty`/`failed`. This is UI embedding, not
the control channel - the web build has no TCP control port. The wasm bundle is
fetched by `scripts/fetch-gridcraft-web.ps1` into gitignored
`web_sota/public/gridcraft-web/` (~19 MB). Chrome stays visible until upstream
exposes `?chrome=0`; asked on PR #1877. Verified: tsc + biome, production build,
static bundle present; the frame is not interactively browser-tested yet.

## Unreleased (2026-10-20, flows)

Multi-app flows: twelve seeded chains across the 13 apps, stored as JSON and
validated against the real app/demo registry. `/flows` lists them with status
(ready / exploratory / blocked), `/flows/{id}` shows the steps and runs them
sequentially, and `/flows/{id}/edit` is a CRUD editor (add, remove, reorder,
edit, delete). The runner copies each step's artifacts into
`outbox/_flows/<run_id>/<NN>-<app>-<demo>/` and reports per-step status; blocked
flows refuse to start with the reason. API: `/api/flows` CRUD,
`/api/flows/{id}/run`, `/api/flows/runs/{id}`, `/api/flow-artifacts/{path}`.
Verified end to end with a two-step capability-map flow: succeeded, 2 bundles.
Correction (2026-10-20): FilmCraft already has a timeline (sequences, clips,
EDL/XML/FCPXML/OTIO/AAF export); the two film chains are exploratory because our
`film:storyboard` step is storyboard-only, not because the app lacks a timeline.
Dashboard updated: eight KPIs (apps, installed, demos, live demos, flows, flow
runs, jobs, demo runs), quick cards for Flows/Hands-in/Depot, and a readymade
flow strip. Docs: `mcp-central-docs/patterns/CRAFT_MULTI_APP_FLOWS.md`.

## 0.2.0b2 - packaging (2026-10-20)

MCPB packaging fixed and shipped. Replaced the vendored pack script with the
fleet shim (`fleet-mcpb-pack.ps1`), moved the bundle manifest to
`mcpb/manifest.json`, synced `.mcpbignore`, and added the package `__main__` the
launch check expects (HTTP on 39812; stdio stays the manifest entry). The bundle
now passes the import-isolation, AST, pollution and packaged-launch checks, and
is attached to the release as versioned `.mcpb`, stable `.mcpb` and
`install.ps1`. No functional changes.

## 0.2.0b1 - beta 2 (2026-10-20)

Second beta. The hub gained a real job engine, a Depot that keeps every run, and
a Hands-in page with taped playback. New demos: PhotoCraft plate grade and batch
treatment, DeckCraft transition reel with real transition frames, a lighthouse
drawn stroke by stroke, and a SoundCraft melody bounced dry and through a VST3
reverb. The free VST3 set was installed and verified; the SoundCraft VST3
instrument silence was isolated as a host bug (BUG-082, upstream PR #347) with
Reaper as the control.

Known: the job queue is in memory (no crash recovery); SoundCraft VST3
instruments stay silent until upstream #347 lands; the CLI still ships no
engines - install the apps from <https://getartcraft.com> first. Detailed dated
entries follow.

## 0.1.2b1 - 0.1 beta (2026-10-20)

First beta of the demo hub. 13 Craft apps, real headless runs, a job engine with
provenance and cancellation, a Depot that keeps every run, and hands-in playback
with speed control. Ships no engines: install the apps from
<https://getartcraft.com> first (`docs/ONBOARDING.md`).

Highlights since 0.1.1: PhotoCraft plate-grade and batch demos; DeckCraft
transition reel (real intro/outro frames); Grid data-to-chart with streaming;
job engine (`/api/jobs`, SSE events, cancel, retry); Depot cards/list with
history and source links; Hands-in page with taped playback; IncaCraft removed.

## Unreleased (2026-10-20, SoundCraft melody hands-in demo)

`sound/melody-vst3`: writes a 16-note MIDI file, imports it into SoundCraft,
solos the new track, bounces it dry on the built-in synth, inserts Valhalla
Supermassive (VST3) and bounces it wet. Nine seconds, three CLI steps, plus a
waveform and piano-roll frame. No AI writes the notes.

Finding, recorded rather than papered over: **VST3 effects process, VST3
instruments do not (yet) - live or headless.** Valhalla audibly changes the
bounce in both modes. Surge XT and Dexed, set as track instruments, rendered
silence on the same clip while the built-in synth played; the earlier "Surge
bounced -17.7 dB" claim was the demo mix, not the plugin. Reproduced in the live
app over `--control 11250`, so it is host-side, not an offline-render artefact.
Reaper 7.80 renders the same MIDI file through both VST3s (Surge 3.45M, Dexed
1.13M peak samples), confirming the plugins are fine and SoundCraft is at fault.
Filed as BUG-082. `docs/FREE_VST3_SET.md` corrected.

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
