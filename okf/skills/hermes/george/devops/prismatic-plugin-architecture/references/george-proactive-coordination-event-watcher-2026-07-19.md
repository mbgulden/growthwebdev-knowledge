# George proactive Prismatic coordination / event watcher pattern — 2026-07-19

## Trigger

Use this reference when Michael asks George to coordinate Kai/Fred/AGY work proactively, pace prompts, avoid duplicated branches, monitor completions, or become “event-based” / “always on” for Prismatic Engine.

## Durable lesson

George can act as Prismatic’s coordination/verification guard, but should distinguish:

```text
read-only proactive monitoring and prompt generation = allowed by default once policy is authorized
real side effects = explicit Michael authorization required
```

Michael approved this coordination policy:

- George may read repo/runtime/PR/API state, write Kai/Fred prompts, verify reports, flag stale PRs, and recommend merge order.
- George must wait for explicit authorization before merges, production deploys/restarts beyond authorized closeout, real Linear/GitHub side effects, bulk/autopilot dispatch, or closing/deleting PRs.

## Practical immediate pattern

Install a read-only silent-on-no-change watcher as a Hermes cron job when proactive coordination is requested but full Prismatic event-native dispatch is not yet proven.

Shape:

```text
every N minutes
→ read GitHub PR state, repo head, runtime head, service state, local API routes, queue/signals
→ compare with last snapshot
→ emit nothing if no material change
→ emit compact Telegram alert only on change
→ George reviews alert and decides hold / verify / prompt Kai / prompt Fred / recommend merge
```

Use `cronjob(no_agent=True, script=...)` for the watcher when the script itself produces the exact alert. Empty stdout means silent.

## Watcher safety requirements

The watcher must be read-only. It should not:

- merge PRs;
- deploy/restart services;
- write to Linear/GitHub;
- dispatch agents;
- enable auto-merge;
- run bulk/autopilot work;
- close/delete stale PRs.

It may check:

- selected PR state/mergeability/CI;
- `origin/main`, repo HEAD, runtime HEAD;
- `prismatic-gateway.service` active state;
- local runtime routes such as `/health`, `/api/agy/completed-work`, `/api/agy/completed-work/dashboard-linear-dry-run/latest`, `/api/agy/completed-work/verified-pr-dry-run/latest`, `/api/gateway/signals`, `/api/webhooks/queue`;
- packet classifications and side-effect flags such as `posted=false`, `dry_run=true`.

## Event-native target architecture

The stronger future pattern is Prismatic-native event routing:

```text
Kai/Fred/AGY completed-work event
→ durable event/review queue
→ target_agent=george review item
→ George verifies PR/API/runtime/dashboard evidence
→ George creates next Kai/Fred prompt or merge-readiness packet
→ no real side effects without Michael authorization
```

Useful event types:

```text
agent.completed_work_packet.created
agent.completed_work_packet.classified
agent.completed_work_packet.blocked
agent.completed_work_packet.repairable
agent.pr_ready_dry_run.created
agent.dashboard_linear_dry_run.created
github.pr.ci_green
github.pr.merged
runtime.head_changed
runtime.route_marker_changed
```

Each event should include:

```text
event_id
agent
task_id / issue_id
branch
PR
marker
packet_classification
integration_classification
proof_log
side_effect_flags
recommended_next_action
```

## Prompt pacing rule

Do not let multiple agents attack the same blob. Assign lanes by marker:

```text
Kai = golden path / valid completed-work spine
Fred = adjacent boring hardening, e.g. invalid packet repair queue
George = verification, traffic control, prompt preparation, stale-PR guard
```

Examples:

```text
Kai → ONE_AGENT_OPERATOR_VERIFICATION_LOOP_OK
Fred → INVALID_PACKET_REPAIR_QUEUE_OK
George → GEORGE_OPERATOR_PROOF_REVIEW_OK
```

Future gates should stay blocked until dependency markers are real:

```text
MULTI_AGENT_COMPLETED_WORK_LANE_OK
ONE_TASK_RECOVERY_DRY_RUN_OK
LIMITED_OVERNIGHT_READINESS_GUARD_OK
```

## Compact alert shape

```text
STATUS=EVENT_DETECTED
SCOPE=Prismatic PR/runtime/API/queue/signals read-only watch
CHANGES=<state diffs>
REPO_BRANCH=<branch> REPO_HEAD=<sha> ORIGIN_MAIN=<sha>
RUNTIME_HEAD=<sha> SERVICE=<active|inactive|...>
PR329_STATE=<state> MERGE=<state> HEAD=<sha>
COMPLETED_WORK=<summary>
QUEUE=<summary>
SIGNALS=<summary>
GEORGE_NEXT=Review event, decide whether to generate Kai/Fred prompt, verify claims, or hold. Do not merge/deploy/writeback without Michael authorization.
MARKER=GEORGE_PRISMATIC_EVENT_WATCHER_ALERT_OK
```

## Non-claims to preserve

A watcher alert does not claim:

- webhook-native George dispatch;
- automatic merging;
- real Linear/GitHub writeback;
- bulk agent dispatch;
- production/browser proof;
- canonical suite green.
