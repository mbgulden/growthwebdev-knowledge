# Post-merge next gate: Linear write-back + successor freeze without admission

Use this when Michael says “do the next gate” immediately after an exact-head Prismatic PR merge.

## Sequence

1. Treat the request as authorization to perform the bounded next gate, **not** as blanket authorization for deployment, cap increase, producer launch, or arbitrary Linear mutation.
2. Read the live Linear issue first. Integrations may already have projected `Done`/`completedAt` shortly after merge.
3. If Linear is already `Done`, do not issue an `issueUpdate`. The remaining write-back, if useful, should be a bounded comment-only proof with fixed issue fields and an exact marker.
4. Build/freeze a narrow writer before live comment execution:
   - fixed issue UUID and expected live fields;
   - fixed comment body and bundle SHA-256;
   - dry-run default;
   - no state/label/parent/relation/assignment/description mutations;
   - independent exact-byte review before `--execute`.
5. Reuse an existing successor Linear task if one already matches the merged contract. Do not create duplicates just because the next slice is now unlocked.
6. Freeze the successor task contract against the merged base commit/tree and exact task-file hash.
7. Create a clean worktree and copy only the frozen task contract when preparing the successor.
8. Verify freeze/readiness with read-only checks: base/tree, task parity/hash, allowlist, contract hash, no producer process, no tracked mutation.
9. Dispatch independent review of the frozen task contract.
10. Keep admission/producer launch blocked until the event dashboard admits the exact task and cap-1 readiness is proven.

## Proof packet

```text
LINEAR_STATE=<state/completedAt/updatedAt>
LINEAR_MUTATION=<none|comment-only pending review|comment-only executed>
SUCCESSOR_ISSUE=<id/title>
TASK_PATH=<path>
TASK_SHA256=<sha>
BASE=<merge sha>
TREE=<tree sha>
WORKTREE=<path>
ADMITTED=false
LAUNCHED=false
REVIEW=<delegation id/status>
NOT_CLAIMING=deployment, cap increase, producer launch, cron mutation, arbitrary Linear mutation
```

## Pitfalls

- Do not write Linear status fields if the integration already projected them; prove live state and switch to comment-only write-back if needed.
- Do not execute a newly written Linear writer without exact-byte independent review, even when the body is harmless-looking.
- Do not launch the successor just because the task contract is frozen. Freeze/review is not event admission.
- Do not poll processes repeatedly for cap-1; use dashboard/event receipts or a single known-state readback and report the boundary.
