# Post-publish stuck alerts: test debris + scheduler-owned delivery

Session pattern from `Post-Publish Stuck Alert — daily Telegram digest to Michael` (`73dc208351d6`).

## Failure shape

A no-agent alert cron reported a stuck Linear issue:

- `GRO-2268` — `[TEST] Post-publish integration review end-to-end smoke test`
- state: `Done - Doc Pending`
- labels: `agent:post-publish-doc-update`, `agent:done`

The live Linear state was real, but the issue was smoke-test debris, not production work that should page Michael.

A second problem made the alert noisy:

- scheduler already had `deliver=telegram:...`
- producer script also attempted direct Telegram send internally
- wrapper truncated output with `tail -c 1000` and always exited `0`, hiding useful context and surfacing fragments such as `TELEGRAM_BOT_TO...`

## Repair pattern

1. **Verify the issue live before patching**
   - Query Linear for the exact issue identifier/number.
   - Confirm title, state, labels, updatedAt, and whether it is production work or test/smoke debris.
   - If full comment queries 500, retry narrower GraphQL shapes: base fields first, then `comments(first:3)`.

2. **Classify test/smoke debris separately from production stuck work**
   - Filter titles like `[TEST]`, `TEST:`, and `Smoke test` out of Michael-facing stuck alerts.
   - Keep the test issue in Linear if it is useful for fixture history, but do not page it as operational debt.

3. **Use exactly one delivery owner**
   - For no-agent crons with scheduler `deliver=telegram`, the script should print the user-facing alert body to stdout only when there is a real alert.
   - Remove internal Telegram send functions from the producer, or set cron `deliver=local` if the script must own delivery.
   - Do not allow both paths at once.

4. **Make all-clear truly silent**
   - Add `--quiet` mode if needed.
   - In quiet mode, print nothing on all-clear/no-production-alert.
   - Wrapper should call the producer with `--quiet` and exit with the producer status; no truncating tail and no forced `exit 0`.

5. **Verification shape**
   - `py_compile` changed Python.
   - Assert producer and wrapper are executable.
   - Static check for test filter markers and absence of internal-send markers (`send_telegram(`, `TELEGRAM_BOT_TOKEN`, `Sending to Telegram`).
   - Live dry-run JSON should show test/smoke issue excluded from `stuck_count` and `alerts`.
   - Quiet wrapper should return `0` with `stdout_len == 0` and empty stderr in no-alert state.
   - Check scheduler job still points at the wrapper and has `last_status=ok`.

## Pitfall

Do not clear or close a live Linear issue just because it is noisy. First determine whether it is test debris, stale routing label debt, or a real missing OKF-doc handoff. Suppress only the non-production alert class unless there is verified evidence to move the issue state/labels.
