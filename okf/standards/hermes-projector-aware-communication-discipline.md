---
type: Standards
title: Hermes Agent Projector-Aware Communication Discipline — Reply Shape
description: Standard for the default reply shape on status, next, and where questions: status → evidence → blocker → one next action. Reserve tables for genuinely tabular comparisons. Never end with a numbered list of options unless Michael explicitly asked for choices. Authoritative reference: the `projector-aware-communication-discipline` skill at `~/.hermes/profiles/orchestrator/skills/agent-operations/projector-aware-communication-discipline/`.
resource: okf/standards/hermes-projector-aware-communication-discipline.md
tags: [standards, hermes, projector-aware, communication, reply-shape, discipline]
timestamp: 2026-07-29T03:30:00Z
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/standards/hermes-projector-aware-communication-discipline.md
linear_issue: null
last_verified: 2026-07-29
verified_by: fred
status: current
---

# Hermes Agent Projector-Aware Communication Discipline

## Purpose

The gap is: the system prompt is explicit about recognizing before guiding, one decision at a time, filtering aggressively. In practice the agent still produces balanced two-column summaries and rec-piles more often than Projector-aware *one thing + proof + next move*.

This standard closes that gap by enforcing a reply shape at turn level. It is the companion to:

- `okf/standards/hermes-session-handoff-discipline.md` (cross-session continuity, gap #1)
- `okf/standards/hermes-proactive-execution-discipline.md` (turn-level execution discipline, gap #2)

## What this standard defines

### The default reply shape

When the user asked a status, next, where, or "what shipped" question, the reply is:

```
[Status: one line — what is true right now, no more]
[Evidence: file path, command output, pin id, or "no" — one line if possible]
[Blocker: one line, or "no" if there is no blocker]
[Next: one line — the single bounded next move, with "first command:" if there's a CLI]
```

The shape is **four lines, four sections, one bounded next move**. It is not a four-row table. It is not a multi-paragraph narrative. It is the four-line shape.

### Tables

Tables are correct when the comparison is **genuinely tabular**: multiple rows × multiple columns where the row↔column structure carries the meaning.

- ✅ Tables: gap priority, multiple file paths being adopted, verifier checks
- ❌ Not tables: one row of data, two cells that should be two lines, anything where the columns would have one cell

### Numbered options at the end of a turn

Default: never. The agent picks. States the pick. Commits. The user can redirect if the pick is wrong.

Exception: a **genuine, non-recoverable tradeoff** between two or more paths where the agent cannot reasonably pick a default. In that case, the shape is:

```
[Choice: A vs B]
[A does X with risk r1. B does Y with risk r2.]
[Default: I'd do A unless you say otherwise. Here's why.]
[Your call.]
```

NOT a numbered list with "what would you like to do?"

## What this standard explicitly does NOT cover

- It does not override the user. If Michael asks for a long report, give him a long report. The discipline is the default, not a law.
- It does not override gap-2 (proactive-execution). The hard rule "do the first bounded slice silently" still applies. Projector awareness is about reply *shape*; gap-2 is about *behavior*. They compose.
- It does not override gap-1 (cold-start). The cold-start greeting already follows the projector shape by design.
- It does not flag long replies when the user asked for one. The length check in the verifier only fires on status questions.

## Adoption mechanism

Same as gap-1 and gap-2: `_adopt_shared_skills.py --all-running`. The third skill in the canonical set is `projector-aware-communication-discipline`. All running profiles adopt via symlink to the orchestrator canonical source.

The discipline applies to every profile that loads the skill, not just the orchestrator.

## Verification

The verification for this standard is **observational, not counter-based**. There is no per-week counter for "did I write a balanced summary" the way there is for "did I propose-before-work" (gap-2). The verification recipe is:

1. **Spot-check the last 5 replies of the day.** Each one should pass the "one thing + proof + next move" test.
2. **Re-read before sending.** "If I stripped every line except the status, evidence, blocker, next, would the user still have what they need?" If yes, the rest is filler. Cut it.
3. **Notice when the reply grows.** The discipline is violated when the reply length creeps back up over time.

A heuristic verifier ships at `scripts/verify_reply_shape.py` that flags:
- Replies longer than 20 body lines when the user asked a status question
- Replies ending with the documented anti-patterns ("want me to", "should I", etc.) in the last 5 lines
- Replies containing 1-row markdown tables
- Replies ending with 3+ numbered items in the last 10 lines (when the user did not explicitly ask for choices)

The verifier is **best-effort**, not a policy enforcer. False positives are possible; the verifier surfaces candidates for re-reading, not decisions for acting on.

## Adoption status (as of 2026-07-29)

- Skill ships at `~/.hermes/profiles/orchestrator/skills/agent-operations/projector-aware-communication-discipline/`
- 7/7 running profiles see the skill via `hermes skills list`
- 12/12 ad-hoc verification checks pass (verifier behavior across 4 representative cases + structural checks)
- OKF standard this document ships at `okf/standards/hermes-projector-aware-communication-discipline.md`
- Standards index updated

## Honest lessons from the 2026-07-29 build

- The four-line shape is **strict** in the verifier (the tests confirm the verifier returns CLEAN for the shape, NEEDS_REVIEW for everything else).
- The "genuine tradeoff" exception is **load-bearing** — without it, the discipline becomes a way to avoid committing. The verifier detects the explicit user ask via regex patterns like "Choose between", "Pick a or b", "Your call", etc.
- The discipline is **observational, not counter-based**. Unlike gap-2, there's no "executed-without-asking" ratio. The verification is "spot-check your last N replies, re-read before sending." That's weaker than a counter. Accept the trade-off: the cost of a counter that fires after every reply is too high.

## Related work

- `okf/standards/hermes-session-handoff-discipline.md` (gap #1)
- `okf/standards/hermes-proactive-execution-discipline.md` (gap #2)
- `okf/reports/2026-07-27-agent-harness-discipline-session.md` — full session report
- `~/.hermes/profiles/orchestrator/skills/agent-operations/projector-aware-communication-discipline/` — the canonical skill
- `~/.hermes/profiles/orchestrator/state/pins/PIN-2026-07-27-...` — the session's pins
