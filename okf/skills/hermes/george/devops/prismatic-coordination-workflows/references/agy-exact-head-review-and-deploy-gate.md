# AGY exact-head review and deploy gate

Use this reference when coordinating an AGY orchestration/control-plane PR after local proof but before merge/deploy.

## Gate sequence

1. Freeze one exact candidate commit and stop editing it.
2. Bind all proof to the exact commit and tree:
   - `git rev-parse HEAD`
   - `git rev-parse HEAD^{tree}`
   - clean worktree
   - exact base/merge target
3. Run focused adversarial tests for every prior reviewer finding, then canonical local `tests/`, then installed wheel/clean-room proof when runtime packaging matters.
4. Dispatch independent exact-head review against that immutable commit. If any edit/amend happens, mark all earlier reviews stale and redispatch.
5. Do not merge from local proof alone unless the standing policy explicitly permits provider-neutral proof and independent exact-head review has returned `CLEAN`.
6. If GitHub Actions fails before jobs start, classify it as CI infrastructure/billing/setup boundary, not product failure and not CI green. Record annotations and state: "GitHub CI did not execute tests." Do not hide the red check.
7. After merge, deploy by creating an immutable release checkout + dedicated venv + systemd drop-in/override, preserving rollback packet and pre/post state receipts. Do not run production from mutable worktrees.

## Review replacement pattern

If an exact-head reviewer stalls:

- Wait a bounded interval once or twice.
- Keep the candidate frozen.
- Dispatch a replacement reviewer against the same exact SHA/tree with all prior findings and proof hashes.
- Do not treat silence as approval.

## State-machine invariants to require for AGY terminal reconciliation

Future AGY orchestration reviews should explicitly probe:

- one canonical run state machine; no extra wrappers/proof schemas/manual dispatch ceremony;
- terminal `process-result.json` must bind result path/hash/run/event/attempt/task/executable/manifest;
- stale `running` + terminal receipt projects `reconciliation_required` or finalized canonical state, never falsely live;
- cap slot release is cleanup-gated; false/missing survivor data fails closed;
- fake/counterfeit/symlink receipts are rejected;
- slot and lock files are regular private files with symlink/hardlink substitution rejected;
- cancellation receipt cannot be empty/forged and does not override live work improperly;
- status projections must not downgrade `reviewed`/`review_blocked` back to `review_pending`;
- concurrent review decisions serialize fail-closed;
- producers cannot self-review;
- launch failure containment distinguishes pre-spawn cleanup from post-spawn cleanup.

## Proof packet language

Use compact proof blocks and explicit boundaries:

```text
COMMAND=<exact command or grouped command>
RESULT=<PASS|FAIL|BLOCKED>
LOG=<path>
LOG_SHA256=<sha256>
SCOPE=<focused adversarial|canonical tests|clean-room installed|CI infrastructure>
AD_HOC_OR_CANONICAL=<ad-hoc targeted|canonical suite>
NOT_CLAIMING=<e.g. GitHub CI green, merge, deploy, live reconciliation>
MARKER=<marker>
```

## Pitfall

A red GitHub check caused by account billing/spending limits may have zero job steps and no failed test log. Capture check-run annotations via the GitHub API/CLI and comment the boundary on the PR. This preserves transparency while allowing the separate provider-neutral gate to carry the technical proof when policy permits it.
