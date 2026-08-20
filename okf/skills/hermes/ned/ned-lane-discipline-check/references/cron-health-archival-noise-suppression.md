# Cron health archival-noise suppression (GRO-3609 pattern)

Use this when a Prismatic/Ned task asks that cron/factory/health digests report **active failures only** and stop escalating paused/retired archival noise.

## Durable pattern

1. Treat intentionally inactive cron records as archive context, not active alerts:
   - `state in {archived, disabled, paused, retired}`
   - truthy `paused`, `retired`, or `archived`
   - `enabled is False`
2. Apply this gate before classifying current-health buckets:
   - `silent_failures`
   - `stale`
   - `blank_status`
   - `error_not_silent`
3. Preserve visibility by adding a separate archive/context bucket such as `archived_suppressed` instead of dropping the rows. Old `last_status=error` stays visible, but the row must say it is **not a current alert**.
4. If the CLI has `--json`, keep stdout machine-parseable. Do not print dry-run prose or human footer text after the JSON blob. If the script currently prints a banner before JSON, downstream smoke tests can parse from the first `{`, but do not add any trailing prose.
5. Put Ned-owned tests under `prismatic/tests/`, not repo-root `tests/`, to satisfy lane governance.
6. Update operator docs in the same commit; for this class, `scripts/ops/README.md` is the right place to document the health/digest contract.

## Exit-criterion fixture shape

Create a fixture with at least:

- one active `last_status=error`, `deliver=local` job → remains in `silent_failures`
- one `paused=True`, `last_status=error` job → moves to `archived_suppressed`
- one `state="retired"`, `last_status=error` job → moves to `archived_suppressed`
- one disabled blank-status job → moves to `archived_suppressed`, not `blank_status`

Assert the digest contains an `Archived/Paused Suppressed` (or equivalent) section and language like `not a current alert`.

## Verification commands used successfully

```bash
python3 -m ruff check scripts/silent_cron_detector.py prismatic/tests/test_silent_cron_detector.py
python3 -m ruff format --check scripts/silent_cron_detector.py prismatic/tests/test_silent_cron_detector.py
python3 -m pytest prismatic/tests/test_silent_cron_detector.py -q
python3 scripts/silent_cron_detector.py --json --no-telegram | python3 -c '<parse JSON and print bucket counts>'
```

Label this as **ad hoc targeted verification**, not full-suite green, unless the full suite was actually run.
