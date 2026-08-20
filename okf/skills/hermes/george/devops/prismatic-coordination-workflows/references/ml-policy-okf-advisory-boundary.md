# ML Policy OKF Advisory Boundary

## Trigger

Use when Michael asks whether Prismatic should add machine learning, asks to distill ML/AI strategy thoughts into an OKF, or wants a future-facing governance artifact about probabilistic/advisory systems.

## Session-derived pattern

A useful ML OKF for Prismatic should not just answer “yes/no.” It should turn the idea into an authority-bound policy with explicit adoption gates.

Core policy phrase:

> ML may decide where to look. Deterministic gates decide what is true and what may happen.

## Required sections for a durable ML/AI OKF

- Frontmatter with `document_type: OKF`, status, owner, UTC timestamp, review trigger, and a stable marker.
- Executive decision: current LLM/coding-agent help is allowed, but probabilistic ML is excluded from control/verification/authorization/merge/deploy paths until deterministic foundations and telemetry are ready.
- Objective: advisory ML for attention/retrieval/classification/planning only.
- Key results:
  - deterministic authority boundary;
  - approved advisory use cases and maximum authority;
  - current LLM/tooling improvements before custom model training;
  - telemetry schema requirements bound to exact artifacts and downstream evidence;
  - staged adoption gates: deterministic foundation -> offline research -> shadow mode -> advisory mode -> bounded low-risk automation only by separate authorization.
- Evaluation/promotion criteria requiring deterministic baseline, shadow evidence, model/version/input/output provenance, fail-safe unavailability, drift/rollback, and independent review of authority boundaries.
- Explicit anti-goals: ML must not decide exact candidate pass, reviewed commit identity, evidence freshness, completed-work durability, lease/cursor validity, PR merge, deploy/restart, or external side-effect permission.
- Near-term implementation priorities and a future-review checklist.
- Decision record block plus boundary/non-claims.

## Verification pattern

Even for docs/OKF artifacts, create a focused temp verifier when the artifact is intended as durable source-of-truth material:

```text
/tmp/hermes-verify-<topic>.py
```

Verify at minimum:

- required headings/markers exist;
- the original raw chat text/noise is not pasted through unprocessed;
- decision record contains the stable marker;
- authority-boundary language appears;
- line/byte count is plausible for a rich OKF;
- compute SHA-256 of the final artifact;
- delete the temp verifier afterward when possible.

Report proof as ad-hoc focused docs verification, not canonical suite green.

## Non-claims

Creating the OKF does not implement telemetry, train/deploy a model, make runtime paths compliant, authorize merge/deploy/restart, or prove production readiness.
