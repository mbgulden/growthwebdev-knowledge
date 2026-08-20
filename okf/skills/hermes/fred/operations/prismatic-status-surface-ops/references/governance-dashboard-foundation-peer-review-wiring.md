# Governance Dashboard Foundation / Peer Review Wiring

Use this reference when the Foundation tab has Jules/Ned/AGY cards and browser buttons but no live peer-review read model or audit-safe control endpoint.

## Dashboard contracts

```text
GET  /api/gateway/foundation/peer_review
POST /api/gateway/foundation/control/{action}
```

## Read model pattern

Use an adapter like `prismatic/foundation_status.py` to derive status from existing run evidence:

- `AgentRunRecordStore` runs for agents `jules`, `ned`, and `agy`
- dashboard Foundation control state under `PRISMATIC_STATE_DIR`
- no fake peer-review rows or hardcoded success data

The normalized response should include:

```text
source
empty
jules_count / ned_count / agy_count
counts
status_counts
limits + individual limits
current_agy_reviewer
reviewer_reason
last_activity_at
recent_activity
last_control_action
control_actions
evidence
```

## Control safety

`POST /api/gateway/foundation/control/{action}` must be allowlisted. Current safe actions:

```text
orchestrate
sync
```

The endpoint should:

- reject unknown actions with HTTP 400 and `allowed_actions`
- persist operator intent to a Foundation state file under `PRISMATIC_STATE_DIR`
- emit `/api/timeline` item with source `FoundationControl`
- optionally publish EventBus event `dashboard.foundation.{action}`
- never shell out directly from the browser request
- return empty stdout/stderr if retained for dashboard compatibility

## Dashboard requirements

Foundation tab should render:

- loading state
- empty state: no Jules/Ned/AGY run evidence
- visible API error state
- source/evidence line
- last control action
- no `mockFoundation`
- no fake terminal stdout/stderr success output

## Verification pattern

Create `/tmp/hermes-verify-*.py` and report as ad-hoc targeted verification, not suite green.

Verifier should check:

```text
changed paths exist
py_compile server + foundation adapter + tests
node --check extracted dashboard script
focused pytest for Foundation API
GET /api/gateway/foundation/peer_review normalized shape with isolated state
POST /api/gateway/foundation/control/sync emits FoundationControl timeline item
POST /api/gateway/foundation/control/orchestrate emits FoundationControl timeline item
invalid control action returns 400
dashboard contains live fetch/action wiring, loading/empty/error states, no mockFoundation
cleanup removes verifier and temp state
```

For live smoke, start uvicorn with isolated `PRISMATIC_STATE_DIR`, hit `/dashboard`, `GET /api/gateway/foundation/peer_review`, `POST /api/gateway/foundation/control/sync`, then verify `/api/timeline?source=FoundationControl`; kill the temp process and remove temp state.
