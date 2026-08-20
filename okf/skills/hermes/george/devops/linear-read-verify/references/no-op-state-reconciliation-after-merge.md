# No-op state reconciliation after merge

Use this when an accepted Prismatic merge/closeout workflow expects a Linear state transition, but a live readback shows the issue is already in the intended state.

## Rule

Do not send redundant Linear mutations. A state transition that is already satisfied should be reconciled with read-only evidence plus a local receipt.

## Steps

1. Run the bounded read-only broker for the issue and target state.
2. Verify `ok=true`, `issue.read_only=true`, exact identifier, state ID/name/type, and relevant timestamps such as `completedAt`.
3. If the state already equals the intended postcondition, stop before writer invocation.
4. Write a local restricted receipt that records:
   - operation / authorization scope;
   - accepted head/tree and merge commit/tree if relevant;
   - observed issue state and timestamps;
   - `decision=NO_MUTATION_ALREADY_SATISFIED`;
   - `mutation_sent=false`;
   - non-claims.
5. Lock the receipt mode (`600`) and hash it.
6. Optionally post only a bounded completion comment if outbound/publication authority already covers PR closeout comments; otherwise report the receipt locally.
7. Update the Prismatic handoff with the receipt path/hash and explicit `no redundant mutation` boundary.

## Pitfalls

- Do not treat an expected writer step as mandatory when the live tracker already converged.
- Do not add mutation support to read-only brokers for convenience.
- Do not infer current Linear state from session history; inspect Linear live through the broker first.
- Do not print tokens or raw GraphQL errors in the receipt or chat.
