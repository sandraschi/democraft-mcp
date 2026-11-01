# SolidCraft demos

[All apps](README.md) | [Repo README](../../README.md)

**What it is**: parametric 3D CAD - constrained sketches, a feature timeline, user parameters,
assemblies, sheet metal, STEP/IGES/3MF/STL in and out, GPU renders. Its own comparison is
Autodesk Fusion. Driven by `C:\Program Files\SolidCraft\solidcraft-cli.exe` (verified against
0.28.0 and 0.29.0, 2026-11-01).

**Family**: SolidCraft is the first **community** member of the Craft family. It is built by
Tangency Labs (<https://github.com/tangency-labs/solidcraft>, MIT OR Apache-2.0), not by
Storytold, and follows the same conventions: a headless CLI next to the GUI, a JSON command
catalog, an MCP server. democraft models this as `family = "community"` in the registry, so the
next community apps slot in without special cases.

**It updates itself.** Between two calls on 2026-11-01 the installed CLI went from 0.28.0 to
0.29.0 on its own. Every run stamps the build it actually used in `run.json`, and the drift
tripwire flags the change on `/apps` and in the sidebar.

## Demos

| Demo | What actually runs | Artifacts | AI step |
|---|---|---|---|
| `parametric-bracket` | One script defines an L-bracket from five user parameters (width, flange, rise, thickness, hole_d); every sketch coordinate is an expression. Three variants change only the parameters on the saved design and SolidCraft rebuilds the timeline. `eval` measures each. | per variant `.sc`, `.step`, `.stl`, iso `.png`, `eval.json`; `variants.csv`, `variants.png`, `bracket-report.md` | none |
| `enclosure-fit` | SolidCraft's own acceptance project (sensor enclosure: case + lid, standoffs, lid bosses, USB cut-out, snap fit), run as written, then refitted to a board by changing its parameters. | `enclosure.sc`, `.step`, `.3mf`, iso, section and x-ray `.png`, `eval.json`, `enclosure-report.md` | none |
| `capability-map` | The installed CLI's catalog. | `capabilities.txt` | none |

Measured on 0.29.0:

| Bracket variant | Parameters | Mass (Default material) | Bounding box |
|---|---|---|---|
| compact | 60 x 40 x 30, t 6, hole 8 | 28.94 g | 40 x 60 x 30 mm |
| long | 120 x 55 x 30, t 4, hole 6.5 | 49.81 g | 55 x 120 x 30 mm |
| heavy | 90 x 50 x 45, t 10, hole 10 | 96.66 g | 50 x 90 x 45 mm |

Enclosure, script default board (60 x 40 mm): Case 32.77 g, Lid 25.32 g, zero rebuild errors.

**Board presets are limited on purpose.** The script models one `hole_inset` for all four
holes, so only boards with a symmetric hole pattern fit truthfully: Raspberry Pi Zero 2 W
(65 x 30, holes 3.5 mm in) and Adafruit Feather (50.8 x 22.86, holes 2.54 mm in). A Raspberry
Pi 4 would get the right outline but the wrong standoffs, so it is not offered. Type
`W x D inset N` (mm) for your own board.

## Hands-in / Hands-out

| Direction | What |
|---|---|
| Hands-in | a board preset or `W x D inset N` (enclosure); nothing for the bracket |
| Hands-out | STEP for any CAD tool, STL and 3MF for slicers, `.sc` to open in SolidCraft, renders |

## Run it

```
/craft/solid
/craft/solid?demo=parametric-bracket&watch=1
craft(operation="run_demo", app="solid", demo="enclosure-fit")
```

Artifacts: `outbox/solid/<demo>/`. The enclosure script is vendored with attribution in
`assets/solid/` (see `CREDITS.md` there).

## Observed gaps

- ArtCraft community project by Tangency Labs, not a Storytold build: release cadence and conventions may diverge.
- Self-updates in place: the engine version can move between two runs.
- `snapshot` renders orthographic by default; pass a `fov` in `--camera` for perspective.
- No CAM or simulation workspaces.
