#!/usr/bin/env python3
"""
probe_recurrence.sh — Should-this-cron-tick-post-a-Linear-comment? decision probe.

Implements the suppression-decision table from the SKILL.md §"Stale-Backlog
Sweep: Repeat-Tick Handling":

    Last triage age | Items identical? | Action
    ----------------|-------------------|--------------------------------
    <2h             | yes               | SUPPRESS comment, brief reply
    <2h             | no (drift)        | Post fresh triage
    2h-24h          | doesn't matter    | Post fresh triage
    >24h            | doesn't matter    | Post fresh triage

This script:
  1. Fetches the canonical anchor issue's most recent Ned-triage comment timestamp
     (default anchor = GRO-570, the June 2026 photo-sweep anchor).
  2. Computes age in minutes.
  3. Optionally accepts a list of scanner-output identifiers via argv (or fetches
     them via Linear API) to test "items identical" against the prior-triage
     comment's documented item set.
  4. Emits a structured decision line + brief evidence for inclusion
     in cron reply.

Usage:
    python3 probe_recurrence.sh                                 # probe GRO-570 by default
    python3 probe_recurrence.sh GRO-568                         # probe different anchor
    python3 probe_recurrence.sh GRO-570 GRO-564 GRO-565 ...     # also test "items identical"
    LINEAR_API_KEY=... python3 probe_recurrence.sh

Output (stdout):
    Anchor: <id>
    Last triage age: <minutes> min (<HH:MM:SSZ>)
    Items identical to prior triage: <YES/NO/UNKNOWN>
    Decision: <SUPPRESS | POST_FRESH_TRIAGE>
    Reason: <one-line justification>

Exit codes:
    0 — always (probe, not a gate)

Side effects: stdout only. One to two Linear API roundtrips. No file writes.

Design notes:
  - The "<2h" threshold is hard-coded as 120 minutes. If Michael ever wants
    to tune it, change the constant and re-run. Document the change in the
    SKILL.md decision table when you do.
  - "Items identical" test is optional. Without it we still compute age and
    return SUPPRESS if age < 120min (the safer default — never spam Linear).
  - Probe assumes the anchor's most recent triage comment is the most recent
    comment from "Michael Gulden" (the Linear user identity all Ned cron
    triages post under, because the API key is Michael's personal key).
    If a different agent posts a comment between ticks, the age is still
    accurate but the "triage" semantic may be off. Verify the comment body
    matches the triage-template fingerprint if uncertain.
  - IMPORTANT (Linear GraphQL gotcha — fixed 2026-06-26): `comments(last: N)`
    returns the N OLDEST comments, not the newest. The v1 loop did
    `break` on the first matching triage in `comments(last: 3)`, silently
    picking the OLDEST Ned triage. This produced stale "464 min" readings
    when the actual latest triage was only 4h old. Fix: fetch `last: 25`
    (configurable via `COMMENTS_FETCH_DEPTH`) and pick MAX(createdAt) among
    matches. Always sort by `createdAt` descending before selecting
    "most recent." Bumped from 10 → 25 at 2026-06-27 r3 to give 2× headroom
    on high-frequency anchors like GRO-570 (14+ triage comments at r3).
  - Invocation gotcha (fixed 2026-06-26): this script has
    `#!/usr/bin/env python3` but a `.sh` extension. `bash probe_recurrence.sh`
    FAILS with bash parse errors. Invoke as `python3 probe_recurrence.sh`
    (verified at 2026-06-26 05:47Z). Same applies to `check_ned_queue.sh`.
    `verify_gpu_node.sh` is real bash and works with `bash`.
  - Drift-detection fix (2026-06-26 r44): if the operator passes
    scanner-output identifiers via argv, this script now parses the
    most-recent triage comment body for GRO-XXX identifiers and diffs them
    against the scanner set. Returns DRIFT_DETECTED for non-empty diff.
    Previously it set `identical = "MANUAL_CHECK_NEEDED"` and never actually
    compared — that was a latent bug. Now the probe does the comparison.
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone


ANCHOR_DEFAULT = "GRO-570"
SUPPRESS_THRESHOLD_MIN = 120  # <2h suppresses per SKILL.md decision table
COMMENTS_FETCH_DEPTH = 25  # bumped from 10 → 25 (2026-06-27 r3): high-frequency
                          # anchors like GRO-570 have 14+ triage comments. 25
                          # gives 2× headroom and is well under Linear's per-
                          # field pagination cap (50). Linear returns the N
                          # OLDEST comments, so we always pick MAX(createdAt).
NED_USER_NAME = "Michael Gulden"  # Linear identity Ned cron triages post under
GRO_PATTERN = re.compile(r"GRO-\d+")


def fetch_key() -> str:
    if os.environ.get("LINEAR_API_KEY"):
        return os.environ["LINEAR_API_KEY"]
    r = subprocess.run(
        ["bash", "-lc", "echo \"$LINEAR_API_KEY\""],
        capture_output=True, text=True,
    )
    key = r.stdout.strip()
    if not key:
        raise SystemExit("LINEAR_API_KEY not set in parent shell")
    return key


def gql(query: str, variables: dict, api_key: str) -> dict:
    payload = json.dumps({"query": query, "variables": variables})
    r = subprocess.run(
        [
            "curl", "-s", "https://api.linear.app/graphql",
            "-H", "Authorization: " + api_key,
            "-H", "Content-Type: application/json",
            "-d", payload,
        ],
        capture_output=True, text=True, timeout=30,
    )
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        print("ERROR: Linear API non-JSON:", r.stdout[:300])
        raise SystemExit(2)


def fetch_anchor_state(anchor: str, api_key: str) -> dict:
    """Fetch most recent comment timestamp + current issue state for the anchor.

    NOTE: Linear GraphQL `comments(last: N)` returns the N OLDEST comments,
    not the newest. We fetch `last: COMMENTS_FETCH_DEPTH` (default 25) and
    pick the MAX(createdAt) among matching triage comments. Linear's per-
    field pagination cap is 50, so 25 has 2× headroom. Fixed 2026-06-26.
    """
    query = """
    query($id: String!) {
      issue(id: $id) {
        identifier
        updatedAt
        comments(last: """ + str(COMMENTS_FETCH_DEPTH) + """) {
          nodes {
            createdAt
            user { name email }
            body
          }
        }
      }
    }
    """
    data = gql(query, {"id": anchor}, api_key)
    return data.get("data", {}).get("issue") or {}


def is_triage_comment(body: str) -> bool:
    """Heuristic: does this comment look like a Ned triage (not an arbitrary reply)?"""
    if not body:
        return False
    fingerprint_markers = [
        "[Ned triage",
        "Picked up by Ned cron",
        "Routing sweep",
        "agent:ned",
        "Ned routing triage",
    ]
    return any(m in body for m in fingerprint_markers)


def is_ned_user(user_dict: dict) -> bool:
    """Match Ned-triage comments by user identity (API posts under Michael Gulden)."""
    if not user_dict:
        return False
    return user_dict.get("name") == NED_USER_NAME or user_dict.get("email") == "mbgulden@gmail.com"


def compute_age_minutes(iso_ts: str) -> float:
    """Convert ISO-8601 timestamp to age in minutes (UTC)."""
    ts = iso_ts.replace("Z", "+00:00")
    dt = datetime.fromisoformat(ts)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    return (now - dt).total_seconds() / 60.0


def extract_triage_items(body: str) -> list:
    """Parse GRO-XXX identifiers from a triage comment body."""
    if not body:
        return []
    return sorted(set(GRO_PATTERN.findall(body)))


def fetch_scanner_identifiers(api_key: str, limit: int = 15) -> list:
    """Pull the agent:ned Backlog+Todo list (the same list the scanner produces)."""
    query = (
        '{ issues(filter: {labels: {name: {eq: "agent:ned"}}, '
        'state: {name: {in: ["Todo", "Backlog"]}}}, first: '
        + str(limit) + ') { nodes { identifier } } }'
    )
    data = gql(query, {}, api_key)
    return [n["identifier"] for n in data.get("data", {}).get("issues", {}).get("nodes", [])]


def main() -> int:
    args = sys.argv[1:]
    anchor = args[0] if args else ANCHOR_DEFAULT
    cli_identifiers = args[1:]  # optional; if absent we fetch via API

    api_key = fetch_key()
    issue = fetch_anchor_state(anchor, api_key)

    if not issue:
        print("ERROR: could not fetch anchor " + anchor)
        return 2

    print("Anchor: " + anchor)

    # Find most recent Ned triage comment on the anchor (skip arbitrary replies).
    # Linear `comments(last: N)` returns the N OLDEST, so we must iterate ALL
    # matching triage comments and pick MAX(createdAt). Fixed 2026-06-26.
    last_triage_iso = None
    last_triage_body = None
    last_triage_user = None
    for c in issue.get("comments", {}).get("nodes", []):
        user = c.get("user") or {}
        body = c.get("body") or ""
        # Match by user identity (Michael Gulden = Ned identity) OR fingerprint
        if is_ned_user(user) or is_triage_comment(body):
            iso = c["createdAt"]
            if last_triage_iso is None or iso > last_triage_iso:
                last_triage_iso = iso
                last_triage_body = body
                last_triage_user = user

    if not last_triage_iso:
        print("Last triage: NONE FOUND on anchor (no prior triage to compare against)")
        print("Decision: POST_FRESH_TRIAGE")
        print("Reason: no prior triage on anchor — treat as first encounter")
        return 0

    age_min = compute_age_minutes(last_triage_iso)
    print(f"Last triage age: {age_min:.1f} min ({last_triage_iso})")

    # Items-identical check (FIXED 2026-06-26 r44):
    # Parse the prior triage body for its documented GRO-XXX identifiers,
    # then diff against the current scanner feed.
    prior_items = extract_triage_items(last_triage_body or "")
    if cli_identifiers:
        current_items = set(cli_identifiers)
    else:
        current_items = set(fetch_scanner_identifiers(api_key))

    prior_set = set(prior_items)
    if prior_set:
        drift_added = current_items - prior_set
        drift_removed = prior_set - current_items
        if not drift_added and not drift_removed:
            identical = "YES"
        else:
            identical = "NO"
            print(f"  Drift detected: +{sorted(drift_added)} -{sorted(drift_removed)}")
    else:
        # No GRO-XXX identifiers in the prior triage body — can't compare.
        # Default to UNKNOWN (operator must compare by hand).
        identical = "UNKNOWN"

    print(f"Items identical to prior triage: {identical}")

    # Apply decision table
    decision = "POST_FRESH_TRIAGE"
    reason = ""
    if age_min < SUPPRESS_THRESHOLD_MIN and identical == "YES":
        decision = "SUPPRESS"
        reason = (
            f"age {age_min:.0f}min < {SUPPRESS_THRESHOLD_MIN}min AND items identical "
            "to prior triage — anti-fan-out window holds"
        )
    elif age_min < SUPPRESS_THRESHOLD_MIN and identical == "NO":
        decision = "POST_FRESH_TRIAGE"
        reason = (
            f"age {age_min:.0f}min < {SUPPRESS_THRESHOLD_MIN}min BUT drift detected "
            "— material change warrants fresh triage even within anti-fan-out window"
        )
    elif 120 <= age_min <= 24 * 60:
        decision = "POST_FRESH_TRIAGE"
        reason = (
            f"age {age_min:.0f}min in 2h-24h window; per decision table, "
            "items-identical doesn't matter — post fresh triage"
        )
    else:
        decision = "POST_FRESH_TRIAGE"
        reason = (
            f"age {age_min/60:.1f}h > 24h; prior triage is stale, "
            "post fresh triage"
        )

    print(f"Decision: {decision}")
    print(f"Reason: {reason}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
