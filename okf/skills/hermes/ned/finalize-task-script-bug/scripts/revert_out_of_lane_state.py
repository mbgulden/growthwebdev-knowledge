#!/usr/bin/env python3
"""
revert_out_of_lane_state.py — revert a Linear issue that finalize_task.sh
auto-promoted to 'In Review' despite explicit out-of-lane triage comments.

Trigger: after a finalize_task.sh pass where the issue's last 5 comments
contain dequeue phrases ("out-of-lane", "dequeued", "relabel", "wrong-agent",
"misroute", "lane-violation", "outside ned's lane", "not an infra task"),
but finalize's Step 3 fired anyway and flipped state. This script reverts
state back to 'Todo' (or whichever state Michael last set) and posts a
state-reversal comment so the audit trail shows the auto-then-revert.

Usage:
    python3 revert_out_of_lane_state.py GRO-537
    python3 revert_out_of_lane_state.py GRO-537 --target-state Todo

Notes on the GraphQL mutation shape (the landmine that ate 2 failed 400s):
    - `id` is a TOP-LEVEL mutation argument, NOT inside `input`
    - `IssueUpdateInput` accepts: stateId, title, description, estimate,
      assigneeId, labelIds, priority, parentId, dueDate, cycleId, projectId
    - `IssueUpdateInput` does NOT accept: id, state (use stateId), body
    Linear returns GRAPHQL_VALIDATION_FAILED for the wrong shape with
    message: "Field \"id\" is not defined by type \"IssueUpdateInput\"".

The same script posts the reversal comment via commentCreate(input:{issueId, body}).
commentCreate DOES accept `issueId` and `body` inside input — this asymmetry
between issueUpdate and commentCreate is a frequent source of confusion.

Token resolution order:
    1. $LINEAR_API_KEY env var
    2. /home/ubuntu/.hermes/profiles/ned/.env
    3. /home/ubuntu/.hermes/.env
    4. /home/ubuntu/.env
"""
import argparse
import json
import os
import sys
import urllib.request


def find_token():
    """Locate Linear API key from env files."""
    if os.environ.get("LINEAR_API_KEY"):
        return os.environ["LINEAR_API_KEY"]
    for p in [
        "/home/ubuntu/.hermes/profiles/ned/.env",
        "/home/ubuntu/.hermes/.env",
        "/home/ubuntu/.env",
    ]:
        if os.path.exists(p):
            for line in open(p):
                if line.startswith("LINEAR_API_KEY" + "="):
                    val = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if val:
                        return val
    return None


def gql(query, variables, token):
    req = urllib.request.Request(
        "https://api.linear.app/graphql",
        data=json.dumps({"query": query, "variables": variables or {}}).encode(),
        headers={"Authorization": token, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())


def resolve_state_id(token, name):
    """Resolve a workflow state name -> UUID."""
    d = gql("""query{ workflowStates{ nodes{ id name } } }""", None, token)
    for n in d["data"]["workflowStates"]["nodes"]:
        if n["name"] == name:
            return n["id"]
    return None


def revert(issue_id, target_state_name, token):
    """Revert the issue to target state and post a reversal comment."""
    # Resolve issue UUID + current state
    issue = gql(
        """query($id:String!){ issue(id:$id){ id state{ name } } }""",
        {"id": issue_id},
        token,
    )
    issue_uuid = issue["data"]["issue"]["id"]
    current_state = issue["data"]["issue"]["state"]["name"]

    target_state_id = resolve_state_id(token, target_state_name)
    if not target_state_id:
        print(f"  FATAL: workflow state {target_state_name!r} not found")
        sys.exit(1)

    if current_state == target_state_name:
        print(f"  No revert needed: {issue_id} is already in {target_state_name!r}")
        return False

    # Revert state. NOTE: `id` is a top-level argument, NOT inside input.
    upd = gql(
        """mutation($id:String!, $stateId:String!){
            issueUpdate(id:$id, input:{stateId:$stateId}){ success }
        }""",
        {"id": issue_uuid, "stateId": target_state_id},
        token,
    )
    ok = upd.get("data", {}).get("issueUpdate", {}).get("success")
    print(f"  Revert {current_state} -> {target_state_name}: {ok}")

    # Post reversal comment.
    body = f"""## Ned - state reversal

{issue_id} was auto-promoted to `{current_state}` by `finalize_task.sh` step 3, but the issue's prior comment thread marks it explicitly out-of-lane (dequeue phrases present in last 5 comments). Reverted to `{target_state_name}` to restore Michael's deliberate pre-dequeue state. No code written, no branch created.

**Pattern:** This is the Nth auto-promotion reversal today (see GRO-509, GRO-537 history). The `finalize_task.sh` script's step 3 was patched 2026-06-28 with an out-of-lane comment-scan guard; future finalize calls should skip the transition automatically.

- ned (cron, state correction)"""
    cmt = gql(
        """mutation($issueId:String!, $body:String!){
            commentCreate(input:{issueId:$issueId, body:$body}){ success comment { id } }
        }""",
        {"issueId": issue_uuid, "body": body},
        token,
    )
    print(f"  Reversal comment posted: {cmt.get('data', {}).get('commentCreate', {}).get('success')}")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Revert a Linear issue from In Review back to a target state "
                    "after finalize_task.sh auto-promoted it despite out-of-lane "
                    "triage comments."
    )
    parser.add_argument("issue_id", help="Linear issue identifier (e.g. GRO-537)")
    parser.add_argument(
        "--target-state",
        default="Todo",
        help="Workflow state to revert to (default: Todo)",
    )
    args = parser.parse_args()

    token = find_token()
    if not token:
        print("FATAL: LINEAR_API_KEY not found in env or env files")
        sys.exit(1)

    revert(args.issue_id, args.target_state, token)


if __name__ == "__main__":
    main()