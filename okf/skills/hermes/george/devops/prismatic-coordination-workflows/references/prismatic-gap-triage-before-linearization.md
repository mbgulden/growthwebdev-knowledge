# Prismatic gap triage before implementation or Linear mutation

Use this when Fred/Kai/Ned/AGY or another helper returns a broad gap list, sequencing recommendation, or giant backlog document and Michael asks whether to act on it.

Concrete example: `references/foundational-gap-reconciliation-2026-07.md` captures the July 2026 foundational-gap reconciliation pattern: stale lock/rate-limit claims, cron split-brain, destructive profile cleanup, event-router retention, and CLI syntax verification before Linear restructuring.

## Core rule

Do **not** execute, create Linear issues, or restructure backlog directly from an agent-generated gap list. First reconcile the list against current source, accepted ADRs, and current production boundaries. Agent recommendations are inputs, not authority.

## Required triage pass

1. Bind the review to exact current source:
   - record `origin/main` commit and tree when available;
   - state whether code was changed (`false` for triage-only);
   - label all checks as ad-hoc targeted unless the canonical suite actually ran.
2. For each proposed gap, classify it as:
   - `VALID` — absent or materially missing;
   - `PARTIAL` — some implementation exists, but the guarantee is incomplete;
   - `ALREADY_IMPLEMENTED` — current source already has the claimed capability;
   - `STALE` — recommendation no longer matches current source/ADR state;
   - `DUPLICATE` — covered by an existing task/authority;
   - `BLOCKED` — requires prior contract, schema, proof, or explicit authorization.
3. Quote or summarize source evidence compactly: files/modules, behavior checks, and focused test results.
4. Separate implementation existence from production guarantee. A class/module can exist while actual mutating launch paths still do not enforce it.
5. Rescope inaccurate recommendations rather than accepting their labels. Example patterns:
   - “build lock manager” may become “lock-authority convergence and actual-writer integration” if a lock manager already exists;
   - “add rate-limit guard” may become “duplicate-path/integration audit” if a durable guard already exists;
   - “cron registry from zero” may become “schedule-bucket identity, dependency enforcement, supervision, and orphan reconciliation.”
6. Treat feature flags as configuration contracts. Rollback flags may gate enrollment or shadow/enforce mode, but must not silently disable core safety while the system still claims safety.
7. Preserve cap-1 and exact-head discipline. Orthogonal-looking gaps do not authorize concurrent producer work unless Michael explicitly raises the cap.

## Recommended output shape

Lead with a compact proof block, then a gap table:

```text
STATUS=PARTIAL|PASS|BLOCKED
ORIGIN_MAIN=<commit>
ORIGIN_TREE=<tree>
FOCUSED_CHECKS=<summary>
LOG=<path>
LOG_SHA256=<sha256>
AD_HOC_OR_CANONICAL=ad-hoc targeted|canonical suite
LINEAR_WRITTEN=false
CODE_CHANGED=false
```

For the table, include: `Item`, `Finding`, `Decision`.

Then answer any explicit questions directly before suggesting revised sequencing.

## Giant document → Linear packet workflow

When Michael offers or provides a large source `.md` with gaps:

1. Preserve the original unchanged and hash it.
2. Repair visible encoding corruption only in a working copy.
3. Audit each finding against current `origin/main`, accepted ADRs, and existing tasks.
4. Merge architecture findings without overwriting the source agent’s evidence.
5. Produce a downloadable proposal markdown before any Linear write. Include:
   - proposed epic/task titles;
   - problem and behavioral impact;
   - exact source evidence;
   - dependencies and sequencing;
   - acceptance tests;
   - rollout/feature-flag mode;
   - rollback and migration gates;
   - non-claims and authorization boundaries.
6. Ask for explicit approval before creating/updating Linear issues.

## Cron canary acceptance pattern

Avoid accepting “N real crons for seven days” as the first gate. That conflates scheduler correctness with business-command reliability and makes weekly schedules impossible to assess quickly.

Use two gates:

- Deterministic acceptance: exact schedule bucket identity, expected fires equal terminal receipts, zero duplicates/misses, disabled/paused/deactivated/deleted jobs fire zero times, unmet dependencies start zero processes, restart produces zero duplicate execution, timeout/cancel leaves zero survivors, and every receipt binds cron ID, registry generation, command digest, scheduled bucket, start/end time, and exit state.
- Canary/shadow: 24-hour accelerated harmless canary covering success/failure/timeout/dependency block/pause/restart; require zero missed, duplicate, orphaned, or unauthorized executions; then shadow real registry before enrolling low-risk real crons.

## Cross-project dependencies

Prefer runtime enforcement eventually, but not first. Sequence: canonical dependency identity and schema → cycle/missing/stale validation → audit-only projection → compare against real events → fail-closed enforcement for explicitly enrolled workflows. Documentation-only dependencies are advisory and cannot support execution guarantees; immediate enforcement of an undefined graph causes false blocks.
