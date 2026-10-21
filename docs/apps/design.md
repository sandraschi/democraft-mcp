# DesignCraft demos

[All apps](README.md) | [Repo README](../../README.md)

**What it is**: page layout with threaded stories, facing pages, styles, tables and footnotes,
exporting PDF and EPUB. The app's own comparison is Adobe InDesign. Driven by
`C:\Program Files\DesignCraft\designcraft-cli.exe` (verified against 0.11.0).

## Demos

| Demo | What actually runs | Artifacts | AI step |
|---|---|---|---|
| `print-spread` | Renders the sample magazine spread to PNGs; the local model describes the spread for the chosen subject. | spread PNGs, `brief.md` | a two-page spread description (left/right/palette) |
| `capability-map` | The installed CLI's `commands` output (or `--help`). | `capabilities.txt` | none |

Topic presets: Pelican + house spread, Bakery menu spread, Bike catalog spread, Photo essay
spread.

## Hands-in / Hands-out

| Direction | What |
|---|---|
| Hands-in | a subject; the model proposes the spread content |
| Hands-out | rendered spread pages (PNG), and the engine's own PDF/EPUB exports |

Note the division of labour: the AI writes the *brief*, the layout and typography are the
engine's. A demo that only produced the brief would not be a demo of DesignCraft.

## Run it

```
/craft/design
/craft/design?demo=print-spread&watch=1
craft(operation="run_demo", app="design", demo="print-spread")
```

Artifacts: `outbox/design/<demo>/`.

## Observed gaps

- No master-page command surface (parent pages are script-level).
- No cloud collaboration or review.
- Book sync is script-level, not a UI workflow.

## Release 0.11.0 notes

DesignCraft 0.11.0 refactored placed-PDF rendering (`PDFR`), sharing PDF rendering primitives across engines to improve fidelity when importing complex vector PDFs into multipage layouts.
