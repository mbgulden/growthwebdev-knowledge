# Parent epic evidence refresh pattern

Use when the Prismatic scanner dispatches Ned on a parent/epic issue that already has child-task history, comments, or PR evidence.

## Trigger

- Linear issue is labeled `epic` or reads like a parent remediation task.
- Comments already include Ned finalization/evidence reports.
- Children are mixed state, especially one or more still `In Review`.
- A remote branch/PR already exists for the parent.

## Pattern

1. Read the parent issue including comments and children before touching files.
2. Inspect linked child PR/check evidence. A parent with an in-review child is not Done/green just because earlier children are Done.
3. If prior parent comments already show branch/PR/build evidence, do a fresh verification pass and finalization refresh instead of duplicating implementation.
4. For non-`prismatic-engine` repos, run `finalize_task.sh` with explicit overrides:

```bash
PRISMATIC_REPO_ROOT=/tmp/<worktree> \
FINALIZE_LOCK_FILES='docs/operations scripts/operations' \
bash ~/.hermes/profiles/ned/scripts/finalize_task.sh GRO-XXXX ned/GRO-XXXX ned
```

5. Keep parent epics in **In Review**, not Done, until all required child proof is merged/green.

## Pitfall

The scanner can redispatch a parent epic after Ned already opened a PR. Re-read comments and child states; the useful action may be a small evidence refresh/finalize, not another code change. Do not mark a parent Done from intent or partial child completion.
