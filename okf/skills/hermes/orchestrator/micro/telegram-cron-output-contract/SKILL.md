---
name: telegram-cron-output-contract
description: Strict digest contract for Telegram-bound cron stdout. Active problems only. No all-clear sections, no archives, no paused work, no recap paragraphs. One bolded action line per message. Link, not explanation. If nothing is active, the script exits silent. Per the OKF cron-alert-output-contract.
---

# telegram-cron-output-contract

## The rule

For Hermes no_agent=True cron jobs delivered to Telegram, stdout is the user message. Therefore stdout must be either:

1. **empty** when there is no actionable alert, OR
2. a **complete, user-facing alert** with:
   - one bolded action line per message (Markdown bold text)
   - link, not explanation (a URL/path, not a paragraph about why)
   - active problems only (no archives, no paused work, no completed history)

Anything else is a pager bug.

## Required behavior

| Condition | stdout | Delivery outcome |
|---|---|---|
| No production/actionable alert | empty | silent |
| Test/smoke/debris-only alert | empty | silent |
| Real blocker | concise Markdown alert with action line | delivered |
| Upstream/agent failure with actionable impact | concise failure alert with exact blocker | delivered |
| Internal diagnostics | stderr, logs, or cron output artifact only | not user-paged |

## Forbidden stdout patterns

- Recap paragraphs (multi-line summaries of what the cron did).
- Header-only outputs (date + counts but no action).
- All-clear / green-pulse markers (e.g. SILENT, OK, All hostnames locked).
- Debug scaffolding (e.g. Alert sent to Telegram, AGY exit code).
- Internal narrative (Let me check..., I think..., I am going to...).
- AGY background-task scaffolding (An update was received from a background task:).
- Recurring tagged prefixes (NIGHTLY-BACKLOG, CONSULTING-PIPELINE).
- Raw token/env warnings that are not actionable.
- Sections labeled Top, Sample, GitHub activity — these are recap, not alert.

## Implementation requirements

1. Prefer a producer-level --quiet mode for scheduler use. Without --quiet, the producer may emit verbose output that violates the contract.
2. Do not send Telegram internally from a script when the cron already has deliver=telegram or deliver=origin. Double-delivery equals double pings.
3. Filter test/smoke issues before alert generation.
4. Sanitize LLM/AGY output before printing.
5. If sanitized output has no user-facing signal, print nothing. Silent beats noise.
6. Verify with a fresh hermes-verify script that checks stdout length, representative noisy fixtures, and live scheduler config.

## Anti-patterns (in the agent's own replies, not just cron output)

- I noticed X. Here is what I see. Let me fix it. — that is narration.
- Project Y is stale. Project Z has a missing next_action. Project A is doing fine. — recap, not alert.
- 5 projects scanned. 0 stale. 0 missing. 12 GitHub checks attempted. — recap paragraph.

## Pitfall: literal marker text gets delivered as a Telegram message

The bug I see every audit: a cron script prints a string like "SILENT" or "OK" or "No new alerts" then exits. The script author meant the marker as a sentinel that a human reader would interpret as "this is the no-op case." But the cron runner does not interpret the marker — it sees non-empty stdout and delivers the literal text to Telegram. So Michael gets a ping that says SILENT, or a ping that says "everything is fine, nothing to do." Both violate the contract.

The fix is structural, not textual:

- Silent exit means *no* stdout. Replace any `print("...marker...")` followed by `return 0` with just `return 0` (or `sys.exit(0)`).
- The `exit_silent()` helper in `delta_cache.py` historically printed the literal SILENT marker. It now exits with no stdout; the legacy env-var guard is preserved for backward compatibility but produces no output.
- The `not args.quiet` branch in verbose-mode scripts is the only place a recap line is allowed, and that branch is unreachable from cron because the cron wrapper passes `--quiet`.

Verification: after the fix, `print("...marker..."); return 0` should be `return 0` only, and the script's stdout in the no-op case must be empty when invoked from a no-quiet-args wrapper (which is what the cron runs).

## Pitfall: double-delivery

When a script both (a) calls its own Telegram-sending helper and (b) is registered with `deliver=telegram:...` or `deliver=origin`, Michael gets the same message twice. The script's stdout IS the user message; the cron delivers that. Internal `send_telegram()` is a leak. The fix is to keep the script silent on Telegram delivery and let the cron own it.

The `cf_access_health_check.py` case shipped with both: internal `send_telegram()` call AND `deliver=origin`. Audit found this because two `print` statements (`Alert sent to Telegram` and `Telegram send failed`) appeared in stdout. Those are themselves contract violations, but they're also the diagnostic trail showing the script was double-delivering. Remove the internal send, and stdout becomes the single source of truth.

## Pitfall: AGY-exit and "Telegram send failed" must go to stderr

These are scaffolding lines, not user-facing alerts. They look like:

```python
print(f"[CONSULTING-PIPELINE] AGY exit: {result.returncode}")
print(f"  [warn] Telegram send failed for both Markdown and plain text", flush=True)
```

The cron delivers stdout to Telegram. AGY exit codes and send-failure warnings are not actionable for Michael in the alert body — they're diagnostics for whoever reads the cron log. Move them to `file=sys.stderr`. The verifier `telegram-cron-output-check` flags these.

## How to test a cron script against this contract

Three live tests, all quick:

1. **Silent case**: run the script with inputs that produce no actionable findings. Stdout must be empty.
2. **Active case**: run the script with inputs that produce findings. Stdout must start with `**` (bolded action line).
3. **Verifier scan**: run `python3 skills/verifiers/telegram-cron-output-check/verify.py scripts/` — must report `PASS`.

A script that passes tests 1 and 2 but fails 3 has scaffolding leaks; fix those before claiming the script is correct.

## Personal named-recipient briefings (different shape)

This contract is written for operational alerts (infrastructure / monitoring / pipeline state). A different class of Telegram-bound cron — a personal morning briefing to a named user (Becca, Michael, etc.) where the prompt gives a warm-tone format scaffold (greeting + bullet sections + sign-off) — has a reconciliation problem: the prompt explicitly asks for content, but the day may have nothing actionable. The hard structural rules still apply (no narration, no recap-paragraph filler, exit silent when truly nothing active), but the *shape* is different: greeting + one signal line, not one bolded action line. See `personal-named-recipient-telegram-briefings` for the reconciliation guidance and anti-pattern examples.
