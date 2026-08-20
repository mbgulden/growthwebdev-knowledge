# One-shot admission launcher hardening

Use when deriving a task-specific Prismatic admission launcher from a previously accepted launcher.

## Trigger

- A reviewed contract is ready for task materialization/admission-envelope review.
- A one-shot launcher is copied or mechanically derived from a prior task launcher.
- The launcher can POST to the deployed gateway, temporarily open policy/control windows, invoke the ordinary consumer, or start a cap-1 producer.

## Required hardening before envelope freeze

1. **Default invocation must not execute.** Bare invocation exits non-zero with a clear usage/error message. Execution requires an explicit `--execute`; zero-mutation validation requires `--preflight-only`.
2. **No bearer on redirects.** Use an explicit no-redirect opener/handler so HTTP 3xx is rejected before a follow-up request can be constructed with an Authorization header. Test or statically verify this path separately from ordinary POST success.
3. **Task-specific literals must be asserted, not trusted.** After derivation, assert exact values for task id, private launcher path, bus/worktree task paths, task hash, producer identity, worktree path, base/head/tree, and release binding. Retained previous-task literals are launcher defects.
4. **Count external authority sites.** Verify exactly one token-generation site, one POST site, one ordinary consumer invocation, one cap-1 producer path, and no shell wrappers/aliases/alternate entrypoints.
5. **Treat final receipts as source of truth.** If stdout lacks restoration fields, inspect the durable `final-result.json` written from `finally` before declaring preflight failed or clean.
6. **Freeze only after local adversarial proof.** Compile/lint/format, prove bare-invocation refusal, run preflight, prove restoration and zero live state, hash the launcher/envelope/report, then dispatch independent full and adversarial reviews. Do not run `--execute` during this stage.

## Minimal proof block

```text
COMMAND=<compile/lint + bare invocation + --preflight-only + offline authority-site verifier>
RESULT=PASS
LOG=/tmp/hermes-verify-<task>-launcher-v<N>-result.log
SCOPE=bare fail-closed; no redirects with bearer; exact bindings; one POST/token/consumer/cap1; finally restoration; zero live state
AD_HOC_OR_CANONICAL=ad-hoc targeted launcher admission proof
NOT_CLAIMING=event posted, producer started, implementation, candidate, PR, merge, deployment, or Linear write
MARKER=<TASK>_ONE_SHOT_LAUNCHER_HARDENED_REVIEW_PENDING
```

## Pitfalls

- A derived launcher can pass syntax and still point at the previous task's private launcher path or producer identity. Make task-specific binding assertions part of preflight.
- A preflight wrapper may see stdout before `finally` appends cleanup/restoration truth. Read the durable receipt before rerunning or reporting failure.
- A successful local preflight does not substitute for exact-byte review of both the envelope and launcher.
