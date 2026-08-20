# Ned redispatch label cleanup can regress Linear state

## Trigger

After `finalize_task.sh` succeeds and transitions an issue to `In Review`, a stale scanner label such as `dispatch:ready` remains and must be removed manually.

Observed during a GRO-3999 redispatch refresh: removing `dispatch:ready` with `issueUpdate(labelIds: [...])` succeeded, but the issue state changed from `In Review` to `In Progress` even though the mutation did not request a state change.

## Safe pattern

1. Run `finalize_task.sh` with absolute path and explicit `PRISMATIC_REPO_ROOT` / `FINALIZE_LOCK_FILES`.
2. Query Linear state + labels after finalize.
3. Remove only stale scanner labels by setting the retained label IDs.
4. Immediately re-query state + labels.
5. If the correct final state is still `In Review` (for example PR open, remote checks not all green), explicitly set `stateId` back to the team's `In Review` state.
6. Final-query again and update `/tmp/issue-batches/<ISSUE>_RESULT.md` with the actual final state, not the intended pre-cleanup state.
7. Check `swarm.js status` and clear any leftover simple-owner locks using the exact owner/namespace shape used to acquire them.

## Why it matters

A redispatch refresh is usually meant to remove `dispatch:ready` and preserve already-reviewed work. If label cleanup silently regresses the issue to `In Progress`, the queue can pick it up again or misrepresent the real PR/check state.

## Verification snippet

Expected final shape for non-green PR redispatches:

```text
state= In Review
labels= agent:ned,<pipeline labels only>; no dispatch:ready
finalizer_comment_present= True
swarm status: No active locks.
```
