# GRO-3736 — plugin-lane PR base + finalize refresh pattern

Session date: 2026-07-10

## Durable lesson

For PWP/plugin implementation tasks that reference a source/master-plan branch, do not blindly base the worktree on `origin/deploy-fresh` if the target plugin files only exist on the source branch. Use the issue's referenced branch as the feature-branch base when needed, then open the PR back to that branch unless the issue explicitly says otherwise.

## Concrete pattern

1. Read the issue and source links before creating the working branch.
2. If `plugins/pwp/**` or other task files are missing from `origin/deploy-fresh`, check the referenced plan/source branch.
3. Create a clean temp worktree from the source branch:

   ```bash
   git worktree add -b ned/GRO-XXXX /home/ubuntu/work/ned-GRO-XXXX-worktree origin/<source-branch>
   ```

4. Keep verification files inside Ned's writable lane when possible. For plugin tasks, focused tests belong under:

   ```text
   plugins/<plugin>/tests/
   ```

   Top-level `tests/` may run locally, but Ned's pre-push lane guard can reject it.

5. Run the focused verifier from the clean worktree, then push.
6. If `finalize_task.sh` transitions Linear but a later automation touch moves the issue back to `In Progress`, re-query Linear after PR creation and manually restore `In Review` with `issueUpdate` if needed. The Linear query is authoritative, not the finalize transcript.

## Evidence shape to post back

- Branch and PR URL.
- Commit list.
- Changed files.
- Focused verifier command and pass output.
- Remote branch verification via `git ls-remote --heads origin <branch>`.
- Note if lane guard required moving tests into `plugins/<plugin>/tests/`.

## Why this matters

This avoids three recurring failures in one pass:

- starting from a base branch that does not contain the plugin work area,
- losing pushability by placing tests outside Ned's lane,
- trusting `finalize_task.sh` output after Linear state drifted post-finalize.
