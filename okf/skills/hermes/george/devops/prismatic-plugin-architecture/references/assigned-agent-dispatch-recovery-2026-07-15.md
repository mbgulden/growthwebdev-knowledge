# Assigned-agent dispatch recovery — queue, wake routing, and AGY canary (2026-07-15)

## Context

After the AGY bulk-dispatch failure, the recovery work started around the durable ingestion queue and AGY model preflight. Michael clarified that the desired workflow is not AGY-only and not an uncontrolled always-on Ned model. The target is the older useful behavior:

```text
Linear/task event
→ durable queue
→ resolve intended agent from assignee/label/metadata
→ preflight that exact agent
→ wake/dispatch exactly that agent for exactly that task
→ result/blocker writeback to Linear/dashboard
```

Desired examples:

```text
assigned/labeled for Kai → Kai wakes
assigned/labeled for Fred → Fred wakes
assigned/labeled for AGY → AGY wakes
unknown/ambiguous → needs_manual_review and wakes nobody
```

Do not frame future recovery work as `Linear queue → AGY only`.

## Accepted staged proof chain

The session established this recovery chain as sufficient to reopen controlled staged dispatch, with the boundary that it is **ad-hoc targeted recovery proof, not canonical full suite green**:

```text
INGESTION_QUEUE_DURABLE_CONTRACT_OK
INGESTION_QUEUE_DRAIN_SMOKE_OK
DISPATCH_PREFLIGHT_DECISION_OK
DASHBOARD_QUEUE_OPERATOR_PROOF_OK
ASSIGNED_AGENT_RESOLVER_BEHAVIOR_OK
PER_AGENT_PREFLIGHT_BEHAVIOR_OK
ASSIGNED_AGENT_WAKE_BEHAVIOR_OK
AGY_SINGLE_TASK_PROOF_OK
ASSIGNED_AGENT_DISPATCH_RECOVERY_OK
DASHBOARD_DISPATCH_INGESTION_READY_OK
```

Key proof boundaries:

- Queue/dashboard proof may be ad-hoc source/API/JS verification, not visual/browser full proof.
- Assigned-agent wake behavior may first be proven with fake launchers and temp state; do not claim real execution for agents that were not launched.
- Final recovery marker requires the AGY single-task proof; marker/static checks alone are insufficient.

## AGY single-task proof contract

The old assumed AGY command shape was not supported:

```bash
agy --headless --issue ...   # do not use
```

The installed AGY CLI path used:

```bash
agy --print ... --model "Gemini 3.5 Flash (High)" --log-file ...
```

Because the CLI/log path did not expose `dispatch.tokens.actual_input` / `actual_output`, accept equivalent nonzero proof:

```text
prompt_length > 0
task_payload_bytes > 0
result_text_bytes > 0
result_artifact_exists = true
Linear comment/state update exists
no_other_tasks_launched = true
```

The runner should hard-guard the canary issue only, e.g. `ALLOWED_IDENTIFIER = "GRO-3837"`, and refuse other identifiers until the next staged dispatch is explicitly approved.

Expected marker:

```text
AGY_SINGLE_TASK_PROOF_OK
```

## Assigned-agent wake behavior proof

After code-shape/static checks pass, require a behavior verifier that proves:

| Input | Expected behavior |
|---|---|
| `agent:kai` | resolves/wakes Kai only |
| `agent:fred` | resolves/wakes Fred only |
| `agent:agy` | resolves/wakes AGY path only |
| `agent:ned` | signals Ned only if explicitly routed |
| unknown/ambiguous/unlabeled | `needs_manual_review`, wakes nobody |

Expected markers:

```text
ASSIGNED_AGENT_RESOLVER_BEHAVIOR_OK
PER_AGENT_PREFLIGHT_BEHAVIOR_OK
ASSIGNED_AGENT_WAKE_BEHAVIOR_OK
```

If missing/ambiguous routing returns `no_op` or silently skips, fix it to write back a blocker and return `needs_manual_review`.

## Ned clarification

Michael does not want an uncontrolled always-on Ned worker as the primary model. If a Ned subscriber exists, distinguish it from the dispatcher/drain wake contract:

- Dispatcher path should wake/signal Ned only for explicit Ned routing.
- Separate Ned subscribers should be label/topic scoped to Ned-family work, not arbitrary tasks.
- Do not claim “no Ned daemon exists” unless actually verified; instead report whether it is scoped, pausable/disableable, and whether it can claim non-Ned work.

Accepted precise language:

```text
The dispatcher/drain wake contract only wakes Ned for explicit Ned routing. A separate Ned subscriber may exist; if so, verify it is scoped to Ned-family labels/topics and do not expand uncontrolled always-on behavior in this slice.
```

## Post-canary staged dispatch

Once `AGY_SINGLE_TASK_PROOF_OK` and assigned-agent behavior markers are accepted, do not bulk redispatch. Move to staged execution:

1. Review the AGY canary work product normally (for this session, PR #271 / GRO-3837 rubric inventory). Do not merge just because the canary proved dispatch worked.
2. If the work product satisfies the task, merge/comment Linear and mark the output review marker:

```text
GRO_3837_OUTPUT_REVIEW_OK
```

3. Only then open the next small stage, e.g.:

```text
GRO-3838 — Run current PE baseline and assign scores with evidence
GRO-3839 — Create closure ledger template and AGY handoff protocol
```

Expected readiness marker:

```text
STAGED_AGY_DISPATCH_READY_FOR_GRO_3838_3839
```

## Reporting pattern for Michael

Lead with a direct status and boundaries:

```text
Accepted: recovery proof is good enough to reopen staged controlled dispatch.
Boundary: ad-hoc targeted recovery proof, not canonical full suite green.
Not approved: bulk redispatch / uncontrolled always-on worker behavior.
Next: review the canary work product, then dispatch only the next approved stage.
```

When creating Fred prompts, include:

- exact markers to prove,
- no-bulk-dispatch guardrail,
- assigned-agent wake contract,
- explicit Ned caveat,
- a required proof-packet template,
- and a reminder that prompt/checklist docs should not be mixed into Fred implementation branches.
