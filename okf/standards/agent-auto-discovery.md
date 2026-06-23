# Agent Auto-Discovery — The "Install and Forget" UX

**Status:** Active • **Last updated:** 2026-06-23 • **Owner:** Fred
**Linear:** GRO-2295 (epic) + 5 children

## The Vision

> "Hypothetically, the user already has Hermes installed and has their
>  existing orchestrator and 3 other OAuth workers and 2 GPU workers.
>  The user downloads Prismatic engine and installs it and the engine
>  immediately picks up the Hermes install and loads in the proper agents
>  seamlessly to be called in for orchestration."

Prismatic Engine is **prismatic** because it reflects whatever agent
infrastructure already exists. The moment it installs, it discovers what's
there and starts orchestrating.

## What It Does

`agent_discovery.py` (in orchestrator/scripts) does the discovery:

1. **Scans for known agent infrastructure** (5 patterns)
2. **For each discovered agent, gathers metadata** (model, endpoint, capabilities)
3. **Optionally runs a quick capability test** (one prompt, measure latency)
4. **Emits a discovery manifest** (`discovered_agents.json`)
5. **Auto-registers in dispatch state** (`agent_inventory.json`)

The dispatch system then picks up the inventory and includes the new agents
in the best-fit rubric for work assignment.

## Discovery Patterns

### 1. Hermes Profiles
**Scanner:** `discover_hermes_profiles()`
- Scans `~/.hermes/profiles/*/config.yaml`
- Extracts: name, label, model, provider, lanes, role
- **E2E test:** Found 18 profiles (ned, fred, kai, kai-content, kai-css, kai-js, orchestrator, becca, codex-5-4, codex-5-5, deepseekv4, hermeslocal, hdengine, autobot, qwenlocal, ai-consulting, next-step, active-oahu)

### 2. OAuth Workers
**Scanner:** `discover_oauth_workers()`
- Reads `~/.hermes/.env`, `~/.env`, `~/.prismatic/env.d/`
- Detects: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`, `DEEPSEEK_API_KEY`
- Creates virtual agents for each (no actual profile, but available for dispatch)
- **E2E test:** 0 found (no API keys in this env)

### 3. GPU Workers
**Scanner:** `discover_gpu_workers()`
- Probes common ports:
  - 11434 (Ollama) → `GET /api/tags`
  - 8000 (vLLM) → `GET /v1/models`
  - 1234 (LM Studio) → `GET /v1/models`
  - 8080 (llama.cpp) → `GET /v1/models`
  - 5000 (Oobabooga) → `GET /v1/models`
- Discovers all available local models from the response
- **E2E test:** 0 found (no GPU servers running)

### 4. Custom Agents
**Scanner:** `discover_custom_agents()`
- Walks `/home/ubuntu/work`, `/home/ubuntu/.local/share`, `/opt`
- Finds Python files with `def run/main/invoke/handle` AND references to agent/LLM/model
- **E2E test:** 89 found (very noisy — every script that looks like an agent)
- **For now, custom agents are NOT auto-registered** — they require manual review
  to avoid flooding the dispatch system

### 5. Running Processes
**Scanner:** `discover_running_processes()`
- Scans `ps -eo pid,user,comm,args`
- Finds processes with "agent", "bot", "worker" in args
- **E2E test:** 90 found (very noisy)
- **For now, processes are NOT auto-registered** — they need manual review

## Auto-Registration

`register_in_dispatch()` writes two files to `~/.prismatic/prismatic_state/`:

1. **`discovered_agents.json`** — raw discovery results (all 196 found, including noisy ones)
2. **`agent_inventory.json`** — the agents registered for dispatch (only 18 Hermes profiles, the curated set)

The inventory has the schema:
```json
{
  "label": "agent:fred",
  "name": "fred",
  "type": "hermes-profile",
  "model": "default: gpt-5.5",
  "provider": "openai",
  "endpoint": "/home/ubuntu/.hermes/profiles/fred/config.yaml",
  "capabilities": ["chat", "tools", "Orchestrator & Review Gate"],
  "config_path": "/home/ubuntu/.hermes/profiles/fred/config.yaml",
  "registered_at": 1782246023.74
}
```

## Capability Evaluation

When `--evaluate` is passed, the script sends a test prompt to OAuth +
GPU workers (the only types with HTTP endpoints) and measures:
- Latency (seconds)
- Response presence (yes/no)
- Response snippet

The score is then attached to the inventory entry. This lets the
dispatch system prefer faster agents for time-sensitive work.

For Hermes profiles, capability is inferred from the role/lanes in
config.yaml (we don't actually invoke them — they're not HTTP services).

## Cron Wiring

- **Cron ID:** `df04a66d3467`
- **Schedule:** daily at 04:00 UTC
- **Script:** `agent_discovery_cron.sh`
- **Action:** Runs `--register --evaluate`
- **Output:** `~/.prismatic/prismatic_state/{discovered_agents,agent_inventory}.json`

## The "Install and Forget" UX

```
$ curl -fsSL prismatic-engine.dev/install.sh | sh
$ # That's it. Prismatic Engine:
$ # 1. Installs itself
$ # 2. Runs agent_discovery.py on install
$ # 3. Finds 23 agents (18 Hermes + 3 OAuth + 2 GPU)
$ # 4. Registers all 23 in dispatch state
$ # 5. User connects Linear
$ # 6. Dispatch unlocks, work starts flowing to the right agent
```

No manual configuration. No "go register your agents" step. The engine
finds what's there and uses it.

## What It Does NOT Solve (Yet)

- **Capability inference for custom agents** — currently we just count "custom" as a capability. We could run actual capability tests.
- **Workload balancing** — discovery gives us the inventory, but the dispatch system needs to balance load across agents
- **Self-describing agent manifests** — currently we parse configs and probe endpoints. A better design has each agent publish a `/manifest.json` with its capabilities.
- **Conflict resolution** — what if two agents claim the same lane? We currently use first-come-first-served.
- **Auto-unregister** — when an agent disappears (Hermes profile deleted, GPU server down), we should remove it from the inventory.
- **OAuth + GPU worker HTTP wrappers** — we need to build the actual invocation code that uses these endpoints. Currently they're just inventory entries.

## Component Inventory

| Component | Path | Purpose |
|---|---|---|
| `agent_discovery.py` | `orchestrator/scripts/` | The discovery engine |
| `agent_discovery_cron.sh` | `orchestrator/scripts/` | Cron wrapper |
| `discovered_agents.json` | `~/.prismatic/prismatic_state/` | Raw discovery results |
| `agent_inventory.json` | `~/.prismatic/prismatic_state/` | Curated dispatchable agents |
| Cron `df04a66d3467` | daily 04:00 UTC | Periodic re-discovery |

## Related Docs

- `okf/standards/agent-best-fit-rubric.md` — how work is assigned to agents
- `okf/standards/event-driven-post-publish.md` — the post-publish chain
- `okf/standards/post-publish-review-architecture.md` — the post-publish chain
- `okf/standards/agy-architecture-recipe.md` — AGY's role
- `okf/standards/agent-swarm-review-architecture.md` — the review layer

## Linear Tracking

- **GRO-2295** (epic): Agent auto-discovery — DONE
- **GRO-2296**: Add custom-agent self-describing manifest
- **GRO-2297**: Build OAuth + GPU worker HTTP invocation wrappers
- **GRO-2298**: Add workload balancing across discovered agents
- **GRO-2299**: Add auto-unregister for disappeared agents
- **GRO-2300**: Improve capability inference (run actual tests, not just "custom")
