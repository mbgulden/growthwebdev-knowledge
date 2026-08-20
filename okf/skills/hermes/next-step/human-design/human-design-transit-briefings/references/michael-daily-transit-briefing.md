# Michael Daily Transit Briefing Reference

Use when the daily transit cron asks for Michael's personalized briefing, especially when the requested `daily-transit-briefing` / `human-design-guidance-systems` skills are missing but this umbrella skill is available.

## Michael baseline
- 3/5 Splenic Projector.
- Fear Motivation.
- Cross of Rulership 4.
- Birth input: Dec 10 1989, 17:07, Simi Valley, CA.
- Defined centers: G, Heart/Ego, Spleen, Throat.
- Channels: 1-8 Inspiration, 44-26 Surrender.
- Split Definition.
- Open centers: Ajna, Head, Root, Sacral, Solar Plexus.

## Current-work translation layer
Favor actions tied to Michael's real-life lanes:
- Revenue first: Active Oahu Tours follow-ups, booking flow, lead/partner outreach.
- Leads/trust next: concise AI consulting or HD Engine outreach that can become money.
- Avoid turning the brief into more infrastructure tasks unless transits strongly support it.
- Projector/AuDHD constraint: one executable action, not a stack of homework.

## Michael V2 screenshot-ready shape
When the prompt asks for V2, keep the final under the requested line cap and use this exact high-level order even if the prompt also includes an older Version B block:

```text
⚠️ Skill(s) not found and skipped: ...   # only when the cron prompt explicitly requires it

**BOLD ALL-CAPS HEADLINE.**
1-2 sentence opening grounded in computed gates and Michael's design/work.

TODAY'S VIBE: Morning — ...
Afternoon — ...
Tonight — ...

ONE THING: one concrete action Michael can do today, preferably revenue/leads/trust aligned.
FOR YOUR PEOPLE: one concrete action involving Becca or a child.

FAMILY SNIPPETS:
💫 Becca: one sentence.
💫 Benjamin: one sentence.
💫 William: one sentence.
💫 Victoria: one sentence.

SHARE-WORTHY LINE: "..."
— Fred
```

If the prompt supplies an older "So What" / "For them" block AND asks for V2: keep the V2 order, but honor any *explicit constraints* the older block imposes (line cap, missing-skill notice, concrete one-action requirement). Example: a V2 prompt that includes a legacy "So What" section should still produce one concrete revenue-aligned ONE THING and one FOR YOUR PEOPLE action — the older block's required action verb survives.

## Family snippet constraints
If full natal data for family members is not available in the session, do not invent personal transit overlays. Write each snippet from the computed collective transits plus known family context, phrased as practical support.

Known family context from prior briefing templates: Becca is Michael's wife; kids are Benjamin, William, and Victoria.

## Engine vs. user-supplied baseline discrepancy
`calculate_natal_chart()` can return a partial / drift-state chart (Jul 27 2026: it returned profile `2/4`, definition `Single`, defined centers `['Heart/Ego','Spleen']` — missing G, Spleen absent, cross Right Angle of Rulership 4 still came back, but channels list empty). The user-supplied prompt baseline of `3/5, Split Definition, G+Heart+Spleen+Throat, channels 1-8 + 44-26` is authoritative for *thematic* reasoning (motivation / authority / defined-open center framing / channels / incarnation cross framing). Use the engine strictly for today's transit gates and the conditioned-channel list. Do not silently rewrite the briefing to match the engine output.

Quick sanity check that the engine is even close to expected: confirm `personality_sun_gate == 26` (Michael's incarnation-cross sun) before trusting anything else.

## Picking the headline from conditioned channels
When 3–5 channels temporarily complete in one transit, lead with whichever channel theme most aligns with Michael's current revenue/leads lane:

| Channel | Theme | Headline angle |
|---|---|---|
| 21-45 (Money Line) | Resources, hunting, mastery | Active Oahu / HD Engine / consulting asks |
| 30-41 (Recognition) | Fantasy, contracting, feeling-limits | Visibility / branding / a share post |
| 7-31 (Alpha) | Voice leading others | Throat-y work; record audio, lead a call |
| 10-20 (Awakening) | Now, presence | Quiet, fewer words |

A slow-moving transit (Saturn, Pluto, True Node, Lilith) landing on a natal gate that completes a conditioned channel is the strongest specific lever — name the planet + gate.line + the *natal center it lights up* in the opening sentence or headline so the brief is concrete, not abstract.

## Headline dimension: defined-center flood (Projector signal)
When 4+ transit gates all hit a single *defined* center (e.g. Sun 33, Mars 12, Jupiter 31, Uranus 20 all on the Throat), that is itself the headline. Projector-specific signal: defined Throat getting activated by multiple planets at once = invitation pressure crank. Pair with the strongest single channel completion (e.g. 20-10 Awakening) for the *mechanism* and the multi-center flood for the *pressure*. This is a dimension independent of conditioned channels — flagged Jul 31 2026.

## Session transcripts

### Jul 27 2026
- Transit gates: `[11, 17, 20, 21, 26, 29, 30, 31, 38, 41, 45, 47, 53]`.
- Conditioned channels: **7-31 The Alpha**, **10-20 Awakening**, **21-45 Money Line**, **30-41 Recognition**.
- Headline lever: Money Line + Saturn in Gate **21.6 (Master/Hunter)** hitting Michael's natal **Heart/Ego** defined center — biggest single "today" signal. Headline leaned revenue / Active Oahu.
- Notable fast movers landing on natal gates: Sun 31.3 (Alpha voice line), Moon 38.3 (natal Root), Mars 45.4 (natal Throat), Venus 47.3 (natal Ajna).
- Headline picked: **"MONEY LINE LIGHTS UP — HUNT WISELY, OR HUNT EXHAUSTION"** with Saturn-21.6 warning.
- ONE THING: "Pick one Active Oahu or HD Engine ask in your inbox, reply with a clear yes/no, send. Six seconds for the spleen, then send."
- Engine signature drift detected (profile 2/4 vs 3/5); user prompt baseline trusted.

### Jul 31 2026
- Missing-skill notice fired: `daily-transit-briefing` and `human-design-guidance-systems` were listed but absent from the profile. Fell back to this umbrella per the existing pitfall rule. Opened the cron reply with the required `⚠️ Skill(s) not found and skipped: ...` notice verbatim.
- Transit gates: `[6, 10, 11, 12, 17, 19, 20, 21, 29, 30, 31, 33, 41, 53, 55]` (15 planets total — Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto, True Node, Mean Lilith, True Lilith, Earth, South Node).
- Center hits on Michael's defined centers: **G** (True Lilith in 10), **Heart/Ego** (Saturn R in 21.6), **Throat** (Sun 33, Mars 12, Jupiter 31, Uranus 20 — *all four Throat gates active simultaneously*).
- Channel completion: **20-10 Awakening** completed via Uranus 20 + True Lilith 10, lighting up the G center (Michael's identity-circuit). This was the strongest single *mechanism* of the day.
- Headline picked: **"TODAY THE WHOLE THROAT IS LIT — AND YOUR G-CENTER IS WAKING UP"** — fused the multi-center flood (4/4 Throat gates = Projector invitation pressure) with the channel completion (20-10 Awakening = identity-Now).
- ONE THING: "Decline at least one invitation or request today — politely, fast, no explanation. Let the throat pressure discharge as a 'no.'"
- FOR YOUR PEOPLE: "Take Benjamin (or whichever kid is awake) outside for 20 minutes of unstructured time — no phones, no questions, just walk."
- New mechanical learning: ALL defined Throat gates active at once is a *headline by itself* — a Projector-specific signal of invitation/pressure overload. Future briefs should flag this as a dimension independent of conditioned channels.
- New dict-shape learning: `calculate_transit_positions()` returns `{longitude, gate, line, gate_name, center, retrograde}` per planet. `position_in_gate` and `position` are both `None` — do not use them.

### Aug 6 2026
- Missing-skill notice fired again: `daily-transit-briefing` and `human-design-guidance-systems` listed but absent. Loaded umbrella as fallback.
- Transit gates (15 planets): `[7, 23, 62, 46, 12, 33, 21, 20, 17, 41, 30, 11, 61, 13, 29]`.
- Cross-referenced with `/home/ubuntu/work/hd-reports/people-registry.json` and chart JSON files — found full natal gate lists for Becca (11 gates), Benjamin (14), William (15), Victoria (11). Confirmed transit→natal hits without inventing natal overlays.
- Headline mechanism: transit Sun in **Gate 7** + Earth in **Gate 13** = **Channel 7-13 (Leader / Role of Self)** completes on Michael's G Center. This is the G-anchored equivalent of the headline-picking table's existing entries. Picked "CHANNEL 7-13 OPENS — THE LEADER EASTER EGG" as the headline, framed around self-direction + voice + leadership.
- Family cross-references (mechanical, not invented):
  - **Becca** (gates 1,4,11,25,26,44,45,46,51,54,58): Venus 46 hit her defined Gate 46. Snippet = "Venus in her Gate 46 — body-love, physical affection."
  - **Benjamin** (gates 4,5,7,14,25,37,38,40,46,48,51,53,63,64): Sun 7 hit his Gate 7. Snippet = "Sun in his Gate 7 — The Role of Self in the Herd. He wants to be seen."
  - **William** (gates 1,3,4,5,6,25,26,46,49,50,54,59,63,64): Venus 46 hit his Gate 46. Snippet = "Venus in his Gate 46 — touch and warmth."
  - **Victoria** (gates 13,27,34,36,38,39,42,52,58,61,63): Earth 13 hit her Gate 13. Snippet = "Earth on her Gate 13 — the Listener. Tuned to your tone."
- ONE THING: "Reply to the message you've been sitting on for 3+ days — before 3pm." Mars in Michael's Throat Gate 12 + Sun in G = message-as-medicine lever.
- FOR YOUR PEOPLE: "Tell Becca 'you look good' in the first hour." Venus on her Gate 46 needs body-level compliment.
- New mechanical learning: **Channel 7-13 completes on Michael's G whenever transit Sun and Earth both land in G gates** (Sun+Earth walk the I Ching wheel one gate apart in opposing hexagrams 7+13, 1+8, 2+14, etc.). This is the same pairing pattern that produces 10-20 (Awakening via Lilith+Uranus on Jul 31). Adding 7-13 to the headline-picking table.
- New workflow learning: when the cron prompt supplies a family list, **probe `people-registry.json` first** before defaulting to "write collective support snippets." If the registry chart JSON is present and loadable, you get *mechanical* cross-reference data (not invented natal exposition), which produces stronger per-child snippets. The existing pitfall "Do not invent natal overlays for family members" still holds — the rule is about *invention*, not about *looking up data the system already has*.

### Aug 8 2026 — Cross-flood headline signature
- Missing-skill notice fired again (daily-transit-briefing + human-design-guidance-systems listed, absent). Loaded umbrella as fallback.
- Engine path: orchestrator-profile working tree is at `/home/ubuntu/.hermes/profiles/orchestrator/home/work/`, so the engine lives at `/home/ubuntu/.hermes/profiles/orchestrator/home/work/OpenHumanDesignMCP/hd-mcp-server/src`. First candidate failed; second worked. Recording for future cron runs.
- Transit gates (15 planets): `[7, 45, 56, 46, 12, 33, 21, 20, 17, 41, 30, 11, 54, 13, 29]`.
- **Rare signature detected: ALL FOUR gates of Michael's incarnation cross simultaneously activated.** Sun in Gate 7, Earth in Gate 13, North Node in Gate 30, South Node in Gate 29 — Cross of Rulership 4 fully lit. This is the strongest same-day lever possible for Michael's Rulership archetype: leadership-that-sculpts-the-collective, not ego.
- Conditioned channels involving cross gates: 29-46 Discovery (transit Venus 46 + S.Node 29); 30-41 Recognition (Pluto 41 + N.Node 30); 13-33 Prodigal (Jupiter 33 + Earth 13); 7 alone doesn't form a conditioned channel today but anchors the cross.
- Headline picked: **"YOUR CROSS IS FULLY LIT — ALL FOUR GATES, ALL AT ONCE"** — led with the cross-flood, not the channel completions. Channel completions underneath were the *mechanism*, the cross-flood was the *signature*.
- ONE THING: "Pick ONE venture (Prismatic, a tour site, or a stalled deck) and make the call you've been deferring. Don't draft it. Tell one person the answer out loud before lunch. The 7-13 axis wants the word out before noon."
- FOR YOUR PEOPLE: "Sit with Becca for ten minutes of no-phones, no-questions. The 29-46 Discovery channel wants to be witnessed, not solved. Let her find the sentence."
- Family snippets were written from the cross-flood (Becca, Benjamin, William, Victoria) rather than per-gate cross-reference — registration probe wasn't repeated this session, so collective-transit support language was used. The headline mechanism (cross-flood) dominated the family section, which is appropriate when the day's signature is collective.
- New mechanical learning: **All four gates of an incarnation cross activated at once** = cross-flood. This is mechanically predictable because (a) Sun+Earth always oppose each other (gate N ↔ gate N+1 mod 64 in opposing hexagrams), (b) N.Node+S.Node always oppose the same way, and (c) every Right Angle Cross is built from two opposing Sun-Earth pairs. Cross-flood days happen whenever Sun lands in one cross gate while Earth lands in its opposite, and the Nodes simultaneously land in the other pair. Detection recipe: take the four gates of the recipient's incarnation cross; check whether transit Sun, Earth, True Node, and South Node together cover all four. When yes → headline-grade event.
- New headline-picking dimension: cross-flood sits *above* the existing five (cross-gate single hit, slow-mover-on-natal, all-six-undefined-conditioned, single-defined-center flood, top-conditioned-channel-revenue-aligned). When a cross-flood exists, prefer it; conditioned channels underneath are mechanism, not headline.
