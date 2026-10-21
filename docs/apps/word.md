# WordCraft demos

[All apps](README.md) | [Repo README](../../README.md)

**What it is**: document editing with styles, tables and PDF export. The app's own comparison is
Microsoft Word. Driven by `C:\Program Files\WordCraft\wordcraft-cli.exe` (verified against 0.9.0).

## Demos

| Demo | What actually runs | Artifacts | AI step |
|---|---|---|---|
| `demo-report` | The local model drafts a one-page report for your topic; WordCraft's Report template styles it and exports. | `.docx`, `.pdf` | title plus four to six short paragraphs |
| `capability-map` | The installed CLI's `commands` output (or `--help`). | `capabilities.txt` | none |

Topic presets: "Why headless demos beat screenshots", "A field guide to DXF", "The quiet craft
of release notes", "What EDLs remember". Free text works too.

## Hands-in / Hands-out

| Direction | What |
|---|---|
| Hands-in | a topic; the model writes the prose |
| Hands-out | `.docx` and `.pdf` |

The AI writes words only. Styling, pagination and the PDF conversion are the engine's, which is
the part a WordCraft demo has to prove.

## Run it

```
/craft/word
/craft/word?demo=demo-report&watch=1
craft(operation="run_demo", app="word", demo="demo-report")
```

Artifacts: `outbox/word/demo-report/`.

## Observed gaps

- No general DOCX import/export verbs in the command catalog - the demo exports through the
  Report template, which is the verified direction.
- No image-placement verbs.

## Release 0.9.0 notes

WordCraft 0.9.0 added key layout and clipboard verbs:
- `list.multilevelPreset`: Links styles to multilevel numbering presets (`headings` 1 / 1.1 / 1.1.1, `article`, `outlineHeadings`, or `chapter`), resolving the previous gap in structured outline numbering.
- `edit.spike` & `edit.insertSpike`: Word's cumulative "Spike" buffer that gathers multiple distinct text selections and pastes them as a compiled block.
- `view.interfaceTheme`: Theme selection verb.
