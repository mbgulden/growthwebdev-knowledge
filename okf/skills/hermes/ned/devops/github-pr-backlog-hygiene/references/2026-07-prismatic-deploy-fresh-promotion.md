# 2026-07 Prismatic deploy-fresh promotion integration

## When this applies
Use this as an example when a long-lived integration branch is being promoted into `main` after a large PR-backlog cleanup. The key lesson is that local conflict resolution is not enough; GitHub check logs are the source of truth for the last-mile failures.

## Workflow that worked
1. Create a fresh integration branch/worktree from current `origin/main`.
2. Merge the long-lived source branch (`origin/deploy-fresh`) into the integration branch, not into canonical `main`.
3. Resolve conflicts while preserving main-side shims that landed during PR cleanup.
4. Run broad local verification before pushing:
   - `python3 -m pytest -q tests/`
   - `python3 -m pytest -q tests/test_plugin_load_gate.py`
   - `python3 -m prismatic.quality.plugin_load`
   - `python3 -m compileall -q prismatic scripts plugins tests schemas`
   - conflict-marker scan outside `.git`, venvs, node_modules, and caches
5. Push/update the PR branch and wait for GitHub checks.
6. If CI fails, pull the exact failing log:
   - `gh run view <run-id> --repo OWNER/REPO --log-failed`
7. Patch the integration branch, amend/force-push with lease, then wait for green checks before merging.
8. After merge, verify `origin/main` advanced, open PR count is empty/expected, Linear has evidence, and temp worktrees/locks are cleaned up.

## Pitfalls captured
- A check named “Verify shipped plugins load” can fail before plugin loading if the workflow environment is missing test dependencies. Inspect the run log; in this session the last-mile CI blocker was `No module named pytest`, fixed by declaring `pytest` in project dependencies.
- Plugin load can pass locally while CI fails from packaging/dependency drift. Run both `tests/test_plugin_load_gate.py` and the CLI gate locally, then still trust GitHub checks as final gate.
- Long-lived branch promotion can break older/newer compatibility tests simultaneously. Preserve compatibility shims rather than choosing one side wholesale.
- Do not merge a PR just because it is structurally `MERGEABLE`; required checks must be green.

## Evidence shape to leave on Linear
Include PR URL, merge commit, GitHub check names/conclusions, and concise local verification commands/results. Avoid dumping full logs.
