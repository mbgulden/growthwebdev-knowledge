# Final packet/handoff edit re-verification

## Trigger

A post-edit detector still reports `unverified` after an apparently successful verifier, and the changed paths include both code and a packet/evidence file such as `PRISMATIC_CURRENT_HANDOFF.md`.

## Lesson

The detector is right if any handoff/evidence packet was edited after the verifier ran. Treat packet/handoff mutations as first-class changed artifacts, not commentary. A previous code-focused verifier no longer proves the final workspace state.

## Guard-compatible response

1. Do not argue from the earlier receipt.
2. Create a fresh OS-safe temp verifier with `tempfile.mkstemp(prefix="hermes-verify-", dir="/tmp")`.
3. Bind both classes of artifacts:
   - source/test behavior assertions for the changed code;
   - explicit handoff/evidence markers or packet SHA/hash assertions for the final packet bytes.
4. Run direct focused project commands where possible (`ruff check`, `ruff format --check`, focused `pytest`).
5. Remove the temporary executable/probe when possible, but preserve the durable `/tmp/hermes-verify-*` result log and report its SHA-256.
6. Report `AD_HOC_OR_CANONICAL=ad-hoc targeted`; do not claim canonical suite green unless the canonical suite passed.

## Example proof packet

```text
TEMPFILE=/tmp/hermes-verify-<random>.py
TEMPFILE_CREATION=tempfile.mkstemp
SOURCE_BEHAVIOR_ASSERTIONS=PASS
HANDOFF_FINAL_MARKER=PASS
RUFF_CHECK=PASS
RUFF_FORMAT=PASS
FOCUSED_TESTS=<N> passed
TEMP_SCRIPT_REMOVED=true
LOG=/tmp/hermes-verify-<topic>-result.log
LOG_SHA256=<sha256>
AD_HOC_OR_CANONICAL=ad-hoc targeted
NOT_CLAIMING=canonical full-suite green
```

## Pitfall

If you patch the handoff to record the verifier receipt, that patch itself can retrigger the detector. Either include a final marker assertion in a second verifier after the handoff edit, or delay the handoff receipt patch until after the user-facing proof only when the workflow allows it.
