# Alert-only cron all-clear silence pattern

Use this when Michael flags a cron delivery like “0 failures,” “no drift,” “all green,” or routine fleet stats and says it should not be delivered when there are no problems.

## Durable lesson

For no-agent cron jobs, **non-empty stdout is often the delivery payload**. If the user expects silence on all-clear, it is not enough to avoid an explicit Telegram/API call; the all-clear branch must also avoid printing routine summaries to stdout, or the scheduler may still deliver the cron response.

## Repair pattern

1. Identify the source of delivery noise:
   - scheduler `deliver` target, e.g. `telegram:*` / `origin`
   - script-level Telegram/send call
   - no-agent stdout body that the scheduler delivers verbatim
2. Change the cron delivery target to `local` when the script owns alert delivery.
3. In the script:
   - all-clear/no-drift/no-warning branch: write local state/artifacts only and return `0` with empty stdout when possible
   - alert branch: print/send the concise alert with the actual problem details
4. Keep forensic state somewhere local (`state/`, `/tmp`, or cron output), but do not page Michael with “nothing happened.”
5. Verify both branches with monkeypatched fixtures:
   - all-clear returns `0`, stdout is empty, Telegram/send function is not called
   - problem branch still emits/sends and includes the failing condition
   - `py_compile` changed Python files

## Example cases from 2026-07

- Tier-1 Silent Failure Watchdog:
  - all-clear previously printed `Current silent failures: 0` and delivered to Telegram
  - fix: moved routine scheduler delivery to `local`; script posts only on actual silent failures; all-clear branch returns before printing
- Weekly Homelab Inventory Report:
  - all-clear previously sent “No drift or storage warnings detected” plus fleet stats
  - fix: no-drift branch suppresses Telegram; drift/warning branch still sends and may include fleet stats

## Verification language

```text
Ad hoc targeted verification: PASS
- /tmp/hermes-verify-xxxx.py created with tempfile and cleaned up
- all-clear stdout empty / send call not invoked
- alert branch still sends problem details
- py_compile passed
Scope: ad hoc targeted verification only — not full canonical suite green.
```
