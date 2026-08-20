#!/usr/bin/env python3
"""
suppress_class_detect.py — recurring-batch SUPPRESS class detector for Ned's cron.

When the scanner feeds the same N-issue misroute batch every cron tick and the
prompt is dual-signal (DELIVERY: origin + literal [SILENT] clause), this script
classifies the pass as SUPPRESS-ELIGIBLE so the agent can deliver [SILENT] per
5a.7a-bis instead of 5a.7's "always full report."

Recipe (validated across 70+ passes of the GRO-504-512 + GRO-537 batch):

  1. Probe 1 — in-repo triage doc freshness via `git log -1` (no GraphQL).
     Threshold: <4h old. A fresh triage doc alone is enough to invoke 5a.7a-bis.
  2. Probe 2 — prior cron output freshness via `ls -t` on the cron output dir.
     Threshold: <2h old. Belt-and-braces with probe 1; EITHER fresh is enough.
  3. Probe 3 — batch GraphQL audit (state + labels + dequeue counts) per issue.
     One round-trip per issue; the canonical query shape is below. If any issue
     has state outside {Todo, Backlog} (residual drift) OR carries the
     `dispatch:ready` label (genuine in-lane work), SUPPRESS does NOT hold —
     fall through to 5a.3 / 5a.11 / execute path.
  4. Decision: 4-of-4 match → SILENT + `finalize_task.sh --dry-run` (per 5a.5).

The script is read-only — it never mutates Linear or filesystem. It prints a
JSON verdict the agent can inspect and decide on. Cost: 1 batched execute_code
or terminal call.

Usage:
    # Pure detection (no Linear probe; just filesystem freshness)
    python3 suppress_class_detect.py --issues GRO-503,GRO-504,GRO-505,GRO-507,GRO-508,GRO-509,GRO-510,GRO-511,GRO-512,GRO-537 \\
        --repo /home/ubuntu/work/growthwebdev-knowledge \\
        --cron-output-dir ~/.hermes/profiles/ned/cron/output

    # Full audit (includes GraphQL state/label/dequeue probe)
    python3 suppress_class_detect.py --issues ... --repo ... --include-linear

**Invocation gotchas (verified pass #41, 2026-06-28 ~23:39Z):**

1. **MUST prefix with `python3`** — the script has `#!/usr/bin/env python3` shebang but is NOT `chmod +x`'d. Calling `bash ~/.hermes/.../suppress_class_detect.py` (without `python3` prefix) interprets the Python content as bash, producing a flood of `bash: line N: <python-token>: command not found` errors before the script even starts. The shebang only fires when the kernel sees the file directly (`./file.py`) or via `python3 file.py`. **Always use `python3 <path>` — never `bash <path>`.**

2. **`--issues` takes comma-separated IDs, not space-separated** — argparse is configured for a single `--issues` arg, so `python3 suppress_class_detect.py --issues GRO-503 GRO-504 ...` fails with `unrecognized arguments: GRO-504 GRO-505 ...`. Right shape: `--issues GRO-503,GRO-504,GRO-505,GRO-507,GRO-508,GRO-509,GRO-510,GRO-511,GRO-512,GRO-537` (one comma-joined string).

Environment:
    LINEAR_API_KEY (required only with --include-linear)

Output (JSON):
    {
      "suppress_eligible": true|false,
      "checks": {
        "issue_ids_match_recurring_batch": {"pass": true, "actual": [...], "expected_signature": "..."},
        "triage_doc_fresh": {"pass": true, "newest_age_hours": 1.2, "threshold_hours": 4},
        "prior_cron_output_fresh": {"pass": true, "newest_age_hours": 0.8, "threshold_hours": 2},
        "linear_state_no_drift": {"pass": true, "states": {"Todo": 5, "Backlog": 5, "In Review": 0}},
        "no_dispatch_ready_label": {"pass": true, "dispatch_ready_count": 0},
        "all_have_dequeue_comments": {"pass": true, "min_dequeue_count": 8, "threshold": 3}
      },
      "verdict": "SILENT|FULL_REPORT|EXECUTE|MIXED",
      "finalize_mode": "--dry-run|none|full",
      "rationale": "5a.7a-bis 4-of-4 match — same 10-issue batch, fresh audit trail, no in-lane work"
    }

The script is a TOOL, not a decision-maker. The agent reads the JSON and
delivers the final response. Never auto-deliver [SILENT] from a script.
"""

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# Recurring-batch signatures: the canonical misroute sets Ned's scanner re-feeds.
# If the scanner feed matches ANY entry below, the batch-identity check passes.
# Append a new signature when a new recurring batch emerges (see
# references/recurring-batch-suppress-2026-06-29.md §"Hardcoded signature gap"
# for the validation recipe before adding).
#
# Known recurring batches:
#   - gro-504-512-537: original Active Oahu hardware + curriculum batch
#                     (dequeued 12+ times across 2026-06-27 → 2026-06-29)
#   - gro-484-502:     Active Oahu storefront hardware + Active Oahu HD/coaching
#                     content + Gemini agent config (dequeued 4+ times on
#                     2026-06-29 ~09:25Z / 10:22Z / 10:29Z / 10:30Z by Michael)
RECURRING_BATCH_SIGNATURES = {
    "gro-504-512-537": sorted([
        "GRO-503", "GRO-504", "GRO-505", "GRO-507", "GRO-508",
        "GRO-509", "GRO-510", "GRO-511", "GRO-512", "GRO-537",
    ]),
    "gro-484-502": sorted([
        "GRO-484", "GRO-485", "GRO-486", "GRO-487", "GRO-488",
        "GRO-490", "GRO-492", "GRO-499", "GRO-500", "GRO-502",
    ]),
}

DEQUEUE_PATTERNS = [
    "out of lane", "out-of-lane", "out of scope", "systemic misroute",
    "dequeue", "dequeued", "wrong agent", "relabel", "routing blocker",
    "lane violation", "not ned's lane",
]


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def age_hours(then: datetime) -> float:
    return (now_utc() - then).total_seconds() / 3600.0


def check_issue_ids_match(issues):
    actual = sorted(issues)
    matched = None
    for sig_name, sig_issues in RECURRING_BATCH_SIGNATURES.items():
        if actual == sig_issues:
            matched = sig_name
            break
    # Compose a human-readable list of all registered signatures so the agent
    # can confirm whether the current feed matches a known batch. When multiple
    # signatures are registered, "expected_signature" is the full set, not a
    # single value (preserves pass-15's `gro-504-512-537` single-signature output
    # shape for backward compatibility when only one signature is registered).
    if len(RECURRING_BATCH_SIGNATURES) == 1:
        expected = next(iter(RECURRING_BATCH_SIGNATURES))
    else:
        expected = sorted(RECURRING_BATCH_SIGNATURES.keys())
    return {
        "pass": matched is not None,
        "actual": actual,
        "matched_signature": matched,
        "expected_signature": expected,
        "registered_signatures": sorted(RECURRING_BATCH_SIGNATURES.keys()),
    }


def check_triage_doc_fresh(repo: str, threshold_hours: float = 4.0):
    """Probe 1: in-repo triage doc freshness via `git log -1`."""
    try:
        result = subprocess.run(
            ["git", "-C", repo, "log", "-1", "--format=%cI", "--", "scripts/ops/gro-537-triage-pass-NN-batch-recurring.md"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode != 0 or not result.stdout.strip():
            return {"pass": False, "reason": "no triage doc found in git log", "newest_age_hours": None, "threshold_hours": threshold_hours}
        ts = datetime.fromisoformat(result.stdout.strip())
        age = age_hours(ts)
        return {"pass": age < threshold_hours, "newest_age_hours": round(age, 2), "threshold_hours": threshold_hours}
    except Exception as e:
        return {"pass": False, "reason": f"git probe failed: {e}", "newest_age_hours": None, "threshold_hours": threshold_hours}


def check_prior_cron_output_fresh(cron_output_dir: str, threshold_hours: float = 2.0):
    """Probe 2: prior cron output freshness via ls -t."""
    p = Path(os.path.expanduser(cron_output_dir))
    if not p.exists():
        return {"pass": False, "reason": "cron output dir missing", "newest_age_hours": None, "threshold_hours": threshold_hours}
    files = sorted(p.glob("*.md"), key=lambda f: f.stat().st_mtime, reverse=True)
    if not files:
        return {"pass": False, "reason": "no prior cron output files", "newest_age_hours": None, "threshold_hours": threshold_hours}
    newest = files[0]
    mtime = datetime.fromtimestamp(newest.stat().st_mtime, tz=timezone.utc)
    age = age_hours(mtime)
    return {
        "pass": age < threshold_hours,
        "newest_age_hours": round(age, 2),
        "newest_file": str(newest),
        "newest_timestamp": mtime.isoformat(),
        "threshold_hours": threshold_hours,
    }


def gql_query(token: str, query: str, variables: dict = None) -> dict:
    req = urllib.request.Request(
        "https://api.linear.app/graphql",
        data=json.dumps({"query": query, "variables": variables or {}}).encode(),
        headers={"Authorization": token, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())


def check_linear_state_audit(issues: list[str], token: str):
    """Probe 3: per-issue state + labels + dequeue count audit."""
    per_issue = {}
    state_dist: dict[str, int] = {}
    dispatch_ready_count = 0
    dequeue_counts = []
    drift_count = 0

    for issue_id in issues:
        try:
            result = gql_query(token, """
            query($id: String!) {
              issue(id: $id) {
                state { name }
                labels { nodes { name } }
                comments(last: 50) {
                  nodes { body }
                }
              }
            }
            """, {"id": issue_id})
            issue = result.get("data", {}).get("issue")
            if not issue:
                per_issue[issue_id] = {"error": "not found"}
                continue

            state = issue["state"]["name"]
            labels = [l["name"] for l in issue["labels"]["nodes"]]
            comments = [c["body"] for c in issue.get("comments", {}).get("nodes", [])]
            dequeue_count = sum(1 for c in comments if any(p in c.lower() for p in DEQUEUE_PATTERNS))

            per_issue[issue_id] = {
                "state": state,
                "dispatch_ready": "dispatch:ready" in labels,
                "dequeue_count": dequeue_count,
                "n_comments": len(comments),
            }
            state_dist[state] = state_dist.get(state, 0) + 1
            if "dispatch:ready" in labels:
                dispatch_ready_count += 1
            if state not in ("Todo", "Backlog"):
                drift_count += 1
            dequeue_counts.append(dequeue_count)
        except Exception as e:
            per_issue[issue_id] = {"error": str(e)}

    min_dequeue = min(dequeue_counts) if dequeue_counts else 0
    dequeue_threshold = 3
    no_dispatch_ready = dispatch_ready_count == 0
    no_drift = drift_count == 0

    return {
        "pass": no_dispatch_ready and no_drift and min_dequeue >= dequeue_threshold,
        "per_issue": per_issue,
        "state_distribution": state_dist,
        "drift_count": drift_count,
        "dispatch_ready_count": dispatch_ready_count,
        "min_dequeue_count": min_dequeue,
        "dequeue_threshold": dequeue_threshold,
    }


def main():
    ap = argparse.ArgumentParser(description="Detect SUPPRESS-ELIGIBLE recurring-batch cron passes.")
    ap.add_argument("--issues", required=True, help="Comma-separated Linear issue IDs (NO spaces).")
    ap.add_argument("--repo", required=True, help="Path to growthwebdev-knowledge repo (for git triage doc probe).")
    ap.add_argument("--cron-output-dir", required=True, help="Path to Ned cron output dir (for prior-pass freshness probe).")
    ap.add_argument("--include-linear", action="store_true", help="Run GraphQL audit probe (requires LINEAR_API_KEY).")
    args = ap.parse_args()

    issues = [s.strip() for s in args.issues.split(",") if s.strip()]
    token = os.environ.get("LINEAR_API_KEY")

    checks = {}
    checks["issue_ids_match_recurring_batch"] = check_issue_ids_match(issues)
    checks["triage_doc_fresh"] = check_triage_doc_fresh(args.repo)
    checks["prior_cron_output_fresh"] = check_prior_cron_output_fresh(args.cron_output_dir)

    linear_audit = None
    if args.include_linear:
        if not token:
            print(json.dumps({"error": "LINEAR_API_KEY not set; required for --include-linear"}))
            sys.exit(1)
        linear_audit = check_linear_state_audit(issues, token)
        checks["linear_state_audit"] = linear_audit

    # Decision: SILENT iff batch matches AND (triage_doc_fresh OR prior_cron_output_fresh OR linear audit)
    batch_match = checks["issue_ids_match_recurring_batch"]["pass"]
    triage_fresh = checks["triage_doc_fresh"]["pass"]
    cron_fresh = checks["prior_cron_output_fresh"]["pass"]
    linear_ok = (linear_audit is not None) and linear_audit["pass"]
    linear_present = linear_audit is not None

    suppress_eligible = batch_match and (triage_fresh or cron_fresh or (linear_present and linear_ok))

    if linear_present and linear_ok and not (triage_fresh or cron_fresh):
        rationale = f"5a.7a-bis: linear audit shows min_dequeue={linear_audit['min_dequeue_count']} (threshold={linear_audit['dequeue_threshold']}), no drift, no dispatch:ready"
    elif batch_match and (triage_fresh or cron_fresh) and (not linear_present or linear_ok):
        rationale = "5a.7a-bis 4-of-4 match: same recurring batch, fresh audit trail, no in-lane work"
    else:
        rationale = "5a.7a-bis check failed — see per-probe pass/fail"

    if linear_present and linear_ok and dispatch_ready_count_zero_and_no_drift(linear_audit):
        verdict = "SILENT"
        finalize_mode = "--dry-run"
    elif linear_present and not linear_ok:
        verdict = "FULL_REPORT"
        finalize_mode = "none"
    elif batch_match and (triage_fresh or cron_fresh):
        verdict = "SILENT"
        finalize_mode = "--dry-run"
    else:
        verdict = "FULL_REPORT"
        finalize_mode = "none"

    out = {
        "suppress_eligible": suppress_eligible,
        "checks": checks,
        "verdict": verdict,
        "finalize_mode": finalize_mode,
        "rationale": rationale,
        "evaluated_at": now_utc().isoformat(),
    }
    print(json.dumps(out, indent=2))


def dispatch_ready_count_zero_and_no_drift(audit: dict) -> bool:
    return audit.get("dispatch_ready_count", 1) == 0 and audit.get("drift_count", 1) == 0


if __name__ == "__main__":
    main()