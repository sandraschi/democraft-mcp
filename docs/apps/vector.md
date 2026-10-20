# VectorCraft demos

[All apps](README.md) | [Repo README](../../README.md)

**What it is**: vector paths, gradients, text, SVG/PDF export. The app's own comparison is Adobe
Illustrator. Driven by `C:\Program Files\VectorCraft\vectorcraft-cli.exe`.

## Demos

| Demo | What actually runs | Artifacts | AI step |
|---|---|---|---|
| `pelican-vector` | Simon Willison's awkward prompt (a pelican on a bicycle), rendered through the run/export pipeline. | exported vector artifact, PNG preview | the model draws the SVG |
| `capability-map` | The installed CLI's `commands` output (or `--help`). | `capabilities.txt` | none |

The point of running the same prompt through PhotoCraft and VectorCraft is the pipeline, not
the bird: one renders raster, one keeps vectors, and the model's drawing is equally suspect in
both. Compare the two images side by side rather than reading a score.

## Hands-in / Hands-out

| Direction | What |
|---|---|
| Hands-in | a drawing prompt |
| Hands-out | vector export (SVG/PDF) and a raster preview |

![Pelican benchmark, VectorCraft](../screenshots/pelican-vector.png)

*The pelican benchmark through VectorCraft. Same prompt as the PhotoCraft page; different
renderer.*

## Run it

```
/craft/vector
/craft/vector?demo=pelican-vector&watch=1
craft(operation="run_demo", app="vector", demo="pelican-vector")
```

Artifacts: `outbox/vector/pelican-vector/`.

## Observed gaps

- No boolean path operations in the catalog.
- No plugin ecosystem.
