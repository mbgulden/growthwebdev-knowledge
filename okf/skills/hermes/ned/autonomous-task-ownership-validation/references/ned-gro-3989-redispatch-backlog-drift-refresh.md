# GRO-3989 redispatch: Backlog + dispatch:ready drift refresh

Session: 2026-07-19 Ned cron redispatch for GA4 property/data stream verification.

## Pattern

An already-implemented GA4/Admin verification issue can be redispatched even after prior finalize/PR/evidence when Linear drifts back to `Backlog` and retains `dispatch:ready`.

Do not rebuild from the dirty shared checkout. Treat this as an evidence/state refresh:

1. Confirm existing completion signals:
   - remote branch `origin/ned/GRO-3989` exists;
   - PR exists and points at the expected SHA;
   - local `/tmp/issue-batches/GRO-3989_RESULT.md` records prior finalization and blockers;
   - Linear comments contain prior Ned finalization/evidence.
2. Create a clean detached worktree from the remote task branch, not from the dirty shared checkout:
   - `git worktree add --detach /tmp/hd-platform-gro3989-refresh origin/ned/GRO-3989`
3. Rerun fresh verification from that clean worktree:
   - `python3 -m py_compile scripts/operations/verify_ga4_stream.py`
   - `python3 scripts/operations/verify_ga4_stream.py --repo .`
   - `git diff --check`
   - targeted assertions for the doc/verifier and required strings (`G-Q6TPL08VM7`, `Analytics Admin`, `OAuth`)
   - `npm ci` if dependencies are not installed, then `npm run build`
4. Remove generated/ignored verifier artifacts before finalize (`node_modules`, `dist`, `.astro`, `__pycache__`) and confirm the clean worktree has no status output.
5. Refresh `/tmp/issue-batches/GRO-3989_RESULT.md` with the new evidence and current blocker state.
6. Rerun finalize from the clean worktree:
   - `PRISMATIC_REPO_ROOT=/tmp/hd-platform-gro3989-refresh FINALIZE_LOCK_FILES='docs/operations/hde-ga4-property-stream-verification.md scripts/operations/verify_ga4_stream.py /tmp/issue-batches/GRO-3989_RESULT.md' bash ~/.hermes/profiles/ned/scripts/finalize_task.sh GRO-3989 ned/GRO-3989 ned`
7. Re-query Linear after finalize. If it is `In Review` but still has `dispatch:ready`, remove only `dispatch:ready` and add human-review labels when the blocker is OAuth/human consent:
   - `agent:needs-human-review`
   - `requires:human-approval`
8. Remove the clean worktree and verify swarm locks are clear.

## Outcome shape

- Linear state: `In Review`.
- `dispatch:ready`: removed.
- Human-review labels: present when OAuth consent is still needed.
- PR remains open if external checks or live/admin proof are not green.
- Final response should report only meaningful drift/refresh evidence; do not claim green while Analytics Admin OAuth proof, site-wide live tagging, or PR checks remain red.

## Pitfall

`finalize_task.sh` can successfully transition to `In Review` while leaving `dispatch:ready` intact. The scanner may then redispatch the same issue. Always re-query labels after finalize and remove stale dispatch labels explicitly.