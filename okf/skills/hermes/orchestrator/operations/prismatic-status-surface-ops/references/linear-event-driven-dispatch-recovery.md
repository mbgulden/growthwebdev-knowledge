# Linear Event-Driven Dispatch Recovery

Use this reference when Prismatic dispatch is burning Linear API quota, the old broad poller is disabled/gated, or Michael asks to recover the Linear webhook → durable queue → bounded drain path without re-enabling uncontrolled polling.

## Hard boundaries

- Do **not** re-enable the old 30-second broad poller as the primary mechanism.
- Do **not** create `/home/ubuntu/.prismatic/allow-poll-dispatcher` unless Michael explicitly approves restarting the gated poll dispatcher.
- Keep the user-systemd kill switch in place: `ConditionPathExists=/home/ubuntu/.prismatic/allow-poll-dispatcher`.
- Do not enable `prismatic-webhook-drain.service`/timer until the unit points at the durable runtime checkout or stable installed entrypoint, not a mutable dev worktree.
- Do not make live Linear mutations for fixture proof. Use local fixture webhooks and stub the dispatch side effect.
- Do not claim assigned-agent dispatch recovery until resolver/preflight/exact-agent wake behavior is implemented and proven separately.

## Slice markers and scope

### `LINEAR_RATE_LIMIT_CIRCUIT_BREAKER_OK`

Target: every Linear GraphQL call passes through a shared circuit breaker that:

- records Linear request-count headers;
- detects GraphQL `RATELIMITED` errors;
- persists cooldown state;
- makes dispatcher broad scans skip while cooldown is active;
- exposes dashboard/API state.

Focused proof should include py_compile, targeted pytest for cooldown/no-network behavior, API readback, and no live Linear calls.

### `DISPATCHER_POLLING_BUDGET_OK`

Target: fallback polling is cheap, bounded, cached, and visible.

Prove:

- per-cycle Linear call cap;
- TTL cache for label scans;
- cadence skips for broad scan families;
- `/api/gateway/dispatcher/status` and `/api/gateway/linear/rate-limit` include `polling_budget`;
- old poller process is still `0`;
- dispatcher unit is disabled/gated;
- allow-file absent;
- dispatcher log does not grow during idle proof.

### `LINEAR_WEBHOOK_QUEUE_ACTIVE_OK`

Target: durable Linear webhook queue path is active.

Required behavior:

```text
fixture Linear webhook event
→ durable row in linear_webhook_queue.db
→ bounded drain reads it
→ exactly one dispatch attempt or intentional no-op decision
→ status transition persisted
→ API/dashboard show source, queue depth, latest event, and drain result
```

Use `prismatic.ingestion_queue` as the DB adapter when present. Production default should resolve to `~/.prismatic/db/linear_webhook_queue.db`; tests should set isolated `PRISMATIC_STATE_DIR`.

Expected status API keys:

```text
marker=LINEAR_WEBHOOK_QUEUE_ACTIVE_OK
source=linear_webhook_queue.db
queue_depth
pending_count
status_counts
latest_event_identifier
latest_event_status
last_drain_at
last_drain_result
last_drain_counts
```

## Durable queue implementation notes

- `POST /api/gateway/linear` and `POST /webhooks/linear` should enqueue relevant Linear events before/alongside EventBus publish.
- Idempotency should use the Linear event/webhook id (`event_id`, `webhookId`, or payload id) and prevent duplicate dispatch work on replay.
- Store `identifier`, `event_type`, `action`, `received_at`, `raw_json`, `dispatch_status`, and `agent_name` when available.
- Retry is a real mutation: set terminal row back to `pending`, clear `processed_at`, and return `updated=1` for a real row.
- Purge is a terminal-only mutation; keep pending/processing rows.
- Normalize `failed:*` to failed in stats, but preserve concrete status where useful for row details.

## Bounded drain proof pattern

For fixture proof, load the real drainer file and call its shared `drain(args, dispatch_fn=...)` path:

```python
import argparse, importlib.util
spec = importlib.util.spec_from_file_location('drain_webhook_queue', repo / 'scripts/drain_webhook_queue.py')
drainer = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(drainer)

calls = []
def fake_dispatch(*, identifier: str):
    calls.append(identifier)
    return {'ok': True, 'message': 'fixture only; no Linear mutation'}

args = argparse.Namespace(
    max=1,
    dry_run=False,
    stale_only=False,
    backfill=False,
    reset=False,
    since=None,
    until=None,
)
rc = drainer.drain(args, dispatch_fn=fake_dispatch)
```

Assert exactly one call for the fixture identifier and a persisted terminal status such as `dispatched` or an intentional `no_op`.

## Live/runtime proof ladder

After merge/deploy:

1. Runtime HEAD is the merge commit.
2. `python3 -m py_compile prismatic/ingestion_queue.py prismatic/gateway/server.py scripts/drain_webhook_queue.py` passes in runtime checkout.
3. POST a local fixture webhook to `http://127.0.0.1:9000/api/gateway/linear`.
4. Read back `/api/gateway/webhooks/queue` and `/api/gateway/webhooks/queue/status`.
5. Run bounded drainer with stub dispatch scoped to the fixture window; do not call Linear.
6. Verify status transition and drain result.
7. Verify old broad poller remains gated:
   - process count for `prismatic-engine serve` old poller is `0`;
   - `systemctl --user is-enabled prismatic-dispatcher.service` is disabled;
   - `ConditionPathExists=/home/ubuntu/.prismatic/allow-poll-dispatcher` drop-in exists;
   - allow-file absent;
   - dispatcher log no-growth window;
   - gateway/consumer/merge services active.

## Compact stale-guard packet

If Hermes stale guard repeats an old mobile verifier failure, do not argue with it. Emit a fresh compact `/tmp/hermes-verify-*` proof that includes:

```text
CANONICAL_TEST_LINT_BUILD_COMMAND=<exact focused command>
AD_HOC_VERIFICATION=PASS
RESULT=PASS
LOG=/tmp/<proof>.log
SCOPE=<exact slice scope>
MARKER=<slice marker>
changed_paths_checked=<exact paths listed by stale guard, including stale /tmp path>
runtime_head=<short sha when deployed>
queue_status_api=200 marker/source/... fields present
old_poller_processes=0
dispatcher_user_unit_enabled=disabled
allow_file_absent=true
pytest_summary=<actual pytest summary>
NOT_CLAIMING=event_driven_dispatch_complete,assigned_agent_dispatch_complete,Linear_mutations_applied,canonical_full_suite_green,old_poller_reenabled,timer_enabled
cleanup=PASS
fresh_verifier_absent=true
stale_<named>_verifier_absent=true
stale_mobile_verifier_absent=true
```

Label this as ad hoc targeted, not canonical full-suite green.

## Reporting boundaries

Use narrow non-claims explicitly:

```text
NOT_CLAIMING=event_driven_dispatch_complete,assigned_agent_dispatch_complete,Linear_mutations_applied,canonical_full_suite_green,old_poller_reenabled,timer_enabled
```

Do not start the next slice until the current marker is proven.