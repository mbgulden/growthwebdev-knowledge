# Exact-base coordination clone and split-review admission pattern

Use when the durable deployed release is the only checkout at the accepted base, but mutating that checkout would weaken runtime durability.

## Trigger

- The prior worktree registry or dev checkout is stale relative to the reviewed/deployed base.
- The immutable live release has the exact commit/tree needed for admission proof.
- A task is ready for event admission only after exact launcher/envelope review.

## Pattern

1. **Do not use the immutable release as the mutable task worktree.** Preserve live release Git metadata and runtime checkout untouched.
2. **Create or use a separate non-runtime coordination clone** at the accepted remote/base, then make the task worktree from that clone.
3. **Bind base identity before task materialization:** HEAD, tree, branch/worktree path, tracked status, expected untracked task file, remote-branch absence/presence, and task-copy SHA.
4. **Materialize byte-identical task copies** in the bus task path and worktree `.prismatic-task/…` path. Verify both match the accepted contract bytes.
5. **Split review surfaces:**
   - admission envelope: finite JSON template, idempotency, late-bound fields, non-repost/fail-closed semantics, and zero live state;
   - one-shot launcher: runtime controls, POST/consumer/producer sequence, `finally` restoration, receipt truth, no secret emission, and exact live gateway process binding when the launcher posts to a service.
6. **If posting through a deployed gateway, prove the listener is the expected release before controls open.** Check `systemctl` active state and `MainPID`, then resolve `/proc/<pid>/exe`, `/proc/<pid>/cwd`, and `/proc/<pid>/cmdline` to the expected versioned venv, immutable release, and gateway command. Also run a bounded health request against the same host/port and verify a fresh import resolves to the exact deployed module path.
7. **Dispatch parallel independent reviews only after local proof** shows the envelope parses through the deployed parser and the launcher preflight exits cleanly with zero live mutation.
8. **Do not execute until both exact artifacts return CLEAN/PASS.** A clean contract review alone is not enough.

## Local proof requirements

- Deployed source hash and parser behavior from the immutable release, not guessed from dev.
- Worktree exact `HEAD`, `HEAD^{tree}`, tracked-clean status, and expected untracked task file.
- One JSON block and one late-bound timestamp sentinel in the envelope.
- Stable idempotency digest excludes `created_at`; only the timestamp is late-bound.
- Live task admissions/outbox/claims/lifecycle, writer lease, selectable outbox, and active slots are zero before execution.
- A post-verifier mutation check for frozen envelope, launcher, contract, and handoff files.

## Pitfalls

- A launcher that validates expected files/imports can still be blocked if it does not prove the **actual listener process**. File-level validation does not rule out a stale or different process bound to the POST port. Minimum repair: preserve the blocked launcher bytes, create a superseding version, bind `MainPID` through `/proc` exe/cwd/cmdline, run bounded health, prove exact module import path, rerun zero-mutation preflight, and request fresh independent review of both launcher and envelope lineage.
- If a verifier imports the deployed parser, inspect the actual return shape. Some deployed parsers return dictionaries, not dataclass/object attributes; a failure like `AttributeError: 'dict' object has no attribute ...` is verifier setup, not product incompatibility. Patch only the disposable verifier and rerun the full proof.
- Watch task-specific launcher derivation carefully. Copied launchers often retain the previous task’s launcher path or producer binding; assert exact task/producer/private launcher path in preflight.
- Do not classify stale registry state as permission to force a task onto stale `origin/main`, reset the release checkout, or create a fallback admission path.
