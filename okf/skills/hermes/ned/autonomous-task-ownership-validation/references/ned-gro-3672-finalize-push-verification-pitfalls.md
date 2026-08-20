# GRO-3672 finalize / push / verification pitfalls

Session pattern worth reusing for Ned autonomous implementation tasks.

## What happened

A normal implementation task completed with code, tests, docs, commits, `finalize_task.sh`, push, PR, and Linear evidence. Three reusable pitfalls surfaced:

1. **`finalize_task.sh` can exit 0 while Linear side effects fail.** In this run it committed nothing because the tree was clean, but printed warnings for Linear UUID resolution and `commentCreate` HTTP 400. The script still exited 0 and printed a finalization report.
2. **Verify Linear state/comment after finalize when warnings appear.** A follow-up GraphQL query showed the issue had not transitioned. Manual GraphQL `issueUpdate` and `commentCreate` using variables API corrected the state/evidence.
3. **Push can fail from stale/shallow branch ancestry.** Push rejected with `remote unpack failed: index-pack failed` / `did not receive expected object <sha>`. The durable fix was to fetch the remote base branch, rebase the work onto the remote branch that already carried the prerequisite master-plan commit, then push again.
4. **Cron verifier may not detect prior tests as canonical evidence.** When the system says verification is unverified after edits, create a focused `/tmp/hermes-verify-*` script using `tempfile`, run changed behavior through API/CLI/lint checks, remove the script, and report it explicitly as ad-hoc verification — not full suite green.
5. **Redispatch after the issue is already In Review may be verification-only.** If the branch/PR/evidence already exist and Linear is already `In Review`, do a fresh targeted verifier + focused tests and post a verification-refresh comment. Do **not** blindly rerun `finalize_task.sh` when `git status --short` shows unrelated untracked/modified files, because the script runs `git add -A` in the repo and can auto-commit another agent's work.

## Reusable sequence

After `bash ~/.hermes/profiles/ned/scripts/finalize_task.sh ISSUE BRANCH ned`:

```bash
# If finalize printed WARN lines for Linear, verify before claiming state.
# Query issue state and last comments via Linear GraphQL variables API.
# If needed, run issueUpdate + commentCreate manually with variables, not inline JSON.
```

If push fails with missing expected object:

```bash
git fetch origin <base-branch>
git branch <branch>-pre-rebase-backup HEAD
git rebase --onto origin/<base-branch> <old-local-base-sha> <branch>
# Re-run focused verification after rebase, because the base changed.
git push origin <branch>
```

When asked for ad-hoc verification after the fact:

```bash
tmp_script=$(mktemp /tmp/hermes-verify-XXXXXX.py)
# write a small Python verifier that imports/calls changed behavior,
# uses tempfile.TemporaryDirectory(prefix="hermes-verify-...") for mutated fixtures,
# and runs any focused lint/CLI checks.
python3 "$tmp_script"
status=$?
rm -f "$tmp_script"
exit $status
```

Two ad-hoc verifier gotchas from the GRO-3672 re-check:

- A `/tmp/hermes-verify-*` script does not automatically import repo packages even when invoked from the repo. Add the repo root explicitly before imports:

  ```python
  import sys
  from pathlib import Path
  sys.path.insert(0, str(Path.cwd()))
  ```

- Do not assume validator result shapes from memory. Inspect or read the implementation first. For `plugins.pwp.theme_validator.validate_theme_package`, the return value is a `ThemeValidationResult`, and `result.errors` is a list of strings, not objects with `.message`.

Report the result as **targeted ad-hoc verification**, not as canonical suite evidence.
