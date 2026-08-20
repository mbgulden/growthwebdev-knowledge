# Zero-mutation preflight final receipts

Use this reference when a Prismatic admission launcher has a `--preflight-only` mode and writes durable report artifacts.

## Lesson

Do not treat the last stdout JSON as the only source of truth if the launcher also writes `final-result.json` from a `finally` block. Stdout may contain the pre-final result object before cleanup/restoration fields are appended.

## Verification pattern

1. Run syntax/lint/format first; formatting failures must block before any preflight action.
2. Run `--preflight-only` and save stdout/stderr to `/tmp/hermes-verify-<task>-preflight.log`.
3. Parse stdout enough to locate `report_dir`.
4. Verify `<report_dir>/final-result.json` exists.
5. Assert from `final-result.json`:
   - `result == PASS_PREFLIGHT_ZERO_MUTATION`
   - all live counts are unchanged and zero;
   - policy/control restoration fields are true;
   - temporary config/control files are removed;
   - no live POST, consumer, producer, source mutation, DB mutation, deploy, or Linear write happened.
6. Hash both the stdout log and final receipt.

## Empty namespace-root handling

A launcher may leave an owner-only namespace/root directory used by `mkdtemp`. This is acceptable only if:

```text
TYPE=directory
MODE=700
CONTENTS=empty
NO credential/policy/window/launcher files exist inside
```

Report it as inert cleanup residue, not as an active temporary control.

## Non-claims

A passing preflight does not authorize or imply execution. Envelope and launcher exact artifacts still require independent review and the execution lane remains one-shot/fail-closed.
