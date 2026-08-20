# No-repost repair admission to exact-head PR closeout

Use this reference when an authorized Prismatic repair task reaches PR after a messy but bounded event admission: setup drift, a persisted-but-unconsumed event, no-POST recovery, producer completion, local reproduction, independent exact-head review, and PR creation.

## Sequence

1. **Freeze and review the task before admission.**
   - Use a schema-valid task ID.
   - Copy byte-identical task envelopes into the bus/worktree only after deployed schema validation.
   - Require independent task-contract `CLEAN/PASS` before authenticated event posting.

2. **Admit exactly once.**
   - Build one-shot admission from deployed private schemas, not stale scripts.
   - Include required route context/idempotency headers.
   - Parse deployed response nesting.
   - Restore policy/control/config bytes in `finally`.

3. **If admission persisted but consumer failed, recover the existing event.**
   - Do not repost.
   - Prove `EVENT_COUNT=1` and pending/unclaimed state for the exact task/event key.
   - Use a no-POST recovery consumer with deployed CLI flags and temporary policy/config, restored in `finally`.
   - Record `REPOSTED=false` and the successful claim/launch attempt.

4. **Producer closeout.**
   - Attach receipt-bound passive wait; avoid polling, inactivity kills, or guessed result paths.
   - On terminal exit, reconcile process cleanup, harness/result artifacts, exact commit/tree, changed paths, and receipt/lifecycle state.
   - Local reproduction must run from an immutable archive and should include direct adversarial behavior probes, not only nominal tests.

5. **Independent review before PR.**
   - If local reproduction passes but an adversarial bypass appears, freeze a new repair prompt and do not PR.
   - Only after fresh independent exact-head `CLEAN/PASS`, push the exact reviewed branch.

6. **PR creation proof.**
   - Fetch/bind `origin/main` immediately before push/PR.
   - Prove `HEAD`, `TREE`, merge-base, ahead/behind, changed paths, `git diff --check`, and tracked cleanliness.
   - After PR creation, read back live `headRefOid` and verify it equals the independently reviewed commit.
   - Treat untracked task-envelope files separately from tracked code cleanliness.

## Minimum proof packet

```text
TASK_ID=<schema-valid id>
TASK_REVIEW=<deleg id>:CLEAN/PASS
EVENT_COUNT=1
REPOSTED=false
CLAIM_ATTEMPT=<n>
PRODUCER_EXIT=0
CANDIDATE=<sha>
TREE=<tree>
LOCAL_IMMUTABLE_REPRODUCTION=PASS
INDEPENDENT_EXACT_HEAD_REVIEW=<deleg id>:CLEAN/PASS
REMOTE_HEAD_MATCH=true
PR_NUMBER=<n>
PR_STATE=OPEN
MERGED=false
AD_HOC_OR_CANONICAL=ad-hoc targeted exact-PR-head readback
NOT_CLAIMING=merge, deployment, GitHub candidate code execution, Linear write, cron/timer mutation, or canonical full-suite green
```

## Pitfalls

- A local transaction wrapper can fail after the durable admission row exists. The next action is DB reconciliation and no-POST recovery, not another POST.
- Consumer enum/column names drift. Prove live outbox/claim/lifecycle state with observed schema names.
- Local reproduction green is not enough if a direct adversarial probe finds a bypass; freeze the blocker and require a new repair/re-review.
- PR creation is still not merge authorization. The next gate is explicit merge authorization plus live PR-head recheck.