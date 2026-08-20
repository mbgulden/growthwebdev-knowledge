---
name: dispatcher-label-mapping
description: Canonical mapping of Linear agent labels to handler functions, concurrency caps, and handoff chains. Central reference for adding or changing agent dispatch labels.
category: agent-orchestration
---

# Agent Dispatcher Label Mapping

Canonical label-to-agent mapping as of June 2026. Source of truth is the `AGENT_LABELS` and `MAX_CONCURRENT` dicts in `agent_dispatcher.py`.

## All Supported Labels

| Label | Agent | Handler | Max Concurrent | Handoff |
|-------|-------|---------|---------------|---------|
| `agent:agy` | Antigravity CLI | `launch_agy()` | 3 | → `agent:fred` |
| `agent:jules` | Jules CLI | `launch_jules()` | 8 | → `agent:done` |
| `agent:fred` | Fred (orchestrator) | `launch_hermes()` | 10 | → `agent:done` |
| `agent:hermes` | Fred (orchestrator, legacy alias) | `launch_hermes()` | 10 | → `agent:done` |
| `agent:kai` | Kai (Oahu Tours) | `launch_hermes()` | 3 | → `agent:done` |
| `agent:autobot` | Autobot (task distribution manager) | `launch_hermes()` | 10 | → `agent:done` |
| `agent:codex` | Codex CLI | `launch_codex()` | 3 | → `agent:fred` |
| `agent:done` | — | Terminal state | — | — |

## Label Handoff Lifecycle

```
agent:agy → agent:fred → agent:done   (implementation task)
agent:agy → agent:done                 (research/reporting)
agent:codex → agent:fred → agent:done  (code review)
Direct: agent:fred → agent:done        (one-shot tasks)
agent:kai → agent:done                 (tourism content)
agent:autobot → agent:done             (distribution tasks)
```

## Maintaining the Mapping

When adding a new agent label, update three places in lockstep:

1. **`AGENT_LABELS` dict** in `agent_dispatcher.py` — maps label string → handler function name
2. **`MAX_CONCURRENT` dict** in `agent_dispatcher.py` — maps handler name → concurrency cap
3. **Linear labels** — create the `agent:<name>` label via the Linear web UI or GraphQL

The dispatcher queries ALL labels in a single GraphQL batch call. If a label exists in Linear but not in the query, the dispatcher never sees those issues. If a label is in the query but not in `AGENT_LABELS`, the dispatcher finds issues but skips them.

## Script Location

`~/.hermes/profiles/orchestrator/scripts/agent_dispatcher.py`

## Cron

ID: `e2f1a3b4c5d6`  
Schedule: `every 15 minutes`  
Mode: `no_agent=true` (script-only, deterministic delivery)

## Related Skills

- `antigravity-cli-orchestration` — full Antigravity CLI orchestration, Book End protocol, pipeline routing
- `orchestrator-delegation-discipline` — HOW to delegate, not WHICH labels
- `references/linear-agent-dispatch.md` under antigravity-cli-orchestration — full architecture doc
