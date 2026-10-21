# LightCraft demos

[All apps](README.md) | [Repo README](../../README.md)

**What it is**: scene lighting and rendering from the command surface. The app's own comparison
is Blender / Cinema 4D lighting. Driven by
`C:\Program Files\LightCraft\lightcraft-cli.exe` (verified against 0.11.0).

## Demos

| Demo | What actually runs | Artifacts | AI step |
|---|---|---|---|
| `grade-pelican` | Runs a grade pass over the demo PNG; the local model suggests exposure/contrast/saturation tweaks for the chosen intent. | graded PNG, `brief.md` | tweak suggestion JSON |
| `capability-map` | The installed CLI's `commands` output (or `--help`). | `capabilities.txt` | none |

Intent presets: Punchy daylight, Moody evening, Warm print, Cool screen.

## Hands-in / Hands-out

| Direction | What |
|---|---|
| Hands-in | a lighting intent; the model proposes the adjustments |
| Hands-out | the graded render |

The AI suggests, the engine renders. If the model is unavailable the grade still runs with the
demo's own recipe and the AI step is recorded as skipped.

## Run it

```
/craft/light
/craft/light?demo=grade-pelican&watch=1
craft(operation="run_demo", app="light", demo="grade-pelican")
```

Artifacts: `outbox/light/grade-pelican/`.

## Observed gaps

- No material or HDRI authoring in the catalog.
- No bake pipeline.

## Release 0.11.0 notes

LightCraft 0.11.0 introduces background asset reloading, paged catalog reading for large scene collections, and clipping view performance improvements.
