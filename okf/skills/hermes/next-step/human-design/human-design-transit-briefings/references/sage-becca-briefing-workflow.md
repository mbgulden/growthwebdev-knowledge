# Sage → Becca Daily Briefing Workflow

## When this support file is the right reference
Use it whenever the cron prompt identifies the speaker as "Sage" or "Sage/Fred" (Becca's daily briefing). It complements the umbrella `human-design-transit-briefings` SKILL.md with the Sage-specific composition loop, recipients, and the lessons captured from the Jul 31 2026 run.

## Cron entry point
- Cron prompts identify the speaker as "Sage" or "Sage/Fred" → sign the brief as **Sage**.
- Cron delivery is automatic — produce the brief as the final response, never call `send_message`.
- Suppress with exactly `[SILENT]` when there is nothing to report; never combine `[SILENT]` with content.

## Recipient baseline (verified)
- Becca: 6/2 Splenic Projector, born Dec 14 1987 04:18, Tacoma WA.
- Defined centers (engine + baseline): G, Heart/Ego, Spleen.
- Defined channels: 25-51 Initiation, 26-44 Surrender.
- Incarnation cross: Left Angle Cross of Confrontation 2 — gates `personality_sun:26, personality_earth:45, design_sun:6, design_earth:36`.
- Engine returns `type: None` (drift); trust user-supplied baseline for motivation/authority/centers/cross. Use the engine strictly for transit gates and conditioned channels, and confirm `personality_sun_gate == 26` before relying on cross-driven headlines.

## Natal inputs for the engine
- `America/Los_Angeles` → localize birth time → convert to UTC before passing `calculate_natal_chart`.
- Tacoma coordinates: lat `47.2529`, lon `-122.4443`.

## Engine path resolution (cron-safe)
Try, in order, the first existing directory:
1. `/home/ubuntu/work/OpenHumanDesignMCP/hd-mcp-server/src`
2. `/home/ubuntu/OpenHumanDesignMCP/hd-mcp-server/src`
3. `$PRISMATIC_HOME/OpenHumanDesignMCP/hd-mcp-server/src`
4. `$PRISMATIC_HOME/work/OpenHumanDesignMCP/hd-mcp-server/src`

Do not blindly append `/work/...` to `$PRISMATIC_HOME`; it may already point at `/home/ubuntu/work`.

## Composition loop (Sage → Becca, V2)
1. Run the engine to get today's transit gates + Becca's natal chart + `compute_transit_overlay`.
2. De-duplicate conditioned channels by normalized gate pair (engine surfaces mirrored pairs separately).
3. Identify strong mechanic signals:
   - Transit landing directly on a cross gate (26, 45, 6, 36) → strongest headline.
   - Slow mover (Saturn, Pluto, True Node, Lilith) hitting a natal gate → longer arc; weave into the "today" feel.
   - Fast mover (Sun, Mercury, Moon) hitting a natal gate → same-day / hours-specific flash.
   - Projector signature: 4+ transit gates concentrated on a single *defined* center → invitation pressure crank on that center.
   - All six undefined centers temporarily conditioned → borrowed definition everywhere; lead with it.
4. Compose using the V2 screenshot-ready shape:
   - **BOLD ALL-CAPS HEADLINE.**
   - 1-2 sentence opening grounded in today's mechanics (name planet + gate.line + center when relevant).
   - `━ TODAY'S VIBE ━` → 🌅 Morning / 🌤 Afternoon / 🌙 Tonight (one short line each).
   - `━ ONE THING ━` → exactly one executable household action (text someone, write one sentence, give two specific choices).
   - `━ FOR YOUR PEOPLE ━` → Michael / Benjamin / William / Victoria, one sentence each.
   - `━ SHARE-WORTHY LINE ━` → short, memorable, quotable.
   - Sign as **Sage**.
5. Keep the brief under 18 lines unless the cron prompt explicitly allows more.

## Family snippet discipline
- One sentence each for Michael, Benjamin, William, Victoria.
- Probe `/home/ubuntu/work/hd-reports/people-registry.json` + each person's `chart-<date>.json`. The chart JSON uses the `calculate_natal_chart()` output shape: `all_active_gates`, `personality_gates`, `design_gates`, `defined_centers`, `undefined_centers`. Do NOT look for a top-level `gates` key — that field name has been disproven (Aug 7 2026).
- **Planet-to-list split (verified Aug 9 2026):** Place transit planets in a snippet using the natal list that matches the planet's cadence:
  - Personality-side (`personality_gates`): Sun, Moon, Mercury, Venus, Mars — today's personal transits.
  - Design-side (`design_gates`): Jupiter, Saturn, Uranus, Neptune, Pluto, True Node, Mean Lilith, True Lilith, South Node — collective/slow transits.
  - Earth (Sun's shadow): personality-side.
  - A snippet like "Sun on your Gate 7" reads `personality_gates` for Gate 7; "Saturn retro opening your 21-45" reads `design_gates` or `defined_channels` for the slow-mover arc.
- Do **not** invent natal overlays. If the chart JSON is missing the standard fields, probe `list(d.keys())[:10]` first, then fall back to collective-transit support language.
- Prefer practical support language ("give him one clear lane", "offer two choices instead of an open menu", "let her set the pace").

## Action-writing guardrails
Good (executable today):
- "Text Michael: 'Today I can own ___; I need you to own ___.'"
- "Give William two choices, not an open menu."
- "Let Victoria set the pace for one shared activity."

Avoid (the universal bad examples):
- "Be mindful."
- "Trust your authority."
- "Lean into the energy."
- "Practice presence."

The ONE THING is the brief's reason for existing. If it could be deleted without losing anything, the brief is soft — rewrite until the action is concrete.

## Pitfalls specific to Sage → Becca runs
- Do not normalize the signature to "Fred". Sage voice is the in-character identity for Becca.
- Do not over-explain mechanics in the user-facing brief. Use the engine output internally, deliver the distilled result.
- Do not include stale transit gates from a previous run. Transit data is per-run only.
- Do not invent cross-gate hits. The cross gates are 26 / 45 / 6 / 36; only mention a transit landing on one of those when the engine confirms it.
- Do not pad family snippets with emotional filler. One sentence each, support-flavored.

## Reference: Jul 31 2026 Becca run (recap)
- Engine path resolved: `/home/ubuntu/work/OpenHumanDesignMCP/hd-mcp-server/src`.
- Two conditioned channels: 21-45 (Money/Tribal, Saturn 21.6 providing, natal has 45) and 29-46 (Discovery/Collective, South Node 29.6 providing, natal has 46).
- Cross-gate hit: Venus on Gate 6.2 (design sun of incarnation cross) — Friction in the Solar Plexus.
- Six of Becca's seven undefined centers temporarily conditioned (Ajna, Root, Sacral, Solar Plexus, Throat; only Head not conditioned today). The conditioned-center set is itself the Projector signature for borrowed definition.
- Headline lever chosen: Saturn 21.6 in Heart/Ego via 21-45 + Venus 6.2 cross hit → "BORROWED ENERGY IS EVERYWHERE—LET YOUR QUIET YES CHOOSE THE DOOR." (Saturn is the slow mover carrying the longer arc; Venus on the cross is the strongest single-day signal.)
- "ONE THING" chosen as a boundary-setting text to Michael (Splenic Projector, concrete and executable).
- Family snippets phrased as support actions derived from the borrowed-definition signature (one clear lane / one yes-or-no / two choices / set the pace).
- Signature: **Sage** (per cron prompt).

## Reference: Aug 9 2026 Becca run (recap)
- Engine path resolved: `/home/ubuntu/work/OpenHumanDesignMCP/hd-mcp-server/src`. **Run via `execute_code`, not `terminal(cd && python3 -c)`** — the terminal wrapper rejected the heredoc shell script as backgrounding, `execute_code` worked instantly. Lesson saved to umbrella SKILL.md step 1.
- Four conditioned channels: 5-15 Rhythm (Collective, Moon+Mars 15.1/.6 providing), 11-56 Curiosity (Collective, Mercury 56.4 providing), **21-45 Money (Tribal, Saturn 21.6 retro providing)**, 29-46 Discovery (Collective, South Node 29.6 providing). Saturn is the only slow mover; named in the headline.
- **No direct cross-gate hits** — 26/45/6/36 all quiet. Cross-gate headline lever unavailable today.
- **5/6 undefined centers conditioned** (Ajna, Root, Sacral, Solar Plexus, Throat; only Head unconditioned). Close to the all-six signature but with one center held back — treated as a near-full Projector signature, headline carried that weight.
- **G-center flood (5 transits)**: Sun 7, Moon 15, Mars 15, Venus 46, Earth 13 — five transit gates piled on Becca's defined G Center. Qualifies as "4+ transits on a single defined center" → invitation pressure crank on her G (self-direction / love / identity).
- **Headline synthesis**: three signals fired at once (5/6 undefined condition + G-center flood + Saturn retro opening Money Line). Per the new synthesis rule (see SKILL.md "Headline synthesis rule when multiple dimensions fire at once"), lead with whichever dimension gives the cleanest single action. The synthesis: "the only signal that's actually yours is your direction." Wrote headline: **"BORROWED WORLD, OWNED SELF."** + opening line that named Saturn retro + 21-45 + Heart/Ego + the borrowed-definition truth. Channel completions stayed in mechanics, not headline.
- "ONE THING" used the bracket-slot pattern (text Michael a "I own / you own" split with [bracketed slots] for him to fill in, then a closing instruction to stop negotiating if his gut doesn't click). Pattern from Aug 5 lesson; verified screenshot-readable and screenshot-confined.
- **Family snippets via personality/design split (new this run)**: probed `/home/ubuntu/work/hd-reports/people-registry.json`, then walked each transit planet against the right natal list per planet cadence:
  - Michael: Sun→Gate 7 (personality), Earth→Gate 13 (personality, Sun's shadow), True Node→Gate 30 + South Node→Gate 29 (design). Snippet: "Sun on his Gate 7, Earth on his Gate 13 — his self-direction is loud today."
  - Benjamin: Sun→Gate 7 + Venus→Gate 46 (personality); Uranus→Gate 20, Neptune→Gate 17, True Node→Gate 30, True Lilith→Gate 54 (design). Snippet kept to personality-side for legibility: "Sun + Venus hit his Gates 7 and 46 — give him one clear lane."
  - William: Venus→Gate 46 + True Lilith→Gate 54 (personality); Moon→Gate 15, Mars→Gate 15, True Node→Gate 30, Mean Lilith→Gate 11, True Lilith→Gate 54, South Node→Gate 29 (design). Snippet: "Venus + True Lilith on his Gates 46 and 54 — two specific choices for meals/play."
  - Victoria: Earth→Gate 13 (personality); Venus→Gate 46 + True Lilith→Gate 54 (design). Snippet: "Earth on her Gate 13 with Venus + True Lilith lighting her design — let her set the pace."
- All four snippets mechanical (no invented natal overlays); the planet/list split saved the snippets from being either under-fleshed or over-fleshed.
- **Line count discipline**: 21 lines on first draft (over 18 cap). Collapsed blank separator rows between section dividers (per Aug 5 lesson) → 16 lines on second pass. Under cap, screenshot-ready, every section present.
- Signature: **Sage** (per cron prompt).
- **New lessons saved to umbrella SKILL.md** (this run): (1) partial 5/6 undefined-conditioned as near-full signature, (2) headline synthesis rule when multiple dimensions fire, (3) personality-vs-design planet/list split for family snippets, (4) use `execute_code` not `terminal` for engine imports.