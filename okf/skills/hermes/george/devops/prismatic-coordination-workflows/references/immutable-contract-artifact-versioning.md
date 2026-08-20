# Immutable contract artifact versioning

Use this when drafting Prismatic precontracts, blocker packets, launch packets, or review prompts that are frozen to exact bytes and dispatched for independent review.

## Rule

Once an artifact has been frozen by exact path/hash and dispatched to a reviewer, treat those bytes as immutable. If a local verifier, reviewer, or self-review finds a defect after dispatch, do **not** edit the frozen artifact in place.

Create the next version instead:

1. Preserve the prior artifact byte-for-byte.
2. Freeze the correction under a new versioned filename/title (`V7`, `V8`, etc.).
3. State the delta from the prior version in the new artifact.
4. Re-run local exact-byte verification on the new file.
5. Dispatch fresh independent review against the new exact path/hash.
6. Mark the prior version as superseded/blocked in handoff, but keep it available for audit history.

## Verification pattern

```text
OLD_PATH=<path>
OLD_SHA256_BEFORE=<sha256>
OLD_SHA256_AFTER=<same sha256>
NEW_PATH=<path>
NEW_SHA256=<sha256>
DELTA=<one-line reason>
LOCAL_VERIFY=<PASS|FAIL>
REVIEW=<new handle pending|CLEAN|BLOCKED>
NOT_CLAIMING=prior review applies to new bytes
```

## Pitfalls

- A patch tool success message is not enough after a warning or argument corruption; read back and hash both old and new artifacts.
- Do not let stale reviews follow the artifact name. Reviews are bound to exact bytes, not to “latest V7” prose.
- Do not update handoff as if implementation is unblocked just because the new artifact passes local proof; wait for exact-byte independent review.
- If the new version fixes source/provenance evidence, explicitly quarantine older source artifacts and prevent later sessions from citing them as valid evidence.
