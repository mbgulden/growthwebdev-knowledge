# Cron repeated ad-hoc verification with RESULT artifact

## When to use

Use this pattern when Hermes posts one or more verification-only nudges **after** a cron task was already finalized and the detector still says no canonical verification was seen.

Typical signs:
- changed paths include both code/docs and `/tmp/issue-batches/<ISSUE>_RESULT.md`
- the prior reply already mentioned focused pytest/build output
- the platform still wants a fresh `/tmp/hermes-verify-*` proof

## Working pattern

1. **Do not resume implementation.** Treat the nudge as verification-only scope.
2. **Rerun the focused canonical command directly** from the edited worktree, not from memory.
   - Example from GRO-4163:
     - `python3 -m pytest prismatic/shipped_plugins/pwp/tests/test_theme_validator.py prismatic/shipped_plugins/pwp/tests/test_compiler_determinism.py prismatic/shipped_plugins/pwp/tests/test_theme_diff.py prismatic/shipped_plugins/pwp/tests/test_oauth_credentials.py prismatic/shipped_plugins/pwp/tests/test_theme_task_generation.py tests/test_pwp_integration.py -q --tb=short`
3. **Create a fresh `/tmp/hermes-verify-*` script** with an OS-safe tempfile path.
4. Have the verifier assert **both behavior and evidence artifacts**:
   - changed runtime behavior still works
   - doc/example imports point at the rewritten namespace
   - `RESULT.md` exists and contains the expected issue/PR evidence
5. **Delete the verifier** and report cleanup status explicitly.
6. Phrase the reply as **ad-hoc verification of the changed behavior**, not full-suite green.

## Concrete GRO-4163 checks

The verifier was useful only after it checked all of these together:
- `validate_theme_package(...)` passes on the canonical fixture
- `diff_theme_packages(...)` resolves under the rewritten import path
- `PWPDesignTokenPlugin.register_tools()` still exposes the expected tool names
- docs mention `prismatic.shipped_plugins.pwp...` / `prismatic/shipped_plugins/pwp/...`
- `tests/test_pwp_integration.py` references the shipped-plugin manifest path
- `/tmp/issue-batches/GRO-4163_RESULT.md` exists and mentions PR #376
- the focused pytest command passes again

## Why this matters

A prior successful verifier run may still not satisfy Hermes if it did not also prove the artifact paths the detector is tracking. When `RESULT.md` is one of the changed paths, include it in the fresh verifier contract instead of only rerunning tests.
