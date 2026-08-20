# Routed-work parent reconciliation

Use after a lane-blocked child is reassigned and its owner publishes the artifact.

1. Read the authoritative target branch; do not rely on a local commit or an agent finalizer message.
2. Confirm the exact required artifact exists and the scoped proof is green.
3. Re-read every child gate. Each must be `Done` or `In Review` with concrete evidence before advancing a parent.
4. Advance the parent only to **In Review** when the acceptance union is ready for human review. `Done` requires reviewed/accepted final integration, not merely green child evidence or an open PR.
5. State non-claims in the parent comment: no automatic PR merge, PE cutover, monorepo removal, deployment, or production integration unless actually performed.

This preserves visibility after a successful lane handoff without turning intermediate evidence into a false completion claim.
