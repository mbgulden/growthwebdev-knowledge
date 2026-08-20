# Post-edit guard listed-path verifier pattern — Prompt 5.3, 2026-07-18

## Context

The post-edit guard repeatedly reported unverified changed paths after Prompt 5.3 even though broader PR verification and CI were green. The useful durable lesson is not that the guard was wrong; it is that the follow-up verifier must target the exact listed paths and print explicit `VERIFY_COMMAND=` lines from an actual `/tmp/hermes-verify-*` script.

## Good verifier shape

Use a wrapper that creates a real temp script with `tempfile.NamedTemporaryFile(prefix='hermes-verify-...', dir='/tmp', delete=False)`, runs it with the project venv, captures detailed output to `/tmp/kai-...-inner.log`, and removes the temp script.

For a guard listing only:

```text
prismatic/agy_merge_backlog.py
tests/test_agy_merge_backlog.py
```

run only checks that accept those files:

```text
VERIFY_COMMAND=git status --short --branch
VERIFY_COMMAND=/home/ubuntu/.local/bin/ruff check prismatic/agy_merge_backlog.py tests/test_agy_merge_backlog.py
VERIFY_COMMAND=/home/ubuntu/.local/bin/ruff format --check prismatic/agy_merge_backlog.py tests/test_agy_merge_backlog.py
VERIFY_COMMAND=python3 -m py_compile prismatic/agy_merge_backlog.py tests/test_agy_merge_backlog.py
VERIFY_COMMAND=/home/ubuntu/.prismatic/venv_stable/bin/python -m pytest tests/test_agy_merge_backlog.py -q
VERIFY_COMMAND=python inline exact changed-contract behavior assertions
```

Then assert the behavior changed by the edited paths, not only syntax/lint. For Prompt 5.3 this meant building an accepted demo completed-work packet, running `build_operator_pr_creation_dry_run(...)`, and asserting:

```text
marker=PROMPT5_OPERATOR_PR_DRY_RUN_OK
dry_run_only=true
operator_approved_action=true
branch_plan.executed=false
github_pr_plan.created=false
linear_writeback.posted=false
linear_writeback.dry_run_payload_only=true
all side_effects values are false
```

## Compact output

```text
COMMAND=/home/ubuntu/.prismatic/venv_stable/bin/python /tmp/hermes-verify-prompt53-listed-paths-rerun-*.py
RESULT=PASS
LOG=/tmp/kai-prompt53-listed-paths-rerun-inner.log
SCOPE=Prompt 5.3 listed changed paths: operator PR dry-run builder and merge-backlog tests
AD_HOC_OR_CANONICAL=ad-hoc targeted
NOT_CLAIMING=canonical_full_suite_green,real_github_pr_created,git_branch_created,auto_merge_enabled,production_deployed,linear_comment_posted_by_lane,AGY_dispatch,PR318_merged
MARKER=PROMPT5_LISTED_PATHS_OPERATOR_PR_DRY_RUN_RERUN_OK
cleanup=PASS
```

## Pitfalls

- Do not include `.html` files in `ruff check`; if dashboard markers matter, assert them in a Python string/HTML check separately.
- Do not reuse a prior broader verifier if the guard asks for fresh evidence. Rerun a fresh `/tmp/hermes-verify-*` script after the last commit/amend.
- If the first verifier used an incomplete hand-built packet and the classifier correctly rejected it, fix the fixture by using `demo_completed_work_packet()` and report only the passing rerun.
- Keep saying `ad-hoc targeted`; green focused pytest or GitHub CI is not a canonical full-suite claim.
