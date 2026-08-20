# Run-record evidence surfacing — 2026-07-08

## Context

During the Prismatic Proof Loop work, the execution evidence schema and negative Done gate were not enough by themselves. The next durable gap was that `AgentRunRecord` and gateway `/runs` payloads could still show `status=completed` without showing whether the result was verified, partial, blocked, failed, or self-reported.

## Durable pattern

When implementing a verified execution contract, wire it into the surfaces operators actually read — not just docs or standalone schema files.

Minimum run-record fields to expose:

- `verification_status`
- `verification_scope`
- `failure_category`
- `cleanup_status`
- `done_gate_result`
- `done_gate_errors`
- `evidence`

A run may retain legacy lifecycle status, e.g. `status=completed`, but operator completion must come from the evidence gate:

```text
status=completed
verification_status=self_reported
verification_scope=not_run
done_gate_result=not_done
done_gate_errors=Done requires execution evidence
```

Only verified evidence should surface as:

```text
status=completed
verification_status=verified
done_gate_result=done
```

## Implementation notes

- Add evidence attachment to the run-record store mutation path, e.g. `update_run(..., evidence=...)` and/or `attach_evidence(...)`.
- Store summary fields directly on run records so reports/dashboards do not need to parse nested evidence blobs.
- Keep the raw evidence payload too for audit/replay.
- Ensure Markdown reports show verification status/scope/failure/cleanup/done gate.
- Ensure API serializers (`/runs`, `/runs/{run_id}`) include the same fields.
- If a completion endpoint exists, allow an evidence payload to be submitted with the status update.

## Verification recipe

Use a focused `/tmp/hermes-verify-*` wrapper around a repo smoke that creates two fixture records:

1. A completed run with no evidence.
   - Expected: `verification_status=self_reported`, `done_gate_result=not_done`.
2. A completed run with verified evidence.
   - Expected: `verification_status=verified`, `done_gate_result=done`.

The smoke should also prove:

- report text shows verification fields;
- API serializer/payload shows verification fields;
- the base execution-evidence contract regression still passes;
- `ruff check`, `ruff format --check`, and `py_compile` pass for touched files.

## Pitfalls found

- Python 3.10 does **not** provide `enum.StrEnum`; use a compatibility base `class X(str, Enum)` for package code that claims `requires-python >=3.10`.
- CI may catch a lower-Python import failure even if local Python 3.12/3.13 smokes pass. If CI fails, identify the exact layer, patch, rerun the focused verifier, then wait for CI before merging.
- Do not claim canonical/full-suite green from a focused smoke. Label it as ad hoc targeted verification unless the configured canonical suite/CI has also passed.
