---
name: prismatic-admission-launcher-review
description: "Review and repair Prismatic one-shot admission launchers/envelopes safely: preserve blocked checkpoints, bind exact launcher+envelope hashes, require bounded subprocesses, socket-owner health proof, zero-mutation preflight, and independent exact-byte review before execution."
---

# prismatic-admission-launcher-review

## New/recently hardened review rule

- **Hash gates must run before imports, not merely before execution.** For one-shot admission launchers, block packages where frozen-input verification occurs only after `sys.path` changes, deployed-module imports, config reads, report/temp creation, DB reads, or wrapper construction. Use the bootstrap-before-import pattern and adversarial marker proof in `references/bootstrap-before-import-hash-gate.md`.

## Trigger

Use this skill when coordinating, repairing, or reviewing a Prismatic one-shot task-admission launcher or its frozen admission envelope.

Common signals:

- An envelope is `CLEAN/PASS` but the bound launcher is blocked.
- A launcher performs live gateway/process/socket/health checks before opening temporary credentials or controls.
- A one-shot POST/consumer/cap-1 producer lane is being prepared.
- Multiple Vn artifacts must be preserved while a corrected Vn+1 is created.

## Core procedure

1. **Preserve blocked bytes before repair**
   - Copy the blocked launcher to a versioned path such as `*_vN_blocked.py` before editing the live candidate.
   - Keep every frozen envelope version immutable.
   - Record blocked launcher hash, envelope hash, delegation/review id, and first blocking defect.

2. **Repair narrowly**
   - Patch only the defect called out by the review.
   - Do not rewrite the payload, task id, idempotency key, base commit/tree, producer identity, or JSON template unless the review explicitly requires it.

3. **Run local proof before external review**
   - Compile/lint/format the launcher.
   - Run `--preflight-only` and require `PASS_PREFLIGHT_ZERO_MUTATION`.
   - Produce `/tmp/hermes-verify-*` proof that checks exact hashes, zero rows/leases/outbox/slots, and no post-verifier mutation.

4. **Freeze a superseding envelope**
   - Bind previous envelope and launcher hashes/results.
   - Bind the new launcher hash and fresh preflight report path/hash.
   - State exactly what changed and what remained byte-identical.
   - Keep status as review-pending until both exact envelope and exact launcher pass.

5. **Launch independent exact-byte reviews**
   - One reviewer should verify the envelope/live state/lineage.
   - One adversarial reviewer should verify launcher behavior and remaining safety pitfalls.
   - Do not execute the one-shot lane until both return `CLEAN/PASS` at exact bytes.

## Required launcher safety checks

- Live systemd gateway is active and `MainPID` is nonzero.
- `/proc/<pid>/exe`, `/proc/<pid>/cwd`, and `/proc/<pid>/cmdline` match the expected runtime exactly.
- `/proc/net/tcp` and `/proc/net/tcp6` together expose exactly one expected listener.
- Listener inode is owned by an fd under the exact `MainPID`.
- Health check is bounded and returns accepted healthy status.
- After health, recheck `MainPID`, process identity, listener uniqueness/inode, and fd ownership; require no change.
- Live DB rows, writer lease, selectable outbox, and active producer slots are zero before opening controls.
- **Resample zero state immediately before opening controls.** An earlier all-zero snapshot is not enough: after all identity/task/process checks and immediately before token generation or any credential/policy/control write, call the launcher’s canonical count helper again, store the fresh result, and fail closed if any task/outbox/claim/lifecycle/writer-lease/selectable-outbox value is nonzero.
- Exactly one credential/policy window, one POST site, one ordinary consumer invocation, and one cap-1 producer path exist.

## Race-condition pitfall: stale zero snapshots

When a launcher performs many live checks between its first event-log snapshot and credential/control mutation, the initial zero-state proof can become stale. Treat a reviewer flag on this as a real blocker even if the broader launcher review passed. The stricter first-blocker wins: preserve the blocked envelope/launcher hash, patch the launcher narrowly to add a fresh `event_counts()` gate immediately before token/control opening, rerun zero-mutation preflight, and freeze a new envelope bound to the corrected launcher and fresh receipt.

## Frozen-input execution gate pitfall

An envelope can bind many files while the launcher rechecks only one at execution time. Treat this as a blocker: review-time hashes do not prevent execution-time drift. Every envelope-bound input that affects admission authority must be checked by the launcher during preflight and again immediately before opening any policy/control/token/credential window.

Minimum gate coverage:

- policy file hash and restrictive mode;
- control-auth file hash and restrictive mode;
- private/source AGY config hash and restrictive mode;
- dynamically loaded task-admission schema hash, restrictive mode, regular-file type, and no-symlink;
- `task_admission.py` hash, restrictive mode, regular-file type, and no-symlink;
- `task_admission_consumer.py` hash, restrictive mode, regular-file type, and no-symlink;
- `task_admission_agy_launcher.py` hash, restrictive mode, regular-file type, and no-symlink.

The repair proof should failure-inject drift for each frozen input independently, using temporary copies or injected constants rather than mutating live files, and show each drift blocks fail-closed. Preserve the blocked Vn launcher/envelope and freeze a Vn+1 envelope with the corrected launcher hash, fresh preflight hash, and drift-injection proof hash.

## Bounded external-command rule

One-shot admission launchers must not contain unbounded external commands. Every `subprocess.run(...)` that can block the lane needs an explicit timeout and stable, non-secret fail-closed handling.

For Git probes, use a helper pattern:

```python
def bounded_git(command: list[str], timeout_code: str) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            text=True,
            capture_output=True,
            timeout=10,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(timeout_code) from exc
```

Use distinct error codes such as:

- `live_worktree_head_timeout`
- `live_worktree_tree_timeout`
- `live_worktree_status_timeout`

## Reporting contract

Report `PARTIAL` while review is running, even if local proof passes. Lead with:

1. Problem
2. Changed
3. Why it matters
4. State
5. Next move
6. IDs/hashes/logs

Always include boundaries: not claiming event POST, consumer, producer, candidate, PR, merge, or deployment until exact envelope+launcher reviews are clean and execution proof exists.

## References

- `references/stale-zero-snapshot-race.md` — concrete reviewer-blocker pattern for stale event-log zero snapshots before credential/control opening.
- `references/frozen-input-execution-gates.md` — concrete Vn→Vn+1 repair pattern when an envelope binds multiple config/source files but the launcher rechecks only one at execution time.

## Verification

A ready-to-execute admission package has:

- immutable blocked-version artifacts,
- fresh launcher hash,
- fresh envelope hash,
- fresh zero-mutation preflight hash,
- `/tmp/hermes-verify-*` local proof with no post-verifier mutation,
- independent `CLEAN/PASS` for both exact envelope and exact launcher,
- explicit boundary that execution has not yet happened unless the one-shot lane was actually run and receipt-bound.
