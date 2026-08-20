# GRO-3739 finalize-state and lane-push pitfalls

Session pattern: a PWP plugin-lane task was implemented in a clean worktree and finalized, then push revealed out-of-lane files. The task was corrected and pushed, but `finalize_task.sh` had already posted a generic evidence comment and printed a Linear transition that did not actually persist.

Reusable lessons:

1. **Push/lane verification before final state trust**
   - `finalize_task.sh` can run before push, but the pre-push hook is the real lane-enforcement proof.
   - If pre-push rejects files outside Ned lanes (for example top-level `tests/` or `templates/linear/`), move the verifier/test into an owned plugin lane (`plugins/<plugin>/tests/`) or remove the out-of-lane doc edit before claiming completion.
   - After amending to fix lane scope, rerun focused verification and push again.

2. **Do not trust finalize transcript alone**
   - The script may print `Linear transition: ISSUE → In Review` and `Linear comment: ok` while a follow-up query still shows the issue in `In Progress`.
   - This is not a blocker if GraphQL access works: manually re-run `issueUpdate` to the intended state, post an evidence-refresh comment with the real commit/PR/verifier output, then re-query state.
   - Treat the follow-up Linear query as authoritative, not the shell transcript.

3. **Evidence comments must match the final commit**
   - If a branch is amended after finalize (for example to remove out-of-lane files), the original finalize comment may be stale.
   - Post a refresh comment with final commit, PR URL, changed in-lane files, verifier command output, and any manual state correction.

4. **Repeated verifier detector prompts are fresh-evidence contracts**
   - If the system says `Verification status: unverified`, create a new `/tmp/hermes-verify-*` script with `tempfile.mkstemp`, assert the changed behavior directly, run it, print path/exit/stdout/cleanup, and delete it.
   - Do not argue from prior pytest output or prior ad-hoc verifier paths.
