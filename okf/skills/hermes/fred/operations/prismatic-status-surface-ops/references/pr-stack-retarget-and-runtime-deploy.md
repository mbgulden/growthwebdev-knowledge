# PR stack retarget + runtime deploy proof notes

Use this when a dashboard/control-plane feature is built as a stacked PR and then needs to be landed/deployed with proof.

## Stacked PR landing sequence

1. Merge the foundation PR first only after it is `CLEAN` and required checks are green.
2. Update the runtime checkout to the merged `origin/main` commit and smoke the new import/API before calling the foundation deployed.
3. If a child PR was based on the now-deleted foundation branch, expect GitHub to close it and potentially refuse reopen with `Could not open the pull request`.
4. If reopen/retarget fails, create a replacement PR from the same head branch against `main`. Treat the replacement PR as canonical and say the old stacked PR was superseded, not merged.
5. Require checks on the replacement/main-based PR; do not merge from local proof alone.
6. If CI fails on a regression test, fetch the job log, identify the exact failing contract, patch that layer, amend/force-push, and wait for the new-head checks.

## CLI direct-run regression pattern

For scripts under `scripts/` that import project modules and are intended to run directly, add a repo-root bootstrap before project imports:

```python
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
```

Add a regression that runs the script from outside the repo, but do not hardcode `/home/ubuntu/work/...` in the test. Resolve the script path from the test file, e.g. `Path(__file__).resolve().parents[1] / "scripts" / "script.py"`, so GitHub runners pass.

## Runtime deploy/restart proof

For Prismatic gateway runtime deploys:

- update `/home/ubuntu/.prismatic/runtime/prismatic-engine` to `origin/main`;
- run `py_compile` and an import smoke from `/home/ubuntu/.prismatic/venv_stable/bin/python3`;
- prefer `sudo -n systemctl restart prismatic-gateway.service` when available;
- verify live routes on `127.0.0.1:9000` after restart;
- include the runtime commit and gateway process cwd in the proof.

If plain `systemctl restart` fails with interactive auth, do not claim blocked until trying passwordless `sudo -n systemctl ...`. If a service restart is attempted by killing the process, verify the supervisor actually respawned and the port is listening before proceeding.

## Stale guard exact-scope proof

When the stale guard narrows changed paths to one file, the fresh `/tmp/hermes-verify-*` proof should match that exact path and exact changed behavior. Example for a test-only CLI regression:

```text
changed_paths_checked=/abs/path/tests/test_...
COMMAND=python3 -m pytest -q tests/test_...::specific_regression && python3 -m py_compile script_under_test tests/test_...
AD_HOC_OR_CANONICAL=ad-hoc targeted
NOT_CLAIMING=canonical_full_suite_green,additional_code_changes,production_state_mutation
```

Remove stale `/tmp/hermes-verify-mobile-branch-390.py` first if the guard is replaying old mobile overflow evidence, but do not re-run unrelated mobile proof when the current changed path is not mobile/dashboard code.
