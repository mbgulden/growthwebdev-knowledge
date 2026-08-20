# GRO-3997 post-finalize PR/state/lock refresh pitfall

Session pattern: live verification task in `/tmp/hd-platform-gro3997` added a verifier and doc, ran `finalize_task.sh`, pushed `ned/GRO-3997`, opened PR #20, then had to repair post-finalize drift.

## What happened

1. `finalize_task.sh` ran with:

```bash
PRISMATIC_REPO_ROOT=/tmp/hd-platform-gro3997 \
FINALIZE_LOCK_FILES='scripts/live-analytics-coverage.mjs docs/operations/hde-production-analytics-coverage-2026-07-18.md' \
bash /home/ubuntu/.hermes/profiles/ned/scripts/finalize_task.sh GRO-3997 ned/GRO-3997 ned
```

2. The script printed successful unlocks, but its unlock calls used the extra `prismatic-engine` owner/namespace form. The locks still showed as held by `ned` when checked with:

```bash
node /home/ubuntu/.antigravity/swarm.js status | grep -E 'GRO-3997|live-analytics|hde-production-analytics'
```

3. Manual direct unlocks were required:

```bash
node /home/ubuntu/.antigravity/swarm.js unlock scripts/live-analytics-coverage.mjs ned
node /home/ubuntu/.antigravity/swarm.js unlock docs/operations/hde-production-analytics-coverage-2026-07-18.md ned
```

4. After `gh pr create`, Linear drifted from `In Review` back to `In Progress` even though finalize had printed `Linear transition: GRO-3997 → In Review`.

5. A direct Linear `issueUpdate` restored `In Review`, then a final query verified the state.

## Durable rule

For tasks that push/open a PR after finalize, final verification must include all three:

- `git status --short --branch` in the task worktree.
- `node /home/ubuntu/.antigravity/swarm.js status | grep <task paths>` showing no task locks.
- A fresh Linear query showing the issue is still `In Review` after PR creation/comments/automation.

If locks remain, unlock with the exact owner shape shown by `swarm.js status`, not the shape printed by finalize. If Linear state drifted, re-run `issueUpdate` and re-query before claiming completion.
