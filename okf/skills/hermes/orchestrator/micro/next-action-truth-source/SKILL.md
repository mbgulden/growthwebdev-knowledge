---
name: next-action-truth-source
description: The "what ships next" gate discipline. Linear is the dispatchable truth; project-registry.json is the human-readable cache; chat replies are downstream. On any Linear mutation that changes dispatch labels (dispatch:ready, dispatch:paused, dispatch:blocked) or owner-lane labels (agent:fred, agent:agy, agent:kai, agent:george, agent:ned, agent:jules, agent:human, agent:needs-human-review), update the registry in the same turn via registry_writer.py. Stop writing next_actions in chat that aren't mirrored to either source. A weekly cron reconciles Linear to registry.
---

# next-action-truth-source

## The rule

The dispatchable truth lives in Linear. The registry is a human-readable cache. Chat replies are downstream.

**Any Linear mutation that changes a dispatch label or owner-lane label MUST also update the registry in the same turn.** The update goes through `scripts/registry_writer.py` (the single point of registry write) and the mutation script calls `sync_project_from_issue()` after the GraphQL call succeeds.

**No next_action in chat** that isn't mirrored to either source. If you state "next is GRO-4343", the issue must exist in Linear AND the registry must reference it. If it doesn't, you've invented work.

## The hierarchy

1. **Linear**: the source. Every dispatchable issue has a label (`dispatch:ready`, `dispatch:paused`, `dispatch:blocked`) and/or an owner-lane label (`agent:fred`, etc.). Mutations here are the only authoritative ones.
2. **project-registry.json**: the cache. Updated by `registry_reconciler.py` (weekly cron) and by mutation scripts that call `registry_writer.sync_project_from_issue()` immediately after their Linear write.
3. **Chat replies**: downstream. Always re-stated from registry or Linear — never invented.

## The contract

| When | Action |
|---|---|
| Linear mutation that adds/removes a dispatch or owner-lane label | Call `registry_writer.sync_project_from_issue(issue)` immediately after the Linear mutation succeeds. |
| Weekly | Run `registry_reconciler.py --quiet` to catch any drift between Linear and registry. |
| "What's next?" in any channel | Pull from registry (which mirrors Linear), not from chat history. |
| A chat-only next_action (not in registry or Linear) | **Refuse to write it.** Ask the agent to mirror it first. |

## Implementation

Mutation scripts (agy_peer_review.py, agent_backlog_surgeon.py, agy_post_publish_review.py) should:

```python
# After the Linear mutation:
from registry_writer import sync_project_from_issue
sync_project_from_issue(issue, project_key=...)
```

The weekly cron:

```bash
python3 /home/ubuntu/.hermes/profiles/orchestrator/scripts/registry_reconciler.py --quiet
```

## Anti-patterns

- "The registry is stale, let me update it manually in chat." (Use registry_writer, not chat edits.)
- "I'll skip the registry update; the next cron will catch it." (Same turn, not next cron. Drift accumulates.)
- "next_action is X where X is some Linear issue that doesn't exist yet." (Inventing work. Refuse.)
- "I'll write next_action in the chat reply; the user can copy it to Linear later." (User won't. Mirror now or don't write.)

## Verification

A "what's next?" answer in any channel:
1. Pull from registry (or query Linear directly).
2. The registry entry references the issue ID (in `linear_issue_ids[]`) AND the next_action text matches the issue's title.
3. Linear is the source of truth; registry is the cache; chat is downstream.

If any of these don't hold, the chain is broken and the next_action is suspect.
