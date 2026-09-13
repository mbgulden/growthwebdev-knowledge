# Engine internals for verification (OpenHumanDesignMCP, hd-mcp-server/src)

Source root: `/home/ubuntu/work/OpenHumanDesignMCP/hd-mcp-server/src/` (note: `build/lib/` is a stale build copy — don't grep it).

| What | Where | Notes |
|------|-------|-------|
| Channel table | `matrix_mapper.py` → `CHANNELS` dict | `{(g1, g2): "Name (Scope)"}`. If a lit gate pair is missing here it's a table bug, not chart mechanics. |
| Gate→center map | `matrix_mapper.py` → `GATE_CENTER` | Used to derive defined centers. |
| Definition/centers logic | `cosmic_calculator.py` → `compute_defined_centers()` | A center is defined ONLY if it connects a channel whose BOTH terminal gates are active. Gates with `circuit=False` (Ascendant/MC per Jovian spec) are excluded from `all_active_gates`. |
| Type determination | `cosmic_calculator.py` → `determine_type(defined_centers, defined_channels)` | |
| Incarnation cross | `cosmic_calculator.py` → `compute_incarnation_cross()` + `RAX_MAP` | `RAX_MAP` keys are `(p_sun, p_earth, d_sun, d_earth)` → cross name. Unmatched combos fall back to a bare `Cross of (a/b|c/d)` string — if you see that format, the cross is NOT in the map (not necessarily wrong, just unmapped). |
| Node/trajectory | `cosmic_calculator.py` (node color helpers near line 130) | |

## Verified case: Michael Gulden (12/10/1989 5:07pm PST, Simi Valley CA) — 2026-08-28

- Engine chart: Projector, Splenic, 3/5, Split. Defined: Throat, G, Heart/Ego, Spleen. Defined channels: 1-8 (Inspiration), 26-44 (Surrender).
- **Incarnation cross: Right Angle Cross of Rulership 4 = p_sun 26 (Egoist) / p_earth 45 (Gatherer) | d_sun 47 (Realizing) / d_earth 22 (Grace).** Confirmed by humancharts.com, thehumandesignsystem.com, humandesign.zone. Old SOUL.md notes wrongly said 7/13/29/30; patched.
- **48/58 resolved (engine was CORRECT):** `all_active_gates` includes 48 and 58, and `defined_channels` is only 1-8 + 26-44 — verified legitimate: 48's only channel partner is 16 (not active), 58's is 18 (not active). They are isolated gates, not a missing channel. Do not re-flag this as a bug.
- **Contested layer:** engine `variables` = PRR DLR / Alternating Appetite / Active Mountains / Transpersonal / Inner Vision / Hope — conflicts with SOUL.md coaching lines (Outer Vision, Open-Taste, External-Marks, Power, Fear). Coaching lines stay authoritative until settled.

## External verification sources (worked)
- humancharts.com incarnation-cross pages (authoritative gate lists per cross)
- thehumandesignsystem.com /crosses/… (cross gate + life-theme summaries)
- humandesign.zone (alternative cross descriptions)
