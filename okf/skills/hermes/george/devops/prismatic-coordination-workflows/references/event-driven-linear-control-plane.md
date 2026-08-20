# Event-driven Linear control-plane recovery

Session-derived lesson from Michael's correction after Prismatic helper cron jobs saturated Linear API usage.

## Trigger

Use this reference when Prismatic workflow state, Linear tasks, Telegram lanes, or helper-agent queues are being monitored or advanced.

## Durable rule

Prismatic workflow control should be event-driven from the Prismatic dashboard/gateway/event queue. Do **not** manage routine state by frequent cron jobs, Telegram bot polling, or recurring LLM sessions that repeatedly touch Linear.

## Recovery checklist when excessive pollers are found

1. Inventory active cron jobs across all relevant Hermes profiles and shared/orchestrator cron stores.
2. Identify Linear-touching and frequent Prismatic workflow pollers separately from unrelated one-shot reminders/watchdogs.
3. Pause or remove the pollers according to Michael's instruction; do not restart them to gather more state.
4. Check for already-running poller processes and terminate only the offending workflow pollers when safe.
5. Verify the replacement event path is available: dashboard route, health route, event consumer/queue process, and current active-producer cap/state.
6. Report both shutdown and replacement-path proof.
7. Keep generic dispatch paused until a specific dashboard/event-queued task is admitted.

## Required proof markers

```text
ACTIVE_LINEAR_TOUCHING_CRONS=0
ACTIVE_FREQUENT_PRISMATIC_POLLERS=0
DASHBOARD=<url/status>
HEALTH=<url/status>
EVENT_CONSUMER=<running|blocked + evidence>
GENERIC_DISPATCH=<paused|event-driven-only>
ACTIVE_PRODUCERS=<count>
NOT_CLAIMING=<no deploy/restart/Linear write/cap increase unless explicitly authorized>
```

## Reporting format preference

For Michael-facing Prismatic Telegram reports, use this order:

1. Problem found
2. What changed
3. Why it matters
4. Current state
5. Exact next move
6. IDs, hashes, and logs for traceability

Explain behavior and impact before identifiers. IDs/hashes/logs belong in the traceability section, not at the top.
