---
type: Standard
title: claim-work shared active-work registry spec
description: Specification for the shared active-work registry used by agents before editing files. Repaired from old-format PR #12 standard.
resource: okf/standards/claim-work-spec.md
tags: [standard, claim-work, swarm, coordination, agents]
timestamp: 2026-07-18T00:00:00Z
linear_issue: null
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/standards/claim-work-spec.md
last_verified: 2026-07-18
verified_by: fred
status: current
---

# claim-work — Shared Active-Work Registry

**File:** `~/bin/claim-work`
**Status:** v1 shipped 2026-06-29
**Trigger:** Multi-agent coordination bug — bots stepping on each other's toes.

## What It Does

A simple JSON-based registry where agents register their intent to work on
specific files in specific repos. Other agents (or pre-commit hooks) check
the registry before touching those files.

```
~/.antigravity/active_work.json
{
  "claims": [
    {
      "repo": "prismatic-engine",
      "agent": "fred",
      "branch": "feature/gap14",
      "files": ["prismatic/auth.py", "prismatic/gateway.py"],
      "registered_at": 1782700000,
      "last_heartbeat": 1782700000,
      "expires_at": 1782701800,
      "description": "Gap 14 implementation"
    }
  ],
  "version": 1
}
```

## Commands

| Command | Purpose |
|---|---|
| `register` | Register a new claim (or update existing) |
| `heartbeat` | Refresh TTL (call every 5 min) |
| `release` | Remove a claim |
| `check` | Check if a file is claimed by another agent |
| `list` | View all claims |
| `prune` | Remove expired claims |

## TTL + Heartbeat

- **TTL**: 30 min default (configurable per claim)
- **Heartbeat**: agents call `heartbeat` every 5 min to keep claims alive
- **Stale claims**: auto-expire, no manual cleanup needed

## Pre-Commit Integration

Add to `.git/hooks/pre-commit`:
```bash
#!/usr/bin/env bash
# Check each staged file against the active-work registry
REPO=$(basename $(git rev-parse --show-toplevel))
for file in $(git diff --cached --name-only); do
  python3 /home/ubuntu/bin/claim-work check \
    --repo "$REPO" --file "$file" --agent "$(whoami)" || exit 1
done
```

## Lane Ownership Note

This is the **runtime coordination layer** on top of the static `lane` config
in PRISMATIC_ENGINE.yaml. Lanes say "Ned can write to prismatic/"; claim-work
says "Ned is currently writing to prismatic/auth.py on branch X."
