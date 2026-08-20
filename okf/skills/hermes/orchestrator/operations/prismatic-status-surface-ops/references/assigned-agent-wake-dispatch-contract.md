# Assigned-Agent Wake Dispatch Contract

Session learning from restoring the queued webhook → assigned-agent wake path after durable ingestion queue work.

## Trigger

Use this when durable `linear_webhook_queue.db` rows drain, but assigned work does not wake Fred/Kai/Ned/AGY, or when a drainer/import path expects `prismatic.dispatcher.dispatch_issue_by_identifier`.

## Core contract

The reusable platform flow should be:

```text
linear_webhook_queue.db row
→ scripts/drain_webhook_queue.py
→ prismatic.dispatcher.dispatch_issue_by_identifier(identifier)
→ get_issue_by_identifier()
→ resolve_assigned_agent()
→ preflight_dispatch_decision()
→ wake_assigned_agent_for_issue()
→ existing launcher/signal path
→ Linear writeback comment
```

AGY may be the first proof target, but the platform contract must support Fred, Kai, Ned, AGY, and future agents through the same resolver/preflight/wake/writeback path.

## Implementation notes

- `scripts/drain_webhook_queue.py` imports `dispatch_issue_by_identifier`; if `dispatcher.py` does not expose it, the durable queue can drain only with a stub verifier and the live wake contract is broken.
- Add/keep a structured result object such as `AssignedAgentWakeResult` so blocked/deferred/manual-review/no-op states are inspectable.
- `resolve_assigned_agent()` should resolve exactly one plain `agent:*` assignment label.
- Treat AGY model-tier labels (`agent:agy-flash-high`, etc.) as model routing/config labels, not additional assignment labels.
- Ambiguous labels such as `agent:fred` + `agent:kai`, missing plain `agent:*` labels, and unsupported future assignment labels should return `needs_manual_review`, write back the blocker reason, and wake nobody. Do not leave these as silent `no_op` or generic `blocked` results.
- Preserve concrete reasons (`missing_agent_label`, `ambiguous_agent_labels:fred,kai`, `unsupported_agent:<name>`) inside the manual-review result/writeback so operators know the exact routing defect.
- Add missing configured agents, e.g. Ned, to both `AGENT_CONFIG` and `AGENT_LAUNCHERS`; for file-backed agents use the same signal provider path as Fred/Kai.
- Writeback should be explicit and auditable: `Assigned-agent wake dispatched` for successful wakes or `Assigned-agent wake needs manual review` for unresolved/unsupported routing, including agent/status/reason/cycle where applicable.

## Verification pattern

Use a fresh `/tmp/hermes-verify-*` script with an isolated durable queue DB and fake launchers/comments. Do **not** launch real agents during the contract proof.

### Static/drain contract proof

Minimum checks:

```text
CANONICAL_TEST_LINT_BUILD_COMMAND=python3 -m py_compile /path/to/prismatic/dispatcher.py /path/to/scripts/drain_webhook_queue.py
AD_HOC_VERIFICATION=PASS
marker=ASSIGNED_AGENT_WAKE_DISPATCH_OK
real_agent_launches=0
wake_agents=[agy, fred, kai, ned]
drain_statuses all dispatched
writeback_count=4
cleanup=PASS
```

Synthetic rows should cover:

- `agent:fred` + `dispatch:ready` wakes Fred;
- `agent:kai` + `dispatch:ready` wakes Kai;
- `agent:ned` + `dispatch:ready` wakes Ned;
- `agent:agy` + `dispatch:ready` + `agent:agy-flash-high` wakes AGY and normalizes model to `Gemini 3.5 Flash (High)`;
- ambiguous multiple plain `agent:*` labels return `needs_manual_review`, write back `ambiguous_agent_labels:...`, and wake nobody;
- missing assignment labels return `needs_manual_review`, write back `missing_agent_label`, and wake nobody;
- unsupported `agent:future` returns `needs_manual_review`, writes back `unsupported_agent:future`, and wakes nobody;
- single-task AGY gate blocks non-approved AGY work with `agy_single_task_gate:<identifier>`.

### Behavioral proof table

When the user challenges static/stale-guard proof, stop repeating marker checks and run a behavior verifier. The verifier should monkeypatch `AGENT_LAUNCHERS` and `add_comment`, then report a table with exactly this shape:

```text
Input | Expected agent | Actual agent | Wake target | Writeback | Result
```

Minimum behavior rows:

| Input | Expected result |
| --- | --- |
| `agent:kai` | actual/wake target `kai`, dispatched writeback |
| `agent:fred` | actual/wake target `fred`, dispatched writeback |
| `agent:agy` + model label | actual/wake target `agy`, AGY launch path only |
| `agent:future` | `needs_manual_review`, no wake, blocker writeback |
| `agent:fred` + `agent:kai` | `needs_manual_review`, no wake, ambiguous blocker writeback |
| explicit `agent:ned` | actual/wake target `ned`, dispatched writeback |
| no agent label | `needs_manual_review`, no wake, missing-label writeback |

Expected markers for this proof:

```text
ASSIGNED_AGENT_RESOLVER_BEHAVIOR_OK
PER_AGENT_PREFLIGHT_BEHAVIOR_OK
ASSIGNED_AGENT_WAKE_BEHAVIOR_OK
```

Also inspect Ned separately before answering safety questions. The dispatcher/drainer proof may show Ned is explicit-only, while a separate Ned Hermes profile/subscriber can still be running. If present, report that distinction clearly and inspect its label/topic filters instead of claiming no Ned daemon exists.

## Boundary

`ASSIGNED_AGENT_WAKE_DISPATCH_OK` proves the platform resolver/preflight/wake/writeback contract with fake launchers. The behavioral markers prove per-agent routing and unresolved-route safety. Neither proves `AGY_SINGLE_TASK_PROOF_OK`; that still requires one real approved task with token/input/output/result/writeback evidence. Do not claim `ASSIGNED_AGENT_DISPATCH_RECOVERY_OK` until both behavior proof and `AGY_SINGLE_TASK_PROOF_OK` are complete.

## Stale-guard pitfall

If a stale guard flags the temp verifier path (for example `/tmp/hermes-verify-assigned-agent-wake.py`), rerun a new OS-safe `tempfile.NamedTemporaryFile(prefix='hermes-verify-', dir='/tmp')` verifier, include the prior temp path in `changed_paths_checked`, assert it no longer exists, and clean up the new verifier.