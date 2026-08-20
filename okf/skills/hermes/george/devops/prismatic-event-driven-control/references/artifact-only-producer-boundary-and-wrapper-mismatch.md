# Artifact-only producer boundary and admission wrapper mismatch

Use this when advancing a Prismatic successor task through the event gate where the task is intended to produce artifacts/proofs only, not source changes.

## Durable lessons

1. **Classify wrapper assertion failures before retrying.** A local wrapper can fail because it expected the wrong response shape (for example, checking `state=completed` when the consumer emits `status=processed`). Do not repost the admission or invoke the ordinary consumer again until event-scoped SQLite rows are inspected.
2. **Use event-scoped DB proof, not global counters.** Bind status to the exact `event_id`, `claim_id`, and `launch_id`: outbox row count/status, claim state/attempt count, lifecycle entries, writer leases, and active producer slot.
3. **Restore temporary controls immediately after the single event.** Prove one-time operator credentials, policy worktree windows, and private runtime task registry entries were removed/restored after POST + consumer invocation.
4. **Receipt-bound producer state only.** Use the canonical launch receipt/harness/activity paths from the admission runtime directory. Do not guess tmux session names or manifest paths.
5. **Artifact-only tasks fail closed on undeclared worktree mutations.** If the producer creates an undeclared source/worktree file such as `STARTED.md`, mark acceptance held even if later artifacts or `RESULT.md` claim `PASS`. Do not delete or edit the file while the producer is active; preserve it for independent review and same-task repair classification.
6. **No further workflow movement while cap-1 producer runs.** No duplicate admission, no consumer reinvocation, no cap increase, no merge/deploy, and no cleanup of live producer artifacts until durable termination and independent review.

## Minimal proof packet

```text
TASK=<id>
EVENT_ID=<event id>
CLAIM_ID=<claim id>
ATTEMPT=1
LAUNCH_ID=<launch id>
OUTBOX_STATUS=processed
CLAIM_STATE=completed
PRODUCER_STATUS=<running|completed|failed>
PROCESS_ALIVE=<true|false>
RUNTIME_DEADLINE=null
AUTOMATIC_KILL=false
WRITER_CAP=1
SELECTABLE_EVENTS=0
WRITER_LEASES=0
POLICY_RESTORED=true
CONTROL_AUTH_RESTORED=true
PRIVATE_REGISTRY_RESTORED=true
WORKTREE_STATUS=<exact porcelain lines>
ACCEPTANCE_HELD=<true/false + reason>
NOT_CLAIMING=producer completion, artifact correctness, source repair, review, PR, merge, deployment, cap increase
```

## Post-edit detector closeout

If handoff/control files are edited to record this boundary, run a focused `/tmp/hermes-verify-*` verifier that asserts:

- exact task file hash and bus/worktree equality;
- exact head/tree binding;
- `.git/info/exclude` contract for `.prismatic-task/` when used;
- exact event/claim cardinality;
- restored control files and credentials;
- contained legacy consumer/watchdog states, capturing systemd stdout rather than relying on success exit codes;
- handoff contains the event ID, undeclared-file hold, and no-retry language;
- stale temporary admission scripts are absent.

Label this as `AD_HOC_OR_CANONICAL=ad-hoc targeted`; it is not canonical suite green.