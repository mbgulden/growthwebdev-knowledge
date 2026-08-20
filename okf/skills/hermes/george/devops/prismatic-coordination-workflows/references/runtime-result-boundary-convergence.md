# Runtime Result-Boundary Convergence

Use this reference when continuing Prismatic runtime convergence after the filesystem-scoped supervisor transport slice has merged and the next question is how to make raw AGY output and result packets durable without switching live runtime paths.

## Trigger

- A prior runtime-convergence source slice has merged and immutable release proof exists.
- The live supervisor/runtime topology is still split, dirty, or profile-script based.
- The next suspected gap is around `agy_result_packet`, `agent_raw_output_queue`, completion publication, or durable raw-output capture.

## Guardrails

1. **Start read-only.** Map current immutable APIs, call order, validation behavior, and writeback points before admitting a producer.
2. **Do not infer live parity from source merge.** A merged source result-boundary API is not a live supervisor switch, restart, deployment, or consumer-runtime proof.
3. **Keep the slice small.** If raw-output capture and result-packet validation touch more than four source paths or have separate failure domains, split them.
4. **Treat producer evidence as untrusted.** Reproduce actual API behavior, result packet validation, queue persistence, and fail-closed negative cases before commit/PR.
5. **Preserve exact artifact lineage.** Bind base SHA, task file SHA-256, candidate head/tree, PR head, CI, independent review, merge SHA, release path, and log digests.
6. **Do not mutate live state.** No live supervisor switch, systemd unit edit, cursor/state DB mutation, Linear writeback, generic dispatch, deploy, restart, or dirty checkout reset without explicit authorization.

## Read-only analysis checklist

- Locate imports and callers for `prismatic.agy_result_packet` and `prismatic.agent_raw_output_queue`.
- Identify the canonical point where child stdout/stderr/raw output becomes durable evidence.
- Identify the canonical point where a normalized result packet becomes completion-eligible.
- Verify existing validators reject malformed packets fail-closed without publishing `agent.completed`.
- Determine ordering: raw capture first, packet validation second, completion publication last.
- Determine whether retries/relaunches can overwrite, append, or duplicate raw output and result packets.
- Determine whether evidence paths include secrets or sandbox-local mutable paths that should be redacted/classified.

## Producer contract shape

- `BASE_SHA=<fresh current main after predecessor closeout>`.
- `ALLOWED_PATHS<=4` and exact list in `AGY_TASK.md`.
- `NO_DEPLOYMENT`, `NO_RESTART`, `NO_LINEAR_WRITE`, `NO_GENERIC_DISPATCH`, `NO_LIVE_SUPERVISOR_SWITCH`.
- Make the required order explicit in the task, tests, and report:
  `process exit -> RESULT.md semantic assessment -> resolve attempt -> durable raw queue write -> strict canonical packet validation -> active-issue identity binding -> completion eligibility decision -> completed/rejected publication and side effects`.
- Require completion eligibility to gate every promotable side effect on all of:
  `semantic RESULT.md success`, `durable raw capture with exact nonempty raw_output_id`, `canonical_valid`, and `packet issue_identifier == active issue`.
- Treat a queue result with `raw_output_id=None`, an empty string, or a non-string placeholder as capture failure, even if the persist call returned an object or a truthy status. Completion evidence must be durably addressable, not just allegedly written.
- Do **not** require the raw-output queue normalizer to classify a strict raw AGY packet as `accepted` unless its schema is deliberately unified with the completed-work dialect. `agy_result_packet` raw packets and `agent_packet_normalizer` completed-work records can be valid in different dialects; requiring both to accept the same raw sidecar can make canonical success unreachable. Persist raw output first, use strict raw-packet validation plus active-issue/source binding for completion authority, and report queue-normalizer rejection as evidence/classification rather than completion veto when the schemas intentionally differ. Preserve normalizer fields such as `normalization_status`, `canonical_packet_id`, `rejection_reason`, and `repair_hint` in boundary/worker payloads so reviewers can see why evidence is held without scraping logs.
- Treat legacy Markdown/RESULT text as visible evidence only: durably capture it as `legacy_unvalidated`, but do not let it complete, promote, label, or launch quality gates.
- Prefer a dedicated state path for the result-boundary queue (not relative to immutable release code), and prove importing the supervisor does not create or mutate that DB.
- Use no-follow, bounded sidecar reads; protect/clean stale sidecars and repair seeds without reading secret contents or following sandbox-local symlinks. Stale canonical sidecars (`RESULT.md` / `AGY_RESULT_PACKET.json`) must be removed before launch or fail closed before launching AGY; logging and continuing after cleanup failure can let stale evidence satisfy the new boundary.
- Bind raw output to attempt/source identity and verify retry/relaunch idempotency before side effects.
- Require tests for:
  - successful raw-output persistence before validation;
  - fail-closed rejection when queue persistence returns no exact nonempty `raw_output_id`;
  - propagation of queue normalization/rejection/repair evidence into boundary and worker payloads;
  - malformed result packet rejection after raw persistence;
  - missing raw-output / missing packet boundary;
  - relaunch/retry ordering or idempotency;
  - active-issue mismatch hold/reject behavior;
  - no completion publication from invalid, missing, legacy-only, or mismatched evidence.

## Proof packet

```text
TASK=RUNTIME-CONVERGENCE-<N>
BASE_SHA=<sha>
TASK_SHA256=<sha256>
CANDIDATE_HEAD=<sha>
PR=<number/url>
INDEPENDENT_REVIEW=<CLEAN|REPAIR|BLOCKED>
GITHUB_CI=<status>
MERGE_SHA=<sha or none>
RELEASE=<path or none>
RAW_OUTPUT_PROOF=<log + sha256>
RESULT_PACKET_PROOF=<log + sha256>
CANONICAL=<count/log/sha256>
BOUNDARY=no live switch/deploy/restart/state mutation
NEXT=<next exact slice>
```

## Overclaim traps

- A raw-output queue unit test is not proof that the live AGY supervisor writes raw output.
- A valid result packet fixture is not proof that invalid packets cannot publish completion.
- A strict raw AGY packet failing completed-work queue normalization is not automatically a product defect; first determine whether raw AGY and normalized completed-work are intentionally separate dialects. If so, the defect is requiring `accepted` queue-normalizer status for completion instead of strict raw-packet validation plus identity binding.
- GitHub CI green is not independent exact-head review.
- Immutable release proof is not production overlay or runtime parity.
- `current main` being cleaner than the live profile script is not authorization to repoint live services.
- A queue/store mock that returns an object or truthy status but no exact nonempty durable `raw_output_id` is not evidence of durable capture. Completion from such a result is a false-positive path.
- If queue normalization rejects a raw packet, do not hide the rejection. The boundary payload should retain normalization status, canonical packet id when present, rejection reason, and repair hint so review can distinguish schema-dialect classification from product failure.
- Stale sidecar deletion must fail closed before launch; a warning-only cleanup path can allow stale `AGY_RESULT_PACKET.json` to produce a false canonical success.
