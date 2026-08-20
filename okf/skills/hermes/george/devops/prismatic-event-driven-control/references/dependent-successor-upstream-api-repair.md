# Dependent successor blocked by missing upstream operational API

Use this reference when a successor Prismatic task is authorized but its reviewed design depends on APIs that the just-merged predecessor was expected to provide.

## Pattern

1. **Deploy/activate the accepted predecessor first when required by the successor base gate.** A reviewed/merged tree is not enough if the successor contract requires the canonical live release or durable runtime checkout.
2. **Refresh topology against the merged/deployed exact base.** Inspect the actual source/API surface, not the earlier contract language.
3. **If a required canonical API is missing, classify it as an upstream implementation-repair slice, not a successor implementation detail.** Do not hide compensation logic inside the successor with ad-hoc SQL, a duplicate scheduler/parser, or dashboard-local reconstruction.
4. **Freeze one bounded implementation-repair contract.** Keep it narrow: define the missing public API, allowlist, tests, dependency additions, no-authority boundaries, exact base/tree, and exactly-one-descendant rule.
5. **Hash and review the repair contract before any worktree/event exists.** Contract `CLEAN/PASS` is only the first gate.
6. **Prepare admission only read-only until review returns CLEAN/PASS.** Validate deployed task-admission schema shape, task-id compliance, active slots, writer leases, and zero event/claim/lifecycle/outbox rows, but do not POST.
7. **Keep the original successor unstarted.** After the upstream repair is accepted/merged/deployed, refresh the successor contract/base and only then admit/implement the successor.

## Required proof block

```text
PREDECESSOR_DEPLOYED=<true|false + release>
SUCCESSOR_LINEAR_STATE=<state>
MISSING_UPSTREAM_API=<short description>
REPAIR_CONTRACT=<path>
REPAIR_CONTRACT_SHA256=<sha256>
REPAIR_CONTRACT_REVIEW=<pending|CLEAN/PASS|BLOCKED>
EVENT_COUNT=0
PRODUCER_COUNT=0
SUCCESSOR_STARTED=false
NOT_CLAIMING=successor implementation, event admission, producer launch, PR, merge, deploy, or Linear write
```

## Pitfalls

- Do not call this another precontract when the defect is concrete and implementable. It is an implementation-repair contract for the upstream API.
- Do not start the successor just because Michael authorized the broader runway. Authorization still flows through the current exact gate: contract review → task copies/envelope review → explicit one-event/cap-1 admission if required.
- Do not make the successor own duplicate cron/timezone/DST/read-model logic when the dashboard/status task is supposed to consume canonical runner/authority APIs.
- Admission prep may validate schema and zero-state, but `EVENT_COUNT=0` and `PRODUCER_COUNT=0` must remain true until review/admission gates pass.
