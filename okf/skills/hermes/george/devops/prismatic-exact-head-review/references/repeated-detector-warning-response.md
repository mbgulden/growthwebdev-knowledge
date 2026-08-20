# Repeated Prismatic detector warnings

## Lesson

If the platform/user repeats a workspace detector warning after code, tests, or handoff edits, treat it as a fresh current-turn requirement. Do not classify the message as detector non-recognition and do not answer with only a prior log digest.

## Correct response pattern

1. Create a fresh OS-safe verifier path with:

```python
import tempfile
f = tempfile.NamedTemporaryFile(prefix="hermes-verify-", suffix=".py", dir="/tmp", delete=False)
```

2. Keep the verifier minimal and idempotent:
   - exact `HEAD` and tree assertions;
   - changed-path or handoff readback assertions;
   - one focused behavior probe for the changed behavior;
   - focused pytest for the touched module/test where feasible;
   - lint/format/compile/diff checks if the warning asks for build/lint evidence.

3. Remove the verifier file and assert it no longer exists.
4. Report as `AD_HOC_OR_CANONICAL=ad-hoc targeted`, not canonical suite green.
5. If rerun is impossible, name the concrete blocker instead of citing earlier proof as sufficient.

## Why

Michael values detector-shaped evidence over debate about whether the detector recognized a previous run. Re-running a minimal proof is cheaper and safer than leaving the workspace in an externally unverified state.
