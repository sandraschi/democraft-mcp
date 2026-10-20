# Screenshots

Two kinds of image live here, and the difference matters:

| Kind | Files | What it shows |
|---|---|---|
| **Webapp** | `dashboard.png`, `hands-in.png`, `depot.png` | our own React control surface on `:11245` - one page per engine, live steps, run history |
| **Engine output** | `plate-grade.jpg`, `lighthouse-live.jpg`, `transition-wipe.jpg`, `effect-still.jpg`, `pelican-photo.png`, `pelican-vector.png` | artifacts rendered by the Craft CLIs, used as evidence on the per-app pages |

Engine output is not a mockup of the webapp, and the webapp shots are not mockups of the Craft
apps. Do not swap them in the README: the Preview section is about the control surface, the app
pages are about what the engines produce.

## Current set

| File | Source | Captured |
|---|---|---|
| `dashboard.png` | `/` - 13 apps, 32 demos, 6 live demos | 2026-10-20 |
| `hands-in.png` | `/hands-in` - the six streamable demos | 2026-10-20 |
| `depot.png` | `/depot` - 29 runs, artifacts per run | 2026-10-20 |
| `plate-grade.jpg` | PhotoCraft `plate-grade` (Boecklin plate) | 2026-10-20 |
| `lighthouse-live.jpg` | PhotoCraft `lighthouse-live` (stroke demo) | 2026-10-20 |
| `transition-wipe.jpg` | DeckCraft `transition-reel` (wipe frame, t = 0.4) | 2026-10-20 |
| `effect-still.jpg` | EffectCraft `title-card` still (re-encoded from the 2026-10-15 PNG) | 2026-10-20 |
| `pelican-photo.png` | PhotoCraft pelican benchmark | 2026-10-15 |
| `pelican-vector.png` | VectorCraft pelican benchmark | 2026-10-15 |

Rules from the fleet screenshots standard: PNG/JPEG, 1280 px wide at most, **300 KB per file**
(`effect-still.jpg` is a re-encode of a 614 KB PNG for that reason), dark theme because the
webapp ships dark, no keys or local paths in frame.

## Regenerate the webapp shots

Start the app first (`start.bat`, or backend on `:11246` and Vite on `:11245`), then:

```powershell
$env:PATH = "C:\Users\sandr\.bun\bin;$env:PATH"
cd web_sota
bunx playwright screenshot --viewport-size="1280,720" --wait-for-timeout=3500 `
  "http://127.0.0.1:11245/" ..\docs\screenshots\dashboard.png
bunx playwright screenshot --viewport-size="1280,720" --wait-for-timeout=3000 `
  "http://127.0.0.1:11245/hands-in" ..\docs\screenshots\hands-in.png
bunx playwright screenshot --viewport-size="1280,900" --wait-for-timeout=3500 `
  "http://127.0.0.1:11245/depot" ..\docs\screenshots\depot.png
```

The wait is deliberate: the dashboard and depot fill from the API after mount. If a shot shows
`0` KPIs, the backend was still starting - rerun it. The KPI numbers in the image are a snapshot
of the machine that captured it; they are allowed to age, they are not a promise.

## Regenerate an engine still

Run the demo, then copy the artifact out of `outbox/<app>/<demo>/`:

```powershell
craft(operation="run_demo", app="photo", demo="plate-grade")
```

The engine log and `run.json` sit next to the artifact and are the receipt for the image.
