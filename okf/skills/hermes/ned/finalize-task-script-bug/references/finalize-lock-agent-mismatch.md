# finalize_task.sh lock-agent mismatch pitfall

Session signal: GRO-3677 verification/finalization on a clean worktree.

## What happened

The swarm lock CLI and `finalize_task.sh` do not agree on lock argument shape in all cases.

- `node /home/ubuntu/.antigravity/swarm.js lock plugins/pwp prismatic-engine ned` recorded the lock owner as `prismatic-engine`, not `ned`.
- `node /home/ubuntu/.antigravity/swarm.js heartbeat plugins/pwp ned` then failed with `No lock found for plugins/pwp by ned`.
- Correct lock acquisition was `node /home/ubuntu/.antigravity/swarm.js lock plugins/pwp ned`.
- However, `FINALIZE_LOCK_FILES='plugins/pwp' bash finalize_task.sh ...` printed `UNLOCKED: plugins/pwp ← prismatic-engine`, while the lock file still contained `{"path":"plugins/pwp","agent":"ned"}` afterward.
- Manual cleanup required `node /home/ubuntu/.antigravity/swarm.js unlock plugins/pwp ned`.

## Durable rule

After any finalize run that involved custom `FINALIZE_LOCK_FILES`, inspect `/home/ubuntu/.antigravity/swarm_locks.json` or run the swarm status command before claiming locks are released. If the lock remains under `ned`, explicitly run:

```bash
node /home/ubuntu/.antigravity/swarm.js unlock <path> ned
```

Do not trust the finalize log line alone when it says it unlocked `<path> ← prismatic-engine`; that may be an old/domain-shaped unlock path rather than the active lock owner.

## Recommended lock pattern for Ned plugin-lane tasks

```bash
node /home/ubuntu/.antigravity/swarm.js lock plugins/pwp ned
node /home/ubuntu/.antigravity/swarm.js heartbeat plugins/pwp ned
# ... work / verify / finalize ...
PRISMATIC_REPO_ROOT=<clean-worktree> FINALIZE_LOCK_FILES='plugins/pwp' \
  bash /home/ubuntu/.hermes/profiles/ned/scripts/finalize_task.sh GRO-XXXX ned/GRO-XXXX ned
node /home/ubuntu/.antigravity/swarm.js unlock plugins/pwp ned || true
```

The final explicit unlock is idempotent and protects against stale locks when finalize uses the mismatched `prismatic-engine` owner form internally.
