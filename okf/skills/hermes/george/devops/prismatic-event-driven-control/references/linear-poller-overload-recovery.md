# Linear poller overload recovery

Session-derived detail from Michael's correction that 13 active Linear cron jobs were maxing out Linear calls and that Prismatic should be managed from the dashboard/event workflow, not repeatedly polled by Telegram or LLM cron jobs.

## Incident posture

Classify as a control-plane reliability issue. The goal is not merely to quiet one noisy job; the goal is to return Prismatic workflow control to dashboard/event ownership and prevent helpers from creating hidden API pressure.

## Recovery sequence

```text
1. List cron jobs in George, Ned, Kai, Fred/shared/orchestrator profiles as applicable.
2. Separate active Linear-touching/frequent workflow pollers from unrelated one-shot or true watchdog jobs.
3. Pause/remove the offending recurring workflow pollers.
4. Inspect running processes for already-launched pollers and terminate only those offenders when safe.
5. Verify dashboard/health/event consumer availability.
6. Confirm active producer count and generic dispatch state.
7. Write handoff/control state with the event-driven policy so later sessions do not resume polling.
8. Report using Michael's six-part Prismatic order.
```

## Compact proof skeleton

```text
COMMAND=<cron/process/dashboard/health/event-consumer checks, summarized>
RESULT=<PASS|PARTIAL|BLOCKED>
LOG=<path if noisy>
SCOPE=Prismatic Linear-touching cron/poller shutdown and event-driven replacement path
AD_HOC_OR_CANONICAL=ad-hoc targeted control-plane verification
ACTIVE_LINEAR_TOUCHING_CRONS=<0 or count>
ACTIVE_FREQUENT_PRISMATIC_POLLERS=<0 or count>
DASHBOARD=<HTTP/status>
HEALTH=<HTTP/status>
EVENT_CONSUMER=<running|blocked>
GENERIC_DISPATCH=<paused|specific admitted task>
ACTIVE_PRODUCERS=<count>
NOT_CLAIMING=<deploy/restart/Linear write/cap increase unless explicitly authorized>
MARKER=PRISMATIC_EVENT_DRIVEN_CONTROL_PLANE_ACTIVE
```

## Report order reminder

1. Problem found
2. What changed
3. Why it matters
4. Current state
5. Exact next move
6. IDs, hashes, and logs for traceability

Use identifiers as traceability, not as the lead. Michael wants behavior and impact first.
