# Fresh verification after checkout drift

Use this pattern when Hermes/system asks for fresh verification of changed code paths, but the active shared repo checkout no longer contains the PR/branch being verified.

## Trigger

- You edited code, committed/opened a PR, then another process/agent switched the shared worktree to a different branch.
- A verification guard names changed paths from your PR and asks for a fresh `/tmp/hermes-verify-*` script.
- Running against the current checkout would falsely fail because the changed paths/markers are absent.

## Pattern

1. Identify the exact PR branch or commit that contains the changed paths.
2. Create a verifier under `/tmp` with a `hermes-verify-` filename prefix.
3. Inside the verifier, create an isolated temporary git worktree from the PR branch/commit, for example:

```python
SOURCE_REPO = Path('/home/ubuntu/work/prismatic-engine')
BRANCH = 'origin/feature/example-branch'
worktree = Path(tempfile.mkdtemp(prefix='hermes-verify-example-worktree-'))
subprocess.run(['git', '-C', str(SOURCE_REPO), 'fetch', 'origin', 'feature/example-branch'], check=True)
subprocess.run(['git', '-C', str(SOURCE_REPO), 'worktree', 'add', '--detach', str(worktree), BRANCH], check=True)
```

4. Run syntax checks and focused behavior checks inside that temporary worktree.
5. Verify behavior markers and changed-path effects, not just import success.
6. In `finally`, remove the temporary worktree and delete the `/tmp/hermes-verify-*` script.
7. Report as ad-hoc targeted verification:

```text
COMMAND=python3 /tmp/hermes-verify-<name>.py
RESULT=PASS|FAIL
LOG=/tmp/<name>.log
SCOPE=changed-path behavior verification in isolated git worktree
AD_HOC_OR_CANONICAL=ad-hoc targeted
NOT_CLAIMING=canonical suite green, production deploy, live external mutation
MARKER=<MARKER>
cleanup=PASS
```

## Pitfalls

- Do not verify a PR by accidentally running tests against whatever branch the shared worktree currently has checked out.
- Do not convert a checkout-drift failure into a claim that the feature is missing; first verify the PR branch directly.
- Do not call this canonical suite green unless the project-defined canonical suite actually ran.
- Keep setup-state noise separate from behavior proof; a transient missing DB or circuit-breaker warning is not a blocker if the focused behavior is independently asserted and exits cleanly.
