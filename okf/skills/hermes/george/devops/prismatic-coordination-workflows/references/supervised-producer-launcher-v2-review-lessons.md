# Supervised Producer Launcher V2 Review Lessons

Use this reference when coordinating or reviewing Prismatic supervised one-shot/producer launchers and admission gates.

## Durable lessons from GRO-4210 launcher review

- Treat stale async reviews as evidence, not noise. Re-bind each finding to the current exact artifact hash; if the behavior can still occur, it remains a blocker even when the reviewed hash is stale.
- Do not equate local targeted proof with authorization, admission, or production use. A repaired launcher remains blocked until an independent exact-hash review returns CLEAN_TO_USE for the current launcher and supervisor artifacts.
- A strict cap-one launcher needs more than a count of active rows. Count every uncertain active state, including `launching`, `spawning`, and `running`; fail closed/manual on ambiguous `spawning` crashes rather than reclaiming unsafely.
- Reclaim/retry paths need a persistent bounded attempt counter in the ledger. A retry cap held only in process memory or implied by external control is not durable enough for admission.
- Every retry/reclaim path needs an attempt fence/token. Delayed stale launch attempts must fail their state-transition compare-and-swap after a newer attempt has reclaimed the event.
- Bind state updates to the current attempt token, not just `event_id`/`launch_id`, so stale supervisors or delayed parent processes cannot write receipts or final states for superseded attempts.
- Child liveness must be checked with PID plus process start ticks, not PID alone, and it should be checked immediately before receipt issuance as well as when first observed.
- Protect local fixture/ledger parents with owner-only permissions (`0700`) if they gate a valid request. A correct script that cannot write its ledger is still unusable.
- Report boundaries explicitly: no event admission, producer launch, merge, deploy, Linear write, or cap increase unless those side effects actually occurred and were authorized.

## Review packet minimum

```text
ARTIFACT=<path>
ARTIFACT_SHA256=<sha256>
SUPERVISOR=<path>
SUPERVISOR_SHA256=<sha256>
REVIEW=<delegation_id or reviewer identity>
VERDICT=<CLEAN_TO_USE|REPAIR|BLOCKED>
SCOPE=exact-hash launcher/supervisor review
LOCAL_PROOF=<log path + sha256>
BOUNDARY=no admission/use unless CLEAN_TO_USE and explicitly authorized
```
