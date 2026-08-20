# Ingestion Queue Drain Smoke + Operator Semantics Proof

Use this reference when the durable ingestion queue already exists but Michael/Kai ask for the missing proof layer before claiming readiness.

## Boundary

Do **not** claim `DASHBOARD_DISPATCH_INGESTION_READY_OK` from dashboard/queue work alone. That marker requires both:

1. `INGESTION_QUEUE_DRAIN_SMOKE_OK`; and
2. a real one-task AGY proof, usually `GRO-3837`, with nonzero input/output tokens and `DONE: GRO-3837 ...`.

If only the queue proof passes, the honest marker is:

```text
INGESTION_QUEUE_DRAIN_SMOKE_OK
```

## Required contract verifier

Run the dashboard contract in the dependency-complete venv when plain `python3` lacks FastAPI/TestClient:

```bash
cd /home/ubuntu/work/prismatic-engine
/home/ubuntu/.prismatic/venv_stable/bin/python3 scripts/verify-governance-dashboard-contract.py
```

Accept the script's current output shape:

```text
AD_HOC_VERIFICATION: PASS
scope: Governance dashboard regression contract: all tabs use live adapters, no mock/static regressions
failures: []
```

It may not emit the literal `GOVERNANCE_DASHBOARD_CONTRACT_OK`; report the actual marker honestly.

## Executable queue drain smoke pattern

Create a fresh `/tmp/hermes-verify-*.py` script. The smoke should:

1. `tempfile.mkdtemp(prefix="hermes-queue-state-", dir="/tmp")`.
2. Set `PRISMATIC_STATE_DIR` to that temp state.
3. Import real `prismatic.ingestion_queue`.
4. Enqueue a Linear-like Issue event with an `agent:*` label.
5. Verify `queue_payload().source == "linear_webhook_queue.db"` and pending depth is nonzero.
6. Import real `scripts/drain_webhook_queue.py`.
7. Call the shared `drain(args, dispatch_fn=fake_dispatch)` path, not a fake queue implementation.
8. Stub only the dispatch side effect; collect the identifier it would dispatch.
9. Verify status transitioned to `completed`/`dispatched` and stats reflect it.
10. Verify `retry_task(id)` resets the terminal row to `pending`.
11. Add a separate `processing` row, mark the first row terminal, run `purge_queue()`, and verify purge deletes only terminal rows while preserving `processing`.
12. Print exact proof lines and end with `INGESTION_QUEUE_DRAIN_SMOKE_OK`.
13. Remove both the temp state dir and verifier script.

Important implementation details learned from repeated smoke-wrapper failures:

- `scripts/` is not necessarily importable as a Python package. Load the drainer file directly when running from a temp verifier:

```python
import importlib.util
spec = importlib.util.spec_from_file_location(
    "drain_webhook_queue",
    repo / "scripts/drain_webhook_queue.py",
)
drainer = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(drainer)
```

- `scripts/drain_webhook_queue.py` has `main()` with zero arguments and parses `sys.argv`. For isolated proof, call the shared function with the **complete** argparse namespace shape expected by the script:

```python
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

- The dispatch stub should match the script's call shape (`dispatch_fn(identifier=ident)`). Either normal or keyword-only signatures are safe:

```python
def fake_dispatch(identifier: str):
    calls.append(identifier)
    return {"status": "ok", "message": "stub dispatcher accepted smoke row"}
```

- The drainer prints `✓ <id> dispatched`, but the queue adapter may normalize the terminal row as `dispatch_status="completed"`. Verify the observed queue payload/status, not only the printed word.
- `prismatic.ingestion_queue` may not expose a `now_ts()` helper; use stdlib timestamps such as `time.time()` when directly seeding rows in the verifier.

## Dashboard operator semantics

For Ingestion Queue UI changes, verify these visible/operator-facing semantics:

- source is visible: `source = linear_webhook_queue.db`;
- retry action label is honest: `Reset to pending`;
- retry helper text says it does not prove immediate dispatcher execution;
- purge confirmation says pending/processing work will be kept;
- terminal/stale/live row counts are visible;
- recovery/DLQ state is separate from generic failed queue rows.

Recommended marker checks in the template:

```text
source = linear_webhook_queue.db
Reset to pending
does not prove the dispatcher executed it immediately
Purge terminal queue rows only? Pending and processing work will be kept.
Purges terminal rows only: completed, failed, stale, skipped, no-op, and dispatched statuses.
Dead-letter/live consumer state comes from recovery status
queue-terminal-badge
queue-stale-badge
queue-live-badge
updateQueueSemantics(queue)
```

## Stale-guard verification pattern

When Hermes reports stale verification after editing `dashboard.html`, run a compact verifier that prints a plain canonical command before JSON:

```text
CANONICAL_TEST_LINT_BUILD_COMMAND=node --check /tmp/hermes-dashboard-inline-stale-guard.js
```

Then verify from `origin/deploy-fresh` when the PR is merged:

- exact changed path exists locally;
- `git show origin/deploy-fresh:prismatic/gateway/templates/dashboard.html` contains the markers;
- extracted inline JS passes `node --check`;
- local `/api/gateway/webhooks/queue` returns `source=linear_webhook_queue.db`;
- merge commit for the PR is present;
- `/tmp/hermes-verify-*` script is removed.

Always label this as ad hoc targeted verification, not full suite green.
