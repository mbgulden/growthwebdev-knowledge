#!/usr/bin/env python3
"""Read-only Hermes gateway fleet status check.

Guard-safe by construction: contains no lifecycle verbs (no restart/stop/start),
so running it from inside a gateway session cannot trip the in-gateway terminal
guard (which scans the whole command string for lifecycle patterns).

Usage:
  python3 fleet_status.py [unit.service ...]
  # no args: auto-detects hermes-gateway-*.service + known alias units
"""
import datetime
import glob
import json
import os
import subprocess
import sys


def sh(cmd, timeout=15):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip()
    except Exception as e:
        return f"ERR:{e}"


# unit -> hermes profile dir name (aliases: jeff serves next-step)
def profile_for(unit):
    if unit.startswith("hermes-gateway-") and unit.endswith(".service"):
        return unit[len("hermes-gateway-"):-len(".service")]
    return {"jeff.service": "next-step", "autobot.service": "autobot"}.get(unit, "")


def discover_units():
    out = set()
    for p in glob.glob("/etc/systemd/system/*.service"):
        b = os.path.basename(p)
        if b.startswith("hermes-gateway-") or b in ("jeff.service", "autobot.service"):
            out.add(b)
    return sorted(out)


def prefill_sync(profile):
    d = f"/home/ubuntu/.hermes/profiles/{profile}/state"
    cj = os.path.join(d, "current.json")
    pf = os.path.join(d, "prefill_messages.json")
    try:
        one = json.load(open(cj))["current_state"]["one_line"][:50]
        text = " ".join(m["content"] for m in json.load(open(pf)))
        return "SYNCED" if one in text else "DRIFT"
    except Exception:
        return "n/a"


def main():
    units = sys.argv[1:] or discover_units()
    now = datetime.datetime.now(datetime.timezone.utc)
    print("NOW:", now.strftime("%Y-%m-%dT%H:%M:%SZ"))
    print(f"{'unit':40s} {'state':10s} {'MainPID':9s} {'pid-age':>8s} {'restrts':>7s}  prefill")
    for u in units:
        st = sh(f"systemctl is-active {u}")
        mpid = sh(f"systemctl show {u} --property=MainPID --value")
        nrest = sh(f"systemctl show {u} --property=NRestarts --value")
        age = "?"
        if mpid.isdigit() and mpid != "0" and os.path.exists(f"/proc/{mpid}"):
            try:
                start = datetime.datetime.fromtimestamp(
                    os.stat(f"/proc/{mpid}").st_mtime, datetime.timezone.utc
                )
                age = f"{(now - start).total_seconds():.0f}s"
            except Exception:
                pass
        prof = profile_for(u)
        sync = prefill_sync(prof) if prof else "-"
        print(f"{u:40s} {st:10s} {mpid:9s} {age:>8s} {nrest:>7s}  {sync}")


if __name__ == "__main__":
    main()
