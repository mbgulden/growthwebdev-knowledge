# Event-driven control plane and cron-polling shutdown

## Trigger

Use this when Michael reports that Prismatic/Linear/Telegram/LLM cron jobs are over-polling, maxing out API calls, or bypassing the intended dashboard/event-driven workflow.

## Rule

Prismatic workflow control must be event-driven from the dashboard/event queue. Cron may remain for infrastructure maintenance, backups, journals, hardware/service health, memory audits, and explicitly approved low-frequency safety nets, but not for autonomous task scanning, Linear polling, Telegram nudge loops, LLM workflow controllers, or frequent status dispatch loops.

## Correction pattern

1. **Inventory across all relevant Hermes profiles, not only the active profile.** Check Ned, George, Kai, Fred/orchestrator/shared profiles and avoid duplicate symlinked job stores.
2. **Classify before disabling.** Pause jobs that touch Linear, dispatch agents, scan task queues, poll nudges, run post-publish routing, or run frequent Prismatic/LLM control loops. Do not blanket-disable unrelated backup/health/audit jobs.
3. **Pause, do not delete.** Keep the rollback/audit path intact unless Michael explicitly authorizes removal.
4. **Kill or verify absence of in-flight pollers.** Cron pause alone is insufficient if a scan/dispatcher process is already running.
5. **Verify the dashboard/event runtime remains alive.** At minimum prove the dashboard and health endpoint respond and the event consumer process is running.
6. **Update handoff/state files to fail closed.** Record `WORKFLOW_CONTROL=DASHBOARD_EVENT_DRIVEN_ONLY`, `CRON_WORKFLOW_POLLING=DISABLED`, and `TELEGRAM_LLM_POLLING=DISABLED`; reject any cron-written state that admitted successor work without valid review.
7. **Run a fresh ad-hoc verification script.** Assert zero active Linear-touching scheduled crons, zero active frequent Prismatic pollers, dashboard/health OK, and handoff markers corrected.

## Pitfalls

- Do not assume the visible 13 jobs are the whole problem. Shared/orchestrator profiles may contain many more Linear-touching or Prismatic polling jobs.
- Do not leave Telegram/LLM pollers alive just because they do not obviously say “Linear” in the job name; inspect prompt and script contents.
- Do not mark successor tasks admitted if an autonomous cron overwrote handoff state after a `REPAIR` review. Restore the review boundary first.
- Do not resume polling cron as a convenience workaround. Use dashboard/event-queue initiation for workflow movement.

## Proof packet shape

```text
NEWLY_PAUSED=<count>
ACTIVE_LINEAR_TOUCHING_CRONS=0
ACTIVE_FREQUENT_PRISMATIC_POLLERS=0
IN_FLIGHT_LINEAR_POLLERS=0
DASHBOARD_RESULT=HTTP_200
HEALTH_RESULT=HTTP_200
EVENT_CONSUMER=RUNNING
WORKFLOW_CONTROL=DASHBOARD_EVENT_DRIVEN_ONLY
NOT_CLAIMING=deploy/restart/Linear writes/cap increase unless explicitly authorized
```
