# AGY cap-slot ownership containment after one-shot admission launch

## Trigger

Use this reference when reviewing or executing a Prismatic AGY task-admission launch, especially cap-1 / no-overlap admission flows.

## Durable lesson

A successful task-admission POST and consumer `processed` result is not enough to claim the cap-1 runtime is safe. After the launcher returns, verify the active slot's owner identity still protects the live producer.

Observed class of failure:

1. Dispatch writes `active-slots/slot-0.json` with the dispatch process PID/start-ticks.
2. The actual producer continues under a durable tmux anchor/pane and child process tree.
3. The short-lived dispatch PID exits.
4. `_claim_slot()` decides slot activity only by the recorded owner PID/start-ticks.
5. A later dispatch can treat the slot as stale, unlink/reclaim it, and violate the effective cap-1/no-overlap invariant while the producer is still live.

Do **not** encode this as “AGY slots are broken” globally. Treat it as a verification/containment pattern for launches whose slot owner identity is not bound to the durable live process.

## Required post-launch proof packet

After any reviewed one-shot admission launch, capture all of these before claiming launch safety:

```text
EVENT_ID=<task-admission id>
HTTP_STATUS=201
REPLAYED=false
CLAIM_ID=<claim id>
CONSUMER_STATUS=processed
LIFECYCLE=claimed->validated->launch_started->launched
RUN_ID=<runtime id>
HARNESS_STATE=<running|review_pending|...>
PRODUCER_COMPLETED=<true|false>
ACTIVITY_CLASSIFICATION=<working|...>
PROCESS_ALIVE=<true|false>
ACTIVE_SLOT_PATH=<path>
SLOT_RUN_ID=<run id from slot>
SLOT_OWNER_PID=<pid from slot>
SLOT_OWNER_START_TICKS=<ticks from slot>
SLOT_OWNER_ALIVE=<true|false from /proc start ticks>
DURABLE_PANE_PID=<pid from harness-run>
DURABLE_PANE_ALIVE=<true|false from /proc start ticks>
LIVE_CHILDREN=<bounded ps/process-tree proof>
SELECTABLE_OUTBOX=<deployed selector, not generic processed_at null>
WRITER_LEASE_COUNT=<count>
SECURE_WINDOW_ROOT_EMPTY=<true|false if applicable>
```

## Selector discipline

When proving no remaining selectable outbox work, use the deployed consumer's actual selection predicate. Do not substitute generic `processed_at IS NULL`; historical or non-selectable rows can make that count misleading.

## Containment rule

If the slot owner PID/start-ticks are dead or mismatched while the durable tmux/pane/child producer remains live:

1. **Do not dispatch another admission.**
2. **Do not run another ordinary consumer invocation.**
3. **Do not mutate the slot file as an ad-hoc fix.**
4. Preserve the live producer.
5. Freeze a no-overlap hold in the handoff/current state.
6. Request or run a read-only independent audit of the cap-slot ownership contract.
7. Resume admission only after an exact correction/recovery path is reviewed.

### Audit outcome: live pane guard can clear the hold

The same symptom can be **NOT_BLOCKER** if the deployed slot-liveness code checks the durable pane PID/start-ticks before consulting the short-lived dispatcher owner. In that topology, the apparent dead owner is only stale metadata; the live pane identity still prevents slot reclaim/overlap.

Before escalating to a repair, prove the actual `_slot_is_active()` / claim path ordering:

```text
LIVE_PANE_CHECK_BEFORE_OWNER=<true|false>
DURABLE_PANE_PID=<pid from harness-run/launch-receipt>
DURABLE_PANE_ALIVE_DURING_RUN=<true|false>
OWNER_PID_ALIVE=<true|false>
SLOT_RECLAIMABLE_WHILE_PANE_LIVE=<true|false>
PRODUCER_COMPLETED_NATURALLY=<true|false>
PROCESS_TREE_CLEANUP_VERIFIED=<true|false>
ACTIVE_SLOT_RELEASED=<true|false>
AUDIT_DECISION=<NOT_BLOCKER|BLOCKER>
```

If `LIVE_PANE_CHECK_BEFORE_OWNER=true`, pane identity stayed alive during the run, producer exits `0`, process-tree cleanup is verified, and active slot count returns to zero, classify the episode as **contained / not blocker**. Still consider a regression test for "dead dispatcher owner + live durable pane still protects cap-1" because it is a valuable future guard.

## Minimum audit questions

The independent audit should answer:

- Does `_claim_slot()` use only `owner_pid`/`owner_start_ticks` to determine liveness?
- Is the recorded owner the durable process or a short-lived dispatch process?
- Is there any other deployed guard that prevents overlap if the slot is reclaimed?
- What is the minimum safe repair: slot payload owner binding, launch-time slot transfer, reconciler behavior, or consumer/admission fencing?
- What recovery is safe for the already-running producer without killing or overlapping it?

## Handoff wording

Use a boundary like:

```text
CAP_SLOT_CONCERN=slot_owner_pid_exited_while_tmux_pane_and_child_tree_live
CONTAINMENT=no_new_admission_or_dispatch;do_not_mutate_slot;preserve_current_producer
NOT_CLAIMING=producer_completion,repair_correctness,candidate_acceptance,canonical_suite,PR,push,merge,deployment,Linear_mutation,or_parent_completion
```
