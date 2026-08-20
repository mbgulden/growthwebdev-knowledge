---
name: scheduled-reminder-management
description: "Manage Hermes scheduled reminders/cron jobs safely when the user asks to stop, pause, remove, or audit reminders, especially noisy live monitors and watchdogs."
triggers:
  - stop reminder
  - stop cron
  - remove scheduled job
  - pause reminder
  - noisy watchdog
  - live monitor reminders
---

# Scheduled Reminder Management

Use this skill when the user asks to stop, pause, remove, list, or audit scheduled reminders/cron jobs.

## Core rule

When the user says **"stop reminder <name>"**, act immediately. Do not explain first, do not ask for confirmation unless multiple matching destructive choices are ambiguous, and do not leave the reminder running while summarizing.

## Safe removal workflow

1. Run `cronjob(action="list")` first. Never guess job IDs.
2. Match by exact or clearly intended job name/preview.
3. If one clear match exists, remove it with `cronjob(action="remove", job_id=...)`.
4. Run `cronjob(action="list")` again to verify the target job disappeared.
5. Report compactly:

```text
job_id=<id>
name=<job name>
schedule=<schedule>
RESULT=REMOVED
verified_absent=yes
```

## When the user repeats the stop request

A repeated message like:

```text
stop reminder LIVE result writeback reconciler — Prompt 4 agents
stop reminder LIVE result writeback reconciler — Prompt 4 agents
```

is a strong signal to prioritize removal over any in-progress implementation/reporting. Stop the matching reminder first, then resume only if needed.

## Adjacent reminders/watchers

Remove only the exact reminder requested unless the user names additional jobs. If a related watcher remains, say so explicitly instead of silently removing it:

```text
Removed: LIVE result writeback reconciler — Prompt 4 agents
Still running separately: Watch Prompt 4 completed-work packets — Agent Output Resilience
```

If the user then asks to stop that adjacent watcher too, list again, remove that exact job, and verify absence.

## Pitfalls

- Do not confuse **paused** with **removed**. If the user says stop/remove and the job is noisy, removal is usually the expected action.
- Do not report "stopped" from memory. Verify with a fresh cron list after removal.
- Do not remove unrelated recurring business/AOT jobs just because they are also scheduled.
- Do not preserve live monitors after the user clearly asks to stop reminders; noisy live monitors are operator-experience bugs once unwanted.
