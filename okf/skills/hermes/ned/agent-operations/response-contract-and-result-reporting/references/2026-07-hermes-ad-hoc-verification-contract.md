# Hermes ad-hoc verification contract — July 2026

## Trigger

Hermes may append a system correction after code edits when no canonical test/lint/build command was detected. Treat it as a workflow correction, not noise.

Example signal:

> You edited code in this turn, but the workspace does not have fresh passing verification evidence yet. No canonical test/lint/build command was detected. Create a focused temporary verification script under `/tmp` using an OS-safe `tempfile` path with a `hermes-verify-` filename prefix, run it against the changed behavior, clean it up when possible, and summarize it explicitly as ad-hoc verification rather than suite green.

## Required response pattern

1. Create a temporary script under `/tmp` with Python `tempfile.NamedTemporaryFile(prefix="hermes-verify-", suffix=".sh", dir="/tmp", delete=False, mode="w")` or equivalent OS-safe tempfile API.
2. Put the focused verification commands in that script. Exercise the changed behavior, not just file existence.
3. Run the script.
4. Remove the script when possible: `rm -f "$verify_script"`.
5. Report results as **focused ad-hoc verification**. Do not claim the full canonical suite is green unless the canonical suite actually ran.

## Good final evidence shape

```text
verify_script=/tmp/hermes-verify-xxxx.sh
pytest=3 passed
ad_hoc_verification=pass
checks=8
routes=9
dispatch_ready_any=false
verify_script_removed=yes
git_status_lines=0
```

## Pitfall

If the first ad-hoc verification passes but Hermes repeats the correction, rerun the tempfile verifier and restate the ad-hoc scope. Do not argue with the correction or claim prior evidence is enough; create fresh evidence in the required shape.
