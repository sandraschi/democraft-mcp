# docs/CONFIGURATION.md

| Var | Default | What |
|-----|---------|------|
| `DEMOCRAFT_PORT` | `11246` | Backend port (frontend is 11245; registry: `operations/WEBAPP_PORTS.md`) |
| `DEMOCRAFT_MODEL` | `gemma4:12b` | Ollama model for AI steps (8GB default; `qwen3.8-tools` if you have VRAM) |
| `DEMOCRAFT_OLLAMA_URL` | `http://127.0.0.1:11434` | Ollama endpoint |
| `DEMOCRAFT_OUTBOX` | `<repo>/outbox` | Demo artifacts root |
| `DEMOCRAFT_PREFAB_APPS` | `1` | Set `0` to skip Prefab tool registration (CI/headless) |

Ports are claimed via `mcp-central-docs/fleet-gate/claim_ports.py` - never hand-edit.
