# Finite verification and resumable Linear execution

Use this when a Prismatic Linear/dashboard/workflow packet is close but repeated review or recovery loops start expanding the gate.

## User correction captured

Michael flagged the anti-pattern directly: a rigid, ever-expanding approval loop makes the work feel like it will never be approved even when it was close hours earlier. Treat that as a workflow bug.

## Operating rule

Verification must be finite, pre-bounded, and terrain-aware:

1. Define the minimum acceptance contract before the next execution attempt.
2. Separate real blockers from implementation-hardening requests.
3. Preserve completed, independently verified stages instead of rolling back the whole packet for late-stage transport or projection noise.
4. Resume from the last verified checkpoint when the external system supports it.
5. Stop the loop when the agreed contract is satisfied; do not keep adding adversarial findings as new approval requirements.

## Linear-specific terrain lessons

- Linear client-supplied IDs may reject deterministic UUIDv5 even though they are formally valid UUIDs. For deterministic packet objects, freeze a ledger of UUIDv4 IDs instead of deriving UUIDv5 IDs.
- Linear post-write reads can be eventually consistent and can briefly regress after appearing converged. Use bounded convergence windows, not immediate single-read drift failure.
- Avoid monolithic full-run/full-rollback loops under API pressure. They become too chatty and can turn transport pressure into new recovery work.
- Rollback proof and post-recovery proof should be paced. If aggregate proof times out but mutation scope is bounded, run slower independent live verification against the frozen baseline.

## Better execution shape

Use checkpoints:

1. Baseline capture and hash bind.
2. Content updates.
3. New object creation.
4. Topology/parent updates.
5. Relation creation.
6. Final compact proof packet.

At each checkpoint, persist:

```text
CHECKPOINT=<name>
BOUND_OBJECTS=<ids>
EXPECTED_STATE=<hashes or exact field list>
LIVE_PROOF=<receipt path>
RESUME_FROM=<next checkpoint>
ROLLBACK_SCOPE=<only unverified or owned residue>
```

## Approval discipline

A review can block execution only for defects that violate the agreed safety/acceptance contract, such as wrong object, wrong value, ownership leak, irreversible mutation risk, or unreconciled live residue.

Do not block indefinitely for improvements that are merely better engineering after the current safety contract is met. Capture those as the next slice.
