# Semantic-pass contract can still fail deployed admission identity

Use this when a pre-admission Prismatic contract/prompt has a clean semantic review but has not yet produced a task file or event.

## Lesson

A semantic `CLEAN/PASS` review of a repair contract is not enough to materialize task copies or freeze an envelope. The future execution identity must also pass the deployed admission schema and policy.

In the GRO-4318 repair chain, V5 was semantically clean but reserved a descriptive task id shaped like:

```text
CRONSTATUSCORE-1-MIGRATION-REPAIR-1
```

The deployed schema accepted only:

```text
^[A-Z][A-Z0-9]{1,15}-[1-9][0-9]{0,9}$
maxLength=32
```

So V5 stayed preserved as semantic evidence, but it was not executable. The successor V6 changed only the authority-bearing task identity and copy paths, then required fresh full review.

## Required gate before materialization

Before creating bus/worktree task copies or freezing an envelope, validate against the deployed release, not assumptions:

```text
TASK_ID matches deployed schema pattern and maxLength
BUS_TASK path is exact and task-specific
WORKTREE_TASK path is exact and task-specific
TASK_SHA256 is the reviewed artifact SHA
PRODUCER_IDENTITY matches deployed pattern/policy
WORKTREE, BASE_COMMIT, BASE_TREE are exact
IDEMPOTENCY_PREIMAGE uses stable frozen fields only
created_at remains the sole late-bound field
```

If identity fails:

1. preserve the semantic-pass artifact with review id and SHA;
2. create a new version with the minimum identity correction;
3. keep `TASK_FILE_CREATED=false`, `EVENT_CREATED=false`, `SOURCE_MUTATION=false`, `PRODUCER_LAUNCHED=false`;
4. dispatch fresh full review because task identity is authority-bearing.

## Non-claim

Do not report the semantic-pass artifact as ready to execute unless deployed identity compatibility is also proven.
