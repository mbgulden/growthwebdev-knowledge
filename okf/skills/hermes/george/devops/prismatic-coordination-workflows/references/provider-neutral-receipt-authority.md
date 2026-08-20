# Provider-neutral receipt authority for Prismatic

Use this reference when coordinating native verification, completed-work promotion, dashboard acceptance, or doctor policy after a task touches Prismatic verification/governance surfaces.

## Durable lesson

GitHub and GitHub Actions are optional transport/hosted-signal layers unless local policy explicitly requires them. A red GitHub Actions state caused by provider infrastructure (for example billing/spending-limit failure before runner startup) must not become the Engine's native merge/promotion gate.

Native authority should come from a durable provider-neutral receipt path:

1. Signed receipt validator remains the authority for schema, bindings, freshness, revocation, verifier identity, clean-room/source proof, commands/log digests, and non-claims.
2. Store accepted/blocked/revoked/superseded receipts immutably in a durable local store before dashboard promotion.
3. Treat hosted provider signals as optional metadata only: useful evidence, never controlling eligibility unless policy says so.
4. Dashboard copy should say native receipt / provider-neutral verification, not “verified PR” or “GitHub green” as the primary acceptance surface.
5. Doctor defaults should be provider-neutral: disconnected GitHub is WARN/optional transport degradation; it becomes ERROR only when required by local policy.

## Implementation pattern

- Reuse existing receipt schema/validator and clean-room/source-acquisition modules; do not invent a parallel bureaucracy.
- Add deterministic receipt IDs, idempotent replay, conflict detection, concurrent replay coverage, and fail-closed supersession/revocation handling.
- Reject secret-like receipt content before persistence.
- Expose read-only dashboard/API state that includes candidate/base/tree refs, source repository locator, checkout/acquisition/environment digests, verifier identity, proof classes, commands, logs, artifact digests, non-claims, hosted-signal metadata, and side-effect booleans.
- Preserve canonical dashboard shell and regenerate/update any lossless dashboard source fragments/tests after editing `dashboard.html`.

## Verification checklist

Minimum focused proof before independent review:

```text
COMMAND=ruff format/check + py_compile + pytest receipt_store, receipt_validator, doctor, dashboard asset, clean-room, source-acquisition tests
RESULT=PASS
SCOPE=focused provider-neutral receipt authority
AD_HOC_OR_CANONICAL=ad-hoc targeted
NOT_CLAIMING=canonical full-suite green until tests/ passes
```

Canonical proof must follow after fragment/test repairs:

```text
COMMAND=python -m pytest -q -p no:cacheprovider tests
RESULT=PASS required before publish/merge/deploy
AD_HOC_OR_CANONICAL=canonical suite
```

## Pitfalls from the PNVR session

- Do not pause Engine progress just because GitHub Actions is red when the job never started and the failure is hosted-provider billing/infrastructure. Inspect and classify it, then continue using native proof if policy allows.
- If dashboard HTML changes, also update/regenerate the repository's lossless dashboard source-split artifact; otherwise canonical tests can fail even when runtime behavior is correct.
- Avoid shared mocked provider objects in doctor tests; each `run_doctor` call should receive a fresh `ProviderReport` so required/optional mutations do not contaminate earlier assertions.
- When testing supersession with changed candidate/tree refs, update the expected policy bindings too; otherwise the canonical validator correctly blocks with candidate/tree mismatch.
- Treat public dashboard checks as phase-bound: pre-deploy `https://prismatic.growthwebdev.com` health proves the existing shell, while post-merge immutable deploy proof must separately prove the native receipt API/dashboard integration. See `references/provider-neutral-publication-dashboard-proof.md`.
- If publication transport is blocked by local Git credentials, use GitHub CLI device auth plus `gh auth setup-git`, then verify local/remote branch SHA equality; never print credential values.
