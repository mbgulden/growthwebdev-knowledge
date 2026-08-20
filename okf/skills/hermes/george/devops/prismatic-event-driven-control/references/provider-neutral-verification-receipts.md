# Provider-neutral verification receipts

Use this when Prismatic merge/review/deploy flow is tempted to treat GitHub Actions, GitHub availability, or any hosted CI provider as the acceptance authority.

## Durable lesson

Prismatic Engine must validate work through native receipts, dashboard/event-queue state, exact-tree proof, independent review, immutable-release proof, and production/runtime proof. GitHub can publish source and expose optional hosted signals, but GitHub Actions must not be required for Engine progress.

A hosted CI failure caused by billing/spending limits, missing runners, provider outage, or unavailable credentials is not itself a product verification failure. Inspect it to classify whether actual tests ran, then record it as optional hosted-signal evidence.

## Required acceptance authority

Native acceptance should bind these into a durable receipt:

- receipt ID and schema version;
- task/run/producer identity;
- exact source commit and tree;
- exact base commit and tree;
- canonical nonsymlink repository root;
- changed-path containment;
- commands with exit codes;
- log paths plus SHA-256 digests and byte lengths;
- proof class: focused, canonical, clean-room, package, production, browser;
- independent verifier identity and isolation;
- creation time, freshness window, revocation, and supersession;
- final decision plus explicit nonclaims.

The dashboard should render the native receipt as the acceptance truth. GitHub Actions status, when available, should be labeled `OPTIONAL_HOSTED_SIGNAL`, never as merge/deploy authority.

## Dashboard/doctor expectations

- Existing dashboard surfaces should be extended/reconnected, not replaced with a mini-dashboard.
- Completed-work and raw-output rows should preserve evidence and byte/digest identity.
- `doctor` or golden-flow status should not report GitHub as required unless a local policy explicitly opts into that requirement.
- A no-GitHub/no-credentials acceptance test should pass when native proof is complete.
- A red or unavailable GitHub Actions signal should be displayed as optional metadata and must not block native acceptance by itself.

## Proof packet

```text
COMMAND=<native verification commands and dashboard/API checks>
RESULT=<PASS|FAIL|BLOCKED>
LOG=<path>
SCOPE=provider-neutral receipt store, dashboard gate, doctor/status, clean-room/no-GitHub acceptance
AD_HOC_OR_CANONICAL=<focused|canonical|clean-room|package|production|browser>
HOSTED_SIGNAL=<optional/unavailable/red/green + reason>
NOT_CLAIMING=GitHub Actions green, auto-merge, deployment, Linear write, producer admission, cap increase
MARKER=PROVIDER_NEUTRAL_VERIFICATION_RECEIPT_OK
```

## Pitfalls

- Do not pause at GitHub red checks as if they are the gate. Classify whether tests actually ran, then return to native proof.
- Do not phrase reports as though GitHub Actions green is required after native proof is already complete.
- Do not let dashboard copy say PR dry-run or hosted CI is the acceptance truth; describe it as optional transport/status metadata.
- Do not launch a producer merely because a provider-neutral receipt gap is found; create or queue a bounded slice through the dashboard/event path.
