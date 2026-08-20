#!/usr/bin/env python3
"""
anchor_5a5_item3_scorer.py — verify 5a.5 item [3] for Batch B (and similar recurring batches).

Codified 2026-06-29 ~14:30Z after a cron pass where the most recent anchor comment
on GRO-485 was just a `## Ned finalization report` boilerplate (lane-map only,
no full 10-ID name list, no standing cure) and I had to walk the comment
history to find the most recent qualifying "anchor pass N" comment.

5a.5 item [3] (verbatim from references/batch-b-phase1-activeoahu-detector.md):

  3. That prior note already names every issue in the batch + correct lane
     mapping + standing cure.

This script operationalizes that check by walking ALL comments on the anchor
issue, scoring each one against three flags:
  - names_all_batch_ids : ALL batch-B IDs appear in the body (case-insensitive)
  - has_standing_cure   : body contains "relabel" / "patch" / "ned_delta_dispatcher"
                         / "fix the dispatcher" / "standing cure" / "patch the"
  - has_lane_map        : body contains "agent:" (lane label vocabulary)

Then it picks the MOST RECENT comment that satisfies all three AND is <6h old.
That comment is the canonical 5a.5 anchor for the day; finalize_task.sh must
not run; the response is [SILENT].

This is intentionally Batch-B-shaped but trivially parameterized: pass
--anchor and --batch-ids for other recurring batches.

Usage:
    LINEAR_API_KEY=... python3 anchor_5a5_item3_scorer.py \
        --anchor GRO-485 \
        --batch-ids GRO-484,GRO-485,GRO-486,GRO-487,GRO-488,GRO-490,GRO-492,GRO-499,GRO-500,GRO-502 \
        --age-threshold-hours 6

Output (JSON):
    {
      "5a5_item3_satisfied": true|false,
      "qualifying_comment": {
        "createdAt": "...",
        "age_hours": 2.44,
        "names_all_batch_ids": true,
        "has_standing_cure": true,
        "has_lane_map": true,
        "body_preview": "..."
      } | null,
      "all_comments": [
        {"createdAt": "...", "age_hours": 1.01, "names_all_batch_ids": false,
         "has_standing_cure": false, "has_lane_map": true, "qualifies": false},
        ...
      ],
      "verdict": "SILENT|FULL_REPORT",
      "rationale": "..."
    }

Invocation gotchas:
  1. ALWAYS prefix with `python3` (the file is NOT chmod +x'd).
  2. `--batch-ids` is comma-separated, NO spaces.
  3. LINEAR_API_KEY must be sourced before invocation; this script does not
     read ~/.hermes env files. (The agent's terminal typically already has it
     loaded; if not, source /home/ubuntu/.hermes/profiles/orchestrator/.env first.)

The script is read-only. It does not post comments or mutate state. The
agent reads the JSON, applies judgment, and delivers [SILENT] or a full
report per the verdict.
"""

import argparse
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone

# Phrase vocabularies (all lowercased before match). Adding new phrases here
# widens the standing-cure / lane-map detectors; trim aggressively because a
# loose detector produces false positives (which suppress execution when the
# agent should actually act).
STANDING_CURE_PHRASES = [
    "relabel",
    "patch",
    "ned_delta_dispatcher",
    "fix the dispatcher",
    "standing cure",
    "patch the",
    "fix the scanner",
]


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def gql(token: str, query: str, variables: dict = None) -> dict:
    req = urllib.request.Request(
        "https://api.linear.app/graphql",
        data=json.dumps({"query": query, "variables": variables or {}}).encode(),
        headers={"Authorization": token, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())


def score_comment(comment: dict, batch_ids: list[str], now: datetime) -> dict:
    """Return scoring flags for a single comment."""
    body = comment.get("body") or ""
    body_lc = body.lower()
    created_at = comment.get("createdAt", "")
    try:
        created_dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        age_h = (now - created_dt).total_seconds() / 3600
    except Exception:
        age_h = None
    names_all = all(iid.lower() in body_lc for iid in batch_ids)
    has_cure = any(p in body_lc for p in STANDING_CURE_PHRASES)
    has_lane_map = "agent:" in body_lc
    return {
        "createdAt": created_at,
        "age_hours": round(age_h, 2) if age_h is not None else None,
        "names_all_batch_ids": names_all,
        "has_standing_cure": has_cure,
        "has_lane_map": has_lane_map,
        "body_preview": body[:200].replace("\n", " "),
    }


def main():
    ap = argparse.ArgumentParser(
        description="Score anchor-issue comments against 5a.5 item [3] for SUPPRESS eligibility."
    )
    ap.add_argument("--anchor", required=True, help="Anchor issue ID, e.g. GRO-485")
    ap.add_argument(
        "--batch-ids",
        required=True,
        help="Comma-separated issue IDs in the recurring batch (NO spaces)",
    )
    ap.add_argument(
        "--age-threshold-hours",
        type=float,
        default=6.0,
        help="Max age (h) for a qualifying comment. Default 6.0.",
    )
    args = ap.parse_args()

    token = os.environ.get("LINEAR_API_KEY")
    if not token:
        print(json.dumps({"error": "LINEAR_API_KEY not set"}))
        sys.exit(1)

    batch_ids = [s.strip() for s in args.batch_ids.split(",") if s.strip()]
    now = now_utc()

    # Fetch all comments on the anchor (last 25 should be plenty for a daily recurrence)
    d = gql(
        token,
        '{ issue(id: "%s") { identifier comments(last: 25) { nodes { body createdAt } } } }'
        % args.anchor,
    )
    issue = d.get("data", {}).get("issue")
    if not issue:
        print(json.dumps({"error": "anchor issue not found: %s" % args.anchor}))
        sys.exit(1)

    comments = issue.get("comments", {}).get("nodes", [])
    # Sort newest first
    comments_sorted = sorted(comments, key=lambda c: c.get("createdAt", ""), reverse=True)

    scored = [score_comment(c, batch_ids, now) for c in comments_sorted]
    for s in scored:
        s["qualifies"] = (
            s["names_all_batch_ids"]
            and s["has_standing_cure"]
            and s["has_lane_map"]
            and s["age_hours"] is not None
            and s["age_hours"] < args.age_threshold_hours
        )

    # Most recent qualifying comment
    qualifying = next((s for s in scored if s["qualifies"]), None)
    item3_satisfied = qualifying is not None

    verdict = "SILENT" if item3_satisfied else "FULL_REPORT"
    if item3_satisfied:
        rationale = (
            f"5a.5 item [3] satisfied: anchor {args.anchor} comment at "
            f"{qualifying['createdAt']} ({qualifying['age_hours']}h old) names "
            f"all {len(batch_ids)} batch IDs, includes standing cure, includes lane map."
        )
    else:
        rationale = (
            f"5a.5 item [3] NOT satisfied: no comment on {args.anchor} within "
            f"{args.age_threshold_hours}h satisfies all three flags. Need to post "
            f"a consolidated anchor acknowledgment before re-evaluating SUPPRESS."
        )

    out = {
        "anchor": args.anchor,
        "batch_ids": batch_ids,
        "age_threshold_hours": args.age_threshold_hours,
        "5a5_item3_satisfied": item3_satisfied,
        "qualifying_comment": qualifying,
        "all_comments_scored": scored,
        "verdict": verdict,
        "rationale": rationale,
        "evaluated_at": now.isoformat(),
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()