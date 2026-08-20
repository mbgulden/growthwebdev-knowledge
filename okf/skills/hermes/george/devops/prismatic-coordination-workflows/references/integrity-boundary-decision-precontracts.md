# Integrity-boundary decision precontracts

Use when a Linear task asks whether to add cryptographic receipt signing, journal authority, or similar integrity machinery, but the current implemented topology may not yet contain an external trust boundary.

## Decision workflow

1. **Start with implemented topology, not desired architecture.** Enumerate where receipts are constructed, finalized, persisted, and consumed today. Separate local canonical authority from future exported projections.
2. **Do not add signing merely because fields exist.** Placeholder values such as `signing_key_id="unsigned"` and `signature="none"` are not a verifier. Treat them as data until a signer, verifier, key lifecycle, and trust boundary exist.
3. **Ask what signing would actually defend.** A colocated HMAC/key inside the same runner/DB trust domain usually does not defend against compromised runner identity, same-account DB writer compromise, root compromise, false-but-valid construction, or missing uniqueness/fencing/persistence controls.
4. **Require an independent verifier boundary before selecting signing.** Good reopen gates include network/export transport, cross-host replication, dashboard/Linear/journal consumers outside the canonical DB authority, or another receiver with an independently administered trust root.
5. **Freeze a non-executable precontract when the current answer is no.** Include the decision, current authority, current placeholder producers, future reopen gate, all authorization booleans false, and blockers. Do not authorize keys, secrets, source edits, events, producers, deploys, or Linear mutations from a discovery artifact.
6. **Static proof is enough for discovery only.** Bind current source head/tree, count receipt constructors/placeholders, check projection callers/transports, and prove zero event/admission state. Then send for read-only review. It remains blocked/no-dispatch even if the reviewer agrees.
7. **Only promote after prerequisites change.** After predecessor acceptance/merge/deploy and topology proof, refresh Linear/source truth and produce a new implementation contract if needed.

## Minimal proof packet

```text
DECISION=<current_local_boundary_no_signing|signing_required|blocked_unknown>
CURRENT_INTEGRITY_AUTHORITY=<DB/finalizer/constraints/etc>
CURRENT_CRYPTOGRAPHIC_VERIFIER=<none|path>
CURRENT_PRODUCERS=<count + placeholder fields>
PRODUCTION_PROJECTION_CALLERS=<count/list>
FUTURE_REOPEN_GATE=<concrete external trust boundary>
KEY_CREATION_AUTHORIZED=false
SECRET_ACCESS_AUTHORIZED=false
SOURCE_MUTATION_AUTHORIZED=false
EVENT_POST_AUTHORIZED=false
PRODUCER_AUTHORIZED=false
DEPLOYMENT_AUTHORIZED=false
NOT_CLAIMING=dispatch_readiness,source_implementation,key_lifecycle,event,producer,merge,deployment
```

## Sanitizer/tooling pitfall

When writing temporary verifier scripts inside chat-visible tooling, literals such as `...AUTHORIZED=false` can be sanitizer-sensitive. Prefer parsing `KEY=value` lines and asserting JSON booleans are not true over embedding multiple literal false strings. Do not mutate the artifact to satisfy a disposable verifier display/masking bug; fix only the verifier and rerun.