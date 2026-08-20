# Verified Execution Contract + clean publish lessons — 2026-07-08

## When this applies

Use this reference for Prismatic Proof Loop / Golden Thread execution tasks where a result must be promoted from local work to reviewable/merged code with evidence.

## Core pattern learned

### 1. Do not let self-report become Done

For proof-loop work, create a canonical evidence contract before wiring dashboards/status moves:

- `verification_status`: `verified`, `partially_verified`, `blocked`, `failed`, `self_reported`.
- `verification_scope`: `ad_hoc_targeted`, `canonical_full_suite`, `live_integration`, `not_run`.
- `failure_category`: `none`, `timeout`, `blocked_external_api`, `blocked_missing_context`, `verification_failed`, `conflict`, `hallucinated_claim`, `tooling_error`.
- Required payload fields: task/run id, summary, commands and/or artifacts, files changed, external side effects, cleanup status, blocker/failure category when applicable.

A `done_gate("Done", evidence)` style check should return:

- `not_done` when evidence is missing.
- `not_done` when evidence is only `self_reported`.
- `not_done` for partial/blocked/failed evidence.
- `done` only for validated `verified` evidence.

### 2. Clean-branch publish recovery for shallow/local history

If a feature branch fails to push with a remote unpack/missing-object error, do not keep retrying the same bad history. Diagnose briefly:

```bash
git rev-parse --is-shallow-repository
git fsck --full --no-dangling
git show -s --format='%H %P %s' <missing-object-or-suspect-commit>
git merge-base --is-ancestor origin/main HEAD; echo $?
```

If the branch is based on local/shallow ancestry that the remote cannot ingest, create a clean publish branch from the fetched remote tip and cherry-pick only the intended commits:

```bash
git fetch origin main
git worktree add -b feature/<clean-publish-name> /tmp/<clean-worktree> origin/main
cd /tmp/<clean-worktree>
git cherry-pick <commit1> <commit2> ...
```

Then rerun the gates from the clean worktree before pushing. Cherry-picking onto a clean base can expose real packaging gaps that the old local base hid.

### 3. Verify clean-base packaging, not just the original branch

After clean cherry-pick, rerun:

```bash
python3 scripts/distribution_readiness_smoke.py --fresh-install
python3 scripts/<demo-or-contract-smoke>.py --clean
python3 -m ruff check <changed-python-files>
python3 -m ruff format --check <changed-python-files>
```

In the 2026-07-08 run, the clean base exposed a missing runtime dependency (`packaging`) imported by `prismatic.core.registry`. The durable lesson is not the exact missing package; it is that **fresh-install smoke on the clean publish branch is mandatory before claiming first-user readiness or opening a PR**.

### 4. Evidence posting can be blocked separately from code completion

If Linear comment/update helpers start returning schema/API errors after earlier comments succeeded:

- Stop after one or two schema-correct attempts.
- Preserve a Linear-ready evidence comment locally.
- Report the Linear posting blocker separately from PR/verification state.
- Do not keep hammering Linear just to make the task tracker pretty.

### 5. Guard-triggered verification after closeout artifacts

If a closeout/evidence artifact is written after the main verifier ran, rerun a fresh `/tmp/hermes-verify-*` script over the final changed set. Include:

- py_compile for changed Python.
- lint/format checks where applicable.
- the targeted smoke command.
- assertions that docs/evidence comments contain the required scope, blocker, cleanup, and PR/issue references.
- cleanup confirmation for the `/tmp/hermes-verify-*` script.

Label explicitly: **ad hoc targeted verification, not canonical/full-suite green** unless the canonical suite actually ran and passed.
