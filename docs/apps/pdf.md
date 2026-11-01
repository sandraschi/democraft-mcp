# PdfCraft demos

[All apps](README.md) | [Repo README](../../README.md)

**What it is**: PDF operations from the CLI - the working set the other crafts hand their
exports to. The app's own comparison is Adobe Acrobat Pro. Driven by
`C:\Program Files\PdfCraft\pdfcraft-cli.exe` (verified against 0.16.1, 2026-11-01).

## Demos

| Demo | What actually runs | Artifacts | AI step |
|---|---|---|---|
| `portfolio` | Combines the bundled demo PDFs into one portfolio and renders a thumbnail; the local model names four sections for your subject. | combined PDF, thumbnail PNG, `brief.md` | four section names |
| `auto-bookmarks` | WordCraft converts a sectioned report to PDF, with an outline built from its headings. That outline is kept as the answer key and deleted (`stripped.pdf`). PdfCraft's `text_styles` lists the styles; every style larger than the most-used one becomes a bookmark level; `bookmark_from_text_styles` rebuilds the tree (`rebuilt.pdf`). The report scores titles and nesting against the original. Pick a subject and the local model writes the report; the built-in report needs no AI. | `report.pdf`, `stripped.pdf`, `rebuilt.pdf`, `page1.png`, `bookmarks-report.md/.json`, the three PdfCraft scripts | optional: the report text |
| `capability-map` | Discoverable via `tools --json` (or falling back to `--help`). | `capabilities.txt` | none |

The discovery ladder walks `tools --json` to inspect the installed tool schemas, falling back to `--help` if needed.

## Hands-in / Hands-out

| Direction | What |
|---|---|
| Hands-in | the bundled demo PDFs; a subject for the section names |
| Hands-out | a combined PDF and a thumbnail render |

This is the natural sink for the other apps' exports: DesignCraft, WordCraft and GridCraft all
produce PDFs that a portfolio step can combine.

## Run it

```
/craft/pdf
/craft/pdf?demo=portfolio&watch=1
craft(operation="run_demo", app="pdf", demo="portfolio")
```

Artifacts: `outbox/pdf/portfolio/`.

Measured on 0.16.1 with the built-in report: 8 of 8 headings recovered, titles and nesting
identical to WordCraft's outline (levels Carlito 20, 16 and 14 pt over 12 pt body).

## Observed gaps

- Shipped CLI exposes operations through `tools` (JSON Schemas) rather than a `commands` verb.
- `bookmark_from_text_styles` nests its result under a new first bookmark titled "Untitled";
  the demo renames it to "Contents".

## Release 0.16.1 notes (Oct 31 build)

New tools: `text_styles` (the document's font/size/weight styles, largest first, with line and
page counts and a sample) and `bookmark_from_text_styles` (bookmarks for PDFs whose headings
are not tagged).

## Release 0.10.1 notes

PdfCraft 0.10.1 added:
- `page.reverse`: Reverses the order of pages across specified ranges or the entire document.
- Shipped local inference weights in `models/` for offline OCR and layout extraction.
- Fills and border widths on callouts and annotation text boxes.
