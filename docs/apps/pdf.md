# PdfCraft demos

[All apps](README.md) | [Repo README](../../README.md)

**What it is**: PDF operations from the CLI - the working set the other crafts hand their
exports to. The app's own comparison is Adobe Acrobat Pro. Driven by
`C:\Program Files\PdfCraft\pdfcraft-cli.exe`.

## Demos

| Demo | What actually runs | Artifacts | AI step |
|---|---|---|---|
| `portfolio` | Combines the bundled demo PDFs into one portfolio and renders a thumbnail; the local model names four sections for your subject. | combined PDF, thumbnail PNG, `brief.md` | four section names |
| `capability-map` | This CLI has no `commands` verb, so the demo falls back to `--help` and records that. | `capabilities.txt` | none |

The fallback matters: `capabilities.txt` is honest about being `--help` output, not a command
catalog the app does not publish.

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

- No command catalog (the CLI has no `commands` verb).
- Verbs beyond the shipped set are not discoverable from the app.
