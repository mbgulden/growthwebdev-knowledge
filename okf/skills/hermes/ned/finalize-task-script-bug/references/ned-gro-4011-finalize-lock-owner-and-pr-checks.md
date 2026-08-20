# GRO-4011 finalize lock-owner + PR-check verification pattern

## Context

During GRO-4011, Ned implemented a small docs/script product-loop artifact in `hd-platform` from a clean temporary worktree, committed early, ran verification, then invoked `finalize_task.sh` with:

```bash
PRISMATIC_REPO_ROOT=/tmp/hd-platform-GRO-4011 \
FINALIZE_LOCK_FILES='docs/vision/daily-nervous-system-work-product-loop.md scripts/nervous_system_work_product_loop.py /tmp/issue-batches/GRO-4011_RESULT.md' \
bash ~/.hermes/profiles/ned/scripts/finalize_task.sh GRO-4011 ned/GRO-4011 ned
```

Finalize printed successful unlock lines, transitioned Linear, and posted a comment. A follow-up lock check still showed the two repo-path locks present.

## Durable lesson

`finalize_task.sh` currently unlocks with the `prismatic-engine` repo-owner form:

```bash
node /home/ubuntu/.antigravity/swarm.js unlock "$f" prismatic-engine "$AGENT_ID"
```

But Ned often acquires locks with the simpler agent-owner form:

```bash
node /home/ubuntu/.antigravity/swarm.js lock <path> ned
```

Those are not always equivalent. If the follow-up lock status still shows the task paths, manually unlock with the same shape used to acquire the lock:

```bash
node /home/ubuntu/.antigravity/swarm.js unlock docs/vision/<file>.md ned
node /home/ubuntu/.antigravity/swarm.js unlock scripts/<file>.py ned
node /home/ubuntu/.antigravity/swarm.js unlock /tmp/issue-batches/<ISSUE>_RESULT.md ned
node /home/ubuntu/.antigravity/swarm.js status 2>/dev/null | grep -E '<ISSUE>|<keyword>' || true
```

Do not assume finalize's `UNLOCKED` transcript is authoritative. Re-check the lock registry before final reporting.

## PR-check verification nuance

After pushing/opening the PR, inspect checks before claiming completion:

```bash
gh pr view <PR> --json number,state,mergeable,statusCheckRollup,url \
  --jq '{number,state,mergeable,url,checks:[.statusCheckRollup[]? | {name:.name, conclusion:.conclusion, status:.status}]}'
gh pr checks <PR> --watch=false || true
```

For HDE static-site PRs, Cloudflare Pages can pass while `Workers Builds: hd-platform` fails externally. Treat that as **implemented / In Review**, not Done, unless the task explicitly only needs Pages proof and the red Worker check has been separately dispositioned.

## Temp worktree cleanup

For clean-worktree implementation/verification passes:

1. Commit and push the `ned/<issue>` branch.
2. Open/inspect the PR.
3. Refresh `/tmp/issue-batches/<ISSUE>_RESULT.md` with PR/check state.
4. Manually unlock any locks left behind by finalize.
5. Remove the temp worktree only after push/evidence is captured:

```bash
cd /home/ubuntu/work/hd-platform
git worktree remove --force /tmp/hd-platform-<ISSUE>
git branch --list 'ned/<ISSUE>' -vv
```

Keep the local branch; remove only the temporary worktree.