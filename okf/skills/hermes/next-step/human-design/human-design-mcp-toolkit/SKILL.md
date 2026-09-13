---
name: human-design-mcp-toolkit
description: Use for HD charts, gates, transits via mcp__hd__ tools.
---

# Human Design MCP Toolkit (mcp__hd__)

The next-step profile has a live `mcp__hd__` MCP server: **OpenHumanDesignMCP v1.0.0** (Michael's own repo, github.com/mbgulden/OpenHumanDesignMCP, AGPLv3, Swiss Ephemeris backend). Verified live Aug 27 2026: `ping` → Ready; `lookup_gate(26)` → The Egoist, Heart/Ego, 26-44 (Surrender (Tribal)); `calculate_chart` (test chart) → full clean chart with all fields below.

## When to use
- **One-off HD questions in interactive sessions**: "make a chart for X", "what's gate N", "what's transiting today", "how do A and B's designs interact", "cartography lines for a move", "on which days in the next year do all my cross gates light at once (incarnation-cross flood scan — see `references/flood-scan-recipe.md`)".
- The sibling skills own the **daily-briefing cron pipelines** (headline picking, V2 format, family snippets): `human-design-transit-briefings` (umbrella, raw-engine path) and `daily-transit-briefing`. Those are user-owned — do not try to patch them from an autonomous session. For briefings, follow them; this skill is the clean high-level interface for everything else.

## Tool reference

| Tool | Args | Returns |
|------|------|---------|
| `ping` | — | Server status + version. First call after a gap; confirms readiness. |
| `lookup_gate` | `gate_number` | Gate name, center, channel(s). |
| `calculate_chart` | `name, year, month, day, hour` (decimal LOCAL time, e.g. 17.1167 = 5:07 PM), `location` (city name or "lat,lon"), `lat`/`lon` overrides | Full chart: `hd_type`, `strategy`, `authority`, `signature`, `not_self_theme`, `profile`, `incarnation_cross` (name, angle_type, 4 gates), `definition`, `defined_centers`, `undefined_centers`, `defined_channels`, `all_active_gates`, `sun_gate`, `earth_gate`, `variables` (orientation, digestion, environment, perspective, motivation, cognition, sense, trajectory). |
| `calculate_chart_detailed` | same | Same + all planetary positions. |
| `calculate_chart_with_transits` | same + optional `target_year/month/day/hour` | Natal + live transit overlay. Omit target → current UTC. |
| `get_planet_positions` | `year, month, day, hour` (default 12.0, UTC) | All planets with gate/line/center mappings for any moment. |
| `get_astrocartography_lines` | birth args (as calculate_chart) | Natal world lines as GeoJSON. |
| `get_cyclocartography_lines` | birth args + optional target datetime | Natal + transit world lines overlaid, GeoJSON. |
| `analyze_relationship` | `chart_a_gates`, `chart_b_gates` (gate lists), optional `name_a`/`name_b` | Electromagnetic / compromise / dominance dynamics. |
| `analyze_penta` | `charts_json`: `[{name, gates: [...]}, ...]` (3–5 people) | Group/business dynamics. |
| `get_penta_gates` | — | The 12 Penta (business/group material) gates. |
| `get_relationship_composite` | `profile_a`, `profile_b` (registry keys, e.g. "michael", "becca") | Full synastry matrix: electromagnetic, dominance, compromise, companion channels, combined center definition, shared/unique gates. Only works for people in the server-side registry. |
| `batch_calculate_charts` | `csv_data`: `name,year,month,day,hour,location` rows | CSV with computed chart data. |
| `resolve_geo` | `location` string | lat/lon + timezone for a city. |
| `list_prompts` / `get_prompt` / `list_resources` / `read_resource` | — | Server-provided prompts and resources. |

## Usage notes & pitfalls
- **Birth data for `calculate_chart*` is LOCAL time** — the tool handles local→UTC. This differs from the raw engine's `calculate_natal_chart()` which requires a UTC-aware datetime (see the sibling umbrella's pitfalls).
- **`location` accepts city names** ("Simi Valley CA") or `"lat,lon"`; pass `lat`/`lon` if the city won't resolve.
- `get_planet_positions` and the no-target default of `calculate_chart_with_transits` are **UTC-based** — don't feed local hours expecting local alignment.
- `get_relationship_composite` is registry-key based; for arbitrary people (e.g. a client's chart not in the registry) build it from `calculate_chart` outputs + `analyze_relationship` with explicit gate lists instead.
- **Same engine-drift caveat as the sibling umbrella applies**: MCP output is the same engine, so do NOT let engine-computed profile/type/centers override the user-supplied natal baseline in briefing work (Michael = 3/5 Split, G/Heart-Ego/Spleen/Throat; Becca = 6/2). Use MCP strictly for the computation, baseline stays authoritative. **But discrepancies can run in EITHER direction**: on a live check 2026-08-28 the engine's incarnation-cross gates (Rulership 4 = 26/45 | 47/22) were *correct* and the stale family notes were the wrong side. When engine and baseline conflict, verify both against external references (humancharts.com, thehumandesignsystem.com) before correcting either side — and patch whichever side was wrong (SOUL.md section, or flag the engine bug), never assume.
- When a briefing-style ask comes in, check whether the cron/umbrella pipeline already covers it before ad-libbing with MCP tools — the pipelines encode headline-picking rules that a raw tool call would skip.
- **When a future "flood/simultaneity" scan (all cross gates lit on the same day) comes in: sample every 4 hours, never once-daily.** The Moon's per-gate residence is only ~6 h, so a noon-only sample silently misses any configuration where the Moon is an occupant (2026-08-28: noon scan → 1 near-flood day/year; 4-hour rescan → 3). Full recipe (monolith code, save-JSON-before-print, zero-flood horizon extension, Michael's verified anchor dates) in `references/flood-scan-recipe.md`.
- **Verification map for engine internals** (channel table location, `RAX_MAP` cross lookup, definition logic, the verified Michael-Gulden case, working external cross-check sites): `references/engine-internals.md`.
- **When `all_active_gates` contains gates missing from `defined_channels`, verify before suspecting an engine bug**: check whether the lit gates are actually the two terminals of a real channel by grepping the engine's channel table (`matrix_mapper.py` → `CHANNELS`). Lit gates are often *isolated* (their true channel partner is simply not active) — that's legitimate chart mechanics, not a bug. Verified 2026-08-28 on Michael's chart: gates 48/58 lit, but 48↔16 and 58↔18, neither partner active → engine's defined list (only 1-8, 26-44) was correct. Only if a genuinely completed channel (both terminals lit, pair exists in `CHANNELS`) is missing is it an engine table bug.
- **The `variables` (Four Transformations) block is a contested layer**: on 2026-08-28 the engine output (PRR DLR / Alternating Appetite / Active Mountains / Transpersonal / Inner Vision / Hope) directly contradicted the established coaching lines in SOUL.md (Outer Vision / Open-Taste / External-Marks / Power / Fear). Until the layer is settled, keep the SOUL.md coaching lines for coaching work and do not narrate the `variables` field in readings without flagging the conflict.
