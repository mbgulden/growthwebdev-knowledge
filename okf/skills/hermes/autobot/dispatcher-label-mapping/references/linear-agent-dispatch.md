# Linear Agent Dispatch Architecture (rehosted reference)

This reference mirrors the content from `antigravity-cli-orchestration/references/linear-agent-dispatch.md` 
with the updated label mapping.

## Architecture

```
Every 15 minutes (cron e2f1a3b4c5d6):
  agent_dispatcher.py
    ├── Query Linear: issues with any agent:* label
    ├── Filter: only non-completed, non-canceled issues
    ├── Check agent capacity (max concurrent per handler)
    └── Dispatch via AGENT_LABELS dict
```

## How to Assign Work

Add a label to any Linear issue in the GrowthWebDev team:

- `agent:orchestrator` — orchestrator (visual design, research, UI/UX)
- `agent:jules` — Jules CLI (async GitHub PR work)
- `agent:fred` — Fred (implementation, deployment, strategy)
- `agent:hermes` — Fred (legacy alias, same handler)
- `agent:kai` — Kai (Active Oahu Tours content)
- `agent:autobot` — Autobot (task distribution manager)
- `agent:codex` — Codex CLI (visible code review)
- `agent:done` — Terminal state
