# CADCraft demos

[All apps](README.md) | [Repo README](../../README.md)

**What it is**: 2D drafting with a scripted command surface - metric plans, elevations, room
schedules, DXF/PDF/SVG export. The app's own comparison is AutoCAD / BricsCAD. Driven by
`C:\Program Files\CADCraft\cadcraft-cli.exe` (verified against 0.10.0).

## Demos

| Demo | What actually runs | Artifacts | AI step |
|---|---|---|---|
| `house-plan` | A scripted metric plan (rooms, labels, dimensions) plus a south elevation. The topic titles the sheet. | `.dxf`, `.png`, `.pdf`, `.svg` | the room list and notes for the chosen topic |
| `capability-map` | The installed CLI's `commands` output (or `--help`), verbatim. | `capabilities.txt` | none |

Topic presets: Machiya townhouse, Alpine hut, Danube houseboat, Courtyard house. Free text is
accepted too.

## Hands-in / Hands-out

| Direction | What |
|---|---|
| Hands-in | a house type or free text; the model returns the room programme |
| Hands-out | DXF for a CAD tool, PDF/SVG for review, PNG for the gallery |

## Run it

```
/craft/cad
/craft/cad?demo=house-plan&watch=1
craft(operation="run_demo", app="cad", demo="house-plan")
```

Artifacts: `outbox/cad/house-plan/`.

## Observed gaps

- No AutoLISP dialect (generic scripting only).
- 2D engine: no true isometric or 3D solids.
- Dynamic-block parametrics are scriptable via Express Tools (`burst`, `mocoro`, `breakline`), but full UI dynamic grip authoring remains desktop-only.

These are limits of the installed CLI, not a roadmap.

## Release 0.10.0 notes

CADCraft 0.10.0 added AutoCAD Express Tools verbs:
- `breakline`: Draws standard architectural zigzag break lines with midpoint/size options.
- `burst`: Explodes block references while preserving attribute text values (unlike standard explode).
- `mocoro`: Move, copy, rotate, and scale in a single command invocation.
- `txt2mtxt`: Converts and combines single-line TEXT into multiline MTEXT blocks.
