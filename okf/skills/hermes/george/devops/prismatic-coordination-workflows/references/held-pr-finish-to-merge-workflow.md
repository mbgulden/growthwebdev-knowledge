# Held PR finish-to-merge workflow

Use this when Michael authorizes taking an old held/untrusted Prismatic PR from review hold toward merge.

## Reusable sequence

1. **Preserve the held head first.** Record PR number/title/state, remote branch head, tree, and current `origin/main`. Do not force-push or mutate the remote branch before local review.
2. **Create an isolated finish worktree/branch.** Bring the held branch onto current `origin/main` with an explicit merge/rebase decision. Report whether the old branch is behind and whether textual conflicts exist.
3. **Review the integrated diff against today’s main.** Verify the cumulative diff is bounded to intended paths. If formatters create unrelated churn, restore legacy files and reapply only semantic changes before committing.
4. **Repair completion gaps only after review.** Encode public bounds, docs, and adversarial regressions where the old PR’s contract is incomplete; do not broaden scope just because the branch is old.
5. **Classify baseline-red canonical failures with immutable-base parity.** If canonical commands fail, reproduce exact failing tests on immutable `origin/main`. Only label candidate proof as acceptable when the failure set is proven pre-existing/baseline-parity or repaired. Do not call baseline parity canonical green.
6. **Use commit-specific verification environments when setup ambiguity appears.** A shared venv missing optional deps is verifier setup non-evidence. Create a clean candidate venv matching the workflow extras, then rerun from the beginning.
7. **Bind clean-wheel proof to installed bytes.** Build from `git archive HEAD`, install from the wheel in a fresh/unrelated context, and assert the installed module file/hash is not coming from the source checkout.
8. **Freeze before publication.** Record HEAD/TREE/base, final changed paths, proof logs, and PR body. Push/PR-update/merge/Linear completion remain blocked until exact-head independent review returns clean/pass and Michael’s publication policy allows mutation.

## Proof packet fields

```text
PR=<number>
HEAD=<candidate commit>
TREE=<candidate tree>
BASE=<origin/main commit>
REMOTE_PR_HEAD=<remote branch head before mutation>
DIFF_SCOPE=<paths/additions/deletions>
CANONICAL=<green | baseline-parity classified | blocked>
CLEAN_WHEEL=<pass + installed source/hash proof>
INDEPENDENT_REVIEW=<pending|pass|blocked>
NOT_CLAIMING=<merge, deployment, Linear completion, or canonical green when not actually green>
```

## Pitfalls

- A branch that is many commits behind can merge textually cleanly while still having stale contract/documentation gaps.
- Formatter churn can inflate an otherwise small PR and hide review scope. Diff the cumulative candidate against `origin/main` after every formatting repair.
- A failed workflow under a reused venv may be setup non-evidence; prove with a workflow-matching fresh env before judging candidate code.
- Do not use Linear state changes or PR publication as verification. They are post-acceptance mutations gated by proof and authorization.
