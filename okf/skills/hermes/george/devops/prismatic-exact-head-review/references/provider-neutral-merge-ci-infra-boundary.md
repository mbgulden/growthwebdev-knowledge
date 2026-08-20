# Provider-neutral merge when GitHub CI fails before code execution

Session pattern captured from CRONAUTH-1 acceptance/merge.

## Durable lesson

GitHub CI can report `failure` without executing candidate code. Treat that as an infrastructure boundary only when job metadata proves there was no runner assignment and no step execution.

Evidence shape:

```text
JOB=<job id>
conclusion=failure
runner_name=""
steps=[]
started_at/completed_at differ by only a few seconds
```

If all failed jobs match that shape, do **not** claim GitHub tests passed or failed. Record:

```text
GITHUB_CI=INFRA_FAILURE; runner_name empty; steps empty; no code executed
NOT_CLAIMING=GitHub test execution
```

This does not by itself authorize merge. It only prevents a no-run CI failure from overriding a separate accepted proof path.

## Safe merge prerequisites

Before merging under provider-neutral proof, verify all of these:

1. Michael has authorized merge policy for exact-head independent/local proof.
2. PR `headRefOid` equals the independently reviewed candidate head.
3. PR base SHA and remote `main` still equal the reviewed base.
4. Worktree is clean at the reviewed head/tree.
5. Independent review is fresh, exact-head, and CLEAN/PASS.
6. Local exact archive/adversarial proof and required focused/regression/static gates pass.
7. CI failure, if present, is explicitly bounded as no-run infrastructure, not test evidence.

## Post-merge binding proof

After merge, verify the merge commit is exactly base plus reviewed head:

```bash
git fetch origin main
MERGE=<merge sha>
git rev-parse "$MERGE^{tree}"
git show -s --format='%P' "$MERGE"
```

Expected:

- merge tree equals reviewed candidate tree;
- parents equal `<reviewed-base> <reviewed-head>` in that order;
- remote `main` equals the merge commit.

## Reporting boundary

Always separate:

- `independent CLEAN/PASS`;
- `local exact archive proof`;
- `GitHub CI no-run infra failure`;
- `merged`;
- `deployed` / `live migration` / `runtime activation` / `Linear write`.

A valid proof packet should include:

```text
RESULT=PASS
SCOPE=<reviewed-head-to-merge binding>
AD_HOC_OR_CANONICAL=ad-hoc targeted post-merge exact-head verification
NOT_CLAIMING=GitHub test execution, deployment, live migration, runtime activation, Linear mutation, or successor admission
MARKER=<slice>_<merge>_MERGE_BOUND_OK
```
