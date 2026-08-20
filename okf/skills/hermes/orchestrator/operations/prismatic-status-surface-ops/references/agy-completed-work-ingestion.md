# AGY completed-work ingestion and stale-guard proof pattern

Use after the bounded AGY completed-work gate exists and Michael asks to persist real completed AGY result packets rather than demo/fixture gate state.

## Scope boundary

Target marker:

```text
AGY_COMPLETED_WORK_INGESTION_OK
```

This slice should implement persisted ingestion only. Do **not** implement or claim the next packets until requested:

```text
AGY_CLEAN_PR_CREATE_UPDATE_OK
AGY_PR_VERIFICATION_GATE_OK
```

Non-claims for proof packets should explicitly include auto-merge / clean-PR / PR-verification / production deploy / canonical-suite boundaries.

## Implementation pattern

1. Branch from the current completed-work gate base if it is still stacked (for example PR #296 branch), not from `main` unless the gate has landed.
2. Patch the gate proof contract so `non_claims: [...]` is canonical and legacy `not_claiming` is only backward-compatible input. This avoids false-positive validators treating negated strings like `auto_merge` as positive claims.
3. Add `prismatic/agy_completed_work.py`:
   - SQLite store under `PRISMATIC_STATE_DIR` or `PRISMATIC_AGY_COMPLETED_WORK_DB`;
   - deterministic `agy-cw-<hash>` row IDs based on packet source/proof identity;
   - persist packet JSON, gate JSON, normalized non-claims, markers, classification, merge eligibility, proof result/marker;
   - feed every accepted row through `classify_completed_work()` before persistence.
4. Add `scripts/ingest_agy_result.py`:
   - accepts packet path or `-` stdin;
   - optional `--db`, `--dirty-source`, `--source-is-stale`, repeated `--conflict`;
   - prints JSON `{status: ok, completed_work: ...}`.
5. Add real API endpoints plus gateway aliases:

```text
POST /api/agy/completed-work/ingest
GET  /api/agy/completed-work
GET  /api/agy/completed-work/{completed_work_id}
POST /api/gateway/agy/completed-work/ingest
GET  /api/gateway/agy/completed-work
GET  /api/gateway/agy/completed-work/{completed_work_id}
```

6. If touching the dashboard, switch minimal status cards from fixture/demo endpoints to real persisted rows, e.g. `/api/gateway/agy/completed-work?limit=1`. Keep the shell intact and preserve existing mobile/dashboard proof markers.

## Tests to add

- Store persists merge-ready row and gate state.
- Store upserts deterministic IDs.
- Store persists blocked/failing gate classifications.
- List returns newest first.
- `non_claims` list avoids false-positive claim validation.
- Legacy `not_claiming` is still accepted and normalized.
- Existing gate schema test asserts `non_claims` exists and `not_claiming` is absent from the minimum packet schema.

## Focused verifier

Use a fresh tempfile-created `/tmp/hermes-verify-*` script and remove it before reporting. Include exactly the changed paths in `changed_paths_checked` if a stale guard repeats an old proof.

Minimum proof:

```text
python3 -m py_compile prismatic/completed_work_gate.py prismatic/agy_completed_work.py prismatic/gateway/server.py scripts/ingest_agy_result.py
python3 -m pytest -q tests/test_completed_work_gate.py tests/test_agy_completed_work.py tests/test_budget_caps.py
node --check /tmp/hermes-dashboard-inline-agy-completed-work-ingestion.js
```

Then prove behavior with temp HOME/state:

```text
CLI scripts/ingest_agy_result.py persists merge_ready row with AGY_COMPLETED_WORK_INGESTION_OK
POST /api/gateway/agy/completed-work/ingest -> accepted row
GET /api/gateway/agy/completed-work -> listed row
GET /api/gateway/agy/completed-work/{id} -> same row
GET /api/agy/completed-work/{id} -> local alias matches gateway payload
```

Compact proof block:

```text
COMMAND=tempfile-created /tmp/hermes-verify-agy-completed-work-ingestion-*.py
RESULT=PASS
LOG=/tmp/fred-agy-completed-work-ingestion-verify.log
SCOPE=AGY completed-work ingestion persistence/API/CLI/dashboard real rows
AD_HOC_OR_CANONICAL=ad-hoc targeted
NOT_CLAIMING=auto_merge,clean_pr_create_update,pr_verification_gate,production_deploy,canonical_full_suite_green
cleanup=PASS
MARKER=AGY_COMPLETED_WORK_INGESTION_OK
```

## PR hygiene

- Auto-checkpoint commits may split the branch; squash to one clean `[Fred] ... (#ISSUE)` commit relative to the stacked base before final proof.
- If GitHub does not trigger checks for a non-main stacked PR, report `checks=[] / no checks triggered` plainly and rely on local proof; do not call it CI green.
- Release Antigravity locks after verification/PR.
