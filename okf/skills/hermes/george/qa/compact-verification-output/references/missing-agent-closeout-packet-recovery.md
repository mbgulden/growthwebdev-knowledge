# Missing agent closeout packet recovery

Use this when an assigned agent reports or appears to have finished, but the required compact proof packet is missing, incomplete, or does not expose the exact decision field the dispatch required.

## Pattern

1. Independently verify the available runtime/API/repo evidence first. Do not accept `finished` as proof.
2. Report the result as `PARTIAL` when core evidence passes but the agent packet is missing or ambiguous.
3. Separate **observed runtime fields** from the **requested closeout contract**. Example: `classification=merge_ready`, `integration_classification=pass_ready_for_review`, and `recommended_action=open_or_update_pr` may be useful, but they are not the same as a literal `promotion_decision=ready_for_operator_review` unless the contract allows mapping.
4. Create a narrow follow-up prompt asking only for the missing fields, not a rerun of the whole task.
5. Include the prior evidence summary so the agent can close the gap without redoing everything.
6. Require the agent to state whether a PR was opened/not required and whether any side effects occurred.
7. Keep the original marker unchanged so the closeout packet ties back to the assigned task.

## Follow-up prompt skeleton

```text
<Agent>, George reviewed the available evidence. Core proof looks <good/partial>, but George cannot fully accept <MARKER> until you provide the required final packet and clarify <missing field>.

Already verified:
- <route/command/result>
- <classification/proof/side-effect summary>

Please return one compact packet that answers:
1. Was a PR opened, or was no PR required?
2. What is the exact <decision field>? Use one of: <allowed values>.
3. If runtime does not expose a literal field, say that directly and map current fields to the intended decision.
4. Confirm side-effect safety booleans.
5. State the next blocker or next recommended slice.

COMMAND=<exact command or grouped command summary>
RESULT=<PASS|FAIL|BLOCKED>
LOG=<path>
SCOPE=<closeout packet scope>
AD_HOC_OR_CANONICAL=ad-hoc targeted
PR_OPENED=<url or none>
PR_REQUIRED=<yes|no>
<DECISION_FIELD>=<allowed value>
<DECISION_FIELD_SOURCE=<literal runtime field|mapped from current fields|other>
REAL_LINEAR_WRITEBACK_POSTED=false
DRY_RUN_LINEAR_WRITEBACK=true
REAL_GITHUB_PR_CREATED=false
AUTO_MERGE_ENABLED=false
NOT_CLAIMING=<explicit non-claims>
NEXT=<next blocker or recommended slice>
MARKER=<original marker>
```

## Reporting boundary

Do not mark the task fully accepted until the missing packet/field is supplied or a verified patch makes the runtime expose the contracted field. The correct interim status is usually `PARTIAL`, not `PASS`.
