# Guard-compatible `/tmp/hermes-verify-*` post-edit evidence

Use this when a Prismatic system verifier says changed paths are still unverified after edits and explicitly requests an OS-safe temporary verification script.

## Durable pattern

1. Allocate the verifier with Python `tempfile.mkstemp(prefix="hermes-verify-", suffix=".py" or `.sh`, dir="/tmp")`; do not hand-pick a fixed filename.
2. For behavior regressions, prefer a real pytest file and run it directly: `pytest -q /tmp/hermes-verify-*.py`. This is more detectable than running Python from inside a shell script.
3. Then run the project-focused checks literally in the foreground: focused `pytest`, generated-dashboard/build check, linter, formatter check, compile, and `git diff --check` as applicable.
4. Write noisy output to a `/tmp/hermes-verify-*` log and print a compact proof footer:
   - `RESULT=PASS`
   - `AD_HOC_OR_CANONICAL=ad-hoc_targeted`
   - `NOT_CLAIMING=canonical_full-suite_green_deployment_public_unblock`
   - unique `MARKER=...`
   - log SHA-256
5. Clean up the temporary script when possible; preserve the log.
6. If the guard still reports unverified after this successful run, classify the blocker as guard-state recognition rather than mutating candidate bytes or rebranding ad-hoc proof as canonical suite green.

## Boundary

This pattern supplies fresh ad-hoc post-edit evidence. It does not prove canonical full-suite green, deployment, public unblock, or independent acceptance review.
