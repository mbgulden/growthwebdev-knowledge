# Durable agent-bus dispatch and change-only watcher pattern

Session-derived pattern for when Telegram lane prompting does not visibly start a Prismatic helper task, but the work should continue without uncontrolled bulk/autopilot dispatch.

## Trigger

Use this when a bounded Fred/Kai/Ned task has been announced but no artifact, worktree, branch, PR, or result packet appears after a reasonable check.

## Pattern

1. **Verify absence before re-dispatching.** Check for the expected shared artifact, outbox result, worktree, branch, PR, and marker. Do not assume lack of chat response means lack of work if artifacts already exist.
2. **Use one bounded filesystem-bus task.** Create/dispatch a single task packet with explicit hard boundaries in `CONTEXT.json` such as `merge=false`, `deploy=false`, `linear_writeback=false`, `github_pr_create=false`, `auto_merge=false`, `bulk_dispatch=false`, and `production_restart=false`.
3. **Start from a clean merged base.** Require an isolated worktree from merged `main`, a named branch, and a marker-specific result contract.
4. **Capture the worker invocation log.** Record the bus log path and the required outbox `RESULT.md` path; do not claim completion until the result packet and/or shared artifact exists.
5. **Install a change-only watcher.** A short-interval `no_agent=True` cron script should emit one-line updates only on material state changes, otherwise stay silent. Good state fields include task id, worker service state, worktree, branch, base/head SHA, dirty path count, ahead count, diff stat, result existence, shared artifact existence, and parsed result status.
6. **Feed watcher state into the control plane.** The main audit-control script should read the watcher's latest JSON so global status can report `STARTED`/`AWAITING_ARTIFACT`/`FAILED` instead of a stale generic blocker.
7. **Update the handoff immediately.** Add the task id, worktree, branch, base SHA, watcher job id, marker, and side-effect boundary to `PRISMATIC_CURRENT_HANDOFF.md`.
8. **Review independently before PR action.** Once the result appears, George reviews the diff/evidence and distinguishes implementation done from tests/PR/merge/deploy.

## Good update shape

```text
Status: STARTED — <agent> claimed bounded task; no push/PR/merge/deploy authorization.
Task: <task_id>
Worktree: <path>
Branch: <branch>
Evidence: service active; diff stat; watcher last_status=ok
Boundary: result packet/shared artifact not yet present; not claiming tests/PR/merge/deploy
Next: wait for result packet, then George independent review
```

## Pitfalls

- Do not create multiple competing bus tasks for the same marker unless the previous one has clearly failed or been cancelled.
- Do not treat an active worker process or dirty worktree as completion.
- Do not make watcher output chatty; Michael asked for ongoing updates, but the durable pattern is change-only, evidence-based updates.
- Do not grant side effects implicitly through the bus. The task packet must preserve the same authorization boundary as chat.