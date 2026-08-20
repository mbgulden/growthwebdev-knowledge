# Governance Dashboard Queue / Webhook / Retry Detail Wiring

Use this reference when the Ingestion Queue dashboard shows static queue depths, fake retry candidates, fake dead-letter items, or unsafe retry/purge controls.

## Dashboard contracts

```text
GET /api/gateway/webhooks/queue/detail
GET /api/gateway/webhooks/queue/{task_id}
POST /api/gateway/webhooks/queue/retry/{task_id}
POST /api/gateway/webhooks/queue/purge
```

## Real state sources

Normalize existing evidence only:

- `AgentRunRecordStore` / `run_records.json`
- gateway webhook counters (`_webhook_counters`)
- dispatcher status from `ingestion_status.dispatcher_status_payload(...)`
- recovery status from `ingestion_status.recovery_status_payload(...)`
- queue control ledger from `dashboard_queue_controls.json`
- timeline from `timeline.list_timeline(...)`

Do not shell out from browser requests. Retry/purge dashboard controls are audit-only unless a safe in-process queue mutation already exists and is explicitly allowlisted.

## Normalized queue detail shape

`GET /api/gateway/webhooks/queue/detail` should include:

```text
source
generated_at
empty
queue_depths
items
retry_candidates
dead_letter
skipped
processing
completed_recently
failed_recently
webhook_counters
dispatcher_context
recovery_context
recent_timeline
evidence
```

Each item should include:

```text
id
run_id
issue_id
issue_url
agent
status
dispatch_status
retryable
dead_lettered
skipped
processing
attempts
last_error
failure_category
started_at
completed_at
last_activity_at
source
evidence
```

## Classification rules

```text
processing: running/processing/active run status
completed_recently: completed/success within 24h
failed_recently: failed/error/blocked within 24h
retryable: failed and not dead-lettered/skipped
dead_lettered: error/evidence/status mentions dead_letter, dead-letter, or dlq
skipped: status or evidence mentions skipped
failure_category: ingest_auth / ingest_parse / routing / artifact / state_sync / execution / none based on run error/evidence text
```

## Controls

`POST /api/gateway/webhooks/queue/retry/{task_id}` and `POST /api/gateway/webhooks/queue/purge` must:

- validate/allowlist the action
- record operator intent in dashboard queue state
- emit timeline source `QueueControl`
- optionally publish EventBus event
- return `stdout: ""` and `stderr: ""`
- never call shell/systemctl/git/gh/docker/agent CLIs from browser request

## Dashboard UI requirements

The queue tab should render:

- loading state
- empty state
- visible API error state
- queue depth chips
- retry candidates
- dead-letter/skipped items
- processing/completed/failed recent items
- per-item detail drill-down backed by `/api/gateway/webhooks/queue/{task_id}`
- source/evidence line
- retry/purge controls wired only to safe endpoints
- no mock queue fallback

## Verification pattern

Create `/tmp/hermes-verify-*.py` and report as ad-hoc targeted verification, not suite green.

Seed isolated `PRISMATIC_STATE_DIR` with run records covering:

```text
pending
processing/running
completed recent
failed retryable
failed dead_letter/dlq
skipped
```

Verifier checks:

```text
changed paths exist
py_compile changed Python files
node --check extracted dashboard JS
focused pytest passes
GET /api/gateway/webhooks/queue/detail normalized shape and classifications
GET /api/gateway/webhooks/queue/{task_id} detail shape
POST retry emits QueueControl timeline and empty stdout/stderr
POST purge emits QueueControl timeline and empty stdout/stderr
dashboard has live queue detail/detail/action wiring
dashboard has loading/empty/error states
dashboard has no mock queue fallback
cleanup removes verifier/temp state
```

Live smoke pattern:

1. Create isolated temp state and seed `run_records.json`.
2. Start uvicorn with `PRISMATIC_STATE_DIR`.
3. Hit `/dashboard`, `/api/gateway/webhooks/queue/detail`, and one `/api/gateway/webhooks/queue/{task_id}`.
4. POST retry and purge.
5. Verify `/api/timeline?source=QueueControl` contains QueueControl events.
6. Kill gateway and remove temp state.
