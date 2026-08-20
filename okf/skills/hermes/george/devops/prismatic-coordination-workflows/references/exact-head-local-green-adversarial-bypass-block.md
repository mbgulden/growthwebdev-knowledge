# Exact-head local-green candidate blocked by adversarial decision-path bypass

## When to use

Use this pattern when an AGY/Fred/Ned candidate passes its contracted local suite but review or a targeted semantic probe shows the production decision path still admits an unverified shape.

## Session lesson

A CRON export repair candidate completed cleanly and passed immutable exact-head local reproduction:

```text
focused tests passed
bounded regression passed
ruff/format/compile passed
cron/spool/timer invariance passed
```

However, a targeted archive probe inspected the actual classifier path, not only the helper tests, and found a production-admissible bypass:

```text
INPUT=full-commit hook path, no release digest, no config digest, no binding record
HOOK_EXISTS=true
RESULT=(True, "admissible")
```

The candidate was therefore preserved as a blocked checkpoint, even though local reproduction was green.

## Reusable workflow

1. Bind the completed producer to exact candidate commit/tree and clean tracked status.
2. Run the full immutable archive reproduction from the beginning.
3. If custom semantic assertions fail, classify the failure:
   - **verifier setup failure** when the assertion guessed symbol names, schema keys, paths, or shell quoting;
   - **candidate/product failure** only when observed behavior violates the contract.
4. Correct verifier setup by inspecting the real source identifiers or schema, then rerun the whole sequence rather than only the failed assertion.
5. Add at least one adversarial decision-path probe that exercises the production classifier/adapter directly, not just helper functions.
6. For fail-closed contracts, explicitly test missing-field/missing-binding cases with otherwise-valid surrounding shape. Example: existing hook + no digest flags + no binding record.
7. If the adversarial probe admits the candidate, freeze a review packet with:
   - exact candidate commit/tree;
   - local reproduction log/SHA;
   - bypass input and result;
   - bounded non-claims;
   - independent review request.
8. Update the handoff to `LOCAL_BLOCKED_REVIEW_PENDING` or equivalent. Do not launch a successor repair without separate authorization.
9. When the successor repair returns, prove the bypass is actually closed with a direct production-path probe from an immutable archive, not only with the producer's new tests. For the missing-binding class, mock the hook as existing and require a fail-closed result such as `(False, "missing_release_digest")`; also assert evidence gates and strict `is_verified_pair is True` checks precede hook existence.

## Verifier construction pitfall

Nested shell heredocs are brittle in long exact-head closeouts. If quoting breaks or command wrappers become unreadable, switch to a disposable Python orchestrator that:

- runs literal subprocess commands;
- writes noisy output to a log;
- snapshots and compares mutable system state before/after;
- removes the archive in `finally`;
- prints a compact proof packet and log digest.

This is a verifier setup repair, not a candidate repair. Keep the failed verifier attempts visible enough to explain why the full rerun was repeated.

## Reporting shape

```text
RESULT=BLOCKED
LOCAL_REPRODUCTION=PASS
ADVERSARIAL_REVIEW=BLOCKED
BYPASS=<minimal input and observed admissible result>
LOG=<local reproduction log>
BYPASS_LOG=<targeted probe log>
INDEPENDENT_REVIEW=<delegation/status>
AD_HOC_OR_CANONICAL=<exact class>
NOT_CLAIMING=acceptance, PR, merge, deploy, cron/timer mutation, canonical full-suite green
MARKER=<blocked-review-pending marker>
```
