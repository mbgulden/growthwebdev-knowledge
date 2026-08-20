# Adversarial timeout review and same-task repair

Use this reference when coordinating Prismatic provider-neutral/source-acquisition or runner work where subprocesses, streams, deadlines, bundles, or offline verification are in scope.

## Session-derived lesson

Canonical green is not sufficient when the frozen contract requires fail-closed behavior under adversarial process behavior. In GRO-4206 Repair 2, configured proof was green, but independent exact-head review found that periodic child output refreshed the per-command timeout. A child emitting output every interval shorter than `command_timeout_seconds` returned normally after roughly 4x the command deadline instead of failing at the fixed per-command deadline.

Class-level risk: selector/read loops often recompute a timeout budget after each readable event. If the code uses the full per-command timeout on every event instead of a launch-time absolute deadline, periodic stdout/stderr can keep the command alive until the longer total deadline or natural completion.

## Coordinator response pattern

1. Treat any valid independent `REPAIR` as stop-the-line, even after canonical/local full-suite green.
2. Independently reproduce the reported bypass with a minimal temporary probe before dispatching repair when feasible.
3. Freeze a same-task repair packet on top of the rejected exact head; do not launch successor work.
4. Bind the repair contract to:
   - rejected head/tree/parent;
   - reproduction log path and SHA-256;
   - exact allowed paths;
   - mandatory direct regressions;
   - no push/merge/deploy/Linear/cap-increase boundary.
5. Dispatch at writer cap 1, read back task hash/base/path scope, start the worker once, and verify the claim.
6. Rebind watcher, queue, control state, and handoff to the repair task. Mark older reviews as `SUPERSEDED_HEAD_ONLY` so they cannot promote a rejected head.
7. Leave preparatory next-slice analysis as `READ_ONLY / IMPLEMENTATION_NOT_ADMITTED` only.

## Regression prompts to require for deadline/streaming code

Require tests that prove:

- periodic stdout cannot extend per-command deadline;
- periodic stderr cannot extend per-command deadline;
- mixed stdout/stderr cannot extend per-command deadline;
- silent child still times out;
- total deadline shorter than command deadline returns stable `total_timeout`;
- command deadline shorter than total deadline returns stable `command_timeout`;
- timed-out process plus spawned child/process group is terminated and reaped;
- timeout exceptions do not include emitted canary output;
- successful short command remains unaffected;
- overflow and previous negative matrix tests remain green.

Implementation guidance to include in repair contracts: compute immutable launch-time absolute deadlines (`command_deadline = launch_monotonic + command_timeout_seconds`, caller-supplied `total_deadline`, `effective_deadline = min(command_deadline, total_deadline)`) and ensure readable selector events never refresh either deadline.

## Reporting boundary

When reporting this class of issue, separate:

- ad-hoc adversarial reproduction;
- configured canonical proof;
- independent review verdict;
- current active producer/review count;
- successor admission state.

Never claim current-head `CLEAN`, PR readiness, or successor admission while a valid repair is active.