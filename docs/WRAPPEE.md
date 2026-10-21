# What ArtCraft is

**ArtCraft** is a family of thirteen local creative applications for Windows. Each one is a
desktop alternative to an established industry tool (AutoCAD, InDesign, Premiere Pro, and so
on) and ships a headless command-line binary next to the GUI. The apps run on your machine;
there is no cloud requirement to open a file or render a demo.

Official site and installers: <https://getartcraft.com>

democraft-mcp is **not** an ArtCraft product. It is the demo bench and MCP control surface for
installed ArtCraft apps: it drives the CLIs, records what happened, and keeps the artifacts.
The apps themselves are licensed separately by ArtCraft.

## Disambiguation

"Craft" is a crowded word. This repo is about the **ArtCraft** desktop creative suite. It is
not related to Craft CMS (Pixel & Tonic), Craft Docs, Craft.co, or the various "craft" plugin
ecosystems for other editors.

There is also no single "ArtCraft CLI": each app ships its own binary, listed below.

## The thirteen apps

| App | Does | Local alternative to | CLI (under `C:\Program Files\<App>\`) |
|---|---|---|---|
| CADCraft | 2D drafting: plans, elevations, room schedules, DXF/PDF/SVG | AutoCAD / BricsCAD | `cadcraft-cli.exe` |
| DeckCraft | Slide decks, transitions, PNG/GIF export | PowerPoint / Keynote | `deckcraft-cli.exe` |
| DesignCraft | Page layout: threaded stories, facing pages, PDF/EPUB | Adobe InDesign | `designcraft-cli.exe` |
| EffectCraft | Motion graphics: keyframes, cameras, audio, renders | Adobe After Effects | `effectcraft-cli.exe` |
| FigCraft | Interface design: frames, auto layout, components | Figma | `figcraft-cli.exe` |
| FilmCraft | Timeline editing: sequences, transitions, colour, export | Adobe Premiere Pro | `filmcraft-cli.exe` |
| GridCraft | Workbooks: formulas, charts, pivots, XLSX/PDF | Microsoft Excel | `gridcraft-cli.exe` |
| SoundCraft | Session audio: MIDI, mixing, effects, bounce | Ableton Live / Pro Tools | `soundcraft-cli.exe` |
| WordCraft | Documents: styles, tables, DOCX/PDF | Microsoft Word | `wordcraft-cli.exe` |
| PdfCraft | PDF combine, render, anatomy | Adobe Acrobat Pro | `pdfcraft-cli.exe` |
| LightCraft | Scene lighting and rendering | studio lighting tools | `lightcraft-cli.exe` |
| PhotoCraft | Raster editing: layers, masks, adjustment stacks, batch | Adobe Photoshop | `photocraft-cli.exe` |
| VectorCraft | Vector paths, gradients, text, SVG/PDF | Adobe Illustrator | `vectorcraft-cli.exe` |

The "alternative to" column is the app's own comparison, repeated here so a reader can place
each tool. It is not a feature-parity claim; [each app page](apps/README.md) lists the gaps we
actually observed.

## How democraft uses them

- **Headless first.** Demos call `<app>-cli.exe` with `--project` / `run` / `render` style
  commands. The GUI does not need to be open.
- **Never bundled.** Install the app yourself. Missing apps return `wrappee_missing`.
- **CLI version matters.** FilmCraft 0.10.0 is what the timeline demo was verified against;
  `craft_commands(app=...)` prints the catalog your installed build actually exposes.
- **Licence and cost are ArtCraft's.** Democraft adds no account, no token and no subscription.
  ArtCraft's own AI generation (where an app offers it) is account-gated. No demo here depends
  on it; the error taxonomy reserves `needs_account` for the day an engine gates a feature.

## Links

- Official site: <https://getartcraft.com>
- Per-app demos and observed gaps: [apps/README.md](apps/README.md)
- Install and first run: [ONBOARDING.md](ONBOARDING.md)
