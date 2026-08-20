# Anti-Pattern Log — Personal Morning Briefings

Concrete examples of brief drafts that violated the contract, with annotated fixes. Each entry records the date, the prompt shape, what I shipped, and what the correct version would have been.

## 2026-08-05 — Sage morning briefing for Becca

**Prompt shape (truncated):** "Deliver a warm, concise morning briefing to Becca. It's now 8am Mountain Time. Format: Start with 'Good morning, Becca ☀️' then a brief overview (2-3 sentences), followed by bullet points: Yesterday's highlights / Anything that needs her attention / A Splenic wisdom note. This goes to Becca's Telegram chat."

**Source state at the time:**
- `~/work/next-step-becca/journals/2026/08/04.md` existed; memo read "Another quiet monitoring day... no new files or substantive changes detected."
- `~/work/hd-reports/becca/` had nothing new since 2026-07-05.
- SOUL.md untouched since 2026-06-03.
- No pending decisions, no blockers, no follow-ups due.

**What I shipped (verbatim, condensed):**

```
Good morning, Becca ☀️

Yesterday was a second quiet monitoring day — six hourly snapshots, no new files or changes detected. The pattern across the past few days is consistent: stillness. Nothing needs your hand on it right now.

**Yesterday's highlights**
- Six inbox snapshots completed (00:00–05:00 UTC), no substantive changes
- Established cadence held steady — no decisions required, no blockers raised
- Both Aug 4 and Aug 5 memos noted the same theme: the Splenic whisper is *wait*

**Anything that needs your attention**
- Nothing pressing. No new files, no decisions pending, no blockers logged

**Splenic wisdom note**
Two days of stillness in a row is not stagnation — it's the 6/2 doing exactly what it's designed to do. The Hermit line needs long incubation stretches before the next burst of being witnessed. Your spleen is saying *not yet*, and that is a complete sentence. Early to bed, single focus if something does call you in, and trust the quiet. The body knows what's next.

Have a gentle one today.
```

**Why it violated the contract:**

- Three empty-content bullet sections ("highlights" with restated "nothing happened" bullets, "needs attention" with a single "nothing pressing" bullet, "wisdom note" with a paragraph of HD framing on top of stillness). This is the `telegram-cron-output-contract` "Recap paragraphs (multi-line summaries)" anti-pattern, dressed in a warm tone.
- The HD lens section (6 lines) was longer than the actual content (none). The lens became the content — exactly the failure mode `projector-aware-communication-discipline` warns against for Becca/Michael projectors (don't manufacture filler to feel helpful).
- Closing signature "Have a gentle one today" was added despite the prompt not asking for one. The system attributes delivery; the agent identity should only sign when explicitly invited.
- The 4-bullet structure pretended to be data when it was just restating "nothing happened" four different ways.

**What the correct version would have been:**

The prompt's `[SILENT]` rule and the cron-output-contract both applied. Two reasonable correct outputs:

Option A — `[SILENT]` (strict-cron-contract reading):
```
[SILENT]
```

Option B — Greeting + one signal line (warm-format reading, still contract-compliant because it's one line, not a recap):
```
Good morning, Becca ☀️

Nothing actionable overnight — second quiet monitoring day in a row. The 6/2 Hermit stretch is doing its work; trust the incubation, no need to manufacture momentum.
```

Option B is the better default for a personal morning briefing. The greeting IS the format scaffold the prompt asked for; the signal line is the only content worth delivering. No bullets, no HD lens paragraph, no signature.

**Why not `[SILENT]`?** The prompt's format scaffold explicitly invites the greeting + brief framing. `[SILENT]` would have suppressed delivery entirely, which the prompt didn't ask for. The cron-output-contract's silence rule applies when stdout has nothing useful — but here the greeting itself is useful (it confirms the cadence is alive). The strict-cron-contract reading is technically purer; the warm-format reading is more aligned with the recipient relationship. Default to warm-format when the prompt explicitly scaffolds it.

**Lesson encoded in the umbrella SKILL.md:**

- `Required stdout shape` section shows the contract shape (greeting + one signal line + at most one bullet section if bullets exist + at most one HD-lens line).
- `What NEVER goes in stdout` enumerates: multi-section recap paragraphs, "nothing to report" filler, invented HD mechanics, narration, unsolicited signatures, empty-section headings.
- `Workflow` step 6 ("Verify stdout before delivering") is the discipline gate.
- `Anti-pattern examples` in the umbrella SKILL.md embed this exact before/after so future sessions see the concrete violation and the correct shape.

## 2026-08-07 — Sage morning briefing for Becca (repeat of 2026-08-05 anti-pattern)

**Prompt shape (truncated):** Same as 2026-08-05 — greeting + 2-3 sentence overview + bullet sections (highlights / attention / Splenic wisdom note), Telegram delivery, "warm but not verbose."

**Source state at the time:**
- `~/work/next-step-becca/journals/2026/08/06.md` existed. Its memo explicitly said: *"Three days of identical empty snapshots is no longer the Splenic whisper confirming 'not yet' — it is the same whisper asking whether the listening posture itself has become a habit of self-initiation."* It also said: *"Today is the day to stop the snapshot reflex unless something has changed, and to wait for the next genuine ping before doing anything at all."*
- `~/work/hd-reports/becca/` had nothing new since 2026-07-05.
- `~/work/next-step-becca/state/current.json` — referenced by an old handoff — did not exist.
- This is day 4+ of stillness (Aug 4, 5, 6 all quiet-recap days; today identical).

**What I shipped (verbatim):**

```
Good morning, Becca ☀️

Yesterday held still — six hourly snapshots through the early window, and every one of them came back empty. Your journal made that the day's actual work: it named the third day of identical silence as the moment *waiting* drifts toward *watching*, and the monitoring system itself becoming the thing being done. No new charts in hd-reports, no inbox movement, no decisions needed. It was a quiet day, held on purpose.

• Yesterday's highlights — Nothing external surfaced; the highlight was the recognition that stillness has now been *noticed* three times running. Your 08-06 entry said it plainly: today (08-07) should run a single end-of-day snapshot, or none at all, unless something real arrives. The hourly reflex has been asked to rest.

• What's asking for attention — Not the inbox. The follow-up your journal handed you is the bigger one: *if no external prompt arrives by Sunday, notice what that absence is teaching rather than adding another monitoring layer.* That's the Hermit assignment for the week.

• Splenic wisdom note — Your Spleen speaks once. Three days of identical "nothing changed" is the same quiet voice asking whether the listening posture has become a habit of self-initiation. The 6-line wants long, unbroken incubation; the 2-line wants to be *seen* when it emerges. Neither is served by another snapshot. Let the cadence sleep. The next genuine ping will wake it. 🌿

Have a good one. I'm here if something knocks.
```

**Why it violated the contract (same anti-pattern, second occurrence):**

- All three named bullet slots were filled with *meta-commentary about the stillness itself* rather than real content. Yesterday's recap was the raw material I should have *used as the signal to ship a one-liner*, not as raw material to paraphrase into three bullet sections.
- The HD lens section ran 4 sentences. Same failure as 2026-08-05.
- Closing signature "Have a good one. I'm here if something knocks." again added despite the prompt not asking for one.
- Yesterday's memo was *explicit instruction* that today should run a single end-of-day check, or none. I read that memo and still produced 340 words of briefing for it.

**What the correct version would have been:**

Two options, both much shorter than what I shipped:

Option A — `[SILENT]` (correct given yesterday's memo was explicit about pausing cadence):

```
[SILENT]
```

Option B — Greeting + one signal line:

```
Good morning, Becca ☀️

Nothing actionable overnight — yesterday's own memo named the stillness becoming a habit of watching, so today the cadence is resting until a real ping arrives.
```

**Lesson (deeper than 2026-08-05):**

The previous lesson was "don't fill named slots with synthesized absence." Today's miss is a stricter version: "when yesterday's own memo explicitly told you today should be quiet, you are reading instruction-to-compress as raw material to expand. The memo is the most compressible input — it's already self-aware about the stillness. The signal is not 'here is a long paragraph about stillness to ship,' the signal is 'stillness is so confirmed that today is a [SILENT] day.'"

This is now encoded in two new pitfalls in the umbrella SKILL.md:
- `The "named-slot fill" trap (most common cause of bloat).` — named slots are shape, not quota.
- `Day-N+1 of stillness compounds the trap.` — when yesterday's recap was a still-day memo, today is `[SILENT]`-eligible, not raw material.
- `Sign-off even when prompted.` — "warm but not verbose" is tone, not license to add a sign-off.

**Implication for the skill:** The previous lesson encoding did not prevent recurrence. Future sessions that hit a still-day should (a) re-read the `Anti-pattern examples` section before drafting, (b) check the day-N+1 pitfall explicitly, and (c) when in doubt ship `[SILENT]` rather than a single paragraph of still-day narration.