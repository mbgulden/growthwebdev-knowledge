#!/usr/bin/env python3
"""
check_ned_queue.sh — Reproducible Ned-queue state probe for ownership validation.

Fetches every issue carrying the agent:ned label, buckets them by state, and
prints a structured summary suitable for inclusion in a triage comment or cron
reply. Designed to be cheap to re-run on every cron tick (one GraphQL roundtrip,
~2 KB output) so the "0 actionable" verdict can be re-verified each cycle.

Usage:
    bash check_ned_queue.sh                  # probe agent:ned filter
    bash check_ned_queue.sh agent:sam        # probe any other agent label
    LINEAR_API_KEY=... bash check_ned_queue.sh  # explicit key

Output format (stdout, structured for grep/awk):
    Total <agent_label> issues: N
    <state>: M — <identifiers...>
    Actionable (Todo/In Progress, no human-review): N — <identifiers...>
    Human-blocked (needs-human-review): N
    In Progress WITHOUT needs-human-review (carve-outs): N — <id> <title...>
    Empty-queue verdict: <YES|NO>  (YES = zero actionable in any bucket)

Exit codes:
    0 — always (validation, not a gate)

Side effects: prints to stdout only. One Linear API roundtrip (~250 req / 15min
budget leaves plenty of headroom). No file writes, no network calls beyond the
GraphQL fetch.
"""

import json
import os
import subprocess
import sys
import urllib.parse
from collections import defaultdict


def fetch_key() -> str:
    """Resolve LINEAR_API_KEY from shell env (cron parent shell)."""
    if os.environ.get("LINEAR_API_KEY"):
        return os.environ["LINEAR_API_KEY"]
    r = subprocess.run(["bash", "-lc", "echo \"$LINEAR_API_KEY\""],
                        capture_output=True, text=True)
    key = r.stdout.strip()
    if not key:
        raise SystemExit("LINEAR_API_KEY not set in parent shell")
    return key


def fetch_issues(label: str, api_key: str, first: int = 100) -> list:
    """Fetch issues filtered by a single agent label, with full payload."""
    # Note: page=100 is fine for the rate limit (2500/15min); escalate to
    # pagination only if Ned's queue ever exceeds 100 (was 50 in case study,
    # 100 as of 2026-06-26).
    query = (
        '{ issues(filter: {labels: {name: {eq: "'
        + label
        + '"}}}, first: '
        + str(first)
        + ') { nodes { identifier title description state { name } labels { nodes { name } } } } }'
    )
    payload = json.dumps({"query": query})
    r = subprocess.run(
        [
            "curl",
            "-s",
            "https://api.linear.app/graphql",
            "-H",
            "Authorization: " + api_key,
            "-H",
            "Content-Type: application/json",
            "-d",
            payload,
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    try:
        data = json.loads(r.stdout)
    except json.JSONDecodeError:
        print("ERROR: Linear API returned non-JSON:")
        print(r.stdout[:500])
        raise SystemExit(2)
    if "errors" in data:
        print("ERROR: Linear API errors:")
        print(json.dumps(data["errors"], indent=2))
        raise SystemExit(2)
    return data.get("data", {}).get("issues", {}).get("nodes", [])


def bucket(issues: list) -> dict:
    """Group issues by state × human-review flag; identify carve-outs."""
    by_state: dict = defaultdict(list)
    actionable: list = []
    human_blocked: list = []
    carveouts: list = []  # In Progress w/o needs-human-review
    for n in issues:
        labels = [l["name"] for l in n.get("labels", {}).get("nodes", [])]
        state = n["state"]["name"]
        has_human = "agent:needs-human-review" in labels
        bucket_key = state + (" [needs-human-review]" if has_human else "")
        by_state[bucket_key].append(n["identifier"])
        if has_human:
            human_blocked.append(n["identifier"])
        elif state in ("Todo", "In Progress", "Backlog"):
            actionable.append(n["identifier"])
        if state == "In Progress" and not has_human:
            carveouts.append((n["identifier"], (n.get("title") or "")[:60]))
    return {
        "by_state": by_state,
        "actionable": actionable,
        "human_blocked": human_blocked,
        "carveouts": carveouts,
    }


def main() -> int:
    label = sys.argv[1] if len(sys.argv) > 1 else "agent:ned"
    api_key = fetch_key()
    issues = fetch_issues(label, api_key)
    b = bucket(issues)

    print("Total " + label + " issues: " + str(len(issues)))
    print("")
    for state in sorted(b["by_state"].keys()):
        ids = b["by_state"][state]
        preview = ", ".join(ids[:5])
        if len(ids) > 5:
            preview += "..."
        print("  " + state + ": " + str(len(ids)) + " — " + preview)
    print("")
    print(
        "Actionable (Todo/In Progress/Backlog, no human-review): "
        + str(len(b["actionable"]))
    )
    if b["actionable"]:
        print("  IDs: " + ", ".join(b["actionable"][:10]))
    print("Human-blocked (agent:needs-human-review): " + str(len(b["human_blocked"])))
    print("")
    if b["carveouts"]:
        print("⚠️  In Progress WITHOUT needs-human-review (CARVE-OUTS):")
        for cid, ctitle in b["carveouts"]:
            print("  " + cid + " — " + ctitle)
        print("")
    empty = len(b["actionable"]) == 0 and len(b["carveouts"]) == 0
    print("Empty-queue verdict: " + ("YES" if empty else "NO"))
    return 0


if __name__ == "__main__":
    sys.exit(main())