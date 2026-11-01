# democraft-mcp 0.3.0b1 (2026-11-01)

Oct 31 ArtCraft builds, SolidCraft as the first community member, six new demos, and a
redesigned webapp.

## Craft family

- **SolidCraft joins as a community member** (Tangency Labs, parametric 3D CAD, Autodesk Fusion
  alternative). The registry gains `family` (`core` | `community`) and `maker`; the API, sidebar
  and dashboard group apps by family. 14 apps: 13 Storytold core + 1 community.
- **Oct 31 builds verified.** All 13 core CLIs moved (e.g. EffectCraft 0.18 to 0.19, PhotoCraft
  0.17 to 0.18, VectorCraft 0.18 to 0.19). Catalog drift is additive only (104 new verbs, none
  removed). All 25 pre-existing demos and 13 capability maps re-run green on the new builds
  (LightCraft fed a real PNG);
  baselines accepted for all 14 apps.
- **Upstream clones current as of 2026-11-01.** All 15 Craft clones under `_upstream/`
  fast-forwarded; local edits there were stashed (`democraft-refresh-2026-11-01 ...`), not
  discarded.

## New demos (src/democraft_mcp/recipes.py)

- `grid/macro-replay`: typed macro saved, dry-run (`macro.check` footprint), refused on bad
  input with the cell named, fixed, run on two tables.
- `pdf/auto-bookmarks`: WordCraft report, outline deleted, rebuilt by PdfCraft from text styles,
  scored against the original (8/8, exact nesting).
- `vector/cleanup-pass`: Artwork Cleanup check/fix/simplify with anchor counts and a pixel diff
  (traced sample: 1,030 to 493 anchors, 0.34% pixels changed; app icon: -41% anchors).
- `solid/parametric-bracket`: five-parameter L-bracket, three rebuilt variants, STEP/STL, mass.
- `grid/vba-to-macro`: a VBA module translated to typed macros by the local model, one call per
  procedure; each macro is saved, dry-run and run by the engine, refusals go back to the model
  once with the engine's message. Typical result: 3 of 4 valid, the Shell procedure refused.
- `solid/enclosure-fit`: SolidCraft's acceptance enclosure refitted to a board (presets or
  `W x D inset N`), STEP/3MF, iso/section/x-ray renders.
- Tried and not shipped: EffectCraft 3D camera track to Blender. The solve on synthetic CAD
  footage is unreliable (16-21 of 36 frames, 61-102 deg vs 66 deg true); measurements in
  `docs/apps/effect.md`.

## Flows

- `product-sheet`: SolidCraft enclosure, DesignCraft spec sheet, PdfCraft assembly.

## Webapp

- Dashboard opens on a contact sheet of the newest real renders (`GET /api/gallery`), then the
  apps grouped Storytold / Community with live versions and drift, and what is new.
- Craft pages: build/baseline/maker facts, "new" markers, the last run's outputs inline, run
  results as an artifact grid (fixes links that used absolute Windows paths).
- Bench tokens (Geist, JetBrains Mono, warm paper text on zinc), per-app hue and icon, active
  navigation, Ctrl+K jump palette. Removed the Companion topbar button, which opened nothing.
- `scripts/shots.mjs` regenerates README screenshots (run with Node; Playwright hangs under Bun
  on Windows).

## Fixes

- CADCraft gap corrected: AutoLISP is supported (`lisp`, `appload`, `script`; core language,
  `defun c:`, `command`, `entmake`), VLAX/ActiveX is not. SolidCraft is labelled an ArtCraft
  community project in the registry, dashboard and docs.
- HERO gaps corrected where the Oct 31 builds made them false (VectorCraft booleans, GridCraft
  macros, PdfCraft catalog).
- README counts regenerated from the registry (they were stale before this release).
