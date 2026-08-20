# GRO-4010 temp-worktree push + repeated fresh-verification lessons

## Trigger

A Ned task is implemented in a clean temp worktree cloned from a local checkout, then finalized and pushed/opened as a PR. The system may also repeat the “workspace does not have fresh passing verification evidence” prompt after a summary.

## Lessons

### Local-origin clone is not a GitHub push

If the temp worktree was created with `git clone /home/ubuntu/work/<repo> /tmp/<repo-task>`, its `origin` remote points at the local checkout. `git push -u origin HEAD` only updates that local repo. `gh pr create/view` will then fail with:

```text
none of the git remotes configured for this repository point to a known GitHub host
```

Fix:

```bash
git remote add github https://github.com/OWNER/REPO.git 2>/dev/null || \
  git remote set-url github https://github.com/OWNER/REPO.git
git fetch github main --prune
git push -u github <branch>
gh pr create --repo OWNER/REPO --base main --head <branch> ...
gh pr view <branch> --repo OWNER/REPO --json number,url,statusCheckRollup,mergeStateStatus
```

Verify the remote branch SHA with `git ls-remote --heads github <branch>` before claiming the branch is on GitHub.

### Finalize exit 0 still needs state + lock verification

After `finalize_task.sh`, re-query Linear state/comments. In this pass finalize printed `Linear transition: GRO-4010 → In Review`, but a follow-up query showed `In Progress`; a manual `issueUpdate` to the `In Review` state was required, followed by another query.

Also inspect swarm locks after finalize. If locks remain for the changed paths, unlock the exact paths with the same agent owner and confirm the lock listing is clean.

### Repeated verifier prompts require a new run, not an argument

If the system repeats the fresh-verification prompt after a summary, rerun the relevant commands in the changed worktree and report the fresh output. Do not cite earlier output as sufficient.

For this class of HD Platform task, the fresh verifier bundle was:

```bash
cd /tmp/hd-platform-gro4010
node --check scripts/hde-green-status.mjs
node scripts/hde-green-status.mjs GRO-4010   # expected rc=1 while children remain incomplete
npm run build
python3 - <<'PY'
from pathlib import Path
s=Path('/tmp/issue-batches/GRO-4010_RESULT.md').read_text()
for marker in ['PR:', 'node --check', 'npm run build', 'GRO-4012']:
    assert marker in s, marker
print('RESULT markers verified')
PY
git status --short --branch
```

If a verifier intentionally exits nonzero to encode “not green yet,” state that explicitly and assert the expected exit code in the shell script so the overall verification command still fails on unexpected outcomes.
