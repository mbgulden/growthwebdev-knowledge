# Runtime completed-work integration review repair patterns

Session-derived addendum for `AGY_COMPLETED_WORK_INTEGRATION_GATE_OK` / RUNTIME-CONVERGENCE-4 style slices.

## Trigger

Use when a producer or takeover candidate wires completed-work persistence into supervisor/worker/scheduler/circuit flows and an independent review returns `REPAIR`, especially around early exits or completion side effects.

## Review traps found

1. **Stale prior-result reuse**
   - Long worker loops can accidentally reuse a prior iteration's `result` via `locals().get("result")` or a variable that is not reset before every early exit.
   - A later quota/sandbox/error path can then inherit `completion_eligible=True` from an earlier task.
   - Required fix: reset per-task state before all early exits and have final disposition read only the current iteration's result.

2. **Sandbox-failure completion bypass**
   - Sandbox setup failure is an infrastructure/runtime failure, not completed work.
   - It must not publish `agent.completed`, mark scheduler completion, increment success/circuit reset, or make the task non-requeueable.
   - Required fix: keep `allow_requeue=True`, preserve failure evidence, and avoid `mark_completed`/completion-visible side effects.

3. **Circuit-success reset bypass**
   - Circuit breaker success/reset must be gated by exact final completion eligibility, not merely absence of thrown exception or existence of a result dict.
   - Required fix: require `result.get("completion_eligible") is True` (or equivalent exact authoritative final gate) before success/reset.

## Regression checklist

- A previous successful task followed by quota/blocked early exit cannot publish completion or reuse prior success.
- Sandbox setup failure remains requeueable and does not call scheduler completion or any completed-work publication path.
- Circuit failure counters are reset only when final completion eligibility is true.
- Ledger persistence failure keeps completion false and records diagnostic evidence without leaking raw exception/secrets.
- Worker payloads preserve completed-work markers/classification/evidence for reviewers but do not convert rejected rows into completion authority.

## Proof packet shape

```text
COMMAND=<focused worker/control-plane regressions plus exact-head ad-hoc verifier>
RESULT=<PASS|FAIL|BLOCKED>
LOG=<path>
SCOPE=completed-work ledger ordering, early exits, scheduler completion, circuit accounting
AD_HOC_OR_CANONICAL=<ad-hoc targeted|canonical suite>
NOT_CLAIMING=recovery/replay ordering, external writeback transactionality, live supervisor switch, deploy/restart
MARKER=AGY_COMPLETED_WORK_INTEGRATION_GATE_OK or task-specific repair marker
```

## Boundary

These repairs prove completed-work persistence gates completion-side effects for the reviewed code path. They do **not** prove recovery/replay ordering, exactly-once external writeback, live runtime parity, or authorization to deploy/restart unless separately verified.
