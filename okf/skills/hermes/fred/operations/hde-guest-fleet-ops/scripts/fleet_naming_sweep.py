#!/usr/bin/env python3
"""Read-only sweep of all 12 HDE guest chart stores for dev/test-name records.

Never deletes — produces a report for a human (Michael) to act on.
Run: /usr/bin/python3 scripts/fleet_naming_sweep.py
"""
import glob
import json
import os
import re

GUEST_ROOT = "/home/ubuntu/users"
GUESTS = [2, 3, 23, 29, 30, 31, 32, 38, 39, 40, 42, 43]
BLOCKED = {"michael gulden", "michael", "becca", "becca gulden",
           "test", "tester", "test guest", "guest test", "qa", "dev"}


def blocked_names_in(blob):
    found = set()
    for name in re.findall(r'"name"\s*:\s*"([^"]+)"', blob):
        m = name.lower().strip()
        if m in BLOCKED:
            found.add(m)
    return found


def main():
    report = []
    total = 0
    for n in GUESTS:
        d = os.path.join(GUEST_ROOT, f"guest_{n}")
        files = []
        files += glob.glob(f"{d}/people/*.json")
        files += glob.glob(f"{d}/charts/**/*.json", recursive=True)
        files += [f for f in (f"{d}/conversation_history.json",
                              f"{d}/conversation_state.json",
                              f"{d}/greeting_state.json",
                              f"{d}/guest_family.json") if os.path.isfile(f)]
        hits = []
        for f in files:
            try:
                bad = blocked_names_in(open(f, encoding="utf-8", errors="replace").read())
            except OSError:
                continue
            if bad:
                hits.append((os.path.relpath(f, d), sorted(bad)))
        total += len(hits)
        report.append({"guest": n, "hits": hits})
        print(f"guest_{n}: " + ("; ".join(f"{p} {nm}" for p, nm in hits) if hits else "clean"))
    print(f"\nSWEEP COMPLETE: {len(GUESTS)} guests scanned, {total} file hits (READ-ONLY, nothing deleted)")
    out = "/tmp/hfg_naming_sweep.json"
    json.dump(report, open(out, "w"), indent=2)
    print(f"report: {out}")


if __name__ == "__main__":
    main()
