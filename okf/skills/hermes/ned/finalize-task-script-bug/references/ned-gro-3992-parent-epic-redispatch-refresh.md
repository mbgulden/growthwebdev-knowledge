# Ned GRO-3992 parent-epic redispatch refresh

## Trigger

A parent epic that already had a branch/PR/result and finalization evidence was redispatched by the scanner because Linear drifted back to `Backlog` with stale `dispatch:ready`.

## Durable pattern

1. Re-read the autonomous task skeleton first; do not skip it even for a drift refresh.
2. Query Linear including comments and children before rebuilding. Confirm there is no dequeue/out-of-lane instruction.
3. Check prior session/result evidence and existing remote branch/PR. If the branch already contains the work and the issue is a parent epic, do not create new implementation just to satisfy the scanner.
4. Create a temporary clean worktree from the existing `ned/...` remote branch.
5. Reacquire/heartbeat only the files already owned by the branch.
6. Run fresh verification (`npm ci`, `npm run build`, or the issue’s verifier) before finalizing.
7. Run `finalize_task.sh` with absolute path and explicit env:

```bash
PRISMATIC_REPO_ROOT=/tmp/<worktree> \
FINALIZE_LOCK_FILES='docs/operations/file-a.md docs/operations/file-b.md' \
bash /home/ubuntu/.hermes/profiles/ned/scripts/finalize_task.sh GRO-XXXX ned/GRO-XXXX ned
```

8. After finalize, explicitly remove stale `dispatch:ready` if it remains. `finalize_task.sh` transitions state and comments, but does not always clear scanner labels.
9. Run `swarm.js status`; if simple-owner locks remain, unlock with the same simple owner form used to acquire them:

```bash
node /home/ubuntu/.antigravity/swarm.js unlock <path> ned
```

10. Verify Linear state/labels after cleanup. The success condition for drift refresh is `In Review`, no `dispatch:ready`, result file present, and no active locks.

## Pitfall

Do not mark a parent epic Done/green just because finalize succeeded. If child issues are still In Review and a live verifier remains red, finalization is only queue hygiene; the epic remains non-green until child PRs merge/deploy and the live verifier returns `ok=true`.
