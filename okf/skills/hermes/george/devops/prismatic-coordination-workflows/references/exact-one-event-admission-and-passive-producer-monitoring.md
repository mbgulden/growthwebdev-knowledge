# Exact-one event admission and passive producer monitoring

Use this when Michael explicitly authorizes a Prismatic event admission plus one cap-1 producer after contract/envelope review is CLEAN/PASS.

## Guardrails

- Treat generic continuation as insufficient for event POST authority. Require explicit scoped wording for the event/task ID and cap-1 producer.
- Before POST, prove: exact task bytes/hash, exact clean base/tree, local-only branch/worktree if applicable, schema-valid payload, zero existing ledger rows for the task/event scope, and current gateway/policy/control coordinates from live files.
- If an HTTP attempt is rejected before ledger mutation, record it as a pre-ledger rejection, prove event/outbox/claim counts remain zero, restore temporary policy/control/config bytes, and do **not** call it a repost. Repost only means an accepted event already exists and another accepted event is attempted.
- Build one-shot admission utilities so they contain exactly one HTTP request call and exactly one consumer invocation. Static-check this before execution.
- Validate the exact payload against the deployed schema locally before the final accepted attempt.
- After accepted admission, prove one event, one processed outbox row, one completed claim with `attempt_count=1`, lifecycle through `claimed,validated,launch_started,launched`, no writer leases, cap-1 active slot, process identity via PID/start ticks, and policy/control/temp config restoration.
- Attach passive receipt-bound completion monitoring with `tail --pid=<pane_pid> -f /dev/null` plus a closeout proof script. Do not poll, impose a deadline, or kill the producer.
- Stop at producer-running unless/ until passive completion fires. Do not claim implementation correctness, candidate acceptance, PR, merge, deployment, cron/timer mutation, canonical suite green, or Linear write.

## Proof packet shape

```text
RESULT=PASS
HTTP_ATTEMPTS=<n>
PRELEDGER_REJECTIONS=<n>
ACCEPTED_POST_COUNT=1
EVENT_COUNT=1
EVENT_ID=<event id>
OUTBOX=processed
CLAIM_ATTEMPT=1
CLAIM_STATE=completed
LIFECYCLE=claimed,validated,launch_started,launched
LAUNCH_ID=<launch id>
PANE_PID=<pid>
PROCESS_IDENTITY_MATCH=true
ACTIVE_SLOT_COUNT=1
RUNTIME_DEADLINE=null
PRODUCER_STATUS=running
REPOSTED=false
POLICY_RESTORED=true
CONTROL_AUTH_RESTORED=true
TEMP_CONFIG_REMOVED=true
ONE_SHOT_UTILITY_REMOVED=true
PASSIVE_WAIT=<process session id>
AD_HOC_OR_CANONICAL=ad-hoc targeted admission/launch detector proof
NOT_CLAIMING=producer completion, implementation correctness, candidate acceptance, remote push, PR, merge, deployment, cron/timer mutation, canonical suite green, or Linear write
MARKER=<task>_ONE_EVENT_CAP1_RUNNING_OK
```
