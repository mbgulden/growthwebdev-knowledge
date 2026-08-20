# AGY catalog/workdir/result verification addendum

Use this reference when a Prismatic assigned-AGY child is recovered or relaunched after stale model IDs, stale task caches, ignored workdir selection, or a misleading `DONE`/`RESULT.md` packet.

## Trigger

Apply this when any of these happen:

- AGY launch fails before edits because a model name/display label is stale or rejected.
- A supervisor receives an explicit `--workdir`, but the sandbox or source checkout binds to a different repository/base.
- `RESULT.md` claims a commit, but the sandbox `HEAD` is unchanged or the commit lives in another checkout.
- A child task is blocked by historical issue-batch files, cached task text, or generic dispatch false-completion claims.
- You need to choose an AGY model for a bounded Prismatic producer.

## Required sequence

1. **Freeze generic dispatch and keep cap 1.** This is assigned-child recovery, not a generic queue resume.
2. **Catalog from the child AGY auth HOME.** Run the authenticated model catalog from the same HOME the child will use, not George/default shell HOME. Use canonical emitted IDs, not display names.
3. **Smoke the selected model.** After catalog/auth changes, run a one-line authenticated smoke before launching a substantive producer.
4. **Normalize aliases only at the boundary.** Convert legacy/display names to canonical IDs before launch; do not persist stale display labels as defaults.
5. **Prefer current Flash tiers when proven by live catalog.** In the 2026-07-23 recovery, `gemini-3.6-flash-high` was the best default for complex multi-step agentic/coding work; `medium` fit bounded routine work; `low` fit simple throughput; 3.5 Flash remained only a fallback/regression lane. Re-check current catalog/provider guidance before treating that ranking as timeless.
6. **Make explicit `--workdir` highest precedence.** A CLI workdir must override issue-batch hints, cached source paths, or default Prismatic Engine checkouts. Fail closed if the selected source checkout is not the requested repository/base.
7. **Use non-launching preflight when available.** `--prepare-only` should generate the sandbox/task and stop before the child runs. Verify sandbox HEAD/tree, task hash, repository, allowed paths, and stale-instruction absence.
8. **Inspect the actual consumed task.** Read/hash the generated `AGY_TASK.md`; a clean Linear comment or regenerated issue-batch file is not proof of what AGY consumed.
9. **Treat `DONE` and `RESULT.md` as untrusted.** Verify real Git object location, parent, tree, changed paths, file hashes, secret scan, and whether the claimed commit is in the sandbox or a separate source worktree.
10. **Preserve tmpfs/source candidates before review.** If the commit exists outside the sandbox, classify it as an untrusted candidate, create a durable local ref/worktree, and bind review to the exact commit/tree/path hashes.
11. **Only advance after closure.** The sibling issue or next cap-1 task starts only after exact independent review, focused PR, exact-head CI, merge, remote-main tree parity, and post-merge main CI.
12. **Patch tier-switch tools carefully.** Scope string replacements to model-routing blocks/functions. Do not replace earlier identical keys in agent-ID/UUID maps.

## Verification packet

```text
CATALOG_HOME=<child auth HOME used for `agy models`>
CATALOG_MODELS=<count>
MODEL=<canonical emitted ID>
SMOKE=<PASS|FAIL + log>
REQUESTED_WORKDIR=<path>
SELECTED_SOURCE=<path>
SOURCE_REPO=<owner/repo>
SOURCE_BASE=<sha>
PREPARE_ONLY=<PASS|N/A>
TASK=<path>
TASK_SHA256=<sha256>
SANDBOX_HEAD=<sha>
SANDBOX_TREE=<tree>
RESULT_MARKER=<DONE|ABANDONED|ERROR|missing>
CLAIMED_COMMIT=<sha|null>
ACTUAL_COMMIT_LOCATION=<sandbox|source-worktree|none>
CHANGED_PATHS=<count/list>
SECRET_SCAN=<PASS|FAIL>
CANDIDATE_REF=<durable ref/worktree if preserved>
INDEPENDENT_REVIEW=<delegation id + verdict>
PR=<url|null>
PR_CI=<run + result>
MERGE=<sha|null>
POSTMERGE_MAIN_CI=<run + result>
NOT_CLAIMING=<deploy/Linear/generic dispatch/cap increase/etc.>
```

## 2026-07-23 session receipts

- Assigned PWP recovery completed sequentially at cap 1 for GRO-4152 and GRO-4154.
- `gemini-3.6-flash-high` became the canonical default after authenticated catalog/smoke proof.
- An explicit-workdir defect was caught because GRO-4154 prepared against Prismatic Engine instead of standalone PWP; the producer was killed and relaunched only after repair.
- A `DONE` packet was not accepted when `RESULT.md` falsely implied the commit was in the sandbox; the actual commit was preserved from the clean source worktree and sent to independent exact review.
- Final closure required exact-head PR CI, squash merge, remote-main tree parity, and post-merge main CI for both PRs; deployment/Linear/cap increase remained unauthorized.
