#!/usr/bin/env python3
"""
linear-routing-classify/verify.py — match SKILL.md contract.

For each Linear issue in the orchestrator's MBG team:
- agent:* labels match dispatch:* labels (e.g., agent:needs-human-review ↔ dispatch:paused).
- dispatch:ready requires every upstream agent:completed marker in the blocker chain.
- agent:needs-human-review issues must have a handoff entry pointing at them.

Exit codes: 0 (clean) / 1 (inconsistencies) / 2 (input/runtime error).
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


DEFAULT_TEAM = "GRO"
DEFAULT_HARNESS_PROFILE = "orchestrator"

# agent:* label ↔ dispatch:* label pairs. Both must be applied together or not at all.
AGENT_DISPATCH_PAIRS = {
    "agent:needs-human-review": ("dispatch:paused",),  # paused == awaiting human
    "agent:blocked-external": ("dispatch:paused",),
    "agent:ready": ("dispatch:ready",),
    "agent:dispatching": ("dispatch:ready",),
}
# These agent labels do NOT require a paired dispatch label.
NEUTRAL_AGENT_LABELS = {
    "agent:in-progress",
    "agent:completed",
    "agent:needs-triage",
    "agent:needs-second-witness",
}


def linear_graphql(query: str, variables: dict | None = None) -> dict:
    """Invoke linear_budgeted_query.py via subprocess. Path comes from
    LINEAR_QUERY_SCRIPT env var, falling back to ~/.hermes/profiles/<HERMES_PROFILE>/scripts/linear_budgeted_query.py."""
    import uuid

    env_default = (
        Path.home() / ".hermes" / "profiles" /
        os.environ.get("HERMES_PROFILE", "orchestrator") / "scripts" / "linear_budgeted_query.py"
    )
    script_path = Path(os.environ.get("LINEAR_QUERY_SCRIPT", str(env_default)))
    if not script_path.exists():
        raise RuntimeError(f"linear_budgeted_query.py not found at {script_path}")
    payload = json.dumps({"query": query, "variables": variables or {}})
    agent_name = "verifier.linear-routing-classify"
    result = subprocess.run(
        ["python3", str(script_path), agent_name],
        input=payload,
        capture_output=True, text=True, timeout=30, cwd=str(script_path.parent),
    )
    if result.returncode != 0:
        raise RuntimeError(f"linear_budgeted_query failed: {result.stderr.strip()}")
    data = json.loads(result.stdout)
    if "errors" in data:
        raise RuntimeError(f"linear_budgeted_query error: {data['errors']}")
    return data


def fetch_team_issues(team: str, days_back: int) -> list[dict]:
    """Pull every non-completed Linear issue in the team, paginated.

    The --days-back arg is honoured via client-side filter on updatedAt;
    passing it as a GraphQL filter would require timezone-correct TimelessDateTime.
    """
    query = """
        query Issues($filter: IssueFilter!, $after: String) {
            issues(filter: $filter, first: 100, after: $after) {
                pageInfo { hasNextPage endCursor }
                nodes {
                    id identifier title updatedAt
                    state { name type }
                    labels { nodes { name } }
                    inverseRelations(first: 30) {
                        nodes {
                            type
                            issue { id identifier updatedAt state { name type } labels { nodes { name } } }
                        }
                    }
                }
            }
        }
    """
    variables = {"filter": {"state": {"type": {"neq": "completed"}}}, "after": None}
    from datetime import datetime, timedelta, timezone
    cutoff = datetime.now(timezone.utc) - timedelta(days=days_back)
    out: list[dict] = []
    seen = set()
    for _ in range(10):  # up to 1000 issues
        data = linear_graphql(query, variables)
        page = data.get("data", {}).get("issues", {})
        nodes = page.get("nodes", []) or []
        for n in nodes:
            if n.get("id") in seen:
                continue
            seen.add(n["id"])
            out.append(n)
        pi = page.get("pageInfo", {}) or {}
        if not pi.get("hasNextPage"):
            break
        variables["after"] = pi.get("endCursor")
        if not variables["after"]:
            break
    # client-side date filter
    filtered = []
    for n in out:
        updated = n.get("updatedAt")
        if not updated:
            filtered.append(n); continue
        try:
            u_dt = datetime.fromisoformat(updated.replace("Z", "+00:00"))
        except Exception:
            filtered.append(n); continue
        if u_dt >= cutoff:
            filtered.append(n)
    return filtered


def get_label_names(issue: dict) -> set[str]:
    return {node["name"] for node in issue.get("labels", {}).get("nodes", []) if node.get("name")}


def check_agent_dispatch_consistency(issue: dict) -> list[str]:
    """Return list of reasons the issue's agent/dispatch labels are inconsistent."""
    reasons: list[str] = []
    labels = get_label_names(issue)

    agent_labels = {l for l in labels if l.startswith("agent:")}
    dispatch_labels = {l for l in labels if l.startswith("dispatch:")}

    # Map each agent label to its required dispatch label(s).
    for agent, required_dispatches in AGENT_DISPATCH_PAIRS.items():
        if agent in labels:
            missing = [d for d in required_dispatches if d not in dispatch_labels]
            if missing:
                reasons.append(
                    f"has '{agent}' but missing paired dispatch label(s): {missing}"
                )

    # Reverse direction: dispatch:ready implies some non-paused agent label.
    if "dispatch:ready" in labels:
        agent_labels_no_neutral = agent_labels - NEUTRAL_AGENT_LABELS
        if not agent_labels_no_neutral:
            reasons.append("dispatch:ready but no non-neutral agent:* label")

    return reasons


def check_dispatch_ready_blockers(issue: dict) -> list[str]:
    """If issue is dispatch:ready, all upstream blockers must be completed/marked agent:completed."""
    labels = get_label_names(issue)
    if "dispatch:ready" not in labels:
        return []
    blockers = (
        issue.get("inverseRelations", {})
        .get("nodes", [])
    )
    reasons: list[str] = []
    for rel in blockers:
        # We only inspect "blocks" relations where THIS issue is blocked-by the other.
        if rel.get("type") != "blocking":
            continue
        related = rel.get("issue", {}) or {}
        related_labels = get_label_names(related)
        related_state = (related.get("state", {}) or {}).get("type", "")
        if related_state == "completed":
            continue
        if "agent:completed" in related_labels:
            continue
        reasons.append(
            f"dispatch:ready but upstream blocker {related.get('identifier')} "
            f"is not completed (state={related_state})"
        )
    return reasons


def check_handoff_pending_decisions_for_agent_labels(
    issue: dict, harness_profile_root: Path
) -> list[str]:
    """If agent:needs-human-review is set, the assigned agent must have a pending_decisions entry for this issue."""
    labels = get_label_names(issue)
    if "agent:needs-human-review" not in labels:
        return []

    # Look up the assigned agent profile name from agent:* label.
    agent_label = next((l for l in labels if l.startswith("agent:")), None)
    if not agent_label or agent_label.startswith("agent:needs-"):
        return []  # not an "owned" issue
    assigned = agent_label.split(":", 1)[1]
    profile_root = harness_profile_root
    candidate = profile_root.parent / assigned
    if not candidate.exists():
        return []  # not a real profile; no handoff expected here
    handoff_path = candidate / "state" / "current.json"
    if not handoff_path.exists():
        return [f"agent:needs-human-review but no handoff at {handoff_path}"]
    try:
        handoff = json.loads(handoff_path.read_text())
    except Exception as exc:
        return [f"agent:needs-human-review but handoff unreadable: {exc}"]

    decisions = handoff.get("pending_decisions_for_human", []) or []
    identifier = issue.get("identifier", "")
    matched = any(identifier in (d.get("question") or "") for d in decisions)
    if not matched:
        return [
            f"agent:needs-human-review on {identifier} but no matching "
            "pending_decisions_for_human[] entry in agent handoff"
        ]
    return []


def default_harness_profile_root() -> Path:
    home = Path.home()
    return home / ".hermes" / "profiles" / DEFAULT_HARNESS_PROFILE


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--team", default=os.environ.get("LINEAR_TEAM", DEFAULT_TEAM))
    parser.add_argument("--days-back", type=int, default=int(os.environ.get("LINEAR_DAYS_BACK", "30")))
    parser.add_argument("--json", action="store_true", help="emit JSON output")
    parser.add_argument("--harness-profile-root", default=None)
    args = parser.parse_args(argv)

    harness_root = (
        Path(args.harness_profile_root).expanduser().resolve()
        if args.harness_profile_root
        else default_harness_profile_root()
    )

    try:
        issues = fetch_team_issues(args.team, args.days_back)
    except Exception as exc:
        if args.json:
            print(json.dumps({"verdict": "ERROR", "reason": str(exc)}, indent=2))
        else:
            print(f"ERROR: failed to fetch Linear issues: {exc}", file=sys.stderr)
        return 2

    inconsistencies: list[dict] = []
    for issue in issues:
        identifier = issue.get("identifier", issue.get("id", "?"))
        reasons = []
        reasons += check_agent_dispatch_consistency(issue)
        reasons += check_dispatch_ready_blockers(issue)
        reasons += check_handoff_pending_decisions_for_agent_labels(issue, harness_root)
        if reasons:
            inconsistencies.append({
                "identifier": identifier,
                "title": issue.get("title", ""),
                "state": (issue.get("state", {}) or {}).get("name", ""),
                "labels": sorted(get_label_names(issue)),
                "reasons": reasons,
            })

    verdict = "PASS" if not inconsistencies else "FAIL"

    if args.json:
        print(json.dumps({
            "verdict": verdict,
            "team": args.team,
            "issues_scanned": len(issues),
            "inconsistencies": inconsistencies,
        }, indent=2))
    else:
        print(f"verdict: {verdict}")
        print(f"issues_scanned: {len(issues)}")
        print(f"inconsistencies: {len(inconsistencies)}")
        for inc in inconsistencies:
            print(f"  - {inc['identifier']}: {inc['title']}")
            for r in inc["reasons"]:
                print(f"      • {r}")

    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
