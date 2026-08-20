# Telegram dispatch proof and no-agent change watchers

Use this addendum when George coordinates a Prismatic helper through Telegram and needs a low-cost wait state after issuing a repair or same-branch continuation prompt.

## Delivery proof standard

Generated cron output is the message body, not delivery proof by itself. Upgrade a Telegram dispatch from `UNVERIFIED` to `VERIFIED` only after all of these are true:

1. The cron/scheduler/gateway log contains a success line binding the job id to the intended Telegram target, for example `Job '<id>': delivered to telegram:<chat_id>` or `via live adapter`.
2. The cron output artifact is read back and contains the exact helper mention (`@FredTheBotFredTheBot`, `@KaiactiveOahu_bot`, `@Nedbotnedbot_bot`, etc.) plus the intended bounded task/repair scope.
3. Handoff/control state records both the delivery receipt and the boundary: GitHub PR/comment packets remain the durable authoritative task record when available.

If a manual `cronjob run` returns malformed/local delivery or `execution_success=false`, do not count the manual response as proof and do not assume failure either. Treat the manual run as discarded unless gateway logs later prove real delivery. Use this reconciliation order:

1. Poll the scheduler/gateway log for a line binding the exact job id to the intended Telegram target.
2. Read back the generated cron output artifact and verify exact mention, immutable references, scope, and non-authorization boundary.
3. List cron jobs after proven delivery. If the one-shot is still scheduled/enabled, remove it before final reporting to prevent duplicate Telegram pings; if it is absent, record that no duplicate will fire.
4. Create a fresh one-shot only if there is still no gateway delivery proof and the target still needs a message, then update durable state to the live retry job rather than the discarded run.

## No-agent watcher pattern

Use a script-only cron watcher when the active gate is waiting on a material external change (PR head, checks, state, artifact existence) and LLM reports would create churn.

1. Write the watcher under the active profile's scripts directory and schedule it by **relative script filename only** (for example `watch_pr378_head.py`), not an absolute or home-relative path.
2. Seed a JSON state file with the rejected/known baseline.
3. Normalize snapshots to JSON-native values before comparison. Avoid tuple-vs-list drift: if the state is stored as JSON, construct current snapshots with lists/dicts/strings/numbers, not Python tuples.
4. Test unchanged baseline behavior before scheduling:

```bash
out=$(python3 ~/.hermes/profiles/george/scripts/<watcher>.py)
test -z "$out"
```

5. Schedule as `no_agent=True` with `deliver=origin` and `attach_to_session=True` only when replies need to continue in this thread. Empty stdout must mean silent; non-empty stdout should be a compact proof packet with old/new head, check delta, URL, and next action.
6. Record the watcher job id, cadence, state file, baseline head/artifact, and `STDOUT_ON_UNCHANGED=0 bytes` proof in `PRISMATIC_CURRENT_HANDOFF.md` and the control JSON.
7. Pause/remove stale completed-slice watchers after merge/deploy/closeout so they do not report old gates.

## Report boundary

A watcher proves waiting discipline, not repair correctness. On any new head or material state change, invalidate prior exact-head CI/review evidence and rerun the exact-head review/semantic probes before merge or next dispatch.
