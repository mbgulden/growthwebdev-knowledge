---
name: personal-named-recipient-telegram-briefings
description: Deliver warm, brief, personal morning briefings to a named user via Telegram when the prompt gives a formatted-briefing template (greeting + bullet sections). Covers the tension between warm-format prompts and the strict Telegram cron output contract — when nothing is actionable, deliver the greeting + one signal line, not manufactured bullets. Use when a Hermes cron job is registered with deliver=telegram and the prompt names a specific person, asks for a warm tone, and gives an explicit format scaffold (greeting, bullets, sign-off). Distinct from `telegram-cron-output-contract` (operational alerts, one bolded action line) and `scheduled-journal-recaps` (recap file generation, not user-facing delivery).
---

# Personal Named-Recipient Telegram Briefings

## When to load

Load this skill when a Hermes cron job has all of:

- `deliver=telegram` (or similar) — the agent's stdout IS the user message.
- The prompt names a specific person (Becca, Michael, etc.) and addresses them in second person.
- The prompt gives a warm-tone format scaffold: a literal greeting ("Good morning, NAME"), bullet sections, a sign-off.
- The cron fires on a daily / morning cadence and reads from a journal / inbox / report tree for the past 24h.

This includes personal morning briefings, weekly review pings, evening wind-downs, and "here's what moved today" digests for a single named user. It does NOT cover operational alerts (use `telegram-cron-output-contract`) or recap file generation (use `scheduled-journal-recaps`).

## The core tension (and the resolution)

The Telegram cron contract (`telegram-cron-output-contract`) says: stdout must be empty when nothing is active. A prompt that says "Start with 'Good morning, NAME' then 2-3 sentences + bullets" appears to contradict that — it explicitly asks for content.

The resolution is structural, not textual:

- The greeting and the *shape* of the format are non-actionable headers. They are scaffolding, not content.
- The *content* of the briefing must be either genuinely actionable signal OR an explicit "nothing to act on" line.
- Do not manufacture bullets to fill empty sections. If "Yesterday's highlights" would be empty, omit the heading. If "needs attention" would be empty, omit the heading. If everything is empty, the briefing is one line past the greeting: "Nothing actionable overnight — staying quiet is the move."
- The user's design (Human Design, energy profile, role) is a *lens*, not content. One line of lens framing at most, never a paragraph on top of a quiet day.

## Required stdout shape

```
Good morning, <Name> ☀️

[Single signal line OR one short paragraph if there IS something actionable.]

[OPTIONAL: one bullet section, only if it has ≥1 non-empty bullet]
- <bullet>

[OPTIONAL: HD-lens line, only if the prompt asks for one and the day has something to frame]
```

That is the entire deliverable. No section labels for empty sections, no "Everything is fine, nothing to do" filler, no closing signature unless the prompt explicitly asks for one.

## What NEVER goes in stdout

- Multi-section recap paragraphs ("Yesterday's highlights / Today's focus / What's blocked / Splenic note") when each section is just restating that nothing happened.
- "Nothing to report, all systems nominal, staying quiet today" — this is a recap paragraph pretending to be silence. Either say one line or say nothing.
- Invented chart/transit/HD mechanics to fill the lens slot. If the day is genuinely still, the lens says "stillness is correct" — that's one phrase, not a paragraph.
- "Let me check..." / "I noticed..." narration.
- Closing signatures like "— Sage" unless the prompt asked for them; the system adds delivery metadata.
- Bullet lists of zero items under a section heading.

## Workflow

1. **Resolve the date** in the recipient's timezone with `date` and the prior date for "yesterday." Use the recipient's TZ (Mountain Time for Michael/Becca), not UTC, for the greeting and section labels.
2. **Read the source of truth** for the past 24h. For Becca morning briefings this is `~/work/next-step-becca/journals/YYYY/MM/DD.md` (yesterday's recap) + any new HD reports in `~/work/hd-reports/<name>/`. The path may need the HOME-expansion recipe (see Pitfalls).
3. **Read SOUL.md** once per session to refresh the recipient's design constraints. Don't re-read every cron run — load on cold start.
4. **Decide the signal shape.** Three options, in priority order:
   - **Silence path:** if there are zero actionable items AND no new content of any kind AND yesterday's recap itself was a quiet-monitoring day, return `[SILENT]` (per the cron contract).
   - **Single-signal path:** if there is one concrete thing (a new report landed, a decision is pending, a follow-up is due), one short paragraph plus one bullet section if the bullet count is ≥2.
   - **Quiet-day framing:** if the day is quiet but the prompt explicitly asks for a daily briefing shape (most do — they want *some* delivery to keep the cadence visible), greeting + one "nothing actionable overnight — X is the move" line. No bullets.
5. **Lens discipline:** if the prompt asks for an HD lens line, write one short line that names the design's correct response to the *actual* day. "Two days of stillness = Hermit incubation" is fine. "Splenic authority whispers wait" is fine. Four sentences of HD framing on top of pure stillness is content, not a lens.
6. **Verify stdout before delivering.** Re-read what you're about to send. If it has section headings with no content under them, delete the headings. If it has a "nothing to report" paragraph, compress to one line or `[SILENT]`. If the HD lens section is longer than the actual content, the lens is the content — that's wrong.

## Pitfalls

- **HOME expansion trap.** When the cron runs from a Hermes profile (e.g. `fred`, `sage`, `orchestrator`), `$HOME` resolves to `/home/ubuntu/.hermes/profiles/<name>/home`, not `/home/ubuntu`. `~/work/next-step-becca/journals/...` expands to the profile-home variant and exists via the symlink, but `read_file` and `stat` from a fresh terminal may follow or may not — verify by reading the file once and confirming. If it fails, use the canonical path `/home/ubuntu/work/...` or the absolute path the symlink resolves to. Don't loop on path guessing.
- **Don't re-read SOUL.md every run.** It changes rarely. Read once per cold start; quote from memory or session context on subsequent cron runs. Re-reading wastes the session's tool budget.
- **The "format asks for X" trap.** A prompt that says "Start with greeting, then bullets, then sign-off" is a *shape*, not a *quota*. If you would write "Yesterday's highlights: None" then the section doesn't exist — write nothing instead. The recipient will trust a shorter message more than a longer one with empty sections.
- **HD lens ≠ content.** When the day is genuinely still, the lens says "stillness is correct" in one line. A common failure is to fill the lens slot with three paragraphs of design philosophy to balance the absence of news. Don't.
- **Don't pre-narrate.** "Let me check yesterday's journal…" never goes in stdout. It's a tool-call step, not part of the briefing.
- **Don't claim delivery.** The cron runner owns delivery. Stdout is the message; the system handles sending. Do not call Telegram-sending helpers from inside the script.
- **Quiet is not a bug.** A 6/2 Splenic Projector who receives "nothing actionable overnight — staying quiet is the move" is being served correctly. Manufacturing a "here's a thought about your week" filler to feel helpful is a violation of the recipient's design. The spleen speaks once; if there's nothing to say, say nothing.
- **Sign-off lines from the agent identity** (e.g. "— Sage", "— Fred") should only appear when the prompt explicitly asked for them. The system already attributes delivery.
- **Cross-reference yesterday AND today.** When the briefing is at 8am and yesterday's recap was a quiet-monitoring day, check today's date file too — sometimes the morning cron fires before today's recap lands, and the absence itself is the signal.
- **The "named-slot fill" trap (most common cause of bloat).** When the prompt explicitly names slots ("Yesterday's highlights", "Anything that needs attention", "Splenic wisdom note"), there's a strong pull to *fill each named slot with something*. The skill rule is: named slots are a *shape* the prompt is willing to receive, not a *requirement* to fill. If "Yesterday's highlights" would be "nothing happened," the section is omitted, not filled with a paragraph about how nothing happened. If "needs attention" would be empty, omit. If "Splenic wisdom note" would be the same stillness-correct line you wrote yesterday, omit or compress. A briefing with three bullet sections of synthesized absence is worse than no bullets at all.
- **Day-N+1 of stillness compounds the trap.** When yesterday's own recap was about the stillness itself ("three days of identical empty snapshots is no longer the Splenic whisper — it's the same whisper asking whether the listening posture itself has become a habit"), the day-N+1 briefing must NOT then write a multi-sentence essay about the stillness. The previous day's memo is *confirmation* that this is now a `[SILENT]`-eligible day, not raw material for today's lens. If yesterday's recap was already a still-day memo, today is either `[SILENT]` or a one-line continuation.
- **Sign-off even when prompted.** A prompt that says "warm but not verbose" still does not authorize "Have a good one. I'm here if something knocks." unless the prompt *explicitly* asked for a sign-off. The "warm" descriptor is for tone of voice inside the (short) message, not for adding a closing courtesy line. When in doubt: no sign-off.

## When to return `[SILENT]`

Return exactly `[SILENT]` (nothing else) when ALL of:

- The prompt explicitly says "respond with exactly '[SILENT]' (nothing else)" OR the standard cron contract says so.
- There are zero actionable items in the past 24h.
- The day is the second or later in a quiet run (no new content, no new reports, no new decisions).
- The recipient's design lens would say "stillness is correct" — i.e. silence IS the warm delivery.

If the prompt asks for a daily briefing shape but the day is the FIRST of a quiet run (yesterday was busy, today is quiet), one signal line is better than `[SILENT]` — the cadence shift is itself the signal.

## Anti-pattern examples

❌ **Manufactured recap when nothing happened (what I shipped today):**

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

✅ **Correct shape for the same day:**

```
Good morning, Becca ☀️

Nothing actionable overnight — second quiet monitoring day in a row. The 6/2 Hermit stretch is doing its work; trust the incubation, no need to manufacture momentum.
```

Or, if the prompt's cadence-shift rule applies and this is the first quiet day after a busy one:

```
Good morning, Becca ☀️

- No new reports, no new journal entries with substance, no pending decisions.

Quiet day — the spleen says *wait*, and that's a complete answer.
```

## Verification

There is no canonical verifier for this skill yet (TODO). Until one exists, the verification recipe is human review:

1. Re-read what you wrote.
2. If it has empty section headings, delete the headings.
3. If the HD lens section is longer than the content, the lens is the content — wrong.
4. If the briefing could be cut to one signal line without losing information, cut it.
5. If `stdout` starts with anything other than the greeting, the agent narrated — wrong.

A future `scripts/verify_personal_briefing.py` should assert: stdout length < 600 chars by default (override per-recipient), no empty section headings, HD lens line count ≤ 2, no closing signature unless prompt requested, no "Let me / I will / I am going to" narration, no `print(...[SILENT]...)` literal marker (use exit silent).

## Related skills

- `telegram-cron-output-contract` — operational alerts. The hard structural rules (no scaffolding, no narration, exit silent when nothing active) come from there. This skill layers the *warm-format prompt* reconciliation on top.
- `scheduled-journal-recaps` — when the task is to write a recap file to disk, not deliver a Telegram briefing. Different deliverable shape.
- `human-design-transit-briefings` — when the briefing content is computed transit/natal mechanics. Distinct from the daily "what moved overnight" shape.
- `projector-aware-communication-discipline` — Becca/Michael projector-aware defaults that this skill's lens line should respect (one thing at a time, recognition before guidance, don't dump).