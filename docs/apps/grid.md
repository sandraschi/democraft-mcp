# GridCraft demos

[All apps](README.md) | [Repo README](../../README.md)

**What it is**: workbook engine - formulas, charts, pivots, sparklines, import/export. The
app's own comparison is Microsoft Excel. Driven by
`C:\Program Files\GridCraft\gridcraft-cli.exe` (verified against 0.10.0).

## Demos

| Demo | What actually runs | Artifacts | AI step |
|---|---|---|---|
| `homepage-grid` | The local model fills a table for your topic; the engine formats it, adds charts and sparklines, and exports XLSX + PDF. | `.xlsx`, `.pdf` | table JSON (`title`, `headers`, rows) |
| `capability-map` | The installed CLI's `commands` output (or `--help`). | `capabilities.txt` | none |

Topic presets: Sales report 2025, Pelican census, Bike shop inventory, Household energy 2025.
`homepage-grid` is flagged **live** - the fill, format and chart steps are worth watching.

**Declared fallback**: if the model returns unparseable JSON, the demo writes a small real
sales table (six months of revenue and units) instead of failing. That fallback is data the
engine really formats - it is declared in `_grid_data`, not disguised as model output.

## Hands-in / Hands-out

| Direction | What |
|---|---|
| Hands-in | a topic; the model returns column headers and rows |
| Hands-out | `.xlsx` for Excel-compatible tools, `.pdf` for sharing |

## Run it

```
/craft/grid
/craft/grid?demo=homepage-grid&watch=1
craft(operation="run_demo", app="grid", demo="homepage-grid")
```

Artifacts: `outbox/grid/homepage-grid/`.

## Observed gaps

- No VBA/macro compatibility.
- No `.xlsx` round-trip verified (export is the verified direction).

## Release 0.10.0 notes

GridCraft 0.10.0 improves calculation stability across dynamic array formulas and chart generation.

The Studio page embeds GridCraft's **web build**; that is separate from these CLI demos - see
the repo README.
