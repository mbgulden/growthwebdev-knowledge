# Durable evidence promotion gate review

Session-derived checklist for reviewing Prismatic AGY/Fred/Kai completed-work promotion flows after adding durable evidence retention.

## Trigger

Use when an agent adds or repairs logic around:

- `agy_completed_work` ingestion/evidence retention;
- promotion decision/read models;
- operator-action approval previews;
- completed-work integration gates;
- any pathway that turns an agent packet into `decision_ready`, PR creation, approval, or merge/deploy next steps.

## Review sequence

1. **Inventory all decision emitters, not only the new one.** Search for separate ledger/read-model/approval builders that can emit `decision_ready` or `would_execute`. A new canonical evidence gate is insufficient if an older ledger path can still bypass it.
2. **Use both negative and positive fixtures.** Prove historical/unavailable/partial evidence is blocked, then prove complete retained evidence reaches only the intended dry-run approval preview.
3. **Keep real side effects false.** Promotion and operator-approval tests should inspect side-effect flags and execution previews; a policy `pass` must not imply a real PR, merge, deploy, or external write happened.
4. **Build positive fixtures that satisfy the completed-work gate.** `source_path` must be an absolute path under the effective operator `Path.home()`; a temp path under `/tmp` can be rejected as `manual_review_scope` even when evidence files exist. Prefer a temporary directory under `/home/ubuntu` or the active HOME for synthetic complete-evidence packets.
5. **Separate classifications.** Distinguish row/gate `classification`, `integration_classification`, packet `recommended_action`, ledger `status/recommendation`, operator approval `policy_gate`, and execution preview fields. Similar words are not interchangeable.
6. **Pin the branch/commit under review.** Before writing a final proof, assert the checkout `HEAD` equals the expected commit and the working tree is clean; if the active worktree drifted, create a temporary isolated worktree from the PR branch/commit.
7. **Treat a verifier failure as a review finding, not a retry loop.** If an ad-hoc verifier fails, inspect whether the fixture violated gate preconditions before retrying. Update the proof script and log the boundary.

## Minimal proof expectations

A satisfactory review packet should show:

```text
HISTORICAL_EVIDENCE_LEDGER=blocked
HISTORICAL_OPERATOR_APPROVAL=blocked
COMPLETE_EVIDENCE_LEDGER=decision_ready
COMPLETE_EVIDENCE_OPERATOR_PREVIEW=pass_dry_run_only
REAL_SIDE_EFFECTS=false
AD_HOC_OR_CANONICAL=ad-hoc targeted
NOT_CLAIMING=merge,deploy,canonical suite
```

## Pitfalls

- Do not accept an agent's broad pytest pass as proof the approval path is closed; add behavior probes for old ledgers and operator previews.
- Do not call a Kai/Fred PR ready if only the negative/historical evidence path was independently proven. Positive complete-evidence proof is required too.
- Do not fabricate historical evidence to make old records pass. Historical records with unavailable proof should stay held/manual-review until actual retained artifacts exist.
