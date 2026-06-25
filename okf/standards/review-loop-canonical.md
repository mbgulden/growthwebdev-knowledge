---
type: Standard
title: Self-Review + Peer Review Loop (Canonical Codification)
description: The canonical review loop enforced in agent_dispatcher.py. Worker → AGY peer review → Fred verification → agent:done.
resource: okf/standards/review-loop-canonical.md
tags: [review-loop, agent:fred, agent:agy, peer-review, codification]
timestamp: 2026-06-19T10:30:00Z
linear_issue: GRO-2024
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/standards/review-loop-canonical.md
last_verified: 2026-06-25
verified_by: fred
status: current
---

# Self-Review + Peer Review Loop (Canonical Codification)

**Status:** ENFORCED in `agent_dispatcher.py` as of Jun 18 2026.
**Enforcement point:** `agent_dispatcher.py` lines around `next_label = config.get("next_label")`
(see [agent_dispatcher.py](../../../../.hermes/profiles/orchestrator/scripts/agent_dispatcher.py)).

This doc is also referenced from the prismatic-engine spoke bundle:
[`prismatic-engine/okf/review-loop-canonical.md`](https://github.com/mbgulden/prismatic-engine/blob/main/okf/review-loop-canonical.md).

## The loop (canonical)

```text
Worker (Ned, Kai, Jules, Codex, Autobot, AGY sub-lanes)
   ↓
AGY peer review (different agent, read-only)
   ↓
Fred verification (orchestrator confirms review artifact + walkthrough)
   ↓
agent:done → Done state
```

Every agent lane routes through AGY for peer review, except:

- **AGY itself** (the peer-reviewer) routes directly to Fred for verification.
- **Fred** is the only lane that may move to `agent:done`.

## Label chain (single source of truth)

| Source lane | `next_label` | Why |
|---|---|---|
| `agent:kai`, `agent:kai-css`, `agent:kai-content`, `agent:kai-js` | `agent:agy` | Kai ships to AGY for peer review |
| `agent:codex` | `agent:agy` | Codex ships to AGY |
| `agent:autobot` | `agent:agy` | Autobot ships to AGY |
| `agent:ned` | `agent:agy` | Ned ships to AGY |
| `agent:ned-code`, `agent:ned-infra`, `agent:ned-audit`, `agent:ned-review` | `agent:ned` | Ned sub-agents report to Ned |
| `agent:jules` | `agent:fred` | Jules → AGY (via redirect) → Fred |
| `agent:agy`, `agent:agy-*` (8 lanes) | `agent:fred` | AGY peer review complete → Fred verify |
| `agent:antigravity-cli` | `agent:fred` | Antigravity CLI is AGY-equivalent |
| `agent:fred` | `agent:done` | **Only Fred may move to Done.** |
| `agent:done` | terminal | No further routing. |

## Why the loop exists (briefly)

`orchestrator-delegation-discipline/references/pipeline-bypass-detection-case-study.md`
documents the bypass that this codification fixes: in June 2026, 5 Darius Star
issues went `agent:ned → Done` with no AGY peer review. The old label chain
allowed it because `agent:fred.next_label` was `agent:done` with no verification
step between AGY review and Done.

The fix is two-layer:

1. **Label chain enforcement** — every agent's `next_label` routes to either
   `agent:agy` (for peer review) or `agent:fred` (for verification). No
   agent may skip to `agent:done` directly.
2. **Bypass detection in dispatcher** — at the transition point, if any
   source label is trying to move an issue to `agent:done` (other than
   `agent:fred` itself), the dispatcher blocks the transition and re-routes
   to `agent:fred` with a comment explaining why.

## Where this is enforced

- `agent_dispatcher.py` — `AGENT_CONFIG` (the table above) + the
  bypass-detection block right before each `transition_label()` call.
- `agent_output_validator.py` — validates AGY transcripts (walkthrough comment,
  no error markers, artifact paths exist) before allowing the next transition.

## Where the bypass check lives

```python
# Pipeline bypass detection (GRO-2024 review loop enforcement):
# Only Fred (next_label="agent:done") may move an issue to Done.
if next_label == "agent:done" and label_name != "agent:fred":
    bypass_comment = "..."
    transition_label_with_comment(
        issue["id"], label_name, "agent:fred", bypass_comment
    )
    continue
```

## What Fred actually verifies

When `agent:fred` picks up an issue:

1. The validator transcript is clean (no `agent_output_validator` escalation).
2. A Linear comment from the worker exists with file paths or artifact references.
3. The issue has been through `agent:agy` (peer review) at some point — checked
   via label history or `agent:fred` cron pickup.

If any of these checks fail, Fred re-routes to the appropriate agent rather
than transitioning to `agent:done`.

## Failure modes this prevents

- Worker self-review-only (no AGY peer review).
- AGY review without Fred verification (no human-in-the-loop stop).
- Done state with empty transcript (silent validator crash, June 2026).
- Done state with `requires:human-approval` (send outreach, publish profile).

## Related docs

- [`linear-rate-limit.md`](./linear-rate-limit.md) — companion standard
- [prismatic-engine architecture](../projects/prismatic-engine.md) — Tier 4 architecture
- `orchestrator-delegation-discipline/SKILL.md` — top-level discipline overview
- `orchestrator-delegation-discipline/references/quality-loop-enforcement.md` — historical rules
- `orchestrator-delegation-discipline/references/pipeline-bypass-detection-case-study.md` — bypass that motivated this
- `prismatic-engine-operations/SKILL.md` — engine-vs-harness rule
