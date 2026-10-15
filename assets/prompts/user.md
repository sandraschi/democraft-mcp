# democraft-mcp user guide (workflows)

How to demo each Craft app with democraft-mcp: chat calls, CLI equivalents,
what to look at in the artifacts, and what to do when the engine says no.
Conventions: `craft(operation='run_demo', app='<key>')` runs demo #1.
Artifacts land in `outbox/<app>/<demo>/`. AI steps use `DEMOCRAFT_MODEL`
(default gemma4:12b); a down Ollama marks the step skipped and the CLI part
still runs.

## CADCraft: house-plan

Goal: prove the CAD headless loop on the Japanese small house plan. Chat:
`craft(operation='run_demo', app='cad')`. CLI equivalent:
`cadcraft-cli sample floorplan floorplan.dxf`, `cadcraft-cli info
floorplan.dxf`, `cadcraft-cli sample floorplan floorplan.png`. Look at:
floorplan.png (the plan), info JSON stdout (entities, extents - the AI room
reading is grounded in this, not in the model's imagination). The AI step
lists genkan/washitsu/engawa/LD/bath as a reading aid; it does not redraw
the plan. Next: `--script-file` with a CURShapes script for tatami grids -
draft the script with `ai_flow`, run with `run --metric --script-file`,
report engine errors verbatim. If `sample` gains a `machiya` variant, add it
as demo #2 without touching demo #1.

## DeckCraft: pitch-deck

Goal: slide pipeline end to end. Chat: run_demo app deck. CLI:
`deckcraft-cli render --sample --all slides/`. Look at: PNG per slide,
slide count (AI outline must match the rendered count - check it). Then
`describe` one command and `run --sample --cmd` a text swap to show scripted
edits. Transition demo: `render-transition` on the sample with two t values.
Failure mode: sample name changes upstream - `info` first, adapt, never
hardcode slide counts in the page.

## DesignCraft: print-spread

Goal: magazine engine headless. Chat: run_demo app design. CLI:
`designcraft-cli run --sample --all-pages pages/`. Look at: page PNGs,
glyph counts in stdout (thousands = real shaping). AI step describes the
two-page spread (palette from the renders, not invented). Follow-up:
`script` a `.dcs` file placing the pelican PNG from the photo demo into a
frame - the cross-app spread Sandra asked for. IDML export and PDF/X-4 are
demo #2 material; verify flags with `describe` before advertising.

## EffectCraft: title-card

Goal: motion engine without a project. Chat: run_demo app effect. CLI:
`effectcraft-cli info`, then `render-frame --out title-card.png`. Headless
with no project, expect the engine's real refusal - the demo reports the
capability map (info + commands) as the artifact. That is the documented
behavior, not a failure to hide. When a sample project exists, the same demo
retries the still and the page shows both paths. AI step writes the 3-element
title spec (text/palette/timing) used for the retry.

## FigCraft: landing-page

Goal: template-to-PNG proven pattern. Chat: run_demo app fig. CLI: write
`landing.jsonl` with `{"command":"file.newFromTemplate","params":
{"template":"landing-page"}}`, `figcraft-cli run landing.jsonl --out
landing.figcraft`, `figcraft-cli render landing.figcraft -o landing.png`.
Expect ~190 nodes, Desktop 1440 + Phone frames, 20 styles. AI step lists
sections. This exact pattern built democraft's own reference render. Other
templates (dashboard, design-system, wireframe-kit) are demo #2+; enumerate
with `template.list` via run first.

## FilmCraft: storyboard

Goal: honest video-engine demo. Chat: run_demo app film. CLI:
`filmcraft-cli inspect`, `filmcraft-cli inspect sequence`. No project means
empty answers - reported, with the AI 3-shot pelican board alongside.
Assembly (`run` script creating sequence + `render`) is gated on a project
file and stays a declared demo #2. Never render black frames and call them
footage.

## GridCraft: homepage-grid

Goal: spreadsheet round-trip. Chat: run_demo app grid. CLI: write
`lineup.csv`, `gridcraft-cli convert lineup.csv lineup.xlsx`,
`gridcraft-cli cat lineup.xlsx --csv`, `gridcraft-cli eval "6*7"`. Look at:
cat output equals the CSV (fidelity), eval prints 42. AI step summarizes the
sheet. Extension: `check` the xlsx for calc-oracle fidelity, `functions
--search` for one demo formula. Sheets with charts: `info` first.

## SoundCraft: ident-jingle

Goal: audio engine voice. Chat: run_demo app sound. CLI: `soundcraft-cli
run --demo --inspect`. Look at: inspect JSON (tracks, demo project shape).
AI step briefs tempo/key/layers. Bounce (`--bounce out.wav --start/--end`)
is attempted only with explicit params; long bounces get generous timeouts,
never backgrounded silently. Normalize/convert demos (`convert --normalize`)
are demo #2.

## WordCraft: demo-report

Goal: document round-trip. Chat: run_demo app word. CLI: AI drafts
`brief.md`, `wordcraft-cli convert brief.md brief.docx`, `convert brief.md
brief.pdf`, `info brief.docx`. Look at: docx + pdf byte sizes, info pages.
`--markup` converts show tracked changes; `run --author` passes are demo #2
with `--automation-read-root/--write-root` confinement. Zotero commands need
running Zotero - declared dependency, demo #3.

## PdfCraft: portfolio

Goal: combine the chain's PDFs. Chat: run_demo app pdf. CLI: seed via word
chain (`seed.md` -> `brief.pdf`), `pdfcraft-cli combine brief.pdf brief.pdf
--out portfolio.pdf`, `render portfolio.pdf --page 1 --out thumb.png`,
`info portfolio.pdf`. Look at: thumb PNG, page count 2. Extensions: `edit`
(rotate/delete), `extract`, `split`, `audit` (faux-redaction finder), `text`
per page - each a demo #N with real inputs. Never combine the same file
twice without saying so (this demo says so: it is the point).

## LightCraft: grade-pelican

Goal: develop pipeline on real pixels. Chat: run_demo app light. CLI:
`lightcraft-cli commands --json` (map the real ids first - never assume
`develop.set` exists), then the develop run against `grade-in.png` with
`app.export path=grade-out.png`. Missing input returns `needs_input` with
the copy instruction (copy the fig landing.png). AI step suggests
exposure/contrast/saturation from the input's histogram reading where
available, else declares the suggestion ungrounded. Before/after pair is the
artifact; the page shows both.

## PhotoCraft: pelican-photo

Goal: same prompt as vector, photo pipeline. Chat: run_demo app photo. AI
step writes minimal `pelican.svg` (raw shapes, declared AI-drawn). CLI:
`photocraft-cli convert pelican.svg pelican.png`, `info pelican.png`. Look
at: PNG renders, info mode/depth/layers. No generative verbs exist in this
build (verified 2026-10-15: no text-to-image, no tokens, no cloud model) -
if ArtCraft ships any, they become demo #2 with the token pointer.
Format matrix (`--quality`, webp lossy vs lossless, tiff-layers) is demo #3.

## VectorCraft: pelican-vector

Goal: same prompt as photo, vector pipeline. Chat: run_demo app vector. Same
AI SVG. CLI: `vectorcraft-cli run --in pelican.svg --export pelican.png`.
Compare page: both PNGs + both engine logs side by side. If the CLI rejects
SVG import, the rejection is the artifact - file it, do not convert on the
side and pretend. Automation roots (`--automation-read-root outbox`) for
agent-driven sessions.

## Cross-app flows

Word-to-PDF-to-portfolio: word demo-report, then pdf portfolio with the real
brief.pdf (the pdf demo does exactly this). Fig-to-Light: fig landing-page,
copy landing.png as grade-in, light grade-pelican. Pelican compare: photo +
vector demos, compare page. House-to-spread: cad house-plan PNG placed by a
design `.dcs` script (verify `frame.create`/`place_image` ids first).

## Onboarding flow (chat script)

New user: `app_status` (what is installed), red CTA lists missing wrappees
with getartcraft.com/apps links, `ollama_models` (or install Ollama), run
cad house-plan (no inputs needed), open outbox. Pages carry MOCK badges
until their wrappee + one successful run. Never clear a badge by hand.

## When the engine says no

Read `cli_steps[].stderr` first. `wrappee_missing`: install. `needs_input`:
follow the recovery path. Non-zero with empty stderr: re-run with the
narrowest argv (`info`, `commands`) to isolate. Timeouts: 120s per step is
already generous - split the demo, do not raise blindly. Report all of it;
the runs inbox keeps every attempt, including failures.

## Worked sessions (annotated transcripts)

Session CAD (house-plan): call run_demo cad. AI step returns 5 rooms JSON
(model gemma4:12b, ~8s). CLI: sample writes floorplan.dxf (check bytes >
10k), info prints entities JSON (keep, this grounds the caption), sample
renders floorplan.png (check 100+KB). Artifacts 2 files. Caption for the
page: rooms from AI + extents from info. If info shows zero entities, say so
and show the PNG anyway - do not invent rooms.

Session Deck (pitch-deck): run_demo deck. AI outlines 5 slides. render
writes slides/page-*.png. Count files with dir listing; if the sample has 4
slides, correct the outline to 4 in the report. Then describe
`slide.create` (verify id via commands) and note scripted edits as demo #2.

Session Design (print-spread): run_demo design. Sample writes pages/*.png;
stdout carries glyph/word counts - quote the numbers. AI spread description
references left/right by the actual rendered order. Cross-app: place the
photo pelican.png via a .dcs script (frame.create + place_image, verify ids
with describe first), render, attach both.

Session Effect (title-card): run_demo effect. info JSON lists engine
version + open comps (likely none). render-frame attempt returns nonzero +
stderr "no composition" (wording varies - quote it). Report the capability
map: comp count 0, command count from commands listing, title spec from AI
held for retry. Page shows MOCK-until-project badge.

Session Fig (landing-page): run_demo fig. landing.jsonl (1 line),
landing.figcraft (~50KB, ~190 nodes), landing.png (~600KB). Verify with
info: frames Desktop/Phone. AI sections list. This session is the reference
implementation - when other demos behave oddly, compare against this one's
shape (script + build + render + verify).

Session Film (storyboard): run_demo film. inspect -> {} or minimal JSON;
inspect sequence likewise. Report both verbatim (truncated), attach AI
3-shot board (shot/lens/action). Render/assembly stays demo #2 behind a
project file. Never present the board as footage.

Session Grid (homepage-grid): run_demo grid. lineup.csv 4 lines;
lineup.xlsx (~5KB); cat --csv output diffed against input (equal =
fidelity proven); eval prints 42. AI one-liner quoted. Extension session:
`functions --search lookup` then a real VLOOKUP demo on a second sheet.

Session Sound (ident-jingle): run_demo sound. inspect JSON: tracks, sample
rate, demo flag. AI brief quoted (tempo/key/layers). Bounce session (demo
#2): run --demo --bounce ident.wav (full Midnight Groove, ~56s, 300s
budget), verify wav seconds, report duration. convert --normalize on the
bounce is demo #3.

Session Word (demo-report): run_demo word. brief.md (AI or fallback -
state which), brief.docx (~8KB), brief.pdf, info (pages/paragraphs/words).
Open the docx in Word once (human check) during onboarding verification.
Markup session (demo #2): run --author with newComment + trackChanges,
convert --markup, show Comments section - the exact proof from the
21-wordcraft note.

Session Pdf (portfolio): run_demo pdf. Seed chain if needed (wordcraft
convert recorded as its own step with exe path). combine -> portfolio.pdf
(2 pages per info), thumb.png render. Quote page count. Edit session (demo
#2): --rotate/--delete on a copy, render before/after thumbs.

Session Light (grade-pelican): run_demo light. First commands --json -
read it, pick real ids (example shapes only, never assumed). grade-in.png
present? If missing: needs_input + copy instruction, stop, no fake pixels.
Develop run writes grade-out.png; page shows before/after + the exact argv.
AI suggestion labeled grounded/ungrounded.

Session Photo (pelican-photo): run_demo photo. AI SVG saved verbatim (show
first 200 chars on the page). convert -> pelican.png, info (mode/depth).
State plainly: shapes are AI-drawn, pixels are engine-rendered. There is no
generative demo #2 today (no such verbs in this build); a formats matrix
is the honest demo #2.

Session Vector (pelican-vector): run_demo vector. Same SVG bytes as photo
(compare hashes on the page). run --in --export. Rejection (if any) shown
verbatim with the acceptance rule it cites. Compare page: both PNGs, both
logs, hash line.

## Demo #2 backlog (verify ids with describe/commands first, never assume)

CAD: CURShapes tatami script via --script-file (draft with ai_flow, run
--metric). Deck: scripted text swap on the sample (`run --sample --cmd`).
Design: .dcs spread placing the pelican PNG (frame.create + place_image).
Effect: render range (`render --start/--end`) once a project is open.
Fig: dashboard template + icon-set. Film: sequence assembly from the EDL
(newSequence + clip verbs). Grid: VLOOKUP second sheet + check oracle.
Sound: full-groove bounce + normalize convert. Word: --author tracked pass +
--markup export. Pdf: edit rotate/delete before/after + audit faux-redaction
demo. Light: second grade with mapped develop ids. Photo: format matrix
(webp quality, tiff-layers) + generative attempt with tokens. Vector:
document.json-fed caption + automation-roots agent session. Each #2 gets its
own worked session entry when it first runs green.

## Release and promotion discipline

Public repo: no secrets, no tokens, no private paths in code or docs (use
C:\Program Files + outbox/ only). Promotion per FLEET_PROMOTION (no spam):
wrappee GitHub discussions only where demo value is shown (renders
attached), never bare links. MCPB + NSIS tracks per PACKAGING_STANDARDS;
Tauri installer only after the Phase-1 A-J audit. Weekly re-run: all 13
demo #1s headless, diff the runs inbox against last week, file engine
regressions upstream with the exact argv + stderr.

## Failure field guide (real shapes, real fixes)

no active sequence (film inspect in a fresh process): state does not cross
processes - use single-session `run` scripts (openDemoProject + export in
one file). unknown command `inspect` (film run line 2): run-script ids come
from the same command list, but top-level subcommands (inspect, describe)
are not run ids - keep them as separate argv. no composition (effect
render-frame with no project): open the demo project first with exec, same
or separate process (Effect resolves the bundled demo). EDL caveats
(verbatim report lines from a real export): EDLs hold one video track;
synthetic media becomes reel AX; Dip-to-Black/Push become dissolves with
EFFECT NAME comments; Lumetri Color cannot be represented - quote these on
the storyboard page so editors trust the export. empty cat output (grid):
wrong sheet name - info the file first, pass --sheet. convert silence with
zero-byte out (any CLI): target dir missing - run_demo creates run_dir; raw
CLI users must mkdir. Ollama 404 model: pull it or set DEMOCRAFT_MODEL to a
listed tag (ollama_models op). Ollama refused: ollama serve not running.
CLI not found: wrappee_missing - install path, never PATH hacks. Non-UTF8
stdout (glyph stats): subprocess uses text=True with errors default - runner
keeps last 6000 chars; wide tables may clip, re-run narrowed. Timeout at
120s (long bounces/renders): split ranges, never raise blindly. combine with
one input: needs 2+ pdfs (self-combine is declared, not hidden). render
--page beyond count: engine errors - info first for page count. audit finds
faux redaction: that IS the finding - report, do not edit around it. check
exits 1 (grid oracle): diff lines are the bug report - attach them.
--markup convert without comments: Comments section absent is correct, not
an error. Prefab app missing (DEMOCRAFT_PREFAB_APPS=0): plain dicts still
carry content text - hosts without App render stay informed.

## Reading engine JSON

cad info: entities/extents/layers. deck render stdout: slide files written.
design run stdout: glyph/word/page counts. effect exec: {"comp": id};
render-frame: "rendered WxH at Ts in Nms -> path". fig run: one JSON line
per step {command, ok, result|error, ms}; info: frames/nodes/styles/pages.
film run: one JSON line per line {id, line, ok, result|error}; export
results carry bytes+path+report[]. grid cat --csv: raw rows; eval: value.
sound inspect: project/track JSON. word info: pages/paragraphs/words +
properties.created/modified. pdf info: pages + metadata; render: written
path. light run: per-command {command, ok, result|error, ms}. photo info:
size/mode/depth/layers [--compact for short]. vector document.json: full
doc model (large - preview, do not paste whole). commands --json shapes
vary: array (effect/fig/film/grid/word/light/photo/vector) vs text-first
browsing on cad/deck/design/sound/pdf (use FILTER + describe).

## Per-demo verify checklists (human pass, onboarding + quarterly)

CAD: open floorplan.png (plan visible, dimensions legible), info JSON has
entities > 0, dxf > 10KB. Fail: zero entities (sample changed - re-probe).
Deck: count slides/*.png (matches AI outline number), open first/last
(onc-brand, readable). Fail: count drift (correct the outline, note it).
Design: open two page PNGs (type set, images placed), quote glyph count.
Fail: zero glyphs (sample flag changed). Effect: title-card.png 1920x1080
~600KB opens (still from demo project); else capability map shown + MOCK.
Fail: silent empty PNG (check bytes, re-run). Fig: landing.png opens
(hero + sections), info frames Desktop/Phone. Fail: node count collapse
(template changed - list templates). Film: storyboard.edl opens, TITLE +
timecodes present, clip names quoted; AI board attached separately. Fail:
empty EDL (project failed to open - attach line-1 result). Grid:
lineup.xlsx opens in Excel/Libre (3 rows), cat output == csv input, eval 42.
Fail: inequality (report both texts). Sound: inspect JSON has tracks;
bounce wav plays ~56s (full Midnight Groove). Fail: short file (bounce was
clipped - re-run without --start/--end). Word: docx
opens in Word (5 bullets), pdf opens (1 page), info counts match. Fail:
font substitution warnings (note, not error). Pdf: portfolio.pdf 2 pages,
thumb.png shows page 1. Fail: page count != 2 (seed chain broke). Light:
grade-out.png side-by-side with grade-in (visible change or declared
no-op with argv quoted). Fail: identical bytes with success=true (flag as
suspect, re-map ids). Photo: pelican.png opens (shapes visible), info
mode/depth sane, SVG first-200-chars quoted. Fail: empty PNG (convert
rejected svg - attach stderr). Vector: pelican.png opens, hash differs
from photo PNG (different pipelines) or note why identical. Fail: byte-same
as input svg rasterized elsewhere (prove engine ran via logs).

Regression signals week-over-week: artifact byte-size cliffs (±50%),
step-count changes, new stderr lines, ms jumps (10x), command-count drift
in inventories, node/entity/track count moves. Any one: file upstream with
argv + stderr + versions, link the runs.

## Chat playbook (copy-paste openers)

Inventory: "List all craft demo apps with install state." "Which wrappees
am I missing?" "What does the photo demo need?" Single demos: "Run the CAD
house-plan demo and show me the PNG." "Render the deck sample and count
slides." "Build the Fig landing page and tell me node count." "Export the
film EDL and quote three clip names." "Round-trip the grid lineup and prove
fidelity." "Convert the word brief and give me sizes." "Combine the PDF
portfolio and show the thumb." "Grade the pelican PNG and show before/after
argv." "Run the vector pelican and compare with photo." Discovery: "List
EffectCraft commands matching render." "Describe file.exportEdl params."
"Which LightCraft develop commands exist?" AI flows: "Caption the CAD info
JSON in one line." "Draft a CURShapes tatami script for later." "Brief the
ident jingle." Models: "List local Ollama models." "Retry the last demo
with mistral-nemo." Ops: "Show the runs inbox." "What failed this week?"
"Clear a MOCK badge: what is the proof rule?" (Answer: one successful run,
never by hand.)

## Five-minute live demo script

Minute 1: Dashboard (KPIs, red CTA if applicable), app_status in chat.
Minute 2: CAD house-plan run (fastest engines first: grid eval is instant,
word convert seconds). Minute 3: open floorplan.png + Pelican compare page
(photo vs vector, logs side by side). Minute 4: film EDL timecodes +
Effect still fullscreen. Minute 5: runs inbox (every attempt kept) + Q&A
with the failure field guide open. Close: repo link, install is start.bat,
tokens never needed for what they just saw.

## Assessor walkthrough (15 minutes, zero trust)

Minute 0-2: app_status (13 rows, installed flags match C:\Program Files),
ollama_models (or llm_down with recovery). 2-5: run cad + grid + word
demos; open floorplan.png, lineup.xlsx, brief.docx from outbox. 5-8: photo
+ vector pelican (compare hashes, read both logs). 8-11: film EDL (clip
names), effect still (1920x1080), fig landing.png. 11-13: POST /api/demos/run
for deck + design + sound (artifacts in outbox). 13-15: pdf combine, light
needs_input path (do NOT create grade-in for them - watch the declared
error), runs inbox lists all attempts. Pass bar: every op answers, every
failure carries error_type + recovery, zero invented files.

## Demo #3+ ideas (backlog, not promises)

Batch night: all 13 demo #1s in one run, inbox diff vs last week (drift
radar). School workshop: pelican SVG hand-edit session (kids change shapes,
engines re-render live). Engine rodeo: same brief through word convert
formats (odt/rtf/html/tex) compared. EDL cinema: film EDL + effect still +
sound bounce on one compare page. Machiya: CAD CURShapes tatami script from
an AI flow, DXF + PNG. Deck automail: sample-to-PDF handout. Grid audit:
check-oracle on a real budget sheet. All recorded here so they are plans,
not implied features.

## AI step craft notes (model: DEMOCRAFT_MODEL, default gemma4:12b 8GB)

Prompt pattern: task + exact output shape + "No prose" (JSON lists for
readings/briefs, raw SVG only for pelican, markdown bullets for the word
brief). Extraction: photo/vector find "<svg" and slice from there (Ollama
chat models prepend chatter - the slice is the parser). Fallbacks exist for
every demo (5-shape pelican, 3-bullet brief, grid summary template) and the
page states which fired. Keep prompts short: 1-3 sentences; the engine
output grounds the demo, not the model's eloquence.

Model notes: gemma4:12b default (fits alongside engines, follows shape
instructions). qwen3.8-tools (17GB) when VRAM allows - better structured
output, same prompts. mistral-nemo:12b (7GB) lean fallback. qwen3.6-35b
(23GB) overkill for captions - reserve for script drafting (CURShapes,
.dcs). Temperature: default; top-p default. Timeouts 90s per call; demos
never wait on the model past that (skipped step, CLI runs on). Log model +
ms per run (compare page shows it). Never send private document text to
hosted models - local only, that is the doctrine.

## Troubleshooting transcripts (how refusals should read)

1. "Render the film sequence." -> run_demo film -> EDL + note (no open
project across processes) + AI board. Say: "No footage was rendered - the
EDL is real, assembly is demo #2 behind a project file."
2. "Grade my photo." (no input) -> needs_input + copy instruction. Say:
"Nothing was graded - put the PNG where the recovery says and retry."
3. "Make the pelican photoreal." -> pelican.png (SVG pipeline). Say:
"Shapes are AI-drawn, pixels are engine-rendered; no photoreal engine
exists in this build - verified, not assumed."
4. "Ollama is down, still demo?" -> Yes: AI step skipped, CLI ran, page
labels the caption fallback. Demos degrade, never refuse, over a dead LLM.
5. "Effect render failed." -> Quote stderr + comp id + the capability map
that did run. Say which of the two outcomes fired and why.
6. "Is the portfolio hand-made?" -> No: seed chain recorded step by step
(word convert exe + argv, combine argv), self-combine declared. Trust the
run_dir, not the claim.

## Workshop handout (one page, print it)

Setup (10 min): install 2+ Craft apps from getartcraft.com/apps, install
Ollama + gemma4:12b, double-click start.bat, open :11245. Exercise 1 (10
min): CAD house-plan - run, open floorplan.png, read one info entity aloud.
Expected: DXF + PNG + 5-room reading. Exercise 2 (15 min): pelican compare -
run photo, run vector, open both PNGs, vote which reads more pelican, read
both logs for the honesty gap (AI SVG in, engine pixels out). Expected:
different hashes, same source SVG. Exercise 3 (15 min): film EDL - run,
find Ocean_Sunset timecodes, explain what a dissolve comment means.
Expected: quoted clip + one caveat line. Debrief (10 min): pick one refusal
(field guide) and rehearse saying it to a skeptical user. Take-home: repo
link, runs inbox path, "no tokens were needed for anything you saw."

## Demo changelog discipline (argv changes are breaking)

Demos are an API: anyone may script them. Changing a demo's argv, artifact
names, or output shape is BREAKING - announce in CHANGELOG with before/after
argv and migrate the worked session entry the same commit. Adding a demo is
minor. Removing one requires the engine reason (command removed upstream,
with version) plus the named replacement. The runs inbox keeps one run of
the old shape for reference, labeled retired. Never silently swap what a
demo proves: if the pelican pipeline changes engines, the compare page says
so with dates on both sides.

## First-30-days operator calendar

Week 1: install wrappees + Ollama, run all 13 demo #1s, read every failure
with the field guide open, clear MOCK badges by runs only. Week 2: pick two
demo #2s from the backlog, verify ids, ship worked sessions. Week 3: run the
assessor walkthrough on a colleague, fix what confused them, update Help
FAQ. Week 4: weekly re-run ritual, first drift diff, upstream one engine
issue with full argv + stderr. End of month: CHANGELOG entry, prompt pack
re-read, Standards-page-style honesty audit (every claim on every page
still true?).

## Quick reference card (tape to monitor)

Ops: list_apps, app_status, run_demo(app,demo), craft_commands(app),
ollama_models, ai_flow(prompt), help, shutdown(confirm). Errors:
unknown_app, wrappee_missing, needs_account, needs_input, timeout, spawn -
each with recovery. Ports 11246/11245. Model gemma4:12b default. Timeout
120s CLI (300s sound bounce), 90s LLM. Outbox per run. MOCK clears by run only. EDL is real,
render needs a project. Quote stderr, never invent. Escalation: engine bug (file upstream with argv +
stderr + version), demo bug (fix argv, update worked session, CHANGELOG),
prompt bug (fix pack same commit as code), infra bug (ports/Ollama/CORS -
TROUBLESHOOTING first). Severity: wrong artifact (critical), stale docs
(high), slow demo (medium), ugly page (low). No silent downgrades.

## Release honesty rule

Ship honest pixels today and prettier pixels next week, and say in the
CHANGELOG which release did which. Ugliness never blocks a release;
wrongness always does. Every screenshot in docs carries app + version + date.

## Onboarding sessions

First-run: app_status (count installed/13), ollama_models (or install
prompt), cad house-plan (zero inputs), open outbox/cad/house-plan. Each
wrappee install clears its pages' MOCK badges only after one successful
run - the run is the proof, not the installer exit code. Re-run quarterly:
engines update, demos drift; the runs inbox diff tells you what changed.
