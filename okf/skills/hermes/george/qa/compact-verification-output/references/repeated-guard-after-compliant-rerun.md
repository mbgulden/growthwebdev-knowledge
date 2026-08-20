# Repeated Hermes Verification Guard After Fresh Same-Turn Compliance

Use this when Hermes or the platform repeats a post-edit warning such as `No canonical test/lint/build command was detected` after the agent already ran a compliant `/tmp/hermes-verify-*` verifier.

## Pattern

1. Treat the first repeated warning as a real request, not noise.
2. Create the verifier under `/tmp` with Python `tempfile` or `mkstemp` and a `hermes-verify-` prefix.
3. In the same visible terminal command, run command classes the detector asked for when safe:
   - `python -m py_compile`
   - focused `python -m pytest ...`
   - scoped `ruff check`
   - scoped `ruff format --check`
   - project build/check command
   - security/readback/diff checks
4. Put behavior/readback assertions for the exact changed paths inside the temporary verifier.
5. Remove the verifier before final response when possible.
6. Print a compact proof packet with log path, SHA256, cleanup status, and `AD_HOC_OR_CANONICAL=ad-hoc targeted`.
7. If the same warning repeats again after the current-turn compliant verifier is visible, stop the loop: cite the fresh log hash and label it detector non-recognition. Do not rerun identical checks indefinitely.

## Boundary language

Use wording like:

```text
This is ad-hoc targeted verification, not a canonical-suite claim. The repeated warning appears to be verification-detector nonrecognition after a fresh same-turn compliant rerun.
```

Do not claim suite green, merge readiness, deployment, or runtime proof unless those were separately verified.
