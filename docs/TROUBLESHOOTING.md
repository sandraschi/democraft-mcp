# docs/TROUBLESHOOTING.md

## `wrappee_missing`

`<Name> not installed at C:\Program Files\<Name>\<cli>.exe`. Install the app
(see ONBOARDING §3); its page shows MOCK until then.

## `needs_account`

The engine feature needs ArtCraft generation tokens. Buy/enable per the
Craft app, then retry. Demo #1s never need this.

## Ollama down (`ai_step.skipped`)

Demos still run the CLI part. Start Ollama (`ollama serve`), pull
`gemma4:e4b`, or set `DEMOCRAFT_MODEL` to a model you have.

## CLI step failed (non-zero returncode)

Read `cli_steps[].stderr` - it is the engine's real message (bad params, no
project open headless). Nothing was faked; fix params and retry.

## Port busy

`start.ps1` clears :11246/:11245 first. If a zombie holds them:
`Get-NetTCPConnection -LocalPort 11246 | % { Stop-Process -Id $_.OwningProcess -Force }`.
Never kill NSSM children - these are not NSSM services.

## Webapp cannot reach backend

Check `GET http://127.0.0.1:11246/api/health`. CORS allows 127.0.0.1:11245
and Tauri origins only.
