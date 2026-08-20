# Prismatic Dashboard / Completed-Work Runway — 2026-07-17

## Session lesson

Michael pushed back on huge audit blobs. For Prismatic coordination, George should produce a **small execution packet first** and keep giant reports as appendices/downloads.

Preferred handoff layering:

1. **Cheat sheet / do-first packet** — 1-2 pages, ranked A/B/C/D buckets, exact commands, red flags.
2. **Full audit appendix** — exhaustive branch/worktree/source details only when needed.
3. **Review packet** — acceptance criteria and verifier shape before Fred finishes the next slice.
4. **Merge/deploy closeout** — compact proof with local/public/browser evidence.

## Product runway sequence that worked

Dashboard reconnect progressed cleanly as:

```text
source audit (#294)
→ first clean candidate Resources budget caps (#295)
→ completed-work classifier gate (#296)
→ completed-work ingestion (#297, pending fix/review)
```

The key operator boundary:

```text
classification/ingestion ≠ auto-merge
```

Completed-work gate/ingestion should advance in these layers:

```text
contract classifier
→ fixture API/dashboard status
→ real packet ingestion/persistence
→ Linear/dashboard writeback
→ clean PR create/update
→ PR verification gate
→ optional safe merge policy later
```

## George/Fred division of labor

When Fred is locked in and productive, George should not open competing implementation branches. George should own:

- independent PR/report verification;
- merge/deploy after Michael authorizes;
- runtime/public/browser proof;
- next-slice prompt drafting;
- review packets with acceptance criteria;
- digesting audit blobs into operator cheat sheets.

## Review packet pattern

Before Fred returns with a slice, prepare a George-side acceptance packet:

- existing surfaces to reuse / not duplicate;
- exact changed paths expected;
- negative tests and boundary checks;
- no-auto-merge/non-claim requirements;
- fresh `/tmp/hermes-verify-*` script outline;
- compact proof packet shape.

## Merge/deploy closeout pattern

After authorization:

1. Verify PR state and CI.
2. Merge in dependency order.
3. Update durable runtime checkout, not random dev checkout.
4. Restart relevant services.
5. Verify local routes.
6. Verify public routes.
7. Browser-check the dashboard surface and console.
8. Report explicit non-claims.

## Pitfalls found

- `gh pr merge --delete-branch` may merge successfully but fail local branch deletion if a worktree owns the branch. Always re-query PR state before assuming merge failed.
- `gh pr merge` can fail when local worktrees conflict with checkout behavior. If merge state is unclear, re-query GitHub and avoid repeated blind merge attempts.
- A stacked PR may be mergeable against its feature base but not ready for `main`; merge/deploy dependency PRs first, then rebase/retarget the stacked PR.
- Directly running repo scripts as `python3 scripts/foo.py` can miss repo-root imports. For committed CLI scripts expected to run that way, add repo root to `sys.path` before importing project modules, or document/run via module entrypoint. Treat a reported direct-run CLI proof as failing if it only works with ad-hoc `PYTHONPATH`.

## Useful markers from this runway

```text
DASHBOARD_RECONNECT_SOURCE_AUDIT_OK
RESOURCES_BUDGET_CAPS_PORT_OK
RESOURCES_BUDGET_CAPS_REVIEW_OK
AGY_COMPLETED_WORK_INTEGRATION_GATE_OK
AGY_COMPLETED_WORK_INTEGRATION_GATE_REVIEW_OK
AGY_COMPLETED_WORK_INGESTION_OK
```
