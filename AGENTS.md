# democraft-mcp - AGENTS.md

Thin override; fleet rules in `D:\Dev\repos\mcp-central-docs\standards\AGENTS.md`.

- Python: `C:\Users\sandr\.local\bin\uv.exe run python` (never naked).
- Backend :11246 (`democraft_mcp.server:app`), frontend :11245. Never hardcode elsewhere.
- Demos run real Craft CLIs into `outbox/`; tests use tmp outbox. No CLI mocks.
- `just ci` before every commit. Max 5 files per commit.
- Upstream Craft repos (`_upstream/`) are read-only - never edit.
- Stateless server: no DB, no daemon/proxy split. stdio runs tools directly.

## Multi-agent working rules (several agents and IDEs)

Several agents (Claude Code, OpenCode, Cursor, Windsurf and others) work on this repo from
different IDEs, sometimes at the same time. These rules exist because that went wrong once:
one agent ran a commit-all and swept another agent's half-finished manifest edits into a
release and a pushed tag, leaving the pushed tree unbuildable.

Fleet standard with the full reasoning: `mcp-central-docs/standards/MULTI_AGENT_CONCURRENCY.md`.

### Before you start

1. Run `git status` and `git log -5 --format="%h %ad %s" --date=iso`. If the tree is dirty and
   you did not make those changes, someone else is working here. Leave their files alone:
   do not reset, clean, stash or revert them.
2. Prefer your own branch (`agent/<tool>-<topic>`) or a worktree
   (`git worktree add ..\<repo>-<topic> -b agent/<tool>-<topic>`). Merge to the default branch
   only when the work is finished and checked.

### Committing

- Never `git add -A`, `git add .`, `git commit -a` or `git commit -am`. Name your paths:
  `git add <path> ...` then `git commit -m "..." -- <path> ...`.
- Before committing run `git diff --cached --stat` and check every file is yours.
- A manifest (`Cargo.toml`, `package.json`, `pyproject.toml`) and the files it points at go in the
  same commit. Never commit a manifest that names something not in the commit.
- Do not tag or release from a dirty tree, or from a `WIP-Auto` commit made by the nightly sweep.
  Before tagging, a clean clone of the exact commit must build and pass tests.
- Do not move or delete a published tag; add a new one. Do not force-push a shared branch.
- Do not push another agent's commits you did not read.

### Hooks

`.githooks/pre-commit` rejects a commit whose Cargo manifests name workspace members or path
dependencies that are not tracked. Enable it once per clone:

    git config core.hooksPath .githooks

Do not bypass it with `--no-verify`. If it blocks you, the commit really is broken.

### Leave a trail

- Commit messages say what and why. Agent commits end with the tool's own trailer.
- Long-running work: note it in the repo's worklog or plan file so the next agent sees it.
- At the end of a session, say what you left uncommitted and whose it appears to be.
