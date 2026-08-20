# Lane-blocked WIP verification nudge pattern (GRO-4012, 2026-07)

## Trigger

Hermes issues a post-response verification nudge after code was edited in a temporary task worktree, but the implementation is intentionally not pushed/finalized because a lane guard blocked the required file path.

Example shape:

- Changed paths include implementation, docs, and `/tmp/issue-batches/<ISSUE>_RESULT.md`.
- The relevant canonical command is named explicitly, usually `npm run build`.
- Prior verification may be present but marked stale/unverified by the platform.
- The task remains blocked/rerouted because safe-push rejected an out-of-lane file.

## Correct response

Treat this as verification-only scope control:

1. Do **not** resume implementation or try to bypass the lane guard.
2. Run the exact named canonical command from the changed worktree, even if it passed minutes ago.
3. If dependencies are absent in the temp worktree, restore them with the repo's normal install command (`npm ci` when `package-lock.json` exists), then rerun the canonical command. Capture this as setup for the verification run, not as a durable tool failure.
4. Also run a fresh `/tmp/hermes-verify-*` artifact/acceptance verifier that directly inspects the changed files and RESULT marker; remove it before reporting.
5. If the RESULT file is one of the changed paths, update it with the fresh verification evidence before the artifact verifier, so the verifier can assert the RESULT evidence is current.
6. Final response should be short: what passed now, what remains blocked, and the blocker. Do not claim the task is green if the lane guard still blocks push.

## Evidence to report

- `python3 -m py_compile <changed-python-file>` when Python was edited.
- Exact canonical command, e.g. `npm run build`, with summary of build/postbuild output.
- `/tmp/hermes-verify-*` assertions and cleanup.
- Remaining lane blocker, e.g. `reports/server.py` outside Ned's allowed lane.

## Pitfall

A passing build does not override a safe-push lane violation. The correct final state is `verified locally; blocked/rerouted`, not `done`, and the issue should stay out of false-green states.