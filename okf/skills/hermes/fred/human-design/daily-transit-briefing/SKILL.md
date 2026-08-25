---
name: daily-transit-briefing
description: Generate personalized daily transit briefings that are better than Co-Star. Creative quotes, transit-informed guidance, family snippets. For Sage (Becca) and Fred (Michael). Screenshot-worthy output.
category: human-design
triggers:
  - transit briefing
  - daily transit
  - Co-Star
  - Sage briefing
  - personalized HD daily
always-delegate: false
---

# Daily Transit Briefing — Better Than Co-Star

Co-Star knows your sun sign. We know your entire design, your spouse's design, your kids' designs, your current context, and what you've been experiencing. Use ALL of it.

## Birth Data Reference

**Load from `~/work/next-step-bot/family.json` FIRST** — but verify the actual path before reading. On non-Fred profiles the path is `~/.hermes/profiles/<profile>/home/work/next-step-bot/family.json`. Don't grep the filesystem; use `os.path.expanduser()` and check `os.path.exists()` first, then fall back to the profile-scoped path. Read once, then compute.

From that file:

| Person | Design | Key |
|--------|--------|-----|
| Michael | 3/5 Splenic Projector, Fear Motivation, Cross of Rulership 4, channels 1-8 + 44-26, Split | Defined: G, Heart/Ego, Spleen, Throat |
| Becca | 6/2 Splenic Projector | Defined: 3 centers |
| Benjamin (9) | 5/1 MG Emotional | |
| William (7) | 3/6 Generator Sacral | |
| Victoria (5) | 4/1 Generator Sacral | |

## Transit Computation

**Note**: All transit analysis is handled internally by this skill and does not rely on a separate 'human-design-guidance-systems' skill.

Use the transit engine to get today's planetary positions:

```python
import sys, os
_src = next(p for p in ("/home/ubuntu/work/OpenHumanDesignMCP/hd-mcp-server/src", os.path.expanduser("~/work/OpenHumanDesignMCP/hd-mcp-server/src")) if os.path.isdir(p))
sys.path.insert(0, _src)  # terminal env sets PRISMATIC_HOME=/home/ubuntu/work — concatenating '/work/' onto it doubles the path; execute_code sandbox doesn't inherit it at all
from transit_engine import calculate_transit_positions
from ephemeris_engine import julday, init_ephemeris
from datetime import datetime
import pytz

init_ephemeris()
mt = pytz.timezone("America/Denver")
now = datetime.now(mt)
jd = julday(now.year, now.month, now.day, now.hour + now.minute/60.0)
transits = calculate_transit_positions(target_jd=jd)

# transits is dict: planet_name → {gate, line, color, tone, base, gate_name, longitude, sign, degree}
```

**Then run the channel-completion + natal-hit analysis BEFORE writing any prose.** This is how you find the headline. A quote that names a specific transit channel completing today AND a specific natal gate it touches will feel like insight; one that lists "Sun in Gate 4" reads like weather.

Three-step analysis:

1. **Which channels fully light today?** A channel lights when BOTH gates are occupied by any transit body. Use the 36-channel HD dictionary (canonical version lives in `references/transit-analysis-recipe.md`).
2. **Which transit gates touch each person's natal gates?** Compute natal gates for everyone in `family.json`, intersect with today's transit gates.
3. **Match.** The headline is whichever has the most signal:
   - (Best) A fully-lit transit channel where ONE of the two gates is natal for the subject — the channel is being asked to form INSIDE them.
   - (Strong) A fully-lit transit channel that matches a defined natal channel.
   - (Fallback) The single strongest natal gate hit, even without channel completion.

Then layer in the standard mapping:
- Which of their defined channels are being activated by transit?
- Which of their open centers are being conditioned? (Use the gate→center map in `references/transit-analysis-recipe.md`.)
- Which gates in their chart are being hit?

## Output Format — Two Versions

### Version A: Sage → Becca (subject: Becca)

```
✨ [CREATIVE QUOTE — 1-2 sentences inspired by today's transits intersecting Becca's 6/2 Splenic Projector design, her role as mom/wife/HD practitioner, and what she's likely experiencing. Anchored on a specific transit geometry found in the analysis above — not generic.]

━ TODAY FOR YOU ━
🌊 Favorable: [2-3 specific activities supported by today's transits]
⚠️ Watch for: [1-2 things to be aware of based on open centers being conditioned]
🌟 Supported: [What's cosmically backing her up]

━ NEXT STEP ━
→ Do this: [ONE specific action for Becca today. Not "be mindful" — an actual thing she can do or not do. Pulled from the transit data.]
→ For them: [ONE specific action involving Michael or the kids. Something she can actually execute.]

━ FAMILY SNIPPETS ━
💫 Michael: [1 sentence — what transit is hitting his chart, what it means for him today]
💫 Benjamin: [1 sentence]
💫 William: [1 sentence]  
💫 Victoria: [1 sentence]
```

### Version B: Fred → Michael (subject: Michael)

```
⚡ [CREATIVE QUOTE — 1-2 sentences inspired by today's transits intersecting Michael's 3/5 Splenic Projector design, his current ventures/context, Fear Motivation, Cross of Rulership 4. Should feel like insight, not prediction. Anchor on a specific transit-channel-formation or natal-hit from the analysis above.]

━ TODAY FOR YOU ━
🌊 Favorable: [2-3 specific activities]
⚠️ Watch for: [1-2 things — especially spleen signals, invitation quality, energy management]
🌟 Supported: [What's cosmically backing him up]

━ NEXT STEP ━
→ Do this: [ONE specific action for Michael today. Not "be mindful" — an actual thing he can do or not do. Pulled from the transit data.]
→ For them: [ONE specific action involving Becca or the kids. Something he can actually execute today.]

━ FAMILY SNIPPETS ━
💫 Becca: [1 sentence — her transit, what she's navigating]
💫 Benjamin: [1 sentence]
💫 William: [1 sentence]
💫 Victoria: [1 sentence]
```

## Quote Crafting Rules

The quote is the differentiator. Rules:
- Never use "you will" or "today is a day for" — Co-Star language
- Pull from the actual gate names and transit geometry — be specific
- Connect to their real life: Michael's ventures, Becca's practice, their parenting
- Use metaphor grounded in HD mechanics (channels as energies, gates as doors, centers as operating systems)
- If a channel gets fully lit by transit, that's the headline
- If a transit channel includes one of the subject's natal gates, that's the GOLDEN headline
- 1-2 sentences max. Screenshot-length.
- Examples of tone:
  - "The 1-8 channel hums under today's transit — your spleen already knows which venture to nurture. The question isn't what to build, but what to let someone else build for you."
  - "Gate 44 lights up your undefined Ajna today. Ideas will arrive that feel like yours. They're not. Wait 24 hours before committing to any of them."
  - "Channel 58-18 is being asked to form inside you today — your open Gate 58 is receiving the call. Tell the truth about which venture feeds you."

## Activity Guidance Rules

- Activities must be SPECIFIC, not "practice self-care" or "be mindful"
- Connect to their actual life: "Take the kayak delivery route through Kahana" not "spend time in nature"
- Pull from transit-activated gates: if Gate 52 (Stillness) is active, suggest literal stillness
- If a splenic hit occurs, note it: "Your spleen will speak clearly around 2pm — listen for the instant no"

## Family Snippets Rules

- One sentence per person. No fluff.
- Connect transit to their design: "Benjamin's emotional wave gets a boost from today's Gate 39 transit — let him ride it out before asking about homework."
- Include ages implicitly through context (William is 7, Benjamin 9, Victoria 5)

## Cron Setup

Two separate crons:

**Sage → Becca**: `deliver: telegram:8570023972`, schedule: 7am MT (13:00 UTC)
**Fred → Michael**: `deliver: origin` (this chat), schedule: 7am MT (13:00 UTC)

Both load this skill, compute transits, and generate their respective version.

## V2 Format (currently shipping)

The user-preferred format diverges from the V1 templates above. The shipped V2 is:

```
⚡ [BOLD ALL-CAPS HEADLINE — 1 short phrase]

[1-2 sentence opening quote, anchored on a specific transit channel-formation or natal-hit]

━ TODAY'S VIBE ━
**Morning**: [what the morning transit does to them]
**Afternoon**: [what the afternoon transit does to them]
**Tonight**: [what the evening transit does to them]

━ SO WHAT ━
→ **Do this**: [ONE specific concrete action — Notion doc, a message, a thing to NOT do]
→ **For them**: [ONE specific action involving Becca/kids — a text, a question, a permission to ask]

━ WATCH FOR ━
⚠️ [open-center conditioning — Root/Heart/Ajna/Sacral/Plexus wave, not your own]
🌟 Supported: [what's cosmically backing the subject's defined channels/authority today]

━ FAMILY SNIPPETS ━
💫 **Becca**: [1 sentence — her transit today, ages implicit]
💫 **Benjamin** (9): [1 sentence]
💫 **William** (7): [1 sentence]
💫 **Victoria** (5): [1 sentence]

— Fred
```

V2 rules:
- Vibe sections (morning/afternoon/tonight) are derived from Moon position + Sun position + rising sign of the day. They give the briefing a temporal spine Co-Star lacks.
- "So What" replaces "Next Step" — the user-facing terminology. Same discipline: concrete, executable, no "trust yourself" filler.
- The headline anchors on whichever lit transit channel has the strongest natal match. If two are tied, name both and let the quote bridge them ("Three channels, one you" works when there's genuine parallelism).
- Family snippets name the kid and put age in parens the first time, then by name alone — keeps the line tight.
- Output budget: 18–24 lines including signature is fine; V2's vibe sections legitimately need more room than V1's 18-line cap. The hard rule is "screenshot-length" — phone-readable in one scroll on Telegram.

## Pitfalls

- Never use generic horoscope language — no "the stars align" or "universal energy"
- Don't mention gates/channels by number without their name/meaning
- If the transit engine fails, say so honestly — don't fake it
- Family snippets should feel like a parent noticing their kid, not an astrologer
- The quote must feel like it could ONLY be about that specific person today
- **Delegation Trap**: When delivering the final briefing as text (e.g., for Telegram cron jobs), ensure the Python code for generating the final formatted output is executed directly via `execute_code`. Delegating the entire briefing generation task can result in a subagent returning its *plan* instead of the actual formatted *text*, which breaks the delivery contract. The Python code blocks provided within this skill are intended for direct execution, not for re-planning by a subagent.
- **Keep output screenshot-length**: V1 ≤18 lines; V2 (shipped) 18–24 lines including signature — the vibe sections legitimately need more room. The hard rule is phone-readable in one scroll on Telegram, not a line count.
- **The NEXT STEP is the most important section.** The user's directive: "Becca and I need to know 'so what!?' Like, the next step. What do I do about that?" If the briefing only describes what's happening without giving a concrete action, it failed. Actions must be specific and executable: "Text Michael the one word: 'spleen'" or "Say 'I'll think about it' to the first request" — not "practice presence" or "trust yourself."
- **Load family birth data from `~/work/next-step-bot/family.json` FIRST**, before computing anything else. Don't grep the filesystem looking for it. On every profile tested in this deployment, plain `~` already resolves into the profile home, so the file lives at `os.path.expanduser("~/work/next-step-bot/family.json")` — do NOT build `~/.hermes/profiles/<profile>/home/work/...` paths: they nest the profile home inside itself and 404 (verified failure 2026-08-20). Use `os.path.expanduser()` and verify with `os.path.exists()` before `open()`. If the file doesn't exist, fail loudly rather than inventing birth data.
- **Run the channel-completion + natal-hit analysis BEFORE drafting the quote.** This is the single highest-leverage move for quality. Without it the quote falls back on horoscope language.
- **Use `cosmic_calculator.calculate_natal_chart(name, birth_dt_utc, lat, lon, tz)` from `~/work/OpenHumanDesignMCP/hd-mcp-server/src`, not a made-up `compute_natal_gates()` function.** The chart dict exposes `chart["all_active_gates"]` (list of ints) and `chart["defined_channels"]` (list of `{"name": str, "gates": tuple}`). The standard `chart["personality_planets"]`/`chart["design_planets"]` dicts also work. `chart["type"]` can be None even on a correct run — rely on `profile`, `authority`, `defined_centers`, `undefined_centers`, `all_active_gates` (verified 2026-08-20). See `references/transit-analysis-recipe.md` for the worked example.
- **Don't trust the gate→center map in the reference file blindly.** It has known mis-classifications (gate 21 listed in both Head and Heart, gate 38 placed under Root when it's Spleen/Root, gate 30 mis-mapped). When the map matters for "open center conditioning" notes, cross-check against the actual transit_planet center field returned by `calculate_transit_positions` (`d['center']`) before writing.

## Reference Files

- `references/transit-analysis-recipe.md` — canonical `CHANNEL_NAMES` dict, gate→center map, and the three-step analysis recipe with a worked example. Read this if the transit computation section above isn't specific enough.

Read reference files with `skill_view(name='daily-transit-briefing', file_path='references/transit-analysis-recipe.md')` — never `find /` or a filesystem search for them (a bare `find /` hung 180s+ once; the skill files live under the active profile's skills dir, not a shared path).