# HD Platform finalize lock-shape pitfall (2026-07-18)

## Context

During HD Platform task GRO-3993, the work was done from a clean temporary worktree (`/tmp/hd-platform-gro3993`) with explicit locks taken as:

```bash
node /home/ubuntu/.antigravity/swarm.js lock src/layouts/Layout.astro ned
node /home/ubuntu/.antigravity/swarm.js lock scripts/route-complete-build.mjs ned
node /home/ubuntu/.antigravity/swarm.js lock scripts/docs/hde-analytics-loader-20260718.md ned
```

Finalize was invoked correctly with a repo override and explicit lock list:

```bash
PRISMATIC_REPO_ROOT=/tmp/hd-platform-gro3993 \
FINALIZE_LOCK_FILES='src/layouts/Layout.astro scripts/route-complete-build.mjs scripts/docs/hde-analytics-loader-20260718.md' \
bash /home/ubuntu/.hermes/profiles/ned/scripts/finalize_task.sh GRO-3993 ned/GRO-3993 ned
```

The script transitioned Linear and posted the finalization comment, but the unlock transcript showed the wrong lock owner/shape:

```text
UNLOCKED: src/layouts/Layout.astro ← prismatic-engine
UNLOCKED: scripts/route-complete-build.mjs ← prismatic-engine
UNLOCKED: scripts/docs/hde-analytics-loader-20260718.md ← prismatic-engine
```

A post-finalize lock check still showed the original locks held by `ned`:

```text
src/layouts/Layout.astro                    ned
scripts/route-complete-build.mjs            ned
scripts/docs/hde-analytics-loader-20260718.md ned
```

Manual cleanup with the same two-argument shape used for acquisition cleared them:

```bash
node /home/ubuntu/.antigravity/swarm.js unlock src/layouts/Layout.astro ned
node /home/ubuntu/.antigravity/swarm.js unlock scripts/route-complete-build.mjs ned
node /home/ubuntu/.antigravity/swarm.js unlock scripts/docs/hde-analytics-loader-20260718.md ned
```

## Durable lesson

When using `finalize_task.sh` outside its default Prismatic Engine repo assumptions, do not trust the unlock transcript by itself. Always run a post-finalize lock check for the exact changed paths. If locks remain under `ned`, unlock them manually with the same path + agent shape used when acquiring the lock.

## Checklist for future HD Platform / temp-worktree finalization

1. Acquire locks with the actual repo-relative path and `ned` owner.
2. Invoke finalize with `PRISMATIC_REPO_ROOT=<clean-worktree>` and `FINALIZE_LOCK_FILES='<actual changed paths>'`.
3. Re-query Linear state/comments because finalize exits `0` on warnings.
4. Re-check swarm locks for the exact changed paths.
5. If locks remain, manually run `node /home/ubuntu/.antigravity/swarm.js unlock <path> ned` for each path.
