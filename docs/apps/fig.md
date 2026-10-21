# FigCraft demos

[All apps](README.md) | [Repo README](../../README.md)

**What it is**: interface design with frames, auto layout, components, variants, styles and
prototyping. The app's own comparison is Figma. Driven by
`C:\Program Files\FigCraft\figcraft-cli.exe` (verified against 0.9.0).

## Demos

| Demo | What actually runs | Artifacts | AI step |
|---|---|---|---|
| `landing-page` | Builds the landing-page template headless, sets 14 text nodes (brand, hero, features, cards, quote, CTA) from your topic, then renders. | project file, PNG render, `brief.md` | landing-page copy brief |
| `capability-map` | The installed CLI's `commands` output (or `--help`). | `capabilities.txt` | none |

Topic presets: Pelican bike shop, Vienna coffee map, Sourdough bakery, Danube cycling guide.

The honest limit: the 14 text nodes change, the stats, person image and buttons stay template.
This is a copy-and-layout demo, not a generative UI designer.

## Hands-in / Hands-out

| Direction | What |
|---|---|
| Hands-in | a topic; the model writes the headline, three sections and a call to action |
| Hands-out | the design file and a PNG render of the page |

## Run it

```
/craft/fig
/craft/fig?demo=landing-page&watch=1
craft(operation="run_demo", app="fig", demo="landing-page")
```

Artifacts: `outbox/fig/landing-page/`.

## Observed gaps

- No multiplayer editing.
- No community/plugin marketplace.
- No cloud file history.

## Release 0.9.0 notes

FigCraft 0.9.0 added:
- Component set and variant discoverability improvements.
- Fixes to SVG export for live text capitalization and subpath reversal.
- Pages scroll area support.
