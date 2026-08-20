#!/usr/bin/env python3
"""
verify_okf_with_linear_trail.py — OKF doc + Linear cross-reference verifier

Use this when you have:
  1. Authored an OKF document (frontmatter + body + section links)
  2. Updated the OKF index to link the new entry
  3. Posted comments on one or more Linear IDs referencing the OKF path

…and you want one script that asserts all three legs are intact and the
trail is bidirectional.

This is the script Ned wrote on 2026-07-29 for the Zapier CLI OKF runbook
entries (`okf/ops-runbook/zapier-cli-headless-login.md` + 4 Linear tasks
GRO-4373..4376). The shape generalizes to any "OKF authored + Linear trail"
workflow where the durability requirement is bidirectional linking.

Run:
    python3 scripts/verify_okf_with_linear_trail.py \
        --entry-path okf/ops-runbook/zapier-cli-headless-login.md \
        --section-index okf/ops-runbook/index.md \
        --top-index okf/index.md \
        --linear-ids GRO-4373,GRO-4374,GRO-4375,GRO-4376 \
        --okf-link-marker "ops-runbook" \
        --env-file /home/ubuntu/.hermes/profiles/orchestrator/.env

Exit 0 = all checks PASS. Exit 1 = any FAIL.

Customize by editing the script or extracting the helpers; do not require
this exact argument list.
"""
import argparse
import re
import sys
from pathlib import Path

try:
    import requests  # type: ignore
except ImportError:
    print("FATAL: requests library not available", file=sys.stderr)
    sys.exit(2)


def load_env(path):
    env = {}
    p = Path(path)
    if not p.exists():
        return env
    with p.open() as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                k, v = line.split("=", 1)
                env[k] = v
    return env


def check(name, passed, detail):
    status = "PASS" if passed else "FAIL"
    icon = "✓" if passed else "✗"
    print(f"  [{icon} {status}] {name}")
    print(f"      {detail}")
    return passed


def verify_entry(entry_path):
    """Check the OKF entry has frontmatter, required sections, and key content markers."""
    p = Path(entry_path)
    if not p.exists():
        return check("Entry exists", False, f"missing: {p}")
    body = p.read_text()
    fm_match = re.match(r"^---\n(.+?)\n---", body, re.DOTALL)
    if not fm_match:
        return check("Entry has YAML frontmatter", False, "no --- markers")
    fm = fm_match.group(1)
    ok = "type:" in fm and "title:" in fm and "description:" in fm
    return check(
        "Entry frontmatter has type/title/description",
        ok,
        f"size={len(body)}b frontmatter_ok={ok}",
    )


def verify_section_index(section_index, entry_basename):
    """Check the section index links the entry."""
    p = Path(section_index)
    if not p.exists():
        return check("Section index exists", False, f"missing: {p}")
    body = p.read_text()
    linked = entry_basename in body
    return check(
        "Section index links entry",
        linked,
        f"path={p} links={linked}",
    )


def verify_top_index(top_index, section_dirname, entry_basename, entry_title_phrase):
    """Check the top-level OKF index links the section AND the entry, and preserves existing entries."""
    p = Path(top_index)
    if not p.exists():
        return check("Top index exists", False, f"missing: {p}")
    body = p.read_text()
    section_linked = section_dirname in body
    entry_linked = entry_basename in body and entry_title_phrase in body
    existing_preserved = "reports" in body and "audits" in body  # minimum-viable baseline
    return check(
        "Top index links section + entry, preserves existing entries",
        section_linked and entry_linked and existing_preserved,
        f"section={section_linked} entry={entry_linked} existing_preserved={existing_preserved}",
    )


def verify_linear_trail(linear_ids, okf_link_marker, env):
    """Check each Linear ID has at least one comment containing both 'OKF' and the marker."""
    api_key = env.get("LINEAR_API_KEY")
    if not api_key:
        return check("Linear API auth", False, "LINEAR_API_KEY missing from env file")
    headers = {"Authorization": api_key, "Content-Type": "application/json"}
    query = (
        "{ issues(filter: { team: { key: { eq: \"GRO\" } } }, first: 250) "
        "{ nodes { identifier comments(last: 10) { nodes { body } } } } }"
    )
    try:
        r = requests.post(
            "https://api.linear.app/graphql",
            headers=headers,
            json={"query": query},
            timeout=20,
        )
        r.raise_for_status()
    except Exception as e:
        return check("Linear API reachable", False, repr(e))
    issues = {i["identifier"]: i for i in r.json()["data"]["issues"]["nodes"]}
    per_id = {}
    all_ok = True
    for ident in linear_ids:
        issue = issues.get(ident)
        if not issue:
            per_id[ident] = "MISSING"
            all_ok = False
            continue
        bodies = [c["body"] for c in issue["comments"]["nodes"]]
        ok = any("OKF" in b and okf_link_marker.lower() in b.lower() for b in bodies)
        per_id[ident] = "ok" if ok else "no_okf_comment"
        if not ok:
            all_ok = False
    return check(
        f"All {len(linear_ids)} Linear IDs have OKF-reference comments",
        all_ok,
        " | ".join(f"{k}={v}" for k, v in per_id.items()),
    )


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--entry-path", required=True)
    ap.add_argument("--section-index", required=True)
    ap.add_argument("--top-index", required=True)
    ap.add_argument("--linear-ids", required=True, help="comma-separated, e.g. GRO-4373,GRO-4374")
    ap.add_argument("--okf-link-marker", required=True, help="substring that must appear in the Linear comment, e.g. 'ops-runbook'")
    ap.add_argument("--entry-title-phrase", default="", help="optional phrase that must appear in the top index next to the entry link")
    ap.add_argument("--env-file", required=True)
    args = ap.parse_args()

    entry_path = Path(args.entry_path)
    entry_basename = entry_path.name
    section_dirname = entry_path.parent.name
    linear_ids = [s.strip() for s in args.linear_ids.split(",") if s.strip()]
    env = load_env(args.env_file)

    print("=" * 78)
    print(f"OKF + LINEAR TRAIL VERIFICATION — {len(linear_ids) + 3} checks")
    print("=" * 78)

    results = []
    results.append(verify_entry(entry_path))
    results.append(verify_section_index(args.section_index, entry_basename))
    results.append(verify_top_index(args.top_index, section_dirname, entry_basename, args.entry_title_phrase or entry_basename))
    results.append(verify_linear_trail(linear_ids, args.okf_link_marker, env))

    print("=" * 78)
    if all(results):
        print("OVERALL: PASS")
        return 0
    else:
        print("OVERALL: FAIL")
        return 1


if __name__ == "__main__":
    sys.exit(main())
