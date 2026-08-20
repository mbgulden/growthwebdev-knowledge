# HDE Green-State Plan + Execute Pattern — 2026-07-18

Use this reference when Michael asks for comprehensive epics/children **and** says to start executing once planning is done.

## Pattern

1. Convert the audit/gap list into class-level epics, not one flat issue dump.
2. Create parent epics first, then children with exact-title idempotency.
3. Put all children in `Todo` unless the user explicitly says execution should start.
4. If the user says “once planned, start executing,” immediately begin the first dependency-safe slice after Linear verification.
5. Update Linear state/comments as real work progresses, not just at the end.
6. Keep blocked external-auth tasks `In Progress` only when there is an active next action; name the blocker and required human action.

## HDE example shape

Seven epics covered the audit categories:

- North Star OKF/governance
- Operational file consolidation
- Google authentication via Kai and registration
- Site-wide analytics/conversion instrumentation
- SEO/index hygiene
- Security/performance/operational reliability
- North Star daily-work product progression

The first execution slice was:

- write North Star + green rubric docs;
- inventory stray operational files;
- copy reusable scripts into the canonical repo without deleting active runtime copies;
- prove Kai AGY authentication separately from reusable Google API scopes;
- mark completed child issues `Done`, set the next true blocker/next actions `In Progress`, and comment evidence on each issue.

## Verification notes

- Linear tree creation is not done until re-read from Linear with parent child counts.
- Planning is not done when execution was requested until at least the first safe tranche has actually executed.
- Use branch/commit evidence and real verifier output in the Linear comments.
- For OAuth/auth blockers, do not paste tokens; record account, scopes, API response class, and the precise next human step.
