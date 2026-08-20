# Governance Dashboard Merge Pipeline Wiring

Use this reference when the Merge Pipeline tab has pending/history tables or merge controls but no live merge read model or audit-safe control endpoint.

## Dashboard contracts

```text
GET  /api/gateway/merge/status
POST /api/gateway/merge/control/{action}
```

## Real state source

The existing merge primitive is the merge-pipeline state JSON, defaulting to:

```text
/home/ubuntu/.prismatic/merge-pipeline/state_v6.json
```

Allow tests/smokes to override with:

```text
PRISMATIC_MERGE_STATE_PATH=/tmp/.../state_v6.json
PRISMATIC_STATE_DIR=/tmp/.../state
```

Use an adapter like `prismatic/merge_status.py`; do not replace real merge state with fake rows.

## Normalized read model

`GET /api/gateway/merge/status` should include:

```text
source
state_path
generated_at
empty
status
pending_count / open_count
merged_count
mergeable_count
blocked_count
conflict_count
checks {passed, failed, unknown}
duplicate_families
duplicate_family_count
pending
merged
last_scan
last_apply
latest_activity_at
drift_detected
last_control_action
control_actions
evidence
```

Use existing governance triage (`MERGE_BACKLOG_TRIAGE`) for canonical duplicate families/winners when available.

## Control safety

`POST /api/gateway/merge/control/{action}` must be allowlisted. Current safe actions:

```text
refresh
promote
hold
```

The endpoint should:

- reject unknown actions with HTTP 400 and `allowed_actions`
- persist operator intent under `PRISMATIC_STATE_DIR`
- emit `/api/timeline` item with source `MergeControl`
- optionally publish EventBus event `dashboard.merge.{action}`
- never shell out, run git, run gh, merge PRs, or mutate branches from the browser request
- return empty stdout/stderr only for dashboard compatibility

## Dashboard requirements

Merge tab should render:

- loading state
- empty state
- visible API error state
- source/evidence line
- open / mergeable / blocked / conflict counts
- checks passed/failed/unknown
- duplicate-family/canonical-winner list
- last control action
- no `mockMerge`
- no fake terminal stdout/stderr success output
- no claim that browser controls auto-merge to staging

## Verification pattern

Create `/tmp/hermes-verify-*.py` and report as ad-hoc targeted verification, not suite green.

Verifier should check:

```text
changed paths exist
py_compile server + merge adapter + tests
node --check extracted dashboard script
focused pytest for Merge API
GET /api/gateway/merge/status normalized shape with isolated merge state
POST /api/gateway/merge/control/hold emits MergeControl timeline item
POST /api/gateway/merge/control/promote emits MergeControl timeline item
POST /api/gateway/merge/control/refresh emits MergeControl timeline item
invalid control action returns 400
dashboard contains live fetch/action wiring, loading/empty/error states, duplicate-family panel, no mockMerge
cleanup removes verifier and temp state
```

For live smoke, start uvicorn with isolated `PRISMATIC_STATE_DIR` and `PRISMATIC_MERGE_STATE_PATH`, hit `/dashboard`, `GET /api/gateway/merge/status`, `POST /api/gateway/merge/control/hold`, then verify `/api/timeline?source=MergeControl`; kill the temp process and remove temp state.
