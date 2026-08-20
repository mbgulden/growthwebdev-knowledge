# Provider-neutral native verification receipts — session learning

Use this reference when coordinating or implementing Prismatic provider-neutral verification, durable receipt stores, dashboard gates, doctor policy, or promotion authorization.

## Durable acceptance authority

- Hosted-provider signals (GitHub Actions, billing state, PR status) are optional transport/telemetry. They may be stored and displayed, but they must not decide native merge/deploy eligibility unless local policy explicitly requires them.
- Native acceptance must bind to an exact task/artifact pair, usually `task_id` + `candidate_sha`; missing, stale, revoked, superseded, or non-matching native receipt blocks promotion fail-closed.
- Stored receipt rows are audit history, not perpetual authorization. Recompute effective eligibility at read time from signed receipt JSON + current policy, then overlay lifecycle events.

## Required native binding checks

Authoritative native receipt ingestion should verify against a real clean checkout, not synthetic SHA fields:

1. Canonical absolute repository root resolves to the Git top-level and is not a symlink alias.
2. Checkout `HEAD` equals signed `candidate_sha`.
3. Candidate tree equals signed `candidate_tree_sha`.
4. Base commit tree equals signed `base_tree_sha`.
5. Signed changed paths exactly equal `git diff --name-only <base> <candidate>`.
6. Allowed-root containment uses path components, not string-prefix matching.
7. Signed changed-path digest matches canonical changed-path list.
8. Passing proof scopes link to executed command IDs that actually exist in the receipt.

## Verifier isolation fields

Native receipts should carry explicit isolation evidence and expose it in API/dashboard readback:

- independent verifier identity,
- filesystem isolation,
- clean checkout ID / source acquisition ID,
- network isolation status,
- proof-scope statuses for focused, canonical, clean-room, package, production, and browser proof.

## Lifecycle model

Supersession/revocation/freshness must be fail-closed without mutating the immutable receipt body:

- Keep original receipt JSON and initial decision immutable.
- Add append-only lifecycle events for supersession or later state.
- Project effective state at read time.
- Counts, dashboards, and promotion decisions should use projected effective state, not raw stored columns.

## Dashboard/source workflow

Do not patch generated dashboard templates as the source of truth. Patch canonical dashboard source fragments first, then rebuild deterministically and run the lossless check.

Typical sequence:

```bash
python3 scripts/build_dashboard.py
python3 scripts/build_dashboard.py --check
```

## Doctor policy pattern

Doctor should separate:

- required native components: receipt store, dashboard surface, durable event queue, exact-tree/source verifier, release-evidence contract, production-health contract;
- optional providers/transports: GitHub Actions, PR metadata, external CI signals.

Required native component failures drive `ERROR`. Optional provider failures are `WARN` unless policy explicitly requires that provider.

## Promotion authorization pattern

Promotion/merge/deploy authorization must consume native receipt state directly:

- Resolve completed-work task ID and exact candidate SHA.
- Look up the latest effective native receipt for that exact pair.
- Missing store, missing match, stale/revoked/superseded receipt, wrong candidate, or receipt read failure blocks.
- PR/Linear dry-run planning may remain visible as operator UX, but must not be the acceptance authority.

## Proof/reporting boundary

When interrupted mid-build, report clearly:

- what has passed with command/log evidence,
- what latest edits are unverified,
- exact known defects/static diagnostics,
- what is not claimed: canonical full-suite green, clean-room proof, package proof, independent review, PR, merge, deploy, production proof.
