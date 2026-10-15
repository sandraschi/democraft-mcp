---
name: democraft
description: Run real headless demos for the 13 ArtCraft apps via the craft tool.
---

# democraft (OpenCode skill)

Before starting work: `craft(operation="app_status")` for wrappee state.
Run demos with `craft(operation="run_demo", app="<key>")`; artifacts land in
outbox/<app>/<demo>/. Report engine stderr verbatim, never invent artifacts.
At end of work: gates green, commit small, tree clean.
