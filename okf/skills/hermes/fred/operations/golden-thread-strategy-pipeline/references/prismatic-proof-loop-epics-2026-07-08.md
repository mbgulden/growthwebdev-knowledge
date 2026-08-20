# Prismatic Proof Loop Epic Build-Out — 2026-07-08

## Durable pattern

When a Golden Thread strategy produces multiple workstreams, create **parent epics + child tasks**, not a flat list. For Michael, `Done` must mean **exit criterion completion with evidence**, not code/docs completion.

## Epic/task shape used

Each parent epic included:
- Goal.
- Exit criterion.
- Judgement rule: close only when the exit criterion is evidenced.

Each child task included:
- Concrete implementation description.
- Explicit child exit criterion.
- Shared footer: `Done means exit-criterion completion`.
- Parent epic exit criterion copied into the child description.

## Five Prismatic Proof Loop epics

1. Distribution Readiness / First-User Gate.
2. Linear/GitHub Automation Demo Wedge.
3. Verified Execution Contract.
4. Operator Control Plane / Phone-First Factory View.
5. Private Deployment Offer / Revenue Path.

## Linear rate-limit handling pattern

Linear rate-limited mid-flight after some epics/tasks were created. Correct handling:

1. Query/verify partial state that already exists.
2. Report partial state plainly; do not say all done.
3. Write an idempotent finish script that upserts missing issues and updates existing descriptions/parent links.
4. Write a retry wrapper that:
   - stays silent while Linear is still rate-limited,
   - creates a completion marker after success,
   - stays silent if already complete,
   - outputs final issue list + next-step prompt exactly once.
5. Create a real recurring/limited cron for the retry rather than relying on memory or manual follow-up.

## Verification pattern

For script changes, create `/tmp/hermes-verify-*.py` via `tempfile`, run `py_compile`, statically verify declared epic/task structure, and fixture-test retry behavior without mutating Linear.

Scope label: ad hoc targeted verification, not canonical/full-suite green.
