# Governance Dashboard GCP / Model / Subscription Quota Wiring

Use this reference when the Quotas tab calls `/api/quota` or `/api/quota/poll` but has no live normalized quota/cost/subscription read model.

## Dashboard contracts

```text
GET  /api/quota
POST /api/quota/poll
```

## Real state sources

Preserve and normalize existing primitives:

- `prismatic.vertex_telemetry.VertexBillingLedger` for Vertex/GCP quota snapshots and poll errors.
- `prismatic.credit_tracker.AIUltraCreditTracker` for Google AI Ultra 25,000 monthly AI credit pool.
- `prismatic.cost.tracker.cost_summary` for local per-dispatch cost DB.
- `telemetry_credit_ledger` for session/credit/API usage observations.
- Dashboard quota control ledger under `PRISMATIC_STATE_DIR` for poll intent.

Support isolated tests/smokes with:

```text
PRISMATIC_STATE_DIR=/tmp/.../state
PRISMATIC_EVENT_ROUTER_DB=/tmp/.../state/event_router.db
PRISMATIC_COST_DB=/tmp/.../cost.db
```

## Quota classes to track

Include subscription/session/API quota entries even when exact provider telemetry is unavailable:

```text
Google Jules / Jules CLI: 300 sessions/day
AGY CLI / Google Antigravity: daily and weekly session caps; exact numeric cap unknown unless provider telemetry provides it
Google AI Ultra AI Credits: 25,000 credits/month for AGY SDK Gemini Omni, Veo, Lyria, etc. ($199/mo subscription)
GCP Google Cloud credits: $100/month from Google AI Ultra
OpenAI Codex: $200/mo subscription
Minimax: $50/mo subscription
DeepSeek: standard metered API rates
```

## Normalized read model

`GET /api/quota` should include:

```text
source
generated_at
snapshot_at
snapshot_age_sec
last_poll
empty
pressure
status_counts
current
provider_pressure
subscription_pressure
model_pressure
cost_summary
ai_ultra_credits
recent_events
control_actions
evidence
```

Each `current` item should include, where known:

```text
id
display_name
provider
model
region
metric_type / quota_type
period
subscription
monthly_cost_usd
usage
limit_value
remaining_value
usage_pct
remaining_pct
status
exhausted
unit
reset_time
last_recorded_at
source
notes
```

## Control safety

`POST /api/quota/poll` should:

- record operator intent under `PRISMATIC_STATE_DIR`
- emit `/api/timeline` item with source `QuotaControl`
- optionally publish EventBus event `dashboard.quota.poll`
- return empty stdout/stderr for dashboard compatibility
- never shell out from the browser request
- only call an in-process provider poll if explicitly allowlisted and safe; otherwise intent-only is correct

## Dashboard requirements

Quota tab should render:

- loading state
- empty state
- visible API error state
- source/evidence line
- AI Ultra credit summary
- cost summary
- known quota item count
- subscription/session/API quota cards
- recent quota/poll errors
- last poll intent
- no `mockQuota`
- no fake sync success or terminal output

## Verification pattern

Create `/tmp/hermes-verify-*.py` and report as ad-hoc targeted verification, not suite green.

Verifier should check:

```text
changed paths exist
py_compile server + quota adapter + tests
node --check extracted dashboard script
focused pytest for Quota API
GET /api/quota normalized shape with isolated Vertex/cost/credit state
POST /api/quota/poll emits QuotaControl timeline item
POST /api/quota/poll returns stdout/stderr as empty strings
dashboard contains live fetch/action wiring, loading/empty/error states, subscription/cost/credit panels, no mockQuota
cleanup removes verifier and temp state
```

Live smoke pattern:

1. Create isolated temp `event_router.db` and `cost.db`.
2. Seed `VertexBillingLedger.record_quota_snapshot` plus `telemetry_credit_ledger` rows for Jules session and Google AI Ultra credits.
3. Start uvicorn with isolated env vars.
4. Hit `/dashboard`, `GET /api/quota`, `POST /api/quota/poll`, and `/api/timeline?source=QuotaControl`.
5. Kill process and remove temp state.
