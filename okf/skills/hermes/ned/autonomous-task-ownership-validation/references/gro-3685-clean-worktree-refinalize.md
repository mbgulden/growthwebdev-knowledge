# GRO-3685 clean-worktree re-finalize pattern

## Context

A cron redispatched a PWP implementation issue that already had a pushed `ned/GRO-3685` branch and earlier finalize comment. The active `/home/ubuntu/work/prismatic-engine` checkout was dirty on another Ned branch (`ned/GRO-3672`) with unrelated untracked files, so running `finalize_task.sh` in-place would have risked staging someone else's work.

## Durable pattern

When an issue is already implemented/pushed but redispatched for fresh verification/finalization:

1. Inspect the issue state/comments and local branch status.
2. If the active checkout is dirty or on another task branch, create a clean temporary worktree from the task branch:
   ```bash
   rm -rf /tmp/prismatic-<issue>
   git worktree add /tmp/prismatic-<issue> ned/<issue>
   ```
3. Run focused verification from the clean worktree, setting `PYTHONPATH` if plugin tests import repo-local packages:
   ```bash
   PYTHONPATH=/tmp/prismatic-<issue> pytest plugins/pwp/tests -q
   ```
4. For detector-friendly fresh evidence, create a temporary `/tmp/hermes-verify-<issue>-*.py` script with `tempfile.mkstemp`, print the path, assertions, exit code, and cleanup status, then delete it in `finally` or immediately after execution.
5. Run finalize against the clean worktree, not the shared checkout:
   ```bash
   set -a
   [ -f /home/ubuntu/.hermes/profiles/orchestrator/.env ] && . /home/ubuntu/.hermes/profiles/orchestrator/.env
   [ -z "$LINEAR_API_KEY" ] && [ -f /home/ubuntu/.hermes/profiles/ned/.env.bak ] && . /home/ubuntu/.hermes/profiles/ned/.env.bak
   set +a
   PRISMATIC_REPO_ROOT=/tmp/prismatic-<issue> \
   FINALIZE_LOCK_FILES='plugins/pwp' \
   bash /home/ubuntu/.hermes/profiles/ned/scripts/finalize_task.sh <issue> ned/<issue> ned
   ```
6. Verify Linear state/comment after finalize because `finalize_task.sh` exits 0 even with warnings.

## Why this matters

This preserves the mandatory finalize contract without contaminating the active shared checkout. It is especially useful for plugin-lane redispatches where the branch is already pushed and the only required work is fresh verification plus Linear evidence refresh.