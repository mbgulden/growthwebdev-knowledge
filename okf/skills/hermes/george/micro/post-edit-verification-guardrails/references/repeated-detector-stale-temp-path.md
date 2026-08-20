# Repeated detector warnings with stale temp paths

## Trigger

A post-edit guard repeats the same warning after a compliant `/tmp/hermes-verify-*` proof already passed, sometimes listing a stale temporary path from an earlier failed or generated helper.

## Durable lesson

Treat the first repeated warning as a fresh current-turn verification requirement. Create a new OS-safe tempfile verifier with `tempfile.mkstemp`/`NamedTemporaryFile`, run it with `pytest`, run the changed project commands directly, clean the temp verifier, and explicitly check that any stale listed temp path is gone when possible.

If the guard repeats again after a visible compliant rerun, perform **one final literal-command rerun** only when the current request permits verification tools. That rerun should make the detector-visible commands impossible to miss: top-level `pytest`, top-level focused project `pytest`, top-level `ruff check`, top-level `ruff format --check`, and `git diff --check`/clean status. Use `tee` or a grouped shell transcript so retained logs have hashes, then clean only the disposable verifier script. If the same detector warning repeats after that, report a detector-ingestion blocker with exact log/hash and boundary rather than entering an infinite verification loop.

Do not save transient launcher/package failures as durable negative rules. If a command resolves to the wrong launcher/interpreter, capture the **fix pattern**: bind the intended project environment before invoking the literal command and print `command -v pytest` or equivalent in the proof log so the receipt shows which tool actually ran.

Do not claim canonical suite green from the ad-hoc rerun.

## Minimal packet fields

```text
TEMPFILE_CREATED_WITH=tempfile.mkstemp
TEMPFILE_PREFIX=hermes-verify-
TEMPFILE_PYTEST=<N> passed
PROJECT_FOCUSED=<N> passed
BUILD_LINT_FORMAT_COMPILE_DIFF=PASS
EXACT_HEAD=<sha>
TOOL_BINDING=command -v pytest -> <project-env-path>
TEMP_SCRIPT_CLEANED=true
STALE_TEMP_PATH_ABSENT=true
AD_HOC_OR_CANONICAL=ad-hoc targeted
NOT_CLAIMING=canonical full-suite green
LOG=/tmp/hermes-verify-<topic>.log
LOG_SHA256=<sha256>
MARKER=<stable_marker>
```

## Pitfalls

- Do not answer the first repeated warning only by citing an immediately prior proof; run a fresh idempotent proof unless the current user request explicitly forbids non-skill tools.
- Do not loop forever on repeated detector warnings. After a current-turn compliant rerun and one final literal-command rerun, classify further repeats as detector ingestion stale/blocker.
- Keep durable logs, but remove disposable verifier scripts where possible.
- If a current task restricts tools to skill/memory updates, honor that restriction and preserve the lesson in the skill library rather than attempting live verification.
