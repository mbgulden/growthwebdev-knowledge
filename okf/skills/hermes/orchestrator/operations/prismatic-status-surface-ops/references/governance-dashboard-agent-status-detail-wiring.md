# Governance Dashboard Agent Status / Detail Wiring

Use this reference when Dashboard Summary or Agent Detail shows hardcoded agent cards, `mockAgents`, `mockWorkers`, fake online states, or static queue/activity labels.

## Dashboard contracts

```text
GET /api/gateway/agents/status
GET /api/gateway/agents/{agent_id}
```

## Real state sources

Normalize existing evidence only:

- `AgentRunRecordStore` / `run_records.json`
- optional live agent registry from `PRISMATIC_AGENT_REGISTRY`
- `ingestion_status.queue_payload(...)`
- `ingestion_status.recovery_status_payload(...)`
- `timeline.list_timeline(...)`
- webhook counters / health context already in gateway

Do not shell out for status from browser requests. Do not infer health from process existence alone.

## Normalized status shape

`GET /api/gateway/agents/status` should include:

```text
source
generated_at
empty
status_counts
agents
workers
queues
recent_activity
awaiting_user_feedback
completed_recently
churning_or_launch_failing
idle
queue_starved
evidence
```

Each agent/worker item should include:

```text
id
name
role
kind
status
phase
current_issue
current_issue_url
current_branch
current_workspace
pid
service_name
queue_depth
last_run_id
last_activity_at
last_success_at
last_error_at
last_error
awaiting_user_feedback
completed_recently
churning_or_launch_failing
idle_reason
queue_starved_reason
source
evidence
```

## Classification rules

Keep phase distinctions explicit:

```text
active: latest run/status evidence is running/processing/active
queue_starved: pending/queued run exists without active execution evidence
awaiting_user_feedback: run/error/evidence text mentions awaiting user feedback/approval
completed_recently: latest completed run is within 24h
errored: latest run failed/errored/blocked or has error_message
churning: run/evidence text mentions churn/restart loop/crashloop
launch_failing: run/evidence text mentions launch failure
idle: known agent exists but no active/pending/error/recent-completion evidence
unknown: no usable evidence
```

Important:

- Do not collapse idle and queue-starved.
- Do not call a worker healthy just because its process exists.
- Do not call a worker broken just because it has no assigned work.

## Detail shape

`GET /api/gateway/agents/{agent_id}` should include:

```text
agent
recent_runs
recent_timeline
queue_context
health_context
evidence
```

## Dashboard UI requirements

Replace `mockAgents`/`mockWorkers` with:

- loading state while fetching
- empty state if no known agents/workers
- visible API error state
- status count chips
- live agent/worker cards
- badges for Awaiting User Feedback, Completed Recently, Queue Starved, Churning / Launch Failing, Error
- source/evidence line
- detail panel backed by `/api/gateway/agents/{agent_id}`
- no fake fallback cards or fake last-run timestamps

## Verification pattern

Create `/tmp/hermes-verify-*.py` and report as ad-hoc targeted verification, not suite green.

Verifier should seed isolated `PRISMATIC_STATE_DIR` and `PRISMATIC_AGENT_REGISTRY` with run records covering:

```text
active
idle
queue_starved
awaiting_user_feedback
completed_recently
errored
churning or launch_failing
```

Check:

```text
changed paths exist
py_compile changed Python files
node --check extracted dashboard JS
focused pytest passes
GET /api/gateway/agents/status normalized shape and classifications
GET /api/gateway/agents/{agent_id} detail shape
dashboard has live status/detail fetch wiring
dashboard has loading/empty/error states
dashboard has no mockAgents/mockWorkers/fake fallback cards
cleanup removes verifier/temp state
```

Live smoke pattern:

1. Create isolated temp state + agent registry.
2. Seed `run_records.json` with representative statuses.
3. Start uvicorn with `PRISMATIC_STATE_DIR` and `PRISMATIC_AGENT_REGISTRY`.
4. Hit `/dashboard`, `/api/gateway/agents/status`, and one `/api/gateway/agents/{agent_id}`.
5. Verify dashboard HTML contains live fetch/detail wiring and no `mockAgents`.
6. Kill gateway and remove temp state.
