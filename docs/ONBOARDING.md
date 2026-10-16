# docs/ONBOARDING.md

## 1. What this is for

Democraft demos all 13 ArtCraft apps (CAD through Word) from one MCP server
and webapp. Each demo runs the real headless CLI plus a local-LLM step and
shows the artifacts. It does not replace the Craft apps, and it does not
generate ArtCraft AI pixels without an account.

## 2. Cost and accounts (money / CC)

| Question | Answer |
|----------|--------|
| Do I need an account? | Only for AI-gated engine features (ArtCraft generation). CLI demos: no. |
| Free tier? | Craft CLIs run free locally once installed. |
| Credit card required? | No, unless you buy ArtCraft generation tokens. |
| Ongoing cost? | None for democraft (local Ollama, local CLIs). |
| Who bills? | ArtCraft, only if you use their hosted generation. |

## 3. Install the wrappees

Install the Craft apps from https://getartcraft.com/apps (default paths under
`C:\Program Files\`). Democraft detects each `<Name>\<cli>.exe` at demo time;
missing apps show MOCK badges on their page until installed.

## 4. AI flows (local Ollama)

Install Ollama, pull a model (`ollama pull gemma4:e4b` - 8GB default).
Override with `DEMOCRAFT_MODEL`. If Ollama is down, demos still run the CLI
part and mark the AI step skipped.

## 5. First demo

`start.bat`, open http://127.0.0.1:11245, Dashboard, CAD page, Run demo #1
(Japanese small house plan). Artifacts land in `outbox/cad/house-plan/`.

## 6. Troubleshooting

See `docs/TROUBLESHOOTING.md` (wrappee missing, Ollama down, engine stderr).
