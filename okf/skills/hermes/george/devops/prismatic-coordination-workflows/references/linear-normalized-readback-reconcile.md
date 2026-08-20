# Linear normalized readback reconciliation

## Trigger
Use this when a reviewed Prismatic Linear writer creates or finds the intended issue, but exact byte readback fails after Linear canonicalizes Markdown/plain-text description formatting.

## Lesson
Linear may normalize submitted descriptions (for example, inserting blank lines before Markdown list blocks). Treat this as a post-mutation reconciliation problem, not permission to retry creation.

## Required recovery pattern
1. Preserve the failed packet/writer version as lineage; do not edit it in place or let it authorize further mutation.
2. Reconcile by exact title and require exactly one non-canceled issue candidate. Check pagination on every Linear connection used for the candidate and readback.
3. Bind the live server identity before any repair: server issue ID, identifier, team, state, labels, and updated timestamp as applicable.
4. Compute a bounded diff between intended description and Linear's actual readback to identify canonicalization vs real drift.
5. Freeze a new packet version that embeds Linear's actual normalized description and explicitly changes authority to reconcile-only.
6. Remove all Linear mutation code paths and mutation strings (`issueCreate`, `issueUpdate`, GraphQL `mutation ...`) from the reconciliation writer. Static absence checks are part of proof.
7. The reconcile-only writer must require the exact known server ID and identifier, then exact full-field readback, before registry mirror.
8. Dry-run must remain filesystem read-only: hash the receipt/lock tree before and after dry-run and require invariance.
9. If registry mirror fails after Linear identity/readback succeeds, report `PARTIAL_REGISTRY_REPAIR_REQUIRED` truthfully; do not imply Linear mutation failed and do not create a second issue.

## Non-claims
- This does not authorize a second Linear issue creation.
- This does not authorize Linear updates, source changes, deployment, runtime restart, event POST, producer launch, or Git cleanup.
- A semantically correct issue is not enough; either exact normalized readback passes or the gate remains blocked.

## Compact proof fields
```text
ISSUE=<identifier + server id>
EXACT_TITLE_CANDIDATES=<count>
DESCRIPTION_NORMALIZED_READBACK=<PASS|BLOCKED>
LINEAR_MUTATION_STRING_ABSENT=<true|false>
DRY_RUN_RECEIPT_FS_UNCHANGED=<true|false>
REGISTRY_MIRROR=<PASS|PARTIAL|BLOCKED>
NOT_CLAIMING=<source/deploy/runtime/etc.>
```
