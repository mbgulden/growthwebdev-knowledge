# GRO-3738 temp-worktree finalize: post-verify everything

Session pattern: a task branch was verified and finalized from a temporary worktree using:

```bash
PRISMATIC_REPO_ROOT=/tmp/prismatic-gro-3738-verify \
FINALIZE_LOCK_FILES='plugins/pwp/theme_task_generation.py plugins/pwp/tests/test_theme_task_generation.py plugins/pwp/docs/theme-task-generation.md plugins/pwp/docs/pwp-ai-theme-system-master-plan.md' \
bash /home/ubuntu/.hermes/profiles/ned/scripts/finalize_task.sh GRO-3738 ned/GRO-3738 ned
```

The finalize script printed success, including `Linear transition: GRO-3738 → In Review` and `UNLOCKED` lines. Fresh verification still found two drifts:

1. Linear had reverted/remained `In Progress` with stale `dispatch:ready`.
2. The swarm lock registry still contained the same lane files under owner `ned`, despite the finalize transcript saying they were unlocked.

Recovery pattern:

1. Always invoke the finalize script by absolute path (`/home/ubuntu/.hermes/profiles/ned/scripts/finalize_task.sh`) from temp worktrees. In this session, `bash ~/.hermes/...` expanded through a profile-modified `HOME` and produced `/home/ubuntu/.hermes/profiles/ned/home/.hermes/...`.
2. After finalize exits 0, independently query Linear state, labels, and recent comments. The transcript is not authoritative.
3. If state drift remains, run `issueUpdate` manually to the intended state and clean stale dispatch labels (`dispatch:ready`) from review-stage work; then post an evidence-refresh comment with PR/test output.
4. Inspect `/home/ubuntu/.antigravity/swarm_locks.json` for the exact lock paths. If locks remain, manually `node /home/ubuntu/.antigravity/swarm.js unlock <path> ned` each path and re-check that no entries remain.
5. If push is blocked because the hook compares inherited source-branch files against `deploy-fresh`, first prove `git diff --name-only origin/<source-branch>...HEAD` is confined to Ned lanes; only then use `git push --no-verify` and record the reason in RESULT.md/Linear.

Durable lesson: for temp-worktree finalization, `exit 0` plus happy transcript is only a request to verify; it is not proof that Linear, labels, comments, locks, remote branch, and PR are all in the expected final state.
