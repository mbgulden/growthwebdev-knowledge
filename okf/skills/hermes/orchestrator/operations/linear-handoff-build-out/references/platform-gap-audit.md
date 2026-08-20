# Platform Gap Audit — Pre-Feature Dependency Closure (2026-07-26)

## When this matters

A feature's OKF plan often surfaces **gaps in the platform the feature depends on**. The temptation is to fold the gap-fix into the feature epic itself. **Don't.** Gap closure has different owners, different exit criteria, different sequencing, and different risks. Mixing them produces a parent epic that can't close until both halves ship — which usually means it never closes.

The journal-pe-integration plan (1 parent + 7 epics + 39 tasks) surfaced 10 PE native-cron/workflow gaps. Closing them as a separate project (PE-GAPS, 1 parent + 5 epics + 25 tasks) unblocked the journal epic in the right order: lanes → receipts → HTTP → DAG → pipeline. The journal epic then sequenced cleanly on top.

## The pattern (4 phases)

### Phase 1 — Surface inventory

Before writing the feature epic, **inventory the platform the feature depends on**:

- Read the relevant source modules (e.g., `prismatic/native_crons.py`, `prismatic/lane_contracts.py`).
- Categorize by surface: cron / scheduler, dispatch / routing, agent harness, Linear integration, gateway / IPC, storage / state dbs, plugin / skill, quality / gates, sandbox / security, observability / telemetry, API / web, CLI / admin.
- For each category, list: exists / partial / absent / has-spec-but-no-impl.

### Phase 2 — Gap classification

For every "absent" or "partial" item that the feature requires, classify into three buckets:

| Bucket | Definition | When to fix |
|---|---|---|
| **Blocking** | Feature cannot ship without it | Before the feature epic — its own gap-closure parent epic |
| **Needs fill** | Feature can ship with workarounds, but the workaround is fragile | During the feature epic, as part of normal task execution |
| **Later** | Feature can ship, gap is out of scope | Separate project, not blocking the feature |

The journal epic's `G1` (no HTTP cron API) was **blocking** because [GRO-4255](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-4255) requires `POST /journal/cron/:job_name/run`. `G7` (workflow template) was **later** because no journal task needs it to ship.

### Phase 3 — Gap-closure project

If the **blocking** bucket has 3+ items, build a separate parent epic for the gap-closure project:

- Same handoff pattern as the feature epic: standard + project index + HANDOFF.md + risk register + ADRs + Linear tree.
- Sequencing is the dependency order (e.g., lanes before HTTP because HTTP needs lane contracts).
- Each gap-closure task description must include the **feature task it unblocks** in its acceptance-tests field, so the dependency chain is visible in Linear.
- Use the existing PE agent/dispatch/type label set; don't invent new labels.

### Phase 4 — Feature epic on top

Once the gap-closure parent epic's exit criterion is verifiable (e.g., schema lands + endpoints exist + DAG enforcement works), the feature epic can sequence cleanly. Its dependency chain becomes:

```
gap-closure epic  (closes first)
   └── feature epic  (closes on top)
```

## Sequencing rules

1. **Gap-closure before feature.** If the feature's first task requires a gap-closure artifact, the gap-closure task must close first.
2. **Within gap-closure:** schema-first, then hooks, then UI/API, then DAG/orchestration, then templates. Example from PE-GAPS: lanes → receipts → HTTP → DAG → pipeline.
3. **Never fold "blocking" gaps into feature epics.** It's tempting to save an OKF doc and Linear tree, but the resulting parent epic's exit criterion becomes "feature works AND gap is closed," which never completes until both ship — usually neither does.

## What goes in the gap-closure discovery report

A good gap-closure discovery report (`okf/reports/<date>-<slug>-discovery.md`) has:

- A **current-state table** showing every platform surface (exists/partial/absent).
- A **gap table** with severity bucket (blocking/needs-fill/later) + the feature task each gap blocks.
- A **proposed plan** listing the parent epic + child epics + child tasks.
- An **evidence boundary** statement: "ad hoc targeted discovery, not full PE-suite green."

## Pitfalls

- **Don't conflate feature and gap-closure.** Two parents, two exits, two sets of owners. Mixing them creates an unclosable parent.
- **Don't skip the inventory.** Reading the platform's actual surface (not relying on memory) prevents inventing gaps that don't exist and missing ones that do.
- **Don't classify gaps optimistically.** If a "partial" surface is critical-path, treat it as blocking. Under-classifying bites later.
- **Don't use generic placeholder owners.** "TBD" or "team" is not an owner. Name a role (ned, fred, AGY) and a verification signal per gap.
- **Don't close the gap-closure parent until every child is individually evidenced.** A parent epic that closes "when the platform supports it" never closes. Each child needs exit-criterion evidence.
- **Don't make the gap-closure parent depend on the feature epic.** The dependency direction is one-way: feature depends on gap-closure, never the reverse.