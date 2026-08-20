# One-task dry run blocked on `source_path` packet contract

Session learning from the first AGY one-task autopilot dry run.

## What was attempted

A governed local-canary AGY task was run after landing/deploying the merge-backlog gate. The intended lane was:

```text
runtime preflight
→ resolved_agent=agy
→ one AGY sandbox task
→ AGY_RESULT_PACKET.json
→ POST /api/agy/completed-work/ingest
→ merge-backlog dry-run plan
→ verification gate
```

## Preflight findings

- PR branch SHA ancestry is not reliable after squash merge. The runtime had squash commit `573da0e` for `[Fred] Add AGY clean PR verification gate (#GRO-3837)`, while the branch commit was `5505a8c3`. A `git merge-base --is-ancestor 5505a8c3 HEAD` check failed even though the feature was deployed. Use deployed endpoint markers plus commit subject/content when proving squash-merged runtime state.
- The installed AGY CLI accepted display model names, not stale internal aliases. `--model gemini-3.5-flash` failed; `--model "Gemini 3.5 Flash (Medium)"` passed.
- The active dispatcher `launch_agy()` path in the repo used an older `--headless --issue` shape, while the installed AGY CLI exposed `--print`, `--sandbox`, and `--add-dir`. For isolated one-task dry-run proof, use the verified installed CLI shape rather than assuming the dispatcher wrapper is current.

## Result

AGY launched exactly once and produced a structured packet. The packet was ingested and assigned row:

```text
completed_work_row=agy-cw-1dde34fce68cdd98
```

However, completed-work classification was rejected:

```text
classification=rejected
reason=missing packet fields: source_path
merge_backlog.action=rejected
verification_gate=blocked
eligible_for_auto_merge=false
```

The correct closeout marker was therefore:

```text
AGY_AUTOPILOT_ONE_TASK_DRY_RUN_BLOCKED
```

not `AGY_AUTOPILOT_ONE_TASK_DRY_RUN_OK`.

## Durable fix for next run

The AGY task prompt and any packet template must require `source_path`. For local canaries, use a sandbox-relative or absolute artifact path that the completed-work gate can reason about, for example:

```json
{
  "source_path": "/tmp/agy-one-task-canary-.../agy-one-task-lane-note.md",
  "changed_files": ["agy-one-task-lane-note.md"]
}
```

Do not synthesize or repair the packet after AGY emits it when the task limit is exactly one. If the packet is rejected, report `PARTIAL_BLOCKED`/`AGY_AUTOPILOT_ONE_TASK_DRY_RUN_BLOCKED` and preserve the row ID/rejection reason.

## Compact closeout pattern

```text
RESULT=PARTIAL_BLOCKED
MARKER=AGY_AUTOPILOT_ONE_TASK_DRY_RUN_BLOCKED
AGY_task_count=1
resolved_agent=agy
preflight_agent=PASS
bulk_dispatch=false
auto_merge=false
real_github_pr_created=false
blocker=AGY packet missing source_path; completed-work gate rejected it
```
