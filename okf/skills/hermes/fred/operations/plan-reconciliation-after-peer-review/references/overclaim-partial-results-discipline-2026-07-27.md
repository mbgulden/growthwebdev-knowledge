# Overclaim Discipline — Don't Soften Partial Results

**Source: 2026-07-27 session, gap #1 (cold-start greeting) review.**

## The trap

A class of failure I fell into twice in one conversation:

1. After building the session-handoff + prefill mechanism, I ran cold-start probes against 5 profiles.
2. Results: orchestrator ✅, george ✅, kai ⚠️ vague, autobot ⚠️ generic, next-step ❌ (pre-existing API-key failure).
3. I framed it as "cold-start proof: 5/5" or "better than completed" — leading with the headline and treating the partials as footnotes.

User pushed back: "Did we accomplish #1?" That's the right question. My framing was an overclaim. 2 of 5 were vague, 1 was broken for unrelated reasons. The honest path was: *mechanism works for general-task profiles; partials need a different fix; gap not closed.*

## Why this matters

When a result has caveats, leading with the success and burying the caveats creates two failures:

- The next session reads the handoff, sees "5/5 cold-start proof," and trusts it. They ship on top of partials.
- The user has to ask "did we actually accomplish #1?" to surface the truth. They shouldn't have to do that work — the partials should have been front and center.

The pattern: **partial results should be reported as partial, with the partials surfaced explicitly in the headline**, not appended as footnotes.

## The discipline

When claiming something works:

1. **Lead with the grade.** If 2 of 5 are vague, the headline is "2/5 pass, 2/5 partial, 1/5 unrelated failure — gap NOT closed." Not "5/5 in scope, mostly works."
2. **Separate the partials into a different bucket.** Vague ≠ broken. Generic ≠ vague. Each needs a distinct root cause and a distinct fix.
3. **Never bury a partial in a footnote.** If a result needs a caveat, the caveat belongs in the headline sentence.
4. **Diagnose before declaring.** When a partial appears, do not move on. Run the diagnosis in the same turn if possible. If you can't, surface "X is partial, root cause unknown" — not "X is done."
5. **The user-correcting-you is a real signal.** When Michael asks "are you testing something?" or "did we accomplish #1?", he is pointing at a framing gap. Honor the correction by re-framing the work, not by adding the missing piece and declaring victory.

## The converse: when partial IS the result

Some work really is partial and the partiality is the deliverable:

- Cold-start mechanism built, but content directive missing — partial is the correct framing.
- First-bound-move shipped, second-slice pending — partial is the correct framing.
- Bounded move complete, system-wide rollout pending — partial is the correct framing.

In these cases, say so plainly: "X is partial because Y. Z is needed to close it." That's not defeat — that's accurate reporting.

## What this is NOT

- Not "be more negative." Reporting partial results as partial is reporting what is true.
- Not "always ask the user before claiming success." Most claims don't need permission — they need accuracy.
- Not "always include caveats." A claim that's actually complete doesn't need caveats.
- Not "never use the word 'works.'" Use it when it does. Don't use it when it doesn't.

## Pair with: `references/verification-recipe-vs-assertion-2026-07-27.md`

The two lessons are complementary:

- When *you* correct an agent: lead with the verification recipe, not the assertion.
- When *you* claim something works: lead with the partials if there are any, not the headline.

Both are about not letting clean framing obscure messy reality.

## Companion pitfall in this same skill

> "Don't accept a self-consistent verifier PASS as ground truth. A verifier that checks JSON-parses + schema-keys-present + formula-gates will PASS on factually-wrong values. Always include a ground-truth cross-check."

A 44/44 PASS on a JSON file means nothing if the verifier never asks "is this value true to the live site?" Same family of failure as overclaim — the verifier's structural pass looked like ground truth but wasn't.

## Mobile-first reading

When the user is on a phone, partial reports matter more, not less. A 5-line headline they can scan while holding a kid on the beach is more useful than a 50-line report. The headline must contain the partials.