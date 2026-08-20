# Post-edit guard rerun pattern — Prompt 7 executor API audit writeback (2026-07-18)

Use when Hermes says a code-edit turn is still `Verification status: unverified` even after a previous proof packet. Treat each guard notice as requiring fresh current-turn evidence, not an argument about prior evidence.

## Pattern

1. Load `compact-verification-output` if available.
2. Create an actual temp verifier under `/tmp` with a `hermes-verify-` prefix using `tempfile.NamedTemporaryFile(..., delete=False)`.
3. Scope the verifier to the exact guard-listed changed paths.
4. Keep `.html` out of `ruff`; validate dashboard HTML via marker/API assertions instead.
5. Run lint/format/compile/scoped pytest inside the temp verifier.
6. Exercise the changed behavior inline, not just static checks.
7. Remove the verifier and print `cleanup=PASS verifier_removed=<path>`.
8. Label proof as `AD_HOC_OR_CANONICAL=ad-hoc targeted`, not suite green.

## Prompt 7 behavior assertions used

```text
dry-run /pr-executor writes audit_writeback
dry-run response includes executor_run_id
executor_run_id is retrievable from list/detail APIs
blocked real-mode /pr-executor also writes side-effect-free audit record
dashboard contains audit_writeback + executor_run_id markers
PRISMATIC_ALLOW_REAL_PR_EXECUTOR remains absent
```

## Commands inside verifier

```text
ruff check prismatic/agy_executor_runs.py prismatic/gateway/server.py tests/test_agy_merge_backlog_api.py
ruff format --check prismatic/agy_executor_runs.py prismatic/gateway/server.py tests/test_agy_merge_backlog_api.py
python3 -m py_compile prismatic/agy_executor_runs.py prismatic/gateway/server.py tests/test_agy_merge_backlog_api.py
python -m pytest tests/test_agy_merge_backlog_api.py tests/test_agy_merge_backlog.py -q
```

## Compact proof shape

```text
COMMAND=/home/ubuntu/.prismatic/venv_stable/bin/python /tmp/hermes-verify-prompt7-post-edit-guard-rerun-*.py
RESULT=PASS
LOG=/tmp/kai-prompt7-post-edit-guard-rerun-verify.log
SCOPE=Prompt 7 changed paths: agy_executor_runs.py, gateway/server.py, dashboard.html, test_agy_merge_backlog_api.py
AD_HOC_OR_CANONICAL=ad-hoc targeted
MARKER=PROMPT7_EXECUTOR_API_AUDIT_WRITEBACK_OK
cleanup=PASS verifier_removed=/tmp/hermes-verify-...
```

## Pitfall

Do not include the HTML file in Python lint commands. Keep it in scope via a dashboard response assertion for specific markers such as `audit_writeback`, `executor_run_id`, `prompt6-executor-audit-canary`, and `stageApprovedPrExecutor`.
