# Linear title-prefix search — pattern + gotchas

## When to use this

Some Linear task sets are grouped by a **bracket-prefix tag in the title**
(e.g. `[PE-KPI-FUNNEL]`, `[PWP Extraction]`, `[PWP–PE Integration]`) rather
than by a Linear project entity or label. When you need to enumerate "all
tasks in this bucket", the right filter is the title prefix.

## The pattern

```graphql
query {
  issues(
    filter: { title: { contains: "[PE-KPI-FUNNEL]" } }
    first: 100
  ) {
    nodes {
      identifier
      title
      state { name type }
      priority
      assignee { name }
      labels(first: 5) { nodes { name } }
      updatedAt
    }
  }
}
```

Works on the live API as of 2026-07-31 (verified via introspection).
`containsIgnoreCase` and `contains` both work; `containsIgnoreCase` is
safer if the bracket prefix may be upper- or lower-cased.

## Falsy-filter traps to avoid

These all return zero results and waste a round-trip:

1. `filter: { project: { name: { contains: "PE-KPI" } } }` — there is no
   Linear project named "PE-KPI-FUNNEL"; the tag is text-in-title only.
2. `filter: { labels: { some: { name: { eq: "PE-KPI-FUNNEL" } } } }` — the
   label literally does not exist. A search for `issueLabels` containing
   `KPI` returns only `plugin:pwp` and `task:shape-violation` (2026-07-31).
3. `filter: { identifier: { contains: "PE-KPI" } }` — `identifier` is
   `Comparable` (eq/in), not `StringComparator` (contains).

## What the live schema actually accepts

Introspect to confirm:

```graphql
{ __type(name: "IssueFilter") { inputFields { name } } }
{ __type(name: "StringComparator") { inputFields { name } } }
```

The full set of `StringComparator` fields is:
`eq`, `neq`, `in`, `nin`, `eqIgnoreCase`, `neqIgnoreCase`, `startsWith`,
`startsWithIgnoreCase`, `notStartsWith`, `endsWith`, `notEndsWith`,
`contains`, `containsIgnoreCase`, `notContains`, `notContainsIgnoreCase`,
`containsIgnoreCaseAndAccent`.

## Worked example: PE-KPI-FUNNEL

The 12 KPI PWP plugin tasks (verified 2026-07-31):

- `GRO-4356` Epic — LLM-driven funnel config + Linear dispatch
- `GRO-4357` F1 — Build LinearClient wrapper
- `GRO-4358` F2 — funnel_config capability (form schema + dispatch)
- `GRO-4359` F3 — Dashboard modal + 'Configure website KPIs' button
- `GRO-4360` F4 — Dashboard 'Edit funnel' modal + refinement task
- `GRO-4361` F5 — Stripe API registration step
- `GRO-4362` F6 — Zapier webhook registration step (Active Oahu v1)
- `GRO-4363` F7 — Multi-tenant groundwork (tenant_id propagation)
- `GRO-4364` F8 — Linear status polling → dashboard ETA
- `GRO-4365` F9 — Agent skill `build_kpi_funnels` (audit + build)
- `GRO-4366` F10 — Active Oahu end-to-end live test
- `GRO-4367` Configure KPIs for ezshare.systems (HIGH priority, the parent)

All 12 were unassigned and in `Backlog` state at the time of audit.

## Pitfall: assume the tag isn't a label

If the system prompt or a previous session's handoff says "the KPI project
is X", always cross-check by enumerating `projects` and `issueLabels` first.
If neither contains your tag, the tag is title-prefix only. This is the
single most common reason An agent's "show me the open tasks for X" query
returns zero results.
