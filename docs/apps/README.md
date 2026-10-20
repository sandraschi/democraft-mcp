# The thirteen apps

One page per ArtCraft app: what it is, what each demo actually executes, what lands on disk,
and the gaps we observed in the installed CLI. The registry that generates these pages and the
webapp is `src/democraft_mcp/crafts.py` - if a page and the registry disagree, the registry is
right and the page is a bug.

| App | Demos | Streamable | Page |
|---|---|---|---|
| CADCraft | 2 | - | [cad.md](cad.md) |
| DeckCraft | 3 | transition reel | [deck.md](deck.md) |
| DesignCraft | 2 | - | [design.md](design.md) |
| EffectCraft | 2 | - | [effect.md](effect.md) |
| FigCraft | 2 | - | [fig.md](fig.md) |
| FilmCraft | 3 | timeline cut | [film.md](film.md) |
| GridCraft | 2 | topic report | [grid.md](grid.md) |
| SoundCraft | 3 | melody dry vs VST3 | [sound.md](sound.md) |
| WordCraft | 2 | - | [word.md](word.md) |
| PdfCraft | 2 | - | [pdf.md](pdf.md) |
| LightCraft | 2 | - | [light.md](light.md) |
| PhotoCraft | 5 | plate grade, lighthouse | [photo.md](photo.md) |
| VectorCraft | 2 | - | [vector.md](vector.md) |

## The demo contract

Every demo here makes the same four promises:

1. **It runs the real engine.** A subprocess call to the installed `<app>-cli.exe`, captured
   with argv, return code, duration and stderr. There is no mock path and no dry-run that
   pretends to render.
2. **It leaves evidence.** Artifacts plus `run.json` (app, demo, topic, start/finish, artifact
   list) in `outbox/<app>/<demo>/`. A previous run is moved to `outbox/_history/`, never
   overwritten.
3. **The AI half is optional and labelled.** The model writes text (topics, briefs, notes) or,
   in the pelican benchmarks, SVG. Pixels are always the engine's. If Ollama is down the step is
   recorded as `skipped` with the error.
4. **Failure is visible.** A non-zero CLI step is reported with its return code and stderr; the
   demo returns `success: false` rather than a green badge over a broken artifact.
5. **Hands-in puts the app on screen.** A `live` demo starts the Craft app if needed, restores
   and maximises its main window, and hands it the foreground before the first CLI step. The
   work still runs through the headless CLI; `run.json` records `focus` (including
   `foreground: false` when Windows refuses the handoff), so "the app was in front" is checkable
   rather than assumed.

The `capability-map` demo on every app is the escape hatch: it dumps the installed build's own
`commands` (or `--help`) to `capabilities.txt`, so you can see what your version supports
without trusting this documentation.

## Running a demo

- Webapp: pick the app in the sidebar, or open `/craft/<app>`.
- Stream it: tick **Watch it build**, or add `?watch=1` (`/craft/film?demo=timeline-cut&watch=1`).
- MCP: `craft(operation="run_demo", app="film", demo="timeline-cut")`.
- Topics: the webapp sends a topic for demos that have a picker; the MCP `run_demo` operation
  uses the demo's default prompt (pass `model` to switch models).

Artifacts stay on your machine under `outbox/`. The Craft documents you open yourself are never
modified by a demo.
