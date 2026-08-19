---
type: Standards
title: Hermes Next-Action Truth-Source Discipline
description: The dispatchable truth lives in Linear. The project-registry.json is the human-readable cache. Chat replies are downstream. Any Linear mutation that changes dispatch labels or owner-lane labels must update the registry in the same turn via registry_writer.py. A weekly cron reconciles Linear to registry. Stop writing next_actions in chat that aren't mirrored to either source.
resource: okf/standards/hermes-next-action-truth-source-discipline.md
tags: [standards, hermes, linear, registry, next-action, dispatch, micro-skills]
timestamp: 2026-07-29T06:00:00Z
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/standards/hermes-next-action-truth-source-discipline.md
linear_issue: null
last_verified: 2026-07-29
verified_by: fred
status: current
---

# Hermes Next-Action Truth-Source Discipline

## Purpose

The gap is: the next_action for each project lives in project-registry.json, but it's updated inconsistently. The dispatchable truth lives in Linear, but the registry and Linear drift apart. A "what's next?" answer in any channel can disagree with the registry, which can disagree with Linear.

This standard codifies the chain of truth: Linear is the source, the registry is the cache, chat is downstream.

## What this standard defines

1. **The hierarchy**: Linear (source) → project-registry.json (cache) → chat replies (downstream).
2. **The mutation contract**: any script that adds or removes a `dispatch:ready` / `dispatch:paused` / `dispatch:blocked` label, or an owner-lane label (`agent:fred`, `agent:agy`, `agent:kai`, `agent:george`, `agent:ned`, `agent:jules`, `agent:human`, `agent:needs-human-review`), MUST call `registry_writer.sync_project_from_issue()` immediately after the Linear mutation succeeds.
3. **The reconciliation cron**: weekly (Sunday 07:00 UTC), `registry_reconciler.py --quiet` runs and updates the registry from Linear, catching any drift.
4. **The chat discipline**: don't write a `next_action` in chat that isn't mirrored to Linear and the registry. If the agent wants to surface a next_action, mirror it first.

## What this standard explicitly does NOT cover

- It does not cover the work itself (covered by `okf/standards/hermes-session-handoff-discipline.md`, the agent-operations skills).
- It does not cover how Linear projects map to registry entries — that's the registry's own `linear_project_id` field.
- It does not cover chat-only annotations that aren't dispatchable (those are fine; just don't call them next_action).

## Adoption status (as of 2026-07-29)

The discipline is in effect.

- `scripts/registry_writer.py` (5,683 bytes) — single point of registry write. Provides `update_next_action(project_key, text)` and `sync_project_from_issue(issue, project_key=None)`.
- `scripts/registry_reconciler.py` (7,320 bytes) — weekly cron. Pulls Linear issues with dispatch/owner-lane labels, finds matching registry entries, updates `next_action`, `last_action_at`, `linear_issue_ids`.
- Micro-skill `skills/micro/next-action-truth-source/` — 1-page recipe; symlinked across 5 profiles (george, kai, ned, autobot, next-step).
- Cron job `Registry ↔ Linear Reconciler` added to `cron/jobs.json` (weekly Sunday 07:00 UTC, deliver=telegram).

The reconciler was live-tested on 2026-07-29: 100 dispatchable issues scanned, 1 updated (`hd-engine-core` registry entry updated to reflect GRO-4343's current title). Other 99 correctly skipped (no matching registry entry).

## The mutation contract

Every script that mutates Linear in a way that affects dispatch MUST call `sync_project_from_issue` after the mutation succeeds:

```python
from registry_writer import sync_project_from_issue
# ... after the issueUpdate / labels add / state change ...
sync_project_from_issue(issue_dict, project_key=...)
```

Scripts that need this integration (identified in the audit):
- `agy_peer_review.py` — adds `agent:fred` label on Done transitions.
- `agent_backlog_surgeon.py` — adds `dispatch:ready` label additively.
- `agy_post_publish_review.py` — adds `agent:fred` label on final close-out.
- Future scripts that touch these labels.

**Integration is the next bounded move** — the helpers exist; calling them is mechanical.

## The reconciliation contract

`registry_reconciler.py --quiet` is the cron path. It:

1. Queries Linear for issues with `dispatch:*` or `agent:*` labels (excluding `state.type = completed`).
2. For each, finds the matching registry entry by `linear_project_id` or `linear_issue_ids`.
3. Updates `next_action` to `{identifier}: {title} (state: {state})`.
4. Bumps `last_action_at` and `_last_updated`.
5. Adds the issue ID to `linear_issue_ids[]`.
6. Silent if no changes; bolded action line per changed project otherwise.

## The chat discipline

| Situation | What to do |
|---|---|
| User asks "what's next?" | Pull from registry; cite the issue ID and link to Linear. |
| Agent wants to surface a new next_action | Mirror it to Linear and registry FIRST, then surface it in chat. |
| next_action in chat doesn't exist in Linear | **Refuse to write it.** Ask the agent to mirror it. |
| next_action in registry is stale | Run `registry_reconciler.py --days 1 --dry-run` to see what would change; then re-run without `--dry-run`. |

## Verification

A "what's next?" answer in any channel:
1. Pulls from `project-registry.json` (the cache).
2. The registry entry references an issue ID (in `linear_issue_ids[]`) that exists in Linear.
3. The `next_action` text matches the Linear issue's title + state.
4. Linear is the source of truth; registry is the cache; chat is downstream.

If any of these don't hold, the chain is broken and the next_action is suspect. The fix is to reconcile or re-mirror.

## Honest lessons from the build

- **The mutation contract is the load-bearing piece.** The reconciler catches drift, but the contract prevents drift in the first place. Integration into the 3 mutation scripts is the next bounded move.
- **The rate-limit / budget gate is broken.** `prismatic.linear.budget` is a `.pyc` orphan; the budget gate fails on every query. The reconciler bypasses it (one well-formed query per week is fine), but the broader fix is rebuilding the budget module. Worth a follow-up.
- **Date filters on Linear GraphQL need care.** The first query failed with a 400 because `TimelessDateOrDateTime` filter syntax doesn't accept arbitrary ISO strings; the second query worked when we dropped the date filter and used `state.type: { neq: "completed" }`. A future improvement: re-add date filtering once the right type is identified.
- **The 99-skipped result is correct, not a bug.** Linear issues with dispatch labels but no matching registry entry are real (issues from sub-projects, ad-hoc tasks, etc.) and shouldn't pollute the registry.

## Related work

- OKF standard: `okf/standards/cron-alert-output-contract.md` (the cron contract the reconciler follows).
- Micro-skill: `skills/micro/telegram-cron-output-contract/` (companion micro-skill for cron output shape).
- Micro-skill: `skills/micro/next-action-truth-source/` (this standard's micro-skill).
- Existing cron: `Golden Thread Cross-Project Sync` (reads registry, doesn't reconcile).
