# Runtime supervisor filesystem transport convergence

Use this reference when continuing Prismatic runtime topology convergence after the runtime-services manifest slice is merged and immutable-release verified.

## Trigger

A live AGY supervisor/profile script contains behavior needed by production, but current-main source still has stale launch/relaunch transport such as signed stdin, HMAC payload signing, or default-secret paths. A read-only semantic review may classify the live behavior as safe to port, but that is not deployment authorization.

## Queue-to-active discipline

1. While another producer is active, keep this as `QUEUED_NOT_DISPATCHED` with `BASE_SHA=DEFER_UNTIL_PREDECESSOR_CLOSES`.
2. Independently reproduce the semantic finding before queueing it: compare live/profile-script behavior with current-main source and verify focused tests still pass.
3. After the predecessor PR merges and its immutable merge-SHA release passes, bind a fresh base SHA, clean workspace, branch, exact task file, and task hash.
4. Keep cap 1: one bounded source producer only. Read-only reviewers may run only if they cannot edit, dispatch, mutate Linear/GitHub, deploy, or restart.

## Exact bounded scope

Default first slice scope:

- `scripts/agy_sandbox_event_supervisor.py`
- `tests/test_agy_sandbox_event_supervisor_control_plane.py`

No live profile path, systemd unit, runtime checkout, state DB, sandbox directory, env file, or service action is in scope.

## Required source behavior

- Initial launch and relaunch must use the same filesystem-scoped command shape: `--dir <sandbox> --print <bounded prompt>`.
- Do not send writable stdin payloads to the child AGY CLI.
- Remove stale signed-stdin/HMAC/default-secret transport from the source path under repair.
- Preserve `agy_cli_child_env()` and the split between supervisor HOME/state and child AGY auth HOME.
- Preserve exact-task binding, repair-seed handling, and fail-closed completion semantics. Transport cleanup must not make abandoned/error/incomplete producers look complete.

## Independent review probes

Before accepting a producer receipt:

1. Enforce exact two-path diff scope and clean worktree state.
2. Inspect the implementation rather than trusting `RESULT.md`, self-review claims, or ad-hoc-only producer logs. If the producer did not supply the canonical packet, George must still reproduce or reject the candidate from actual diff and command behavior.
3. Reproduce initial launch command construction and relaunch command construction; they must match the new filesystem transport.
4. Probe that no `stdin` payload, signing secret, HMAC wrapper, or default secret is required for launch/relaunch. Confirm the actual launch call uses `stdin=None` or equivalent no-pipe behavior rather than only checking helper construction.
5. Verify child environment preservation, especially AGY CLI auth HOME separation.
6. Add/verify hostile hook probes for string/path-like command-builder inputs before conversion. Reject objects whose `__str__`, path conversion, equality, or hash hooks can execute during validation or process construction.
7. Run focused supervisor control-plane tests and adjacent regressions.
8. Run canonical/release/build gates before commit/PR if the candidate is accepted.
9. Preserve candidate commit before independent exact-head review; merge only after fresh GitHub CI and independent review bind to the same head.

## Legacy lint-debt handling

The supervisor file may carry large pre-existing Ruff/format debt. Do not call that lint green, and do not do an unrelated whole-file reformat or blanket ignore inside the transport slice. Instead:

1. Run the repository's actual commit/precommit gate; do not bypass it.
2. If direct whole-file Ruff/format fails, compare base-vs-candidate normalized findings.
3. Accept the slice only when `NEW_FINDINGS=0` and project precommit passes; report `PASS_WITH_WARNINGS` or equivalent, not `lint green`.
4. Preserve the boundary in the PR body and handoff: baseline findings count, candidate findings count, new findings count, and whether commit hooks were bypassed.

## Reporting boundary

A clean source PR/release proves only source convergence for the supervisor transport. It does **not** prove live supervisor switch, unit parity, runtime checkout cleanup, production deploy, restart, cap increase, or autonomous dispatch readiness. Those require separate authorization and runtime proof.

## Proof packet skeleton

```text
TASK=RUNTIME-CONVERGENCE-2
BASE=<sha>
WORKSPACE=<path>
TASK_SHA256=<sha256>
SCOPE=scripts/agy_sandbox_event_supervisor.py,tests/test_agy_sandbox_event_supervisor_control_plane.py
RESULT=<PASS|REPAIR|BLOCKED>
FOCUSED=<counts/log>
CANONICAL=<counts/log>
GITHUB_CI=<state>
INDEPENDENT_REVIEW=<state>
NOT_CLAIMING=live supervisor switch, deployment, restart, runtime parity, cap increase
```
