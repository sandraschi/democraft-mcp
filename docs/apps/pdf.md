# PdfCraft demos

[All apps](README.md) | [Repo README](../../README.md)

**What it is**: PDF operations from the CLI - the working set the other crafts hand their
exports to. The app's own comparison is Adobe Acrobat Pro. Driven by
`C:\Program Files\PdfCraft\pdfcraft-cli.exe` (verified against 0.10.1).

## Demos

| Demo | What actually runs | Artifacts | AI step |
|---|---|---|---|
| `portfolio` | Combines the bundled demo PDFs into one portfolio and renders a thumbnail; the local model names four sections for your subject. | combined PDF, thumbnail PNG, `brief.md` | four section names |
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

## Observed gaps

- Shipped CLI exposes operations primarily through MCP `tools --json` rather than a standard `commands` subverb.

## Release 0.10.1 notes

PdfCraft 0.10.1 added:
- `page.reverse`: Reverses the order of pages across specified ranges or the entire document.
- Shipped local inference weights in `models/` for offline OCR and layout extraction.
- Fills and border widths on callouts and annotation text boxes.
