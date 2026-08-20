# HDE redispatch of completed code work — verification/dequeue pattern

Use this when a Linear issue is redispatched with `dispatch:ready`, but comments/PR history show code was already implemented and the only remaining red signal is the known external `Workers Builds: hd-platform` check.

## Pattern

1. Read Linear comments first. If prior evidence says branch/PR exists, treat the tick as a refresh/dequeue job before building more code.
2. Fetch the remote branch explicitly, because a stale local fetch may claim the branch disappeared:

```bash
git fetch origin +refs/heads/ned/GRO-XXXX:refs/remotes/origin/ned/GRO-XXXX +refs/heads/main:refs/remotes/origin/main
```

3. Create a disposable worktree from the remote branch and switch/create the local `ned/GRO-XXXX` branch inside it.
4. Lock/heartbeat the exact changed files before verification, even if no edits are expected.
5. Run fresh proof commands from the worktree. For browser event instrumentation, a temporary Playwright script can stub APIs and assert the expected events plus `piiLeakCount=0`.
6. Write `/tmp/issue-batches/GRO-XXXX_RESULT.md` with the refreshed evidence.
7. Run finalize with absolute paths:

```bash
PRISMATIC_REPO_ROOT=/tmp/hd-platform-groXXXX \
FINALIZE_LOCK_FILES='path/one path/two docs/proof.md' \
bash /home/ubuntu/.hermes/profiles/ned/scripts/finalize_task.sh GRO-XXXX ned/GRO-XXXX ned
```

8. Immediately verify `swarm.js status`; manually unlock simple-owner `ned` locks if finalizer only unlocked `prismatic-engine` locks.
9. Remove stale `dispatch:ready` and add `agent:needs-human-review` when Cloudflare Pages is green but the duplicate Workers check is red.
10. Remove the disposable worktree.

## State rule

Keep Linear `In Review`, not `Done`, until the issue's live/proof check is green. For HDE Pages PRs with only the duplicate Workers check red, this is a project-owner decision, not more repo code work.