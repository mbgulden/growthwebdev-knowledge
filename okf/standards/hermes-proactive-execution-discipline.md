---
type: Standards
title: Hermes Agent Proactive-Execution Discipline — Close the "what next?" Gap
description: Standard for the per-turn discipline of executing bounded work silently and reporting afterward, rather than asking permission first. Defines the hard rule, the daily briefing shape (moved/blocked/executed, not to-do), and the per-week counter that tracks the ratio of executed-without-asking turns. Authoritative reference: the `proactive-execution-discipline` skill at `~/.hermes/profiles/orchestrator/skills/agent-operations/proactive-execution-discipline/`.
resource: okf/standards/hermes-proactive-execution-discipline.md
tags: [standards, hermes, proactive-execution, discipline, counter, daily-briefing]
timestamp: 2026-07-29T02:00:00Z
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/standards/hermes-proactive-execution-discipline.md
linear_issue: null
last_verified: 2026-07-29
verified_by: fred
status: current
---

# Hermes Agent Proactive-Execution Discipline

## Purpose

The gap is "I wait for Michael to say 'what next?' more than I should. The skill says pick the highest-impact pending item and execute; the practice still has a beat of 'do you want me to...' between me and the work."

This standard closes that gap by enforcing execution-then-report at turn level. It is the companion to `hermes-session-handoff-discipline` (which is about cross-session continuity) — this one is about within-session momentum.

## What this standard defines

- **The hard rule**: when the user gives a direction, do the first bounded slice silently, then report. Never propose the slice first unless there's a meaningful tradeoff.
- **Bounded slice** = a single file write/patch, a single Linear mutation, a single external API call, a single bounded move dispatched to another agent, or a bounded investigation that produces a clear artifact.
- **Meaningful tradeoff** = picking between mutually exclusive strategies, choosing a recipient where getting it wrong is costly, or picking a model/credential/irreversible change. Real tradeoffs are the only place asking is correct.
- **Daily briefing shape**: leads with `Moved since <last_contact>`, `Blocked`, and `Executed without asking`. Never a to-do list.
- **The per-week counter** at `~/.hermes/profiles/<active>/state/proactive-count.json` with one entry per turn (`ts_utc`, `did`, `category`, `was_asked_for`).
- **The health threshold**: a healthy ratio is >70% of bounded moves were not explicitly requested. <50% means the gap is regressing.

## Anti-patterns to refuse

- "Want me to ... ?"
- "Should I ... ?"
- "Shall I ... ?"
- "Let me know if you'd like me to ..."
- "I can do X or Y — which would you prefer?" (when X and Y are both bounded, equally-cheap, and either is fine)
- "Do you want me to draft ... ?"
- A bulleted "options" list at the end of a turn where one option is clearly the bounded next step.

When you find yourself about to write any of these, **stop, do the bounded work first, then report.**

## The counter contract

```json
{
  "week_starting_utc": "2026-07-27",
  "turns": [
    {
      "ts_utc": "2026-07-27T22:00:00+00:00",
      "did": "wired handoff files for kai, george, autobot, next-step",
      "category": "infrastructure",
      "was_asked_for": false
    }
  ]
}
```

`was_asked_for: true` turns count toward the denominator (so the ratio is meaningful). `was_asked_for: false` turns count toward the numerator (executed without asking). Roll over Monday-to-Monday.

## CLI

```bash
COUNT=~/.hermes/profiles/orchestrator/skills/agent-operations/proactive-execution-discipline/scripts/proactive_count.py
BRIEF=~/.hermes/profiles/orchestrator/skills/agent-operations/proactive-execution-discipline/scripts/daily_briefing.py

# Record one bounded move
python3 $COUNT record --profile orchestrator --agent fred \
    --did "wired kai profile handoff" --category infrastructure --was-asked-for false

# Weekly report
python3 $COUNT report --profile orchestrator
# {"ratio_executed_without_asking": 0.7, "verdict": "HEALTHY", ...}

# Daily briefing
python3 $BRIEF --profile orchestrator --save-last-run
# Renders markdown: Moved/Blocked/Executed without asking/Pending decisions

# Verify the counter JSON
python3 $COUNT verify --profile orchestrator
```

## Adoption

The same `_adopt_shared_skills.py` script that adopts `session-state-handoff` adopts this one. See `hermes-session-handoff-discipline.md` for the recipe.

## Verification

- Per-turn: the `was_asked_for` field is set honestly. If you asked permission for a real tradeoff, it's `true`. If you didn't, it's `false`. Don't fudge.
- Per-week: run `proactive_count.py report` and check the verdict (`HEALTHY` / `REGRESSING` / `FAILING`).
- Per-day: the briefing shape pulls moved/blocked/executed from the handoff + counter. No to-do list.

## Honest lessons from the 2026-07-27 session

- A 3/10 ratio of propose-before-work in 10 turns is the gap as it actually manifests. The discipline is not "never ask" — it's "ask only at meaningful tradeoffs."
- The MANDATORY directive in prefill messages backfired (5/5 profiles reverted to one-line "ready" replies). The gentle "REQUIREMENT" wording works. Stronger language is worse, not better.
- A healthy ratio is >70% silent bounded work. 100% is overreach (means no real tradeoffs ever surfaced); <50% is regression.

## Related work

- `okf/standards/hermes-session-handoff-discipline.md` — companion standard for cross-session continuity.
- `okf/reports/2026-07-27-agent-harness-discipline-session.md` (proposed) — full session report.
- `~/.hermes/profiles/orchestrator/skills/agent-operations/proactive-execution-discipline/` — the canonical skill.
