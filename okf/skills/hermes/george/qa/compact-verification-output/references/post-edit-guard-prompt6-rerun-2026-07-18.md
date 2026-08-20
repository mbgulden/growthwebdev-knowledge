# Post-edit guard rerun pattern — Prompt 6 (2026-07-18)

Session lesson: after code edits, the post-edit guard can still report `Verification status: unverified` even when a prior verifier/CI proof was summarized. Treat the guard as a request for **fresh evidence in the current turn**, not as something to debate.

## Pattern that satisfied the guard

1. Create a new temp verifier with `tempfile.NamedTemporaryFile(prefix='hermes-verify-...', dir='/tmp', delete=False)`.
2. Run it with the project venv/interpreter when importing project web/API code.
3. Emit explicit `VERIFY_COMMAND=<exact command>` lines before each subprocess.
4. Scope the verifier to the exact changed paths the guard named:
   - Python files: `ruff check`, `ruff format --check`, `py_compile`.
   - HTML/dashboard files: assert dashboard marker/button/function strings through `TestClient`; do **not** pass `.html` to ruff.
5. Include at least one inline behavior assertion for the changed contract, not only syntax checks.
6. Clean up the temp verifier and report `cleanup=PASS verifier_removed=<path>`.
7. Label the result `AD_HOC_OR_CANONICAL=ad-hoc targeted` and include non-claims.

## Example scope from Prompt 6

Changed paths:

```text
prismatic/agy_executor_runs.py
prismatic/gateway/server.py
prismatic/gateway/templates/dashboard.html
```

Useful behavior assertions:

```text
canary dry-run records durable run
commands_rendered=true
commands_executed=false
real_github_pr_created=false
git_branch_created=false
real mode blocks without PRISMATIC_ALLOW_REAL_PR_EXECUTOR=1
dashboard contains prompt6 marker/button/function/history
state path is temp/env-overridable
```

Compact proof shape:

```text
COMMAND=/path/to/venv/python /tmp/hermes-verify-*.py
RESULT=PASS
LOG=/tmp/<name>.log
SCOPE=<exact changed behavior/files>
AD_HOC_OR_CANONICAL=ad-hoc targeted
MARKER=<marker>
NOT_CLAIMING=canonical_full_suite_green,...
```
