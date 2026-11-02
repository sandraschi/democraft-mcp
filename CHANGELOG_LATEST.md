# democraft-mcp 0.3.0 (2026-11-02)

Official v0.3.0 release integrating Craft Anything (15th Craft App), SolidCraft, TextureCraft, and clean-room reconstruction workflows.

## Craft Family Updates
- **Craft Anything joins the family** (`storytold/craft-anything`, alternative to REA `morluto/rea`).
  - Headless reconstruction pipeline (Study -> Build -> Check -> Ready).
  - Clean-room mode enforcement (visual tokens, DOM hierarchy, and typography without inspecting proprietary source code).
  - Total app count: 15 Craft apps (13 Storytold ArtCraft core + 2 community: SolidCraft, Craft Anything).
- **SolidCraft** (Tangency Labs, parametric 3D CAD): `parametric-bracket` (three timeline-rebuilt variants, STEP/STL/mass) and `enclosure-fit` (sensor box parametric fitting to custom boards).
- **TextureCraft** (Storytold PBR Texturing): `godot-prop` (ORM texture export + headless Godot import) and `material-pick` (model-picked mesh and material validation).

## New Recipes (`src/democraft_mcp/recipes.py`)
- `anything/study-and-spec`: Generates clean-room design tokens, component blueprints, routes, and `SPEC.md`.
- `anything/oracle-check`: Loopback CDP verification comparing target against clone across 3 responsive viewports (Desktop, Tablet, Mobile) with perceptual pixel diffs and route parity scoring.

## Verification
- Full test suite passing with 100% recipe compliance across all 15 craft applications.
