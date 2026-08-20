# Hermes guard: fresh verification after code edits

## Trigger

Hermes may inject a post-edit guard message when code was changed but no fresh verification evidence is detected for the current changed paths.

Typical shape:

```text
Verification status: unverified
Changed paths:
- /path/to/changed/file.py
...
No canonical test/lint/build command was detected. Create a focused temporary verification script under /tmp using an OS-safe tempfile path with a hermes-verify- filename prefix, run it against the changed behavior, clean it up when possible, and summarize it explicitly as ad-hoc verification rather than suite green.
```

## Correct response pattern

1. Do not argue with prior verification or claim an earlier check is enough.
2. Create a temporary verifier with an OS-safe tempfile path, e.g. `mktemp /tmp/hermes-verify-topic-XXXXXX.py`.
3. Verify the exact changed paths named by the guard plus behavior markers relevant to the edit.
4. Write detailed output to a log file under `/tmp`.
5. Delete the temp verifier when possible.
6. Report a compact proof block and explicitly label it `AD_HOC_OR_CANONICAL=ad-hoc targeted`.
7. Include `NOT_CLAIMING=not canonical suite green; not production deploy; ...` as appropriate.

## Example compact receipt

```text
COMMAND=python3 /tmp/hermes-verify-topic-abc123.py
RESULT=PASS
LOG=/tmp/topic-focused-verify.log
SCOPE=changed paths requested by guard: <paths/features>
AD_HOC_OR_CANONICAL=ad-hoc targeted
NOT_CLAIMING=not canonical suite green; not production deploy; not live browser/API verification
MARKER=<PROJECT_TOPIC_ADHOC_OK>
VERIFIER_CLEANUP=PASS
```

## What to verify

Prefer deterministic checks that prove the behavior changed, not just syntax:

- changed files exist and are parseable where applicable;
- route/function/class names introduced by the edit are present;
- safety/governance markers are present;
- old forbidden behavior is absent from the edited block;
- user-facing static pages include required copy, targets, and noindex/robots markers;
- docs mention the operational lifecycle and caveats.

## Pitfall

If you edited files and then gave a final answer, but Hermes says verification is unverified, treat the guard as authoritative for the current turn. Run the fresh focused verifier immediately before summarizing again.