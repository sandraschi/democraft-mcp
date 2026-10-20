# Installing democraft-mcp

> New here? Read [docs/ONBOARDING.md](docs/ONBOARDING.md) first (the Craft apps and the AI
> model). This file is the mechanical install, all paths.

democraft-mcp is an **MCP hand**: it drives the ArtCraft apps that you install yourself. It is
not the apps, and it never bundles them.

## Prerequisites

Install these if you do not have them already. Windows uses winget; close and reopen the
terminal afterwards so PATH refreshes.

| Tool | Needed for | Windows |
|---|---|---|
| ArtCraft apps | every demo (see [docs/ONBOARDING.md](docs/ONBOARDING.md)) | <https://getartcraft.com> |
| Claude Desktop | Options A, B, C | <https://claude.ai/download> |
| Node.js | Option B (mcpb CLI) | `winget install OpenJS.NodeJS.LTS` |
| uv | Option C (manual), Option D | `winget install astral-sh.uv` |
| Git | Option C (manual), Option D | `winget install Git.Git` |
| Ollama | AI steps (optional but recommended) | `winget install Ollama.Ollama` |
| Bun | Option D (webapp build) | `winget install Oven-sh.Bun` |

You do **not** need Python, uv or Node for Option A: the `.mcpb` is self-contained.

## Option A - Drag and drop (.mcpb, recommended)

1. Install the Craft apps you want to demo from <https://getartcraft.com>.
2. Download `democraft-mcp.mcpb` from the
   [latest release](https://github.com/sandraschi/democraft-mcp/releases/latest).
3. Drag it onto Claude Desktop, or use **Settings > Extensions > Install from file**.
4. Quit Claude Desktop completely (tray > Quit) and relaunch.

The bundle registers the MCP server only. It does **not** install the webapp and it does not
install the Craft apps. Without the apps, `run_demo` returns `wrappee_missing` and the demo
pages say so instead of pretending.

## Option A2 - Webapp and dashboard (from source)

The webapp is the best way to watch demos run. It is a source-run today; there is no NSIS
installer for this repo yet.

1. Install **uv**, **Node.js** and **Bun** (table above).
2. Clone the repo and run `start.bat`.
3. Open <http://127.0.0.1:11245>. The backend listens on <http://127.0.0.1:11246>.

`start.bat` starts uvicorn (backend) and Vite (frontend), clearing the ports first. Logs are in
the two console windows it opens.

## Option B - mcpb CLI

```powershell
# Requires Node.js
npx @anthropic-ai/mcpb install https://github.com/sandraschi/democraft-mcp
```

`npx`, not `uvx`: mcpb is an npm package, and `uvx mcpb` fails.

## Option C - Manual configuration

1. Clone and install dependencies:

```powershell
git clone https://github.com/sandraschi/democraft-mcp
cd democraft-mcp
uv sync
```

2. Add the server to `%APPDATA%\Claude\claude_desktop_config.json`
   (macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "democraft": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\\path\\to\\democraft-mcp",
        "run",
        "python",
        "-m",
        "democraft_mcp.mcp_stdio"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

3. Restart Claude Desktop. `democraft` should appear under Settings > MCP Servers.

Other clients (Cursor, VS Code, Claude Code) take the same `command` / `args` in their own
config file.

## Option D - Developer mode

`just` recipes, the test and lint gates, the web build and MCPB packaging live in
[docs/DEVELOPMENT.md](docs/DEVELOPMENT.md). The fleet-wide gate is `just ci`.

## AI steps (Ollama)

Demos work in two halves: the CLI half always runs, the AI half needs a local model.

```powershell
winget install Ollama.Ollama
ollama pull gemma4:e4b          # ~8 GB, the default
ollama list                     # confirm the tag matches DEMOCRAFT_MODEL
```

If your only pulled model is a different tag, point the app at it:

```powershell
$env:DEMOCRAFT_MODEL = "gemma4:12b-fixed"
```

`ai_step` posts to Ollama's `/api/generate`; a non-Ollama OpenAI-compatible endpoint is not
wired in yet. When Ollama is down, the demo still runs the CLI half and marks the AI step
`skipped` with the error - it never fabricates model output.

## Verify installation

```powershell
Invoke-WebRequest http://127.0.0.1:11246/api/health -UseBasicParsing
```

Expected: `{"status":"ok","version":"...","apps":13,"installed":<n>}` where `<n>` is how many
Craft CLIs were found under `C:\Program Files\<App>\`.

Then ask Claude:

> List the Craft apps installed here and run the FilmCraft timeline cut.

Expected: `cli_steps` with real return codes and a `cut.mp4`, `poster.png` and
`transition.png` under `outbox/film/timeline-cut/`.

## Uninstall

Remove the extension from Claude Desktop (Settings > Extensions), or delete `democraft` from
`claude_desktop_config.json`. Demo artifacts stay in `outbox/` until you delete them; the Craft
apps and your Craft documents are untouched.

## Troubleshooting

See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for `wrappee_missing`, a silent AI step,
port conflicts and engine stderr.
