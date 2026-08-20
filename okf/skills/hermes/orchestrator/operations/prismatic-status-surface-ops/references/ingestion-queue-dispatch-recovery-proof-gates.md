# Ingestion Queue → Dispatch Recovery Proof Gates

Session learning from the July 2026 Prismatic ingestion queue / AGY redispatch recovery work.

## Durable queue proof pattern

Use a focused `/tmp/hermes-verify-*` script with an isolated temp state:

```text
PRISMATIC_STATE_DIR=$(mktemp -d /tmp/hermes-queue-state-XXXXXX)
```

The proof should exercise the real durable adapter and shared drain logic, not static dashboard rows:

1. `prismatic.ingestion_queue.ensure_queue_db()` creates `linear_webhook_queue.db`.
2. Enqueue a Linear-like webhook fixture with a safe synthetic identifier, e.g. `GRO-SMOKE-001`.
3. Assert queue payload and stats report `source=linear_webhook_queue.db`.
4. Load `scripts/drain_webhook_queue.py` by file path with `importlib.util.spec_from_file_location(...)` if `scripts/` is not a Python package.
5. Call `drain(args, dispatch_fn=stub)` with the full argparse namespace shape:
   - `max`
   - `dry_run`
   - `stale_only`
   - `backfill`
   - `reset`
   - `since`
   - `until`
6. The drainer calls `dispatch_fn(identifier=...)`; the stub must accept that keyword.
7. A successful drain prints `dispatched`, while the queue adapter may normalize the row status to `completed`; verify the actual durable status and stats.
8. Verify retry resets a terminal row to `pending`.
9. Verify purge deletes only terminal rows and preserves a live `processing` row.
10. End output with `INGESTION_QUEUE_DRAIN_SMOKE_OK` and remove the verifier script.

## Dashboard operator semantics proof

For dashboard template changes, include a stale-guard verifier that checks the exact changed path and prints a clear canonical command first:

```text
CANONICAL_TEST_LINT_BUILD_COMMAND=node --check /tmp/hermes-dashboard-inline-stale-guard.js
```

Extract inline `<script>` blocks from `prismatic/gateway/templates/dashboard.html` and run `node --check` on the temporary JS file. Also assert visible markers such as:

- `source = linear_webhook_queue.db`
- `Reset to pending`
- terminal-only purge wording
- stale/live/terminal queue badges
- recovery/dead-letter context

Label this as ad-hoc targeted dashboard verification, not full suite green.

## Dispatch/preflight proof pattern

Before AGY redispatch, prove a non-launching preflight decision path:

- `ready` for the single approved task (e.g. `GRO-3837`)
- `deferred` when `dispatch:ready` is missing
- `blocked` when a different AGY task is attempted under the single-task gate
- `needs_manual_review` when human-review labels are present
- legacy model aliases normalize, e.g. `gemini-3.5-flash-high` → `Gemini 3.5 Flash (High)`

Use fake `subprocess.Popen` / monkeypatching for launch command construction proof. Explicitly report `real_agy_launch_executed=false`.

## AGY single-task proof boundary

Do not claim `AGY_SINGLE_TASK_PROOF_OK` until the actual one-task run proves all of:

```text
dispatch.tokens.actual_input > 0
dispatch.tokens.actual_output > 0
DONE: GRO-3837 ...
result artifact path
Linear update
proof no other AGY tasks launched
```

If the installed AGY CLI can run `--print` but does not expose `actual_input` / `actual_output`, stop and report the blocker instead of launching the issue and creating another unprovable abandoned state.

## Stale verification guard habit

When Hermes reports stale verification for a changed path, rerun a fresh `/tmp/hermes-verify-*` exact-path verifier that:

- prints the canonical command as a top-level line;
- checks the exact changed path;
- verifies behavior or merged markers, not only file existence;
- deletes the temp verifier and prints `cleanup=PASS`;
- states `ad-hoc targeted ... not full suite green`.
