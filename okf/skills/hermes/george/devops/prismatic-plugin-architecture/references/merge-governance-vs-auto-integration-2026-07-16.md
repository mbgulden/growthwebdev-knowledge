# Merge governance vs automated integration — 2026-07-16

## Session lesson

Michael asked whether Prismatic already had an automated merge workflow and whether AGY completed tasks should still require manual integration. The important distinction:

- Prismatic has **merge/worktree governance** surfaces: merge backlog API, worktree janitor, proof bundles, value classes, and promotion recommendations.
- Prismatic does **not yet have a complete AGY completed-work auto-integration pipeline** that safely converts AGY output into verified PR updates/merges/writebacks.

Do not overclaim the existing workflow as “auto-merge everything.” It is safer and more accurate to call it:

```text
merge triage / worktree governance / promotion recommendation
```

not:

```text
full automated AGY merger
```

## Existing foundations to check

- `prismatic/worktree_janitor.py`
  - `promotion_recommendation` values such as `open-or-update-pr`, `capture-proof-or-promote`, `promote`, `manual-conflict-review`, `safe-remove`.
  - proof-file loading and value classification.
- `prismatic/docs/worktree-janitor.md`
  - safety contract and proof bundle contract.
- Gateway merge backlog API:
  - `GET /api/governance/merge-backlog`
  - `GET /api/gateway/governance/merge-backlog`
- Proof files agents may leave:
  - `.prismatic/worktree-proof.json`
  - `prismatic-worktree-proof.json`
  - `.worktree-proof.json`

## Gap to fill

The missing bridge is:

```text
AGY completed work
→ validated handoff/result packet
→ lane/scope check
→ proof check
→ classify merge-ready / rebuild / blocked / superseded
→ create or update clean PR
→ run verification
→ update Linear/dashboard
→ optionally enable safe merge
```

Until that bridge exists, AGY completions may still require Fred/Kai manual review, PR body correction, clean rebuild, or integration triage.

## Dashboard/operator route lesson

When Michael says the dashboard is down, do not rely on memory. Probe both public and local routes. In this session the Gateway was active and `/health` was 200, but `/` and `/dashboard` were 404 both publicly and locally. `/workspace-tree` was 200. The app had no `/` or `/dashboard` route registered, while `/api/governance/merge-backlog` existed locally.

Use precise language:

- `health 200` ≠ dashboard is up.
- `/workspace-tree 200` ≠ root dashboard is up.
- local API route 200 + public route 404 may indicate nginx/proxy exposure gap.

## Fred prompt shape for the gap

A safe next Fred task is **not** blind auto-merge. It should implement an integration gate:

```text
AGY_COMPLETED_WORK_INTEGRATION_GATE_OK
```

Minimum classifier cases:

- clean merge-ready
- needs clean rebuild
- branch/base mismatch
- out-of-lane files touched
- missing verification proof
- superseded by Fred/manual replacement

Non-goals:

- no bulk auto-merge
- no production checkout mutation
- no closing tasks without Linear/dashboard writeback
- no canonical-suite claims unless the suite actually ran

## Reporting preference

Michael wants this distinction called out directly. Lead with whether the automation exists, then separate:

1. what is implemented,
2. what is only governance/recommendation,
3. what gap remains,
4. the next Fred task.
