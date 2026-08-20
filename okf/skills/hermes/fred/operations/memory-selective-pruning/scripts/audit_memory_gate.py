#!/usr/bin/env python3
"""Audit Hermes profile memory files for selective pruning.

Read-only by default. Prints hot files, exact duplicates inside each file,
stale/task markers, oversized entries, and a placement-gate recommendation.
"""
from __future__ import annotations

from pathlib import Path
import argparse
import hashlib
import re

CAPS = {"MEMORY.md": 2200, "USER.md": 1375}
STALE_MARKERS = re.compile(r"\b(GRO-\d+|PR #|commit|branch|merged|Done|completed|stale|Phase \d+|2026-0[1-9])\b", re.I)
PROCEDURE_MARKERS = re.compile(r"\b(run|command|workflow|procedure|steps?|use .*script|verify with)\b", re.I)
OKF_MARKERS = re.compile(r"\b(governance|standard|incident|audit|architecture|policy|OKF)\b", re.I)


def split_entries(text: str) -> list[str]:
    return [x.strip() for x in re.split(r"\n§\n|§", text) if x.strip()]


def norm(entry: str) -> str:
    return re.sub(r"\s+", " ", entry.lower()).strip()


def recommend(entry: str) -> str:
    if STALE_MARKERS.search(entry):
        return "replace/remove: task-progress or stale marker"
    if PROCEDURE_MARKERS.search(entry):
        return "move-to-skill candidate"
    if OKF_MARKERS.search(entry):
        return "move/link-to-OKF candidate"
    if len(entry) > 260:
        return "compress: oversized durable fact"
    return "keep-if-durable"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("profiles", nargs="*", help="Profile names; default scans all profiles")
    ap.add_argument("--root", default=str(Path.home()/".hermes"/"profiles"))
    args = ap.parse_args()
    root = Path(args.root)
    profiles = args.profiles or sorted(p.name for p in root.iterdir() if p.is_dir())
    for profile in profiles:
        for fn, cap in CAPS.items():
            path = root/profile/"memories"/fn
            if not path.exists():
                continue
            text = path.read_text(errors="ignore")
            entries = split_entries(text)
            pct = 100 * len(text) / cap
            print(f"## {profile}/{fn}: {len(text)}/{cap} chars ({pct:.1f}%), entries={len(entries)}")
            seen = {}
            for idx, entry in enumerate(entries):
                h = hashlib.sha1(norm(entry).encode()).hexdigest()[:12]
                dup = " duplicate" if h in seen else ""
                seen[h] = idx
                rec = recommend(entry)
                if pct >= 80 or dup or rec != "keep-if-durable":
                    preview = re.sub(r"\s+", " ", entry)[:180]
                    print(f"- {idx}: {len(entry)} chars{dup}; {rec}; {preview}")
            print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
