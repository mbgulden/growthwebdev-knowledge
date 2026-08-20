# Failed-producer live acceptance closeout

Use after a cap-1 AGY producer failed or was killed, but a same-task exact candidate was recovered, independently reviewed `CLEAN`, merged, and explicitly authorized for deployment.

## Durable lesson

A live deployment can be accepted, but the original producer failure must remain provenance. Do not backfill `producer_completed=true`, fabricate `RESULT.md`, or silently erase the failed packet/review history. Acceptance belongs to the recovered exact candidate, independent review, merge tree, immutable release, and live proof.

## Closeout sequence

1. Preserve the failed producer boundary in every receipt:
   - `PRODUCER_COMPLETED=false`
   - producer exit/status
   - cleanup proof and survivors
   - prior rejected evidence packet, if any (`V<N>_REVIEW=BLOCKED evidence only`).
2. Bind source acceptance to exact immutable identities:
   - reviewed candidate head/tree;
   - PR head at merge time;
   - merge SHA/tree;
   - `MERGE_TREE == REVIEWED_TREE`.
3. If GitHub Actions did not actually run product steps, record it as infrastructure boundary:
   - `GITHUB_CI_EXECUTED_TESTS=false`
   - `GITHUB_CI_GREEN=false`
   - no product-test-failure claim.
4. Deploy only after explicit authorization or an already-authorized policy path:
   - immutable release checkout;
   - versioned venv;
   - release-specific systemd drop-in;
   - rollback/pre-state written before restart.
5. Prove live behavior from production, not only isolated release smoke:
   - route parity/body parity;
   - rendered browser requests from `/dashboard`;
   - mobile viewport/DPR/physical screenshot dimensions;
   - deep-link/preview endpoint proof when workspace viewer is in scope.
6. Record canonical acceptance through the harness/API path, not by hand-editing run JSON. The canonical record should show `state=accepted`, `verification_status=reviewed`, `review_status=accepted`, and preserve `producer_completed=false`.
7. Write a deployment receipt plus self-verifying SHA ledger, then run a final OS-safe `/tmp/hermes-verify-*` verifier after all receipt/handoff/comment writes that checks:
   - ledger verifies;
   - release head/tree and clean runtime checkout;
   - systemd `cwd`/command point to the immutable release/venv;
   - live route parity;
   - canonical accepted state;
   - dashboard activity state;
   - PR merge binding;
   - handoff markers.

## Proof packet shape

```text
RESULT=PASS
PRODUCER_COMPLETED=false
CANONICAL_STATE=accepted
VERIFICATION_STATUS=reviewed
REVIEWED_BY=<independent review id>
PR=<url>
MERGE_SHA=<sha>
MERGE_TREE=<tree>
EXACT_TREE_MATCH=true
RELEASE=<immutable release path>
VENV=<versioned venv>
SERVICE_ACTIVE=true
LIVE_ROUTE_PARITY=PASS
LIVE_RENDERED_DASHBOARD=PASS
GITHUB_CI_EXECUTED_TESTS=false|true
GITHUB_CI_GREEN=false|true
DEPLOYMENT_RECEIPT=<path>
DEPLOYMENT_LEDGER_SHA256=<sha>
ROLLBACK=<path>
AD_HOC_OR_CANONICAL=ad-hoc focused post-deployment closeout
NOT_CLAIMING=<CI green/canonical rerun/successor admission/etc.>
MARKER=<marker>
```

## Pitfalls

- Do not accept after merge alone. Live production proof and canonical accepted-state write/readback are separate gates.
- Do not write acceptance by directly editing canonical JSON/SQLite files. Use the harness/API path so fail-closed preconditions run.
- Do not let a final PR comment, deployment receipt, or handoff edit be newer than the last verifier. Run one final readback verifier after the last externally visible/control-state write.
- If a systemd `Environment=` assignment contains spaces, quote it as one assignment in the drop-in and verify loaded `systemctl show` output before restart.
