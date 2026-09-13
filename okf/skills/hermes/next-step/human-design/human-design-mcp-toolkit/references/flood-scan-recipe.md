# Future Transit "Flood" Scans — When Do All My Gates Light Simultaneously?

Class of ask: "On which days in the next N days do ALL (or most) of my incarnation-cross gates / natal gates light up at once by transit?" Verified working 2026-08-28 for Michael's RAX-4 (26/45/47/22).

## Core pitfall — Moon residence

The Moon sits in a given gate only ~6 h per passage (moves ~13°/day; a gate is ~5.6°). A **daily** sample (e.g. noon UTC) **misses entirely** any simultaneity in which the Moon is the occupant of one of the target gates. Consequence seen live: the noon scan found only 1 "3-of-4" day in a full year; the 4-hour re-scan found **three** (2027-06-11, 06-25, 06-26).

→ **Sample every 4 hours** (hours 0, 4, 8, 12, 16, 20 UTC; 2 h only if the user demands exactness). A day "floods" if at ANY of its samples all N target gates are lit.

## Method (one `execute_code` monolith — fresh interpreter per call)

```python
import sys, os, json
from datetime import date, timedelta
SRC = "/home/ubuntu/work/OpenHumanDesignMCP/hd-mcp-server/src"
sys.path.insert(0, SRC)
from transit_engine import calculate_transit_positions
from ephemeris_engine import julday, init_ephemeris
init_ephemeris()

TARGET = {26, 45, 47, 22}   # the person's cross gates (or any natal gate set)
day_best = {}
d, end = date(2026,8,28), date(2027,8,28)
while d <= end:
    for hh in (0, 4, 8, 12, 16, 20):
        t = calculate_transit_positions(target_jd=julday(d.year, d.month, d.day, float(hh)))
        occ = {}
        for name, info in t.items():
            if isinstance(info, dict) and info.get("gate"):
                occ.setdefault(info["gate"], []).append(name)
        lit = sorted(TARGET & set(occ))
        k = d.isoformat()
        if k not in day_best or len(lit) > day_best[k][0]:
            day_best[k] = (len(lit), f"{hh:02d}Z", {str(g): occ[g] for g in lit})
    d += timedelta(days=1)
```

Notes:
- **"Lit" = ANY body in the gate** — same rule as natal `all_active_gates`. `calculate_transit_positions` returns 15 bodies (10 planets + True Node + South Node + Earth + Chiron + both Liliths), so floods can be driven by Earth/Nodes/Lilith, not just planets. That is legitimate — always report *which* body occupies each gate.
- **Write the JSON to the workspace BEFORE printing the report.** A print-side crash after the scan loses the file (2026-08-28: a KeyError in the print loop killed the 5-year run after the scan finished, so the save never happened; the rescan cost an extra ~2 s — cheap, but avoidable).
- Cost: 366 days @ 4-h sampling ≈ 2 s; 5 years @ daily ≈ 2 s. Cheap enough to extend the horizon freely.

## Reporting shape (what the user actually wants)

1. **Full flood days** in the requested window, occupants per gate.
2. If **zero** full floods: say so plainly (it's a feature of the cross — floods are *events*, not background hum), list the best **3-of-4 near-miss days**, and **extend the horizon** (e.g. +5 y at daily 12.0 sampling is fine for that pass) so the user gets a concrete date to "mark it."
3. Note the **time window** for Moon-involved configurations (the sample hour tells you the UTC window; convert to the user's local tz).
4. A dense **week** can matter more than a single day (2027-06-21→27: Mars resident in 47, Venus in 45, Moon crossing both — no 4/4 day, but it will *feel* like the flood). Offer to mark the stretch, not just the day.

## Verified anchor data — Michael, RAX-4 = 26 Egoist / 45 Gatherer / 47 Realizing / 22 Grace

- 2026-08-28 → 2027-08-28 (4-h sampling): **0 full floods**. 3/4 near-floods: 2027-06-11 (Earth@26, Sun@45, Moon@47), 2027-06-25/26 (Moon@22, Venus@45, Mars@47).
- First full floods (daily scan 2027-08-29 → 2032-08-28): **2028-06-09/10** (Jupiter@47, Earth@26, Sun@45, True Lilith@22); **2030-03-08→12** (five days: Nodes@26/45, Sun@22, Earth@47); **2031-09-10→13** (Saturn@45, Jupiter@26, Sun@47, Earth@22).
- Raw outputs from the 2026-08-28 run: `~/work/flood-scan-dense.json` (366 d, per-day max + occupants) and `~/work/flood-scan-future.json` (2027→2032 full floods).
