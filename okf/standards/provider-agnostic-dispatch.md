# Provider-Agnostic Dispatch — The "Codex + MiniMax only" Reality

**Status:** Active (2026-06-23)
**Linear:** Epic `GRO-2339` + 4 children (`GRO-2340`..`GRO-2343`)
**Owner:** AGY research + Fred implementation

## Context

Per Michael (2026-06-23):
> "Most users will only have the chatGPT codex OAuth and MiniMax.
> That's why we need this system to work with any provider and dispatch
> to be flexible and be able to work with any agents that happen to be there."

The **target user** of the Prismatic Engine is:
- A small business owner / consultant
- Uses ChatGPT (Codex) for code + daily work
- Uses MiniMax (or equivalent) for content + long-context tasks
- Does NOT have Hermes installed
- Does NOT have AGY/Jules/Kai/Ned agents
- Does NOT have GPU servers
- Does NOT know git/GitHub

The engine must work for THIS user, not just for Michael's full setup.

## What We Built (this turn)

### Provider Dispatch (`provider_dispatch.py`)

Discovers what's actually available:
- API keys in environment
- OAuth tokens on disk
- Local servers (Ollama, vLLM)
- Hermes profiles (Michael's setup only)

Routes tasks to whatever's available:
- `provider:codex` if Codex OAuth is set up
- `provider:minimax` if MiniMax key is set
- `provider:openai` / `anthropic` / `google` for direct API keys
- `agent:agy` / `agent:jules` etc. ONLY if those agents exist

### Linear Labels Updated

19 existing research tasks now carry both labels:
- `agent:agy` (Michael's setup picks up)
- `provider:any` (Codex OAuth / MiniMax workers pick up)

This means: research continues even if AGY doesn't exist.

### New Linear Epic

`GRO-2339` — `[PROVIDER-AGNOSTIC] Design the minimum-viable agent setup`

4 research tasks:
1. `GRO-2340` — Codex OAuth + MiniMax dispatch architecture
2. `GRO-2341` — PWP without CF Pages API access
3. `GRO-2342` — UI surfaces without an orchestrator agent
4. `GRO-2343` — Onboarding flow for minimal user

## What the Target User Looks Like

| They have | They don't have |
|---|---|
| ChatGPT Codex OAuth | Hermes |
| MiniMax API key | AGY/Jules/Kai/Ned |
| CF Pages account (free) OR GitHub Pages | GPU servers |
| Web browser | Local Python install |
| | Linear |
| | Git knowledge |

The engine needs to:
1. **Detect their setup** (run `provider_dispatch.py`)
2. **Adapt the UI** (no Linear/Fred/AGY chatter)
3. **Use what they have** (Codex for code, MiniMax for content)
4. **Deploy where they can** (CF Pages free tier OR GitHub Pages)
5. **Provide version control** without git (snapshots in CF Pages history)

## Provider Label System

```
provider:codex        # ChatGPT Codex OAuth (most common)
provider:minimax      # MiniMax API
provider:openai       # OpenAI direct
provider:anthropic    # Claude direct
provider:google       # Gemini direct
provider:ollama       # Local Ollama
provider:local        # Any local model server
provider:any          # Catch-all (any provider worker can pick up)
```

Linear tasks should carry:
- `provider:any` for things ANY provider can do
- `provider:codex` for things only Codex can do (large code refactors)
- `provider:minimax` for things only MiniMax can do (very long context)
- Multiple labels when multiple providers work

## Roadmap

**Phase 1 (this turn):** Provider-agnostic dispatch + research backlog ✅
**Phase 2 (after research lands):** Update best-fit rubric to use provider scoring
**Phase 3 (next 1-2 sprints):** Build the minimal-viable UI for Codex+MiniMax users
**Phase 4 (when ready):** Free-tier hosting option (no CF Pages API needed)

## Related Docs

- `okf/standards/agent-auto-discovery.md` — the discovery layer
- `okf/standards/agent-best-fit-rubric.md` — will be updated for provider scoring
- `okf/standards/multi-user-research-series.md` — covers UX for multiple users
- `pwp/SETUP.md` — current PWP setup (assumes CF Pages API access)
- `provider_dispatch.py` — the implementation
</content>
