# Ned parent-epic finalization verification — 2026-07-18

Session class: Ned autonomous Linear parent epic finalization with docs/status artifacts and child PR evidence.

## Durable lesson

Finalizing a parent epic is not just `finalize_task.sh` plus a happy summary. There are three post-finalize drift points that need explicit verification before reporting completion.

## Pattern

1. **Fresh build evidence beats stale setup failure**
   - If `npm run build` first fails because dependencies are absent (`astro: not found`), run `npm ci` and rerun `npm run build` in the same worktree.
   - The final report must cite the fresh passing command, not the stale pre-install failure.
   - If a system verification nudge arrives, rerun the canonical command immediately and summarize the fresh output.

2. **Swarm lock owner/shape mismatch can leave locks behind**
   - `finalize_task.sh` may unlock as `unlock <file> prismatic-engine <agent>` while the lock was acquired as `lock <file> <agent>`.
   - After finalize, run `swarm.js status` for touched files.
   - If files remain locked, manually run:
     ```bash
     node /home/ubuntu/.antigravity/swarm.js unlock <repo-relative-path> ned
     ```
   - Verify status is clear before reporting.

3. **Linear state can drift after finalize/PR automation**
   - Re-query Linear after `finalize_task.sh` and PR creation.
   - If the intended handoff state is `In Review` but the issue is back in `In Progress`, reapply `In Review` and post a concrete evidence comment with PR/build/check status.
   - For parent epics that are explicitly not green, use `In Review` with a non-green status artifact; do not mark Done.

## Parent epic reporting rule

For a non-green parent epic, the evidence artifact should say:

- what child PRs/branches exist;
- which checks passed;
- which deployment/check remains stale or failing;
- what live verifier must return before Done;
- that production is not green from intent.

Servers do not care how convincing the Linear tree looked.