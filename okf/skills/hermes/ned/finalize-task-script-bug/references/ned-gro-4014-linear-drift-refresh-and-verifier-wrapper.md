# GRO-4014 redispatch: Linear drift + verifier-wrapper pitfall

Use this when a cron redispatch finds a task with prior branch/PR/RESULT evidence but Linear has drifted out of `In Review`.

## Signals

- `/tmp/issue-batches/<ISSUE>_RESULT.md` says the issue was finalized and has a branch/PR.
- Remote branch exists and the task worktree is clean.
- Linear re-query shows `In Progress` or another non-review state despite a prior finalize comment.
- PR may still have a known external check failure while local/build verification passes.

## Safe refresh sequence

1. Re-read the skeleton and the issue comments; do not trust the stale RESULT alone.
2. Use the clean task worktree or a detached temp worktree for the existing `ned/<issue>` branch; avoid dirty shared checkouts.
3. Run fresh focused verification before finalizing again. For model/spec tasks, assert the durable contract directly (counts, names, forbidden fields, generated output), not just that a command exits 0.
4. Update `/tmp/issue-batches/<ISSUE>_RESULT.md` with the fresh verifier output, PR check state, and known external blockers.
5. Re-run finalize with absolute paths, for example:

   ```bash
   PRISMATIC_REPO_ROOT=/tmp/hd-platform-GRO-4014 \
   FINALIZE_LOCK_FILES='scripts/live_your_design_progression.py docs/vision/daily-live-your-design-progression.md' \
   bash /home/ubuntu/.hermes/profiles/ned/scripts/finalize_task.sh GRO-4014 ned/GRO-4014 ned
   ```

6. Post-finalize, re-query Linear state/comments, swarm locks, remote branch, and PR checks. The script exiting 0 is not enough.
7. If state is restored and no new human blocker exists, cron final output should be `[SILENT]`.

## Verifier wrapper pitfall

Hermes terminal foreground guard can reject a shell heredoc when the embedded Python contains a literal shell-looking background operator pattern such as set intersection with `&` (example: `forbidden & props`). Do not fight the guard or weaken the verifier. Write the verifier script to `/tmp/hermes-verify-<issue>.py` with `write_file`, run `python3 /tmp/hermes-verify-<issue>.py`, then remove it and print cleanup evidence. This preserves fresh ad-hoc verifier evidence without tripping shell parsing heuristics.

## GRO-4014 concrete evidence shape

Fresh verifier asserted:

- version `2026-07-19.gro-4014`
- 6 `hde_` events
- 5 content surfaces
- no forbidden instrumentation properties: `birth_time`, `birth_date`, `journal_text`, `api_key`, `secret`
- markdown output includes `hde_daily_briefing_viewed`, `hde_outcome_signal_recorded`, and `Dashboard metrics`
- temp verifier cleanup completed

PR check interpretation:

- Cloudflare Pages success + local `npm run build` success supported the branch.
- `Workers Builds: hd-platform` remained failed as an external Cloudflare Workers check; record it, but do not call the local work green as live/proof green when acceptance says status is not green until live/proof checks pass.
