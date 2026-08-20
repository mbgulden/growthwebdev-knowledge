# No-agent delta/quotas cron noise suppression

Use this when active no-agent crons are technically `ok` but keep printing routine all-clear output into Hermes cron feeds or Telegram digests.

## Session pattern

Two related producers caused noisy but non-actionable cron output:

1. A shared `DeltaCache` helper printed both a green JSON pulse and `[SILENT]` on no-delta runs. In no-agent cron mode, any non-empty stdout can become a delivered message or a noisy output file.
2. An AGY quota poller printed a full quota table and a benign `GCP_PROJECT_ID not set` warning every 15 minutes even when quota state was healthy.

## Durable fix pattern

### Delta/all-clear helper

- Make `exit_silent()` produce **empty stdout** by default.
- Keep a legacy escape hatch only behind an explicit env var, e.g. `DELTA_CACHE_LEGACY_SILENT_MARKER=1`.
- Make green pulse state write to a local trigger/state file, not stdout.
- Keep a debug/legacy env var if stdout pulses are needed, e.g. `DELTA_CACHE_PRINT_GREEN_PULSE=1`.

### Quota/status poller

- Always update the durable state DB/log.
- Redirect routine full output to a local log such as `/tmp/agy_quota_poller_latest.log`.
- Print stdout only for true alert conditions: non-zero exit, `ERROR`, `CRITICAL`, or `Exhausted yes`.
- Suppress known benign warnings from stdout if state still updated successfully.

## Verification contract

Use a fresh `/tmp/hermes-verify-*.py` verifier and report as ad-hoc targeted, not suite green. Assert:

```text
py_compile delta_cache.py passes
bash -n agy_quota_poller.sh passes
delta_all_clear_stdout_empty=true
green_pulse_file_written=true
quota_poller_stdout_empty=true
quota_poller_log_updated=true
```

Then run the affected cron(s) through the scheduler when safe and read back the latest cron output file to prove it says `Status: silent (empty output)` instead of printing `[SILENT]`, green JSON, or routine tables.

## Pitfalls

- Do not print `[SILENT]` from no-agent scripts. `[SILENT]` is for LLM final responses; no-agent silence means empty stdout.
- Do not remove local state/log writes while suppressing stdout; operators still need forensics.
- Do not call this full suite green. It is targeted cron-output contract verification.
