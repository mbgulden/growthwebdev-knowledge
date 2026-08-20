# Lane-Rejection Owner Routing

## Trigger
A task has a valid local commit, but the repository push guard rejects a required path because it is outside the assigned agent's lane.

## Required disposition
Treat this as a handoff event, never a terminal blocker and never permission to bypass the guard.

1. Read the canonical lane definition for the rejected path.
2. Preserve task-scope labels; remove the blocked `agent:<name>` label; add the path owner's `agent:<name>` label and `dispatch:ready`.
3. Post one handoff comment that includes:
   - exact local commit and path;
   - focused verification already run;
   - permitted action for the owner (inspect/cherry-pick a scoped candidate or reproduce it, then open a PR);
   - the original task's non-goals, such as no blind stale-PR merge/cherry-pick.
4. Re-query Linear and verify `Todo`, owner label, `dispatch:ready`, and the handoff comment.
5. If no agent owns the path, route a lane-governance defect to the governance owner. Do not leave the source task assigned to the blocked agent.

## Documentation paths
When docs have more than one nominal writer, select the designated docs/research dispatcher owner. The receiving agent independently inspects the candidate and publishes through its own lane; a blocked local commit is handoff evidence, not completion.

## Evidence minimum
Keep the candidate commit and a narrow patch/handoff artifact. The handoff comment must be sufficient for a new agent to resume without rediscovering the failure.