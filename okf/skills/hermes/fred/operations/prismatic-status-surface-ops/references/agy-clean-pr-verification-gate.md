# AGY clean PR dry-run + verification gate

Use this reference after AGY completed-work ingestion exists and Michael asks for the next gate: turn persisted completed-work rows into a safe merge backlog / dry-run PR plan with lane verification, without enabling auto-merge.

## Boundary

This slice earns these markers only when proven:

```text
AGY_CLEAN_PR_CREATE_UPDATE_OK
AGY_PR_VERIFICATION_GATE_OK
AGY_CLEAN_PR_AND_VERIFICATION_GATE_OK
```

Hard non-claims:

```text
auto_merge=false
bulk_agy_dispatch=false
overnight_autopilot_ready=false
production_deploy=false
actual_github_pr_created=false unless explicitly authorized and proven
```

Do not start AGY jobs, bulk dispatch, create real GitHub PRs, merge, or deploy from this gate. The correct output is a deterministic backlog item and dry-run PR plan.

## Branch/base discipline

Before continuing any AGY stack, run:

```bash
git status --short
git branch --show-current
git log --oneline --decorate -5
gh pr view <foundation-pr> --json state,mergeCommit
gh pr view <ingestion-pr> --json state,mergeCommit
```

If the foundation/ingestion stack has landed, branch from `origin/main`; do not keep stacking on a closed/deleted branch. If GitHub closes a stacked PR after its base branch is deleted, create a replacement main-based PR and state that plainly.

The checkpoint daemon may insert WIP commits while work is in progress. Before opening/finalizing the PR, inspect `origin/main..HEAD`, then squash to one clean Fred commit and rerun verification on the final head.

## Module contract

Recommended module: `prismatic/agy_merge_backlog.py`.

Input: `CompletedWorkRow` from `prismatic.agy_completed_work`.

Output: `MergeBacklogItem` dict with at least:

```text
merge_backlog_id
completed_work_id
issue_identifier
source_branch
base_branch
changed_files
classification
recommended_action
pr_branch
pr_title
pr_body
verification_required
verification_lane
verification_gate
eligible_for_auto_merge=false
reasons
dry_run=true
side_effects.git_mutation=false
side_effects.github_pr_created=false
side_effects.auto_merge=false
side_effects.production_deploy=false
side_effects.agy_dispatch=false
```

Required action mapping:

| completed-work classification | recommended_action |
|---|---|
| `merge_ready` | `open_or_update_pr` |
| `clean_rebuild_required` | `clean_rebuild_required` |
| `blocked_missing_proof` | `blocked_missing_proof` |
| `blocked_failed_verification` | `blocked_failed_verification` |
| `manual_review_scope` | `manual_review_scope` |
| `manual_review_conflict` | `manual_review_conflict` |
| `superseded` | `superseded` |
| `rejected` | `rejected` |

Even when action is `open_or_update_pr`, the plan is dry-run and `eligible_for_auto_merge` remains false.

## Lane verification gate

Start as a deterministic proof-policy gate; it does not need to execute every suggested command automatically.

Minimum lanes:

| Lane | Gate policy |
|---|---|
| `dashboard-ui` | require dashboard/browser/JS proof; proof text should include `dashboard` and `node --check`; suggested plan includes dashboard API/route proof. |
| `backend-api` | require API/TestClient or focused pytest proof; proof text should include `pytest`. |
| `docs` | require artifact/source proof and `/tmp` log; no runtime claims. |
| `research` | require artifact/source proof and `/tmp` log; no runtime claims. |
| `mixed` / `manual-review` | return `manual_review`; no clean PR auto-plan approval. |
| `unknown` | return `manual_review` or blocked until classified. |

Required output field:

```text
verification_gate=pass|blocked|manual_review
```

## CLI helper

Recommended script: `scripts/agy_merge_backlog.py`.

Commands:

```bash
python scripts/agy_merge_backlog.py list --db <path>
python scripts/agy_merge_backlog.py classify <completed_work_id> --db <path>
python scripts/agy_merge_backlog.py plan-pr <completed_work_id> --db <path>
python scripts/agy_merge_backlog.py verify <completed_work_id> --db <path>
python scripts/agy_merge_backlog.py open-pr <completed_work_id> --db <path>
```

`open-pr` must default to dry-run and return `github_pr_created=false`. If an `--apply` flag exists, leave it blocked/not implemented until Michael explicitly authorizes real PR creation in a later slice.

Use the direct-run import pattern from `scripts/ingest_agy_result.py` so scripts work from `cwd=/tmp`:

```python
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
```

## API endpoints

Add real endpoints that read persisted completed-work rows, not fixture/demo data:

```text
GET  /api/agy/merge-backlog
GET  /api/agy/merge-backlog/{completed_work_id}
POST /api/agy/merge-backlog/{completed_work_id}/verify

GET  /api/gateway/agy/merge-backlog
GET  /api/gateway/agy/merge-backlog/{completed_work_id}
POST /api/gateway/agy/merge-backlog/{completed_work_id}/verify
```

Unknown completed-work IDs must return 404. Responses should include explicit non-claims such as `auto_merge=false`, `production_deploy=false`, `github_pr_created=false`, and `agy_dispatch=false`.

## Dashboard hook

A small additive card is acceptable when it preserves the durable dashboard shell:

```text
data-proof-marker="agy-merge-backlog-card"
fetch(`${API_PREFIX}/agy/merge-backlog?limit=1`)
```

Show latest action, verification gate/lane, dry-run PR branch, and auto-merge disabled. Do not render mock rows or add auto-merge controls.

## Verification

Use `/tmp/fred-agy-clean-pr-verification-gate-verify.log` for full output and a tempfile verifier named `/tmp/hermes-verify-agy-merge-backlog-*.py`. Keep chat output compact.

Minimum command block:

```bash
python3 -m py_compile \
  prismatic/completed_work_gate.py \
  prismatic/agy_completed_work.py \
  prismatic/agy_merge_backlog.py \
  prismatic/gateway/server.py \
  scripts/ingest_agy_result.py \
  scripts/agy_merge_backlog.py
python3 -m pytest -q \
  tests/test_completed_work_gate.py \
  tests/test_agy_completed_work.py \
  tests/test_agy_merge_backlog.py \
  tests/test_agy_merge_backlog_api.py \
  tests/test_budget_caps.py
node --check /tmp/hermes-dashboard-inline-agy-merge-backlog.js
```

Temp smoke should:

1. create temp HOME/state/db;
2. ingest a merge-ready completed-work packet;
3. call CLI `classify`, `plan-pr`, `verify`, and dry-run `open-pr`;
4. call API list/detail/verify via TestClient or local server;
5. verify `eligible_for_auto_merge=false` and `github_pr_created=false`;
6. verify unknown ID returns 404;
7. verify no production deploy/AGY dispatch side effects;
8. remove the verifier script and stale `/tmp/hermes-verify-*` paths named by the guard.

If TestClient emits warnings before JSON, parse the last JSON line in the smoke rather than treating warning output as product failure. If the API subprocess lacks FastAPI, run that subprocess with the Prismatic stable venv Python instead of weakening the API proof.

Compact proof shape:

```text
COMMAND=<exact command(s)>
RESULT=PASS
LOG=/tmp/fred-agy-clean-pr-verification-gate-verify.log
SCOPE=AGY merge backlog / clean PR dry-run plan / lane verification gate / API / dashboard hook
AD_HOC_OR_CANONICAL=ad-hoc targeted + PR CI if available
NOT_CLAIMING=auto_merge,bulk_agy_dispatch,overnight_autopilot_ready,production_deploy,canonical_full_suite_green,actual_github_pr_created
MARKER=AGY_CLEAN_PR_AND_VERIFICATION_GATE_OK
cleanup=PASS
```

## Pitfalls

- Do not claim this gate creates or updates real GitHub PRs; it only plans dry-run PR actions unless explicitly authorized later.
- Do not let `open_or_update_pr` imply auto-merge eligibility. `eligible_for_auto_merge` is false in this slice.
- Do not treat a merged foundation/ingestion stack as still stacked; check real PR state and rebase/branch from `origin/main` when landed.
- Do not stream pytest/build/API logs into chat. Keep logs in `/tmp` and return compact proof.
- When stale guards name old verifier files such as `/tmp/hermes-verify-agy-merge-backlog-smoke.py`, include those exact paths in `changed_paths_checked` and prove they are absent after cleanup.
