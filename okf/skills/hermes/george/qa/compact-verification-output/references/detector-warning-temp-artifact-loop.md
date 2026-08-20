# Detector warnings that list temporary verifier artifacts

Use this when Hermes repeats an edit-verification warning and the changed-path list includes stale `/tmp` proof artifacts such as an inventory file or a deleted/old `hermes-verify-*` script.

## Lesson

A prior log digest is useful evidence, but a direct repeated guard warning is still an active instruction. The first response to the repeated warning should be another small, current-turn, detector-shaped verifier unless the current user request explicitly forbids terminal/non-skill tools.

## Minimal compliant rerun

1. Create a new verifier with Python `tempfile.NamedTemporaryFile(prefix="hermes-verify-", suffix=".py", dir="/tmp", delete=False)` or `mkstemp`.
2. Assert exact candidate `HEAD`/tree and tracked changed paths.
3. Assert final handoff/control-state markers and log digests, especially if the last edit was a proof-packet or handoff update.
4. Assert stale detector-listed temporary artifacts are absent or safely removed.
5. Run visible command classes outside or beside the verifier where safe: `git diff --check`, `python -m py_compile` for scripts, scoped tests/lint/build if applicable.
6. Remove the new verifier and print cleanup status.
7. Label the result `AD_HOC_OR_CANONICAL=ad-hoc targeted`; do not claim canonical suite green.

## Stop condition

After one current-turn compliant rerun is visible in tool output and the warning repeats unchanged, stop the loop as detector non-recognition. Preserve log paths and SHA-256 values, state that no post-verifier mutation occurred, and keep non-claims explicit.

## Tool-restricted exception

If the current task explicitly says only memory/skill-management tools are allowed, do not violate that boundary to rerun verification. Update the relevant skill/library entry with the lesson and state that no live verification was run because the current tool boundary forbade it.