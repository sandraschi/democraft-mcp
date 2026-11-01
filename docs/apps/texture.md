# TextureCraft

PBR texturing with layered smart materials and engine-ready exports. Storytold ArtCraft
(core). Alternative to Substance 3D Painter.

## Demos

### godot-prop: textured prop for Godot

Pick a prop (crate, ball, brick block, pillar, slab). democraft opens the matching
built-in mesh, applies a smart material, exports the Godot 4 (ORM) maps at 1024 px and a
glTF mesh, renders a preview, then imports the result in a local headless Godot and
reports the surfaces and texture slots Godot filled. No AI step.

Output: `godot-report.md`, `prop.tcraft`, `prop.png`, and a `godot/` folder that opens as
a Godot project (`prop.glb`, `textures/`).

Needs Godot 4.x at `C:\Users\sandr\.local\bin\godot.exe` or `DEMOCRAFT_GODOT`. Without
it the demo still exports and the report says the import check was skipped.

### material-pick: the model picks mesh and material

Describe a prop. The local model chooses a built-in mesh and a smart material from fixed
lists (only combinations that exported cleanly in testing). An answer outside the lists is
rejected, the report says so, and a fallback is used. Then the same export and Godot
import runs.

## Measured limits (2026-11-01)

- Only the brick, tile and weave procedural kinds repeat seamlessly; every noise-based
  kind has wrap seams. Plan ground tiles accordingly: use one large texture, not a tile.
- Of the built-in materials tried, only Brick Red tiled cleanly at 512 px.
