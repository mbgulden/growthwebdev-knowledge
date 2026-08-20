# Exact merge release closeout and event-only successor admission

Use after a Prismatic PR-head review returns `CLEAN_TO_MERGE` for an already independently reviewed candidate.

## Durable closeout sequence

1. Re-query the live PR immediately before merge and fail closed unless all expected fields still match:
   - `state=OPEN`
   - `isDraft=false`
   - `baseRefName=main`
   - `mergeable=MERGEABLE`
   - `headRefOid=<reviewed candidate sha>`
2. Merge only when current policy/authorization covers the merge.
3. Fetch `origin/main` and verify:
   - merge SHA is the PR merge commit;
   - merge tree equals the reviewed candidate tree;
   - no extra content entered through the merge.
4. Create a durable release checkout with a fresh non-local clone, e.g. `/home/ubuntu/.prismatic/releases/<merge-short-sha>`.
5. Detach the release checkout at the merge SHA and prove:
   - `git fsck --full` passes;
   - `.git/objects/info/alternates` does not exist;
   - worktree is clean;
   - `HEAD^{tree}` equals the reviewed tree.
6. Run focused release validation from the release checkout:
   - relevant tests for the slice;
   - lints/format checks on changed files;
   - schema parity/content probes if schemas are part of the change;
   - wheel build, isolated install, and packaged-resource import when packaging behavior matters.
7. Before admitting a successor, prove whether the merged release is merely staged or actually active in the runtime:
   - read the loaded systemd `ExecStart` and `WorkingDirectory` with `systemctl show`;
   - inspect `DropInPaths`/`systemctl cat` because stacked drop-ins override the base unit file;
   - compare the live release/venv to the newly staged merge release;
   - if they differ, keep `NEW_TASK_ADMITTED=false` and report an explicit immutable deployment authorization point.
8. Update handoff/control state with accepted/closed status, release proof, live-runtime release, and deployment hold/activation status.
9. Keep the next task queued, not admitted, until the dashboard/event queue contract is verified against the live runtime that actually contains the required gate.

## Proof block template

```text
PR=<url> MERGED
PR_HEAD=<reviewed sha>
PR_HEAD_REVIEW=<delegation id> CLEAN_TO_MERGE
MERGE_SHA=<merge sha>
MERGE_TREE=<tree sha>
MERGE_TREE_EQUALS_REVIEWED_TREE=true
RELEASE=<durable release path>
RELEASE_NO_ALTERNATES=true
RELEASE_FSCK=PASS
RELEASE_LOG=<path>
RELEASE_LOG_SHA256=<sha256>
AD_HOC_OR_CANONICAL=<focused release|canonical suite>
NOT_CLAIMING=<deployment/restart/hosted CI/next-slice admission unless actually done>
```

## Event-only admission pitfall

Do not fabricate or assume a dashboard event endpoint from route guesses. If `/openapi.json` or `/api/openapi.json` are absent, say discovery is unavailable and prepare the next task contract without admitting it until the actual dashboard/event queue contract is verified.
