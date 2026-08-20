---
name: prismatic-admission-control-gates
description: Verify Prismatic task-admission compatibility before freezing envelopes or launching producers, especially for dirty-checkpoint recovery, idempotency, policy, and deployed-release validation gates.
---

# Prismatic Admission Control Gates

Use this skill when a Prismatic task is about to move from reviewed contract/task materialization into event admission, consumer invocation, or producer launch. Also use it when a pre-admission contract is being versioned under independent review and must remain zero-authority until clean.

## Core rule

A reviewed task contract is not automatically admissible. Before freezing an envelope or posting an event, prove the **deployed** admission control plane accepts the exact task shape without weakening trust boundaries or mutating live state.

For pre-admission contracts, a blocked review should create a new versioned artifact rather than overwrite or patch in place. Preserve each blocked version with SHA/reviewer/blocker, make the successor's minimum correction, freeze exact bytes, and run a fresh full review while keeping source/task/event/producer/PR/merge/deploy/Linear authority at zero.

## Standard sequence

1. **Bind the reviewed task**
   - task/contract path and SHA256;
   - independent review handle and verdict;
   - exact task-copy identities if bus/worktree copies exist;
   - worktree HEAD/tree and intended producer identity;
   - whether the worktree must remain clean or intentionally dirty.

2. **Inspect deployed release behavior**
   - use the durable deployed runtime checkout/release, not a mutable dev checkout;
   - record source path and source SHA256;
   - identify schema, policy, Git, idempotency, task-file hash, and status checks that run before admission/launch.

3. **Run zero-mutation preflight first**
   - disposable database only;
   - temporary narrowed policy only if explicitly scoped and restored/removed;
   - no live POST, consumer, producer, source edit, commit, reset, stash, deploy, or Linear write;
   - verify failure mode is the expected gate if blocked.

4. **Only freeze an envelope after compatibility passes**
   - if deployed validation blocks, freeze a blocker artifact instead;
   - include `EVENT_COUNT=0`, `ENVELOPE_FROZEN=false`, and exact non-claims;
   - dispatch fresh exact-artifact review before asking Michael for a resolution choice.

5. **If the only exact base is the immutable release, create a non-runtime coordination checkout**
   - do not mutate the live release Git metadata or make the durable runtime depend on a mutable task worktree;
   - create/use a separate coordination clone at the accepted base and make the task branch/worktree there;
   - bind HEAD, tree, tracked-clean status, expected untracked task file, remote-branch state, and byte-identical bus/worktree task copies before freezing the envelope.

6. **Review envelope and launcher as separate exact artifacts before execution**
   - a clean contract review is not enough for admission;
   - envelope review covers finite JSON, late-bound timestamp, idempotency, no-repost/fail-closed semantics, and zero live state;
   - launcher review covers runtime controls, one POST, one ordinary consumer, one cap-1 producer, `finally` restoration, receipt truth, and no secret emission;
   - when launcher safety depends on a deployed gateway, prove the **actual listener process**, not just expected files on disk: bind `systemctl MainPID` through `/proc/<pid>/exe`, `/proc/<pid>/cwd`, and `/proc/<pid>/cmdline`, require bounded health, and prove the imported module path resolves to the exact deployed source before credentials/policy open;
   - execute only after both exact artifact reviews return `CLEAN/PASS`.

7. **After Michael authorizes execution, keep the lane single-use and receipt-bound**
   - treat authorization as scoped to the exact pending gate: one authenticated event POST, one ordinary consumer invocation, and one cap-1 producer launch unless Michael says otherwise;
   - run the accepted launcher’s built-in preflight first, then execute once; do not retry after any durable admission row exists;
   - prove HTTP status, replay flag, consumer status/attempt, lifecycle rows, writer leases, selectable outbox, and temporary-control restoration;
   - bind the running producer to the launch receipt with `pane_pid`/start-tick identity and active-slot count; active-slot `owner_pid` may be a supervisor/harness PID, so bind slots by `run_id` and wait on the receipt `pane_pid`;
   - if waiting for completion, attach only a passive receipt-bound wait such as `tail --pid=<receipt_pid> -f /dev/null` with no polling, no deadline, no inactivity kill, and notify-on-exit.

## Dirty-checkpoint recovery pitfall

If a recovery contract requires preserving dirty bytes but deployed admission rejects non-empty tracked status (`worktree_dirty` / 422), there is no truthful clean envelope. Do not clean/replay/reset/stash/copy to satisfy admission unless Michael separately authorizes an exact-byte workflow exception. Do not bypass deployed validation locally.

Before asking for that authorization, freeze and review two separate artifacts:

1. a compatibility blocker proving the deployed release rejects the exact dirty worktree in disposable storage, with no live POST or DB mutation; and
2. an operator-exception contract that would create at most one exact-byte local descendant commit from the already-reviewed dirty bytes, excluding operational metadata, then stop for fresh exact-head review.

The exception artifact is not authorization. Keep `authorization=not_granted`, future event count zero, and no commit until Michael explicitly approves the exact option after reviews return clean.

Bounded resolution classes only:

- exact-byte operator commit exception, followed by exact-head reproduction and independent review; or
- versioned, reviewed, deployed recovery-only dirty-checkpoint admission support bound to HEAD/tree/status/diff/path/blob identities without weakening ordinary clean-worktree admission.

## Clean-worktree envelope preflight pitfalls

When the task is tracked-clean and should be admissible through the ordinary deployed path:

- **Temporary policy files must satisfy deployed safety checks.** Create disposable preflight directories owner-only (`0700`) and temporary policy files owner-only (`0600`). A mode error such as `admission_policy_unavailable` before task validation is a verifier setup failure, not task incompatibility. Correct the setup and rerun the entire zero-mutation preflight from the beginning.
- **Do not guess deployed schema, constructor, or policy shapes.** If preflight fails before meaningful product validation, inspect the deployed release source and the last proven launcher/preflight pattern before retrying. Bind to the actual constructor signature, required JSON fields, allowed/forbidden fields, status/version values, policy key names, and private validation call shape. Preserve setup-only failures in the proof log, but do not classify them as task incompatibility.
- **Separate idempotency identity from freshness.** Derive the stable idempotency key from frozen task/base/tree/task-hash/producer/worktree identity, not from `created_at`. In the envelope JSON, make `created_at` the only late-bound field; substitute it immediately before deployed parser/Git/task validation and POST, within the freshness window.
- **Freeze only after validating the exact template.** Extract the JSON block from the frozen envelope, prove there is exactly one timestamp sentinel, substitute a current UTC whole-second timestamp, and run deployed validation on that exact payload using a disposable DB/policy before dispatching envelope review.
- **For checkpoint-first recovery, keep admission clean and materialize dirty bytes only as proof.** If the producer must start from preserved dirty-checkpoint bytes but deployed admission requires a clean tracked worktree, create the dedicated recovery worktree clean at the exact base, prove the checkpoint patch applies and yields exact endpoint blobs in a disposable archive, and require the producer contract to apply/prove that patch as its first tracked mutation after launch. Do not dirty the admitted worktree before preflight/POST.
- **Exact-base coordination clone beats mutable release work.** If the accepted base exists only in an immutable deployed release and the historical worktree registry/dev clone is stale, do not force the task onto stale `origin/main` and do not mutate the release checkout. Create a separate non-runtime coordination clone/worktree at the exact base, then prove task copies, tracked status, remote branch state, and live zero-state from there.
- **Verifier setup failures are not product blockers.** When a local proof script reaches deployed code but assumes the wrong parser return shape, config shape, copied launcher binding, or chat-safe literal rendering, patch only the disposable verifier/launcher derivation, preserve the failed log, and rerun the complete proof. If masking turns an authorization literal into `***` or breaks a heredoc/status string, parse machine fields as booleans and use neutral proof labels rather than changing frozen artifact bytes. Do not reclassify the task contract as blocked unless deployed validation itself fails after setup is corrected.
- **Copied one-shot launchers need task-specific binding assertions.** Assert the exact private launcher path, producer identity, task ID, task-file hash, and worktree path in preflight; a retained previous-task value is a launcher defect, not an authorization to proceed.
- **Bootstrap verification must precede imports and cover schema/modes, not only hashes.** If the launcher imports or uses frozen deployed modules before hash verification, drifted import-time code could run before the mismatch is detected. Keep the top of the launcher self-contained: constants plus `verify_frozen_inputs()`, call it before any `sys.path` mutation/import/config/credential/control/network action, and recheck as the first line of `run()` plus every authority transition. Freeze every admission-affecting input, including dynamically loaded schema files, deployed Python files, private source config, production policy, and control authorization; bind path, SHA256, exact mode, regular-file type, and no-symlink. Failure-inject each frozen input, including all exact-mode drifts, dynamic-schema byte drift, and an import-time-marker drift, then remove proof-created `.pyc` artifacts before freezing. See `references/bootstrap-safe-repair-admission-envelopes.md`.
- **Launcher review must bind the actual live gateway process.** A launcher can still be unsafe if it only verifies expected release files/imports while the POST target is served by a different process, cwd, venv, or stale listener. Immediately before opening temporary controls, require `ActiveState=active`, resolve `MainPID` via `/proc`, compare executable/cwd/exact command line to the expected release + versioned venv, call bounded health on the POST target, and separately prove imported module path equals the exact deployed source. If this is missing, preserve the blocked launcher bytes, supersede with a V2 artifact, and rerun zero-mutation preflight and exact independent reviews.
- **Process identity and health are not enough unless the socket is bound to the same PID.** After proving `systemctl MainPID`, parse `/proc/net/tcp` and `/proc/net/tcp6`, require exactly one port listener for the POST port, extract its socket inode, and verify that inode is present under `/proc/<MainPID>/fd`. Reject multiple listeners/reuse-port ambiguity. After bounded health, repeat MainPID/exe/cwd/cmdline, listener uniqueness/inode, and fd ownership, and require PID/inode stability before opening controls. See `references/gateway-listener-ownership-gate.md`.
- **Validate execution identity before treating semantic review as executable.** A contract can receive semantic `CLEAN/PASS` but still be blocked by deployed admission constraints. Before task materialization or envelope freeze, check the reserved `TASK_ID` against the deployed schema pattern/length, bind exact bus/worktree task-copy paths, and prove idempotency preimage fields, producer identity, and payload fields are admissible. If identity is inadmissible, preserve the semantic-pass version and create a new version with only the identity correction, then run fresh full review.
- **Zero live state remains mandatory.** Confirm task admissions/outbox/claims/lifecycle, writer leases, and selectable outbox are zero before and after preflight. The envelope remains descriptive until independently reviewed and separately authorized.
- **Preflight stdout is not always the final receipt.** If a launcher writes a report directory and appends restoration/cleanup truth in `finally`, verify the durable `final-result.json` rather than only the last stdout JSON. Treat missing restoration fields on stdout as an instrumentation boundary, then read the final receipt before rerunning or declaring failure.
- **Empty namespace directories are not active controls.** A leftover owner-only (`0700`) temporary namespace/root directory is acceptable only if file search proves it contains no credential, policy, launcher, or window files. Report it as an inert empty directory, not as `TEMP_CONFIGS_REMOVED=false`.
- **Envelope safety includes upstream prerequisite receipts.** If an envelope relies on an earlier checkpoint/exact-head/contract-integrity review, bind the durable receipt path + SHA, verdict, exact scope, HEAD/tree/parent if relevant, and explicit non-claims inside the frozen artifact. A quoted `CLEAN/PASS` from chat is not enough, and an integrity-only checkpoint review must not be laundered into implementation acceptance. If this is the only blocker, preserve the blocked envelope and create a successor whose delta is limited to version/status history, prerequisite bindings, and marker; prove launcher/payload/preflight identities are unchanged before fresh full review. See `references/pre-admission-prerequisite-receipt-bindings.md`.

## Proof packet

```text
COMMAND=<deployed source inspection + disposable admission preflight>
RESULT=<PASS|BLOCKED|FAIL>
LOG=/tmp/hermes-verify-<task>-admission-preflight.log
SCOPE=<task id + contract/review identity>
AD_HOC_OR_CANONICAL=ad-hoc targeted deployed compatibility preflight
NOT_CLAIMING=<resolution/envelope/event/producer/source edit/commit/candidate/canonical green/PR/merge/deploy/cron/DB/Linear non-claims>
MARKER=<TASK>_ADMISSION_COMPATIBILITY_<STATE>
```

## References

- `references/dirty-recovery-admission-compatibility.md` — detailed recipe for reviewed dirty-checkpoint recovery blocked by deployed clean-worktree admission.
- `references/clean-envelope-late-bound-preflight.md` — tracked-clean envelope pattern: owner-only disposable policy, `created_at` as sole late-bound field, deployed template validation, and zero-live-state proof.
- `references/cap1-event-launch-passive-wait.md` — post-authorization single-use event/consumer/cap-1 producer launch proof and receipt-bound passive wait pattern.
- `references/checkpoint-first-clean-admission.md` — dirty-checkpoint recovery pattern that keeps deployed admission clean, proves checkpoint bytes in a disposable archive, and makes patch application the producer’s first tracked mutation.
- `references/exact-base-coordination-clone-and-split-review.md` — exact-base admission pattern when the live immutable release is the only good checkout: create a non-runtime coordination clone, bind task copies, and split envelope/launcher review before one-time execution.
- `references/gateway-listener-ownership-gate.md` — launcher review pattern for binding systemd `MainPID` to the actual port listener inode and rechecking identity after health before opening controls.
- `references/versioned-pre-admission-contract-review.md` — versioned contract review pattern for preserving blocked artifacts, freezing successor bytes, and keeping zero authority before task/event admission.
- `references/deployed-identity-before-materialization.md` — semantic-pass contract pitfall: validate future task identity and envelope fields against the deployed schema before task-copy materialization.
- `references/zero-mutation-preflight-final-receipts.md` — verify durable `final-result.json` for cleanup/restoration truth and distinguish inert empty temp directories from active controls.
- `references/pre-admission-prerequisite-receipt-bindings.md` — bind upstream checkpoint/exact-head/contract review receipts into frozen envelopes so semantic safety is not mistaken for executable admission authority.
- `references/one-shot-launcher-hardening.md` — derived one-shot launcher hardening: bare invocation fail-closed, no bearer on redirects, exact task-specific binding assertions, authority-site counts, final-receipt verification, and review-before-`--execute` discipline.
- `references/bootstrap-safe-repair-admission-envelopes.md` — repair admission envelope pattern after a blocked exact-head candidate: bootstrap-before-import hash gates, internal repair event identity, disposable policy boundary, zero-state proof, and explicit one-event authorization separation.

## Verification

The final report names the deployed release/source hash, task/contract SHA, preflight result, live event count, envelope state, and exact next authorization gate. If compatibility did not pass, no envelope/event/producer claim is made.
