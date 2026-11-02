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
- Do not tag or release from a dirty tree. Before tagging, a clean clone of the exact commit must
  build and pass tests.
- Do not move or delete a published tag; add a new one. Do not force-push a shared branch.
- Do not push another agent's commits you did not read.
- The nightly job only writes snapshots to `refs/wip/*`; it never commits to a branch. Your
  uncommitted work is backed up, but that is not a substitute for committing it.

### Line endings: LF only

CRLF/LF mismatches make hooks fail and burn tokens in fix-retry loops. Rules:

- Source, config, docs and scripts are LF, UTF-8 without BOM. `.bat` and `.cmd` may be CRLF.
  Shell scripts, `.githooks/*`, Dockerfiles and anything with a `#!` line must be LF always.
- Editing an existing file: keep the line endings it already has. Use a targeted replace; never
  read the whole file and rewrite it with different endings.
- PowerShell 5.1: do not write source files with `Set-Content`, `Out-File` or `>` (they add CRLF,
  a BOM or UTF-16). Use `[System.IO.File]::WriteAllText($path, $text, (New-Object System.Text.UTF8Encoding $false))`
  and join lines with `"`n"`. Prefer the Edit/Write tools, which do not touch endings.
- The `fileops` `write_file` tool on Goliath writes CRLF, and git here has `core.autocrlf=true`. After writing
  any file with it, run `D:\Dev\repos\mcp-central-docs\scripts\Set-LfEndings.ps1 -Path <files>` (or `-Changed`)
  before committing. Hook scripts and `#!` files with CRLF fail outright.
- `warning: LF will be replaced by CRLF` is noise, not an error. Do not convert files to silence it.
- If a hook (end-of-file-fixer, mixed-line-ending, formatters) rewrites files and fails, run
  `git add <your paths>` and commit once more. If it fails a second time, stop and report the hook
  output. Do not loop.
- If the repo has no `.gitattributes` with `* text=auto eol=lf`, tell the user. Do not run
  `git add --renormalize` on your own: it touches every file.
- Machine setting (owner): `git config --global core.autocrlf input` (commit LF, never convert on checkout)
  and `git config --global core.safecrlf false`.

### Hooks

`.githooks/pre-commit` rejects a commit whose Cargo manifests name workspace members or path
dependencies that are not tracked. Enable it once per clone:

    git config core.hooksPath .githooks

Do not bypass it with `--no-verify`. If it blocks you, the commit really is broken.

### Leave a trail

- Commit messages say what and why. Agent commits end with the tool's own trailer.
- Long-running work: note it in the repo's worklog or plan file so the next agent sees it.
- At the end of a session, say what you left uncommitted and whose it appears to be.
