# Dirty recovery admission compatibility

Use this when a Prismatic recovery contract preserves an existing dirty checkpoint and the next tempting move is to freeze an admission envelope or launch a producer.

## Lesson

A reviewed dirty-checkpoint recovery contract is not automatically admissible through the deployed task-admission control plane. If deployed admission requires a clean tracked status, the conflict must be discovered before event POST or consumer invocation.

## Required sequence

1. **Bind the accepted recovery contract first**
   - exact contract path and SHA256;
   - exact review handle and verdict;
   - byte-identical bus/worktree task copies, if created;
   - exact worktree HEAD, tree, tracked diff digest, and dirty path set.

2. **Inspect deployed admission behavior at the deployed release, not a dev checkout**
   - source path and SHA256;
   - literal clean/dirty status validation behavior;
   - whether validation happens before task-file hash/launch.

3. **Run a zero-mutation compatibility preflight**
   - disposable SQLite/database only;
   - narrowed temporary policy if needed;
   - no live POST, no consumer, no producer;
   - verify the generated body/idempotency matches the reviewed task fields;
   - expected safe blocker for clean-only admission is `TaskAdmissionError("worktree_dirty", 422)`.

4. **If dirty status is rejected, freeze a blocker rather than an envelope**
   - state that no truthful envelope can satisfy both preserving dirty bytes and deployed clean-worktree admission;
   - record `EVENT_COUNT=0` and `ENVELOPE_FROZEN=false`;
   - preserve dirty checkpoint bytes; no reset/clean/stash/replay/copy-as-if-clean.

5. **Offer only separately authorized resolution classes**
   - exact-byte operator commit workflow exception, followed by reproduction and independent exact-head review; or
   - versioned recovery-only dirty-checkpoint admission support bound to HEAD/tree/status/diff/path/blob identities, independently reviewed and deployed without weakening ordinary admission.

## Pitfalls

- Do not treat a CLEAN/PASS recovery contract as authorization to bypass deployed admission.
- Do not create a plausible envelope after a disposable preflight proves deployed `worktree_dirty` rejection.
- Do not mutate the dirty checkpoint to satisfy clean-worktree admission unless Michael explicitly authorizes a workflow exception.
- Do not call a compatibility blocker a candidate, completion, or canonical green.

## Proof packet fields

```text
COMMAND=<deployed source inspection + disposable admission preflight>
RESULT=BLOCKED
LOG=/tmp/hermes-verify-<task>-dirty-admission-blocker.log
SCOPE=<task id and dirty recovery contract>
AD_HOC_OR_CANONICAL=ad-hoc targeted deployed compatibility preflight
NOT_CLAIMING=resolution selection,envelope,event,producer,source edit,commit,candidate,canonical green,PR,merge,deployment/restart,cron/timer mutation,production DB mutation,or Linear write
MARKER=<TASK>_DEPLOYED_DIRTY_ADMISSION_BLOCKER_REVIEW_PENDING
```
