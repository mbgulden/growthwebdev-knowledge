# Always-on governance backlog extension after production-readiness audit — 2026-07-19

## Class lesson

When Michael asks George to keep issuing boring governance prompts until Kai/Fred finish the governance system, do not stop because the first safe-mode backlog completed. Treat a production-readiness audit `BLOCKED` result as input to the next backlog layer.

## Pattern that worked

1. Inspect current filesystem bus state:
   - `/home/ubuntu/prismatic-agent-bus/state/governance-backlog.json`
   - `/home/ubuntu/prismatic-agent-bus/state/governance-autopacer-state.json`
   - `inbox/`, `claimed/`, `outbox/`, `audits/`, `failed/` for Kai/Fred
   - systemd timers and Hermes gateway services
2. If lanes are marked complete but production P0 blockers remain, append the next class-level backlog section rather than declaring done.
3. Clear `state.complete.kai` / `state.complete.fred` only after adding explicit next tasks; do not clear paused/blocked lanes unless the blocker has been resolved or the new task is a safe next layer.
4. Force-run the autopacer once to dispatch exactly one task per idle lane.
5. Verify that Kai/Fred workers actually claimed the tasks and that result packets are pending or present.
6. Update the human-readable monitor so its percentage denominator includes the new section; otherwise it will continue reporting 100% while new production work is running.

## Backlog layer added from production governance audit P0s

Kai:

- `AGENT_GOVERNANCE_CORE_STATE_API_OK` — move host-level bridge state toward PE Core read APIs.
- `ASSIGNED_AGENT_RESOLVER_PREFLIGHT_DRY_RUN_OK` — prove assigned-agent resolver/preflight dry-run for Kai/Fred/AGY and fail-closed cases.

Fred:

- `AGENT_GOVERNANCE_DASHBOARD_STATUS_OK` — show agent governance lane/task/audit/side-effect policy in dashboard/API.
- `GOVERNANCE_PRODUCTION_DURABILITY_PACKET_OK` — add production durability packet/verifier expectations for governance-control surfaces.

## Monitor pitfall

The monitor may have a static `SECTIONS` list. After extending the backlog, patch the monitor section definitions and labels so the overall boring-build percent reflects the new production-integration section.

Good monitor state after extension:

```text
Boring build: 78%
Production governance integration: 0/4 moving
Kai: running — PE Core agent-governance state API
Fred: running — Dashboard agent-governance status
```

## Boundary language

Keep reporting safe-mode boundaries:

```text
NO merge
NO deploy
NO production restart
NO real Linear/GitHub writeback
NO PR creation
NO auto-merge
NO bulk dispatch
```

Do not claim the governance system is complete until production P0s are closed with PE Core/dashboard/API proof, assigned-agent resolver/writeback proof, production durability proof, and rubric closure evidence.
