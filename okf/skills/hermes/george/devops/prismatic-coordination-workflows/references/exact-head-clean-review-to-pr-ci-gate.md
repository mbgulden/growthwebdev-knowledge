# Exact-head CLEAN review to PR CI gate

Use this when a Prismatic cap-1 source slice receives a fresh independent `CLEAN` review for an exact candidate but has not yet merged.

## Preconditions

- Independent review is bound to the exact candidate head/tree and says `CLEAN`.
- The candidate worktree is clean.
- Changed paths are inside the authorized task scope.
- Local proof has already been run on the exact head, but local proof remains separate from GitHub CI.
- Merge/deploy/live-state actions remain gated by current policy.

## Closeout sequence

1. **Preserve the review artifact before public writes.** Write a concise `REVIEW_<HEAD>_CLEAN.md` under the task directory with exact `HEAD`, `TREE`, parent/base, delegation id, material findings, proof summary, non-material notes, and no-side-effect statement. Hash the artifact.
2. **Reconfirm exact candidate.** From the task worktree, assert:
   - `git rev-parse HEAD` equals the reviewed head;
   - `git rev-parse HEAD^{tree}` equals the reviewed tree;
   - `git status --porcelain` is empty;
   - `git diff --name-only <base>..HEAD` matches only expected paths.
3. **Push only the reviewed branch.** Use `git push --set-upstream origin <branch>` and immediately verify the remote ref with `git ls-remote`; do not create a PR if the remote head is not the reviewed SHA.
4. **Create the PR body from a Markdown file.** Include exact base/head/tree, independent review id/verdict, local proof, changed-path allowlist, marker, and explicit non-claims for deployment/restart/live DB/cursor/Linear/generic-dispatch/cap increase. Avoid inline shell PR bodies; backticks/angle brackets/`$VARS` can be mangled before `gh` receives them. Delete the temporary body file after PR creation if it is not intended as a durable artifact.
5. **Create/read back one focused PR.** If `gh pr create` succeeds, immediately re-read it; do not rely on the creation URL alone.
6. **Use supported `gh` fields and REST fallback.** `gh pr view` does not support every REST field (for example, `baseRefOid` may be invalid). If a metadata query fails, discard it and re-read with supported fields plus `gh api repos/<owner>/<repo>/pulls/<number>` for `base.sha`, `head.sha`, `mergeable`, and `mergeable_state`.
7. **Verify PR scope/readback.** Confirm PR is open, non-draft, base is `main`, head SHA equals the reviewed SHA, file list matches expected paths, body markers/non-claims are present, and mergeability/CI state are reported honestly. Treat `mergeable=MERGEABLE` plus `mergeStateStatus=BLOCKED` as CI/review pending until required checks conclude.
8. **Read checks as pending, not failed.** `gh pr checks` is useful for job names and URLs; pending checks are a wait state, not a failure. A readback command may be wrapped with `|| true` only to capture the pending table, never to claim success.
9. **Start a bounded CI watcher if checks are pending.** Use `gh pr checks <PR> --watch --interval <seconds>` or `gh run watch <run> --exit-status` as a background process with `notify_on_complete=true`. Report `CI_PENDING`, not green, until GitHub finishes all required jobs.
10. **Update durable handoff/control state.** Move from `EXACT_HEAD_REVIEW_PENDING` to `PR<NUMBER>_EXACT_HEAD_CI_PENDING`, recording PR URL, base/head SHA, mergeable state, CI run/check URLs, watcher process id, review artifact path/hash, and non-claims.

## Boundaries

- Opening the PR is not a merge.
- `mergeable=true` with `merge_state=blocked` is normally CI/review gate pending, not approval to merge.
- A local canonical pass does not replace required GitHub CI.
- Do not deploy/restart/repoint/mutate live DB or cursor/write Linear/resume generic dispatch/raise cap from this gate.
- If a new commit is added after the CLEAN review, the clean review is stale; return to exact-head review pending.

## Compact proof packet

```text
COMMAND=<push/pr-create/pr-readback/checks>
RESULT=<PASS|PENDING|FAIL|BLOCKED>
PR=<url>
BASE_SHA=<sha>
HEAD_SHA=<reviewed sha>
TREE_SHA=<tree>
REVIEW=<delegation id>
REVIEW_SHA256=<artifact hash>
CHANGED_PATHS=<exact allowlist>
CI_RUN=<run id>
CI_STATE=<pending|pass|fail>
AD_HOC_OR_CANONICAL=GitHub CI/readback + local proof separately
NOT_CLAIMING=merge,deploy,restart,live DB/cursor mutation,Linear,generic dispatch,cap increase
MARKER=PRISMATIC_<SLICE>_SOURCE_OK
```
