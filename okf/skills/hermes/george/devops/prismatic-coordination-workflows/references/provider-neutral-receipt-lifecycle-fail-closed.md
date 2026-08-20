# Provider-neutral receipt lifecycle fail-closed review pattern

Use this reference when coordinating, reviewing, or repairing provider-neutral verification receipt work that feeds merge/deploy/promotion decisions.

## Core lesson

A native provider-neutral receipt is only authoritative if its full lifecycle is revalidated at every consumer boundary. Do not accept a design that records a one-time `accepted` receipt and then lets downstream promotion, approval, or dashboard state treat that fact as permanently actionable.

## Required properties

### 1. Exact clean-checkout binding

Receipt acceptance should bind to a clean, exact checkout, not just commit/tree strings.

Require evidence for:

- canonical repository root;
- exact `HEAD` / candidate commit;
- base commit and base tree;
- candidate tree;
- exact changed paths and allowed-root containment;
- no staged changes;
- no unstaged tracked changes;
- no untracked files;
- signed/digested clean-state observation with freshness.

A useful adversarial test matrix includes:

- tracked file modified after receipt generation;
- untracked file added after receipt generation;
- stale clean-state observation;
- clean-state digest mismatch;
- base/candidate/tree/path mismatch.

### 2. Revocation is not optional metadata

Revocation must be a first-class fail-closed state source, not a static field checked only during initial persistence.

Require:

- canonical revocation source consulted on persistence and every effective-state read;
- missing/malformed/unsafe revocation source fails closed once native state exists;
- append-only revoke lifecycle operation for explicit cancellation;
- revocation overrides supersession when projecting effective state;
- doctor/runtime-state declaration for receipt DB and revocation source.

Regression tests should prove:

- externally revoked receipts no longer authorize;
- missing revocation state blocks instead of self-healing empty;
- malformed revocation state blocks;
- append-only revoke leaves original receipt row immutable;
- revoked receipts disappear from accepted/effective counts or project as revoked according to API contract.

### 3. Downstream authorization must revalidate, not cache

Promotion and operator-approval layers must consume current effective native state. A receipt accepted yesterday is not enough.

Require downstream evidence to bind:

- receipt ID;
- receipt digest/hash;
- repository/task identity;
- base commit and base tree;
- candidate commit and candidate tree;
- clean-state proof.

Every list/detail/actionability read should recompute or overlay current native authorization. Stored approval records must not remain executable after receipt revocation, supersession, expiry, or mismatch.

Adversarial tests should include:

- no native receipt => no `decision_ready` / no executable action;
- revoked native receipt => existing cached approval becomes manual review / non-executable;
- mismatched task or candidate => gate fails;
- stale or superseded receipt => recommendation can remain visible for audit but is not actionable;
- forged nonempty binding fields => gate fails (truthiness is never sufficient);
- format-valid independent mutations of receipt ID, receipt digest, repository, task, base commit/tree, and candidate commit/tree on either the native or expected side => every mutation fails;
- fresh authoritative-store lookup mismatch => gate fails even when cached metadata and formats look valid.

Carry an immutable `expected_native_bindings` object through promotion/revalidation, require strict identifier/digest/Git-OID formats, require native metadata to equal expected metadata, and then compare both to a fresh effective receipt-store read immediately before actionability.

## Coordination checklist

When reviewing an agent report for this class of work, require proof packets that separate:

```text
COMMAND=<exact command>
RESULT=<PASS|FAIL|BLOCKED>
LOG=<path>
SCOPE=<receipt store | downstream promotion | approval cache | doctor | dashboard | canonical suite>
AD_HOC_OR_CANONICAL=<ad-hoc targeted|canonical suite>
NOT_CLAIMING=<merge|deploy|production proof|independent CLEAN>
```

Do not approve merge/deploy until:

1. targeted adversarial tests cover clean checkout, revocation, and downstream cached approval behavior;
2. canonical suite is green on the exact head;
3. package/clean-room proof is green when package consumers are affected;
4. independent exact-head rereview returns CLEAN after any HIGH repair;
5. public dashboard proof is clearly labeled pre-deploy or post-deploy.

## Pitfalls

- Do not treat GitHub/CI availability as native acceptance authority; hosted signals remain optional unless the task explicitly makes them required.
- Do not let a dashboard display an accepted native card unless the backing API projection is lifecycle-aware.
- Do not self-heal missing revocation state after a receipt DB exists; that can erase revocation evidence and fail open.
- Do not cache `merge_authorized` / `deploy_authorized` / `would_execute` as durable truth without read-time revalidation.
- Do not claim production proof from localhost, clean-room, or pre-deploy public-dashboard baseline evidence.