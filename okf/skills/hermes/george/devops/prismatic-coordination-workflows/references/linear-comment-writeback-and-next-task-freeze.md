# Linear comment write-back and next-task freeze

Use this reference when a Prismatic gate needs to write a bounded Linear status/merge-proof comment and then freeze the next assigned-agent task without admitting it.

## Comment-only Linear writer pattern

- Treat a Linear comment write as a mutation gate even when the issue is already `Done`.
- Build a narrow writer with only the approved mutations:
  - allowed: `commentCreate`, `commentDelete`
  - forbidden: issue/state/label/relation/assignee/project mutations
- Freeze the public comment bundle and compile its expected SHA-256 into the writer. Do **not** accept a caller-supplied bundle hash as authority; otherwise a modified bundle plus matching modified hash can pass.
- Run local failure-injection tests before live execution:
  - dry-run no-op
  - success
  - duplicate/idempotent existing marker
  - create applies then times out, followed by stale reads before convergence
  - no-apply timeout
  - postcondition drift after create, with rollback
  - delete/rollback applies then times out, followed by stale reads before absence converges
  - adversarial modified bundle rejected even if caller supplies its matching hash
- Run a live dry-run before execution and an exact-byte independent review before any live write.
- Live postcondition verification should independently re-read Linear and assert exactly one marker comment with exact body and comment ID.

## Important `updatedAt` boundary

Creating a Linear comment legitimately changes the issue `updatedAt`. A post-execution duplicate/idempotence check that still requires the original pre-comment `updatedAt` can fail even when the write is correct.

For post-write verification:

- Compare only guarded issue fields that should remain unchanged: id/identifier/title/state/labels and the exact marker comment body/id.
- Treat `updatedAt` as expected to move because of comment creation.
- If the approved bundle uses field names like `target.title`, do not invent `expected_title`; inspect the frozen bundle schema before writing verifier assertions.

## Next-task freeze without admission

When the next implementation slice already exists, reuse it instead of creating a duplicate issue/task.

For a frozen task contract:

- Bind to the exact merged base commit and tree.
- Copy the task into the clean worktree only as a task artifact; keep tracked repository state clean.
- Separate archive-reproducible tests from repository-provenance assertions. Immutable archives do not include `.git`, refs, or local worktree provenance.
- Require independent review of the frozen task contract before admission.
- Report `TASK_ADMITTED=false` and `PRODUCER_LAUNCHED=false` until Michael separately authorizes event admission/cap-1 launch.

## Compact proof fields

```text
LINEAR_WRITE_OPERATION=comment_only
LINEAR_COMMENT_ID=<uuid>
LINEAR_COMMENT_BODY_SHA256=<sha256>
LINEAR_MARKER_COMMENT_COUNT=1
LINEAR_GUARDED_FIELDS_UNCHANGED=true
LINEAR_UPDATED_AT_CHANGED_BY_COMMENT=true
LINEAR_FORBIDDEN_MUTATIONS=false
NEXT_TASK=<task>
NEXT_LINEAR=<issue>
NEXT_TASK_SHA256=<sha256>
NEXT_TASK_BASE=<commit>
NEXT_TASK_TREE=<tree>
NEXT_TASK_STATUS=FROZEN_REVIEW_CLEAN_NOT_ADMITTED
NEXT_TASK_ADMITTED=false
NEXT_PRODUCER_LAUNCHED=false
NOT_CLAIMING=deployment, hook implementation, cron/timer mutation, task admission, producer launch, canonical suite green
```
