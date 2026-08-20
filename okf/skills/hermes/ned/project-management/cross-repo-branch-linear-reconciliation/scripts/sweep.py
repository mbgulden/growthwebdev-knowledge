#!/usr/bin/env python3
"""
Template: cross-repo agent-prefix branch discovery + tip-dedup + Linear correlation sweep.

This is the second-pass script for the cross-repo-branch-linear-reconciliation skill.
It does NOT delete branches. It produces an inventory report.

Usage:
    AGENT_PREFIX=ned REPO_ROOTS=/home/ubuntu/work LINEAR_SAMPLE=80 python3 /tmp/sweep.py

Output:
    Prints to stdout. Writes a structured JSON to the path given by --out (default
    /tmp/cross_repo_branch_inventory.json).

Requires:
    git CLI on PATH.
    LINEAR_API_KEY env var for the Linear correlation phase.
    Python 3.9+ for subprocess timeout and f-strings.
"""
# This is a TEMPLATE -- copy, edit, run. Do not import as a module.
import argparse
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone

# ---- 1. Repo discovery ----

def find_git_dirs(root, max_depth):
    """Find .git directories under root, up to max_depth.

    PITFALL: in os.walk, you must check `if .git in dirnames` BEFORE
    mutating `dirnames` to exclude .git. Otherwise the check always fails.
    """
    repos = []
    for dirpath, dirnames, filenames in os.walk(root):
        depth = dirpath[len(root):].count(os.sep)
        if depth > max_depth:
            dirnames[:] = []
            continue
        # Check BEFORE filtering
        if ".git" in dirnames:
            repos.append(dirpath)
            dirnames[:] = [d for d in dirnames if d != ".git"]  # don't recurse into .git
        # Prune noisy/non-source roots after the .git check
        dirnames[:] = [d for d in dirnames if d not in {
            ".venv", "venv", "node_modules", "target", "dist", "build", "__pycache__"
        }]
    return repos


# ---- 2. Git helpers ----

def git(args, cwd, timeout=30):
    try:
        result = subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "timeout"
    except Exception as e:
        return -2, "", str(e)


def get_main_branch(repo):
    """Return the main branch name (main or master) or None."""
    for candidate in ("main", "master", "trunk"):
        rc, _, _ = git(["show-ref", "--verify", "--quiet", f"refs/heads/{candidate}"], cwd=repo)
        if rc == 0:
            return candidate
    return None


def find_agent_branches(repo, agent_prefix):
    """Return list of (display_name, full_ref) for every agent-prefix branch.

    Returns LOCAL and REMOTE refs. The display strips "refs/heads/" or "refs/remotes/X/".
    """
    branches = []
    rc, out, _ = git(["for-each-ref", "--format=%(refname)", "refs/heads/"], cwd=repo)
    if rc == 0:
        for line in out.strip().split("\n"):
            line = line.strip()
            if line.startswith(f"refs/heads/{agent_prefix}/"):
                branches.append((line.replace("refs/heads/", ""), line))
    rc, out, _ = git(["for-each-ref", "--format=%(refname)", "refs/remotes/"], cwd=repo)
    if rc == 0:
        for line in out.strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            display = line.replace("refs/remotes/", "")
            if f"/{agent_prefix}/" in display or display.startswith(f"{agent_prefix}/"):
                branches.append((display, line))
    return branches


def batch_tip_shas(repo, refs):
    """Return dict ref -> sha via a single rev-parse batch."""
    if not refs:
        return {}
    rc, out, _ = git(["rev-parse", "--verify"] + refs, cwd=repo)
    if rc != 0:
        return {}
    shas = out.split("\n")
    return dict(zip(refs, shas))


def batch_merged_to_main(repo, refs, main):
    """Return dict ref -> bool.

    For local refs: `git branch --merged <main> --format=%(refname:short)`.
    For remote refs: `git merge-base --is-ancestor <ref> <main>` per ref.

    PITFALL: do not assume that a remote-tracking ref is merged just because a
    local branch with the same short name was merged. The remote tip is the
    remote's tip, not the local's tip.
    """
    if not refs or not main:
        return {r: False for r in refs}
    rc, out, _ = git(["branch", "--merged", main, "--format=%(refname:short)"], cwd=repo)
    merged_set = set(line.strip() for line in out.split("\n") if line.strip()) if rc == 0 else set()
    result = {}
    remote_refs = []
    for r in refs:
        if r.startswith("refs/heads/"):
            short = r.replace("refs/heads/", "")
            result[r] = short in merged_set
        else:
            remote_refs.append(r)
    for r in remote_refs:
        rc, _, _ = git(["merge-base", "--is-ancestor", r, main], cwd=repo)
        result[r] = (rc == 0)
    return result


# ---- 3. Linear helpers ----

def extract_linear_id(branch_name):
    """Extract GRO-XXXX from a branch name (case-insensitive)."""
    m = re.search(r"\b([Gg][Rr][Oo])-?(\d+)", branch_name)
    if m:
        return f"{m.group(1).upper()}-{m.group(2)}"
    return None


def linear_query(query, api_key=None):
    import urllib.request
    if not api_key:
        api_key = os.environ.get("LINEAR_API_KEY")
    if not api_key:
        return None
    body = json.dumps({"query": query}).encode()
    req = urllib.request.Request(
        "https://api.linear.app/graphql",
        data=body,
        headers={"Content-Type": "application/json", "Authorization": api_key},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read())
    except Exception as e:
        return {"errors": [{"message": str(e)}]}


# ---- 4. Main sweep ----

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--agent", default=os.environ.get("AGENT_PREFIX", "ned"),
                    help="agent prefix to scan (default: ned)")
    ap.add_argument("--roots", default=os.environ.get("REPO_ROOTS", "/home/ubuntu/work"),
                    help="comma-separated repo roots to scan")
    ap.add_argument("--max-depth", type=int, default=4)
    ap.add_argument("--linear-sample", type=int,
                    default=int(os.environ.get("LINEAR_SAMPLE", "80")),
                    help="cap on Linear API queries")
    ap.add_argument("--out", default="/tmp/cross_repo_branch_inventory.json")
    args = ap.parse_args()

    roots = [r.strip() for r in args.roots.split(",") if r.strip()]
    repos = []
    for root in roots:
        repos.extend(find_git_dirs(root, args.max_depth))
    print(f"Scanning {len(repos)} repos for '{args.agent}/*' branches...", file=sys.stderr, flush=True)

    per_repo = {}
    all_linear_ids = set()

    for repo in repos:
        rel = repo.replace("/home/ubuntu/work/", "")
        branches = find_agent_branches(repo, args.agent)
        if not branches:
            continue

        main = get_main_branch(repo)
        refs = [r for _, r in branches]

        sha_map = batch_tip_shas(repo, refs)
        tips = defaultdict(list)
        for display, ref in branches:
            sha = sha_map.get(ref)
            if sha:
                tips[sha].append(display)

        merged_map = batch_merged_to_main(repo, refs, main) if main else {r: False for r in refs}

        total = len(branches)
        merged = sum(1 for r in refs if merged_map.get(r, False))
        unmerged = total - merged
        dup_groups = {sha: names for sha, names in tips.items() if len(names) > 1}
        dup_branches = sum(len(names) for names in dup_groups.values())

        for display, ref in branches:
            if not merged_map.get(ref, False):
                lid = extract_linear_id(display)
                if lid:
                    all_linear_ids.add(lid)

        per_repo[rel] = {
            "total": total,
            "merged": merged,
            "unmerged": unmerged,
            "tip_dedup_groups": len(dup_groups),
            "tip_dedup_branches": dup_branches,
        }

    # Linear correlation sample
    sample_ids = sorted(all_linear_ids)[:args.linear_sample]
    by_state = defaultdict(list)
    for lid in sample_ids:
        r = linear_query('{ issue(id: "%s") { identifier state { name } } }' % lid)
        if r and r.get("data") and r["data"].get("issue"):
            state = r["data"]["issue"]["state"]["name"]
            by_state[state].append(lid)

    overall = {
        "total": sum(d["total"] for d in per_repo.values()),
        "merged": sum(d["merged"] for d in per_repo.values()),
        "unmerged": sum(d["unmerged"] for d in per_repo.values()),
        "tip_dedup_groups": sum(d["tip_dedup_groups"] for d in per_repo.values()),
        "tip_dedup_branches": sum(d["tip_dedup_branches"] for d in per_repo.values()),
        "linear_sample_size": len(sample_ids),
        "linear_by_state": {k: len(v) for k, v in by_state.items()},
    }

    out = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "agent_prefix": args.agent,
        "roots": roots,
        "overall": overall,
        "per_repo": per_repo,
        "linear_by_state": {k: v for k, v in by_state.items()},
    }

    with open(args.out, "w") as f:
        json.dump(out, f, indent=2)

    print(f"\n=== OVERALL ===")
    for k, v in overall.items():
        print(f"  {k}: {v}")
    print(f"\nFull report saved to {args.out}")


if __name__ == "__main__":
    main()
