# Dashboard task admission gate pattern

Use this when Prismatic needs to admit a new producer/task through the dashboard/event-driven control plane without reintroducing cron, Telegram, LLM, or Linear polling.

## Durable contract

- Treat admission as **durable intent only**. The endpoint must not launch a producer, contact Linear/GitHub, restart services, or publish into an incompatible legacy consumer path.
- Use a dedicated admission ledger + outbox + append-only audit table; avoid generic event bus paths that can acknowledge failed persistence or be discarded by the current consumer.
- Validate an exact immutable tuple: `task_id`, `producer_identity`, `writer_cap=1`, `base_commit`, `base_tree`, `task_file_sha256`, canonical worktree, relative task file, created-at UTC timestamp, and idempotency key.
- Reject unknown fields and duplicate JSON keys. Keep canonical and packaged schemas in parity.
- Externalize allowlists/policy for producer identities and canonical worktree roots; do not hard-code one fixture as policy.
- Idempotency must be deterministic: exact replay returns the original durable record; changed replay fails closed and creates no duplicate outbox event.

## Dashboard/operator handling

- Reconnect into the existing canonical dashboard shell; do not create a mini fallback dashboard as the primary experience.
- Label the panel plainly: records durable intent only; producer launch is not performed.
- Bearer/operator tokens are transient UI inputs only: password field, cleared in `finally`, never stored in local/session storage, rendered proof, URLs, responses, SQLite, logs, or screenshots.
- Avoid hard-coded route-prefix assumptions. Rendered browser proof must exercise the actual JS path and verify the UI calls the correct API route.

## Verification packet

Minimum proof before claiming readiness:

```text
COMMAND=<focused admission tests + canonical tests/builds/browser proof>
RESULT=<PASS|FAIL|BLOCKED>
LOG=<paths and hashes>
SCOPE=task admission API + durable ledger/outbox/audit + dashboard panel
AD_HOC_OR_CANONICAL=<state honestly>
NOT_CLAIMING=producer launch, deploy/restart, Linear/GitHub side effects, full-suite green unless actually run
MARKER=DASHBOARD_TASK_ADMISSION_GATE_OK or *_PARTIAL
```

Include DB checks for one admission/outbox/audit row, pending dedicated outbox topic, exact replay, `launch_performed=false`, and token absence from the DB bytes. Add rendered desktop/mobile proof when UI is touched.

## Pitfalls from session

- A browser-rendered check caught a route mismatch that unit/static checks missed (`/api/gateway/...` vs `/api/dashboard/...`). Always test the browser submit path, not just endpoint tests.
- If tool-call iteration caps interrupt the run, final reporting must clearly mark the work as partial and list the continuation sequence instead of implying canonical acceptance.
