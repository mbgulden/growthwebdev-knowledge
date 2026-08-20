# No-agent watchdog all-clear silence pattern

Use this when Michael points out that a health/watchdog cron is sending routine “all clear” messages.

## Durable lesson

For no-agent crons, **any non-empty stdout is deliverable output**. If a watchdog has nothing actionable to report, it must emit **empty stdout** and return `0`. Do not print banners, loaded-count summaries, all-clear bodies, or fleet stats before the script knows it has a real alert.

Some scripts also send Telegram internally, independent of the Hermes cron `deliver` setting. In those cases, changing the cron to `deliver=local` is not enough; patch the producer so the all-clear path does not call `send_telegram()`.

## Repair pattern

1. Identify whether the noise comes from scheduler delivery or producer-internal Telegram calls.
   - Scheduler noise: no-agent script prints routine stdout.
   - Internal noise: script calls Telegram/HTTP directly even though cron delivery is local.
2. Move human-readable headers/summary printing **after** the condition check.
3. On all-clear:
   - write local state/forensics if useful,
   - save watchdog state,
   - return `0`,
   - print nothing,
   - do not call Telegram.
4. On alert:
   - preserve the normal alert body,
   - keep enough stdout for cron output evidence,
   - call Telegram/Autobot as before.
5. If the script has a JSON/dry-run mode, preserve it for machine checks; only silence the normal all-clear path.

## Verification fixture

Create `/tmp/hermes-verify-*` and monkeypatch external calls:

- all-clear path: assert stdout is exactly `''` and Telegram/send function is not called.
- alert path: assert stdout/body includes the failing condition and Telegram/send function is called once.
- run `py_compile` for changed Python scripts.
- if the live cron can be safely run, run it and confirm latest cron output says `Status: silent (empty output)` for all-clear.

## Example signals

- “Current silent failures: 0” should be silent.
- “No drift or storage warnings detected” should be silent.
- Fleet stats with no problem attached should be silent.
- Actual drift, storage warning, silent-failure, or recovered critical condition may alert depending on the job contract.
