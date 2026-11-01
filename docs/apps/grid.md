# GridCraft demos

[All apps](README.md) | [Repo README](../../README.md)

**What it is**: workbook engine - formulas, charts, pivots, sparklines, import/export. The
app's own comparison is Microsoft Excel. Driven by
`C:\Program Files\GridCraft\gridcraft-cli.exe` (verified against 0.14.2, 2026-11-01).

## Demos

| Demo | What actually runs | Artifacts | AI step |
|---|---|---|---|
| `homepage-grid` | The local model fills a table for your topic; the engine formats it, adds charts and sparklines, and exports XLSX + PDF. | `.xlsx`, `.pdf` | table JSON (`title`, `headers`, rows) |
| `macro-replay` | One typed macro (amber header, SUM total row, bold rows above 300) saved into the workbook; `macro.check` dry-runs it on two tables (footprint only, nothing written), refuses the second because a number column holds text and names the cell (G3), then the cell is fixed and the macro runs on both. | `macro-replay.xlsx`, `.pdf`, `result.csv`, `macro.json`, `macro-report.md` | none |
| `vba-to-macro` | A four-procedure VBA module (`module.bas`) goes to the local model one procedure at a time. Each answer is a typed macro or a stated refusal. Every macro is saved, dry-run with `macro.check` on a real table, and only then run. An engine refusal goes back to the model once with the engine's own message (a bad answer that is not JSON gets up to three tries). The report gives a verdict per procedure and, for `AddTotals`, checks the total row against what the VBA computes. VBA is never executed. | `module.bas`, `<Procedure>.macro.json`, `<Procedure>.xlsx`, `.csv`, `verdicts.json`, `vba-report.md` | one translation call per procedure (gemma4:e4b: 3 of 4 procedures ended valid in the runs we made; the shell call is correctly refused) |
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

- No VBA execution: an `.xlsm` keeps its VBA project on save and never runs it (a Storytold
  decision, not Microsoft's). Typed macros (`macro.*`, 0.14) are the automation path instead,
  and `vba-to-macro` shows how far a local model gets translating VBA into them.
- No Office Scripts compatibility.

## Release 0.14.2 notes (Oct 31 build)

New `macro.*` verbs: record, save, check (dry run with footprint), run (one undo step, rolls
back on error), debug, list, get, rename, delete. The engine's input validation names the
offending cell, which is what `macro-replay` shows.

## Release 0.10.0 notes

GridCraft 0.10.0 improves calculation stability across dynamic array formulas and chart generation.

The Studio page embeds GridCraft's **web build**; that is separate from these CLI demos - see
the repo README.
