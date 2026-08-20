---
type: Reference
title: "Telegram activity ≠ delivered work — the 2026-07-27 Ned-incident and the bounded-move-with-corrections pattern"
description: "Worked example of how 'is the agent working?' and 'is the agent producing real work?' are different questions. Captures the recipe for closing a 'is the agent unconfirmed' pin: bounded-move-with-corrections carries a verifiable ground truth, the agent self-corrects against it, and the verifier probes the artifact after the fact."
tags: [reference, agent-effectiveness, bounded-move, ground-truth-correction, self-correction, gap-2]
timestamp: 2026-07-29T03:50:00Z
last_verified: 2026-07-29
verified_by: fred
status: lesson
---

# Telegram activity ≠ delivered work — 2026-07-27 Ned incident

## The signal

Michael's exact phrasing: **"Not sure if it worked but he's working, so that's good right?"**

This is the question. Telegram activity — agent is reading messages, replying, opening skill files, doing tool calls — is observable. Delivered work — a file at a real path, with values that match ground truth — is verifiable. **They are not the same thing.** A confident-sounding agent that fabricates values, then writes them into a "verified" file with a `PASS` verdict, has high Telegram activity and zero delivered work.

## What happened in the session

Ned was the test subject. He had Telegram activity (he was pinging, replying, loading skills). The first artifact he produced had:

- A wrong file path (`active-oahu-tours-mirror/` instead of `active-oahu-tours-mirror-2529/`)
- A made-up `tracking_property: G-AOT-PLACEHOLDER` instead of the real `G-PRRRLMBR8Z`
- Four invented event names (`booking_start`, `begin_checkout`, `purchase`, `generate_lead`) that don't exist on the live site

His verifier said "31/31 PASS" because the verifier was checking **internal consistency** (JSON parses, fields present, formula gates pass) — not **external truth** (matches live site, real values, real events). The verifier was correctly verifying a self-consistent fiction.

## The recipe that worked

The closure happened in three steps, each building on the last:

### Step 1: Bounded move with specific target

Instead of asking "Ned, are you sure?" or "Ned, can you re-verify?", I sent a single bounded move with verifiable ground truth:

> Create `/home/ubuntu/work/active-oahu-tours-mirror-2529/scripts/kpis/kpi-collections.json` — one real collection, three real metrics, pwp_dashboard_surface block. JSON only, no code, no external API calls, no Linear mutation. When done, post the file path + a one-line Telegram status update.

The bounded move:
- Names the exact file path
- Names the exact schema shape
- Names the exact constraint (no code, no deploy, no Linear)
- Names the exact reply format (file path + one-line status)

### Step 2: Corrections with verifiable ground truth, not assertions

When the first attempt failed (wrong path, made-up ID, invented events), I sent corrections **with a verification recipe** the agent could run to confirm each correction:

> `tracking_property` must be `G-PRRRLMBR8Z`, not `G-AOT-PLACEHOLDER`. I confirmed that ID live on the mirror 30 min before your file. Grep `site/index.html` for `gtag.*config` if you want to re-verify.

The correction is not "the right value is X" (an assertion) — it is "here is how to confirm X is the right value" (a recipe). The agent can self-verify the correction without trusting me. This is the difference between a correction that produces dependency and a correction that produces self-correction.

### Step 3: Independent re-verification by the verifier

After the second attempt, I re-verified the artifact independently:

| Claim | Live state | Match |
|---|---|---|
| File at correct path | exists at 1659 bytes | ✅ |
| `tracking_property: G-PRRRLMBR8Z` | only ID present in live mirror | ✅ |
| Only `booking_click` and `booking_complete` events | no others exist on live mirror | ✅ |
| Old wrong-path file deleted | gone | ✅ |

The verifier was **independent of Ned's verifier** — I ran my own checks against the live site, not a self-consistent re-parse of his output. The four claims matched.

## The three durable patterns (for any future "is the agent working?" question)

1. **Telegram activity is a leading indicator, not a verdict.** A chatty agent may be producing fiction. A quiet agent may be executing bounded work. **Ask for the artifact, not for "are you working?"**
2. **A bounded-move-with-corrections is the right shape for closing an "unconfirmed" pin.** The bounded move has a specific target, a specific shape, a specific constraint, and a specific reply format. Corrections carry verification recipes, not assertions. The agent self-corrects.
3. **The closing verifier is independent of the agent's verifier.** When the agent's own checker says "31/31 PASS", that proves internal consistency, not external truth. The closing check must probe the live system, not re-parse the agent's output.

## Anti-patterns to refuse

- "He's typing, so he's working." — Activity ≠ progress.
- "31/31 verifier PASS." — Internal consistency ≠ external truth, especially for a self-consistent fiction.
- "Can you re-verify?" — Vague re-verification request. The agent re-runs the same internal checker and gets the same result. The re-verification recipe must be specific.
- "Are you sure?" — The agent will say yes. The right question is "show me the artifact and how it matches the live state."
- Closing the pin on the agent's word alone. **The pin closes when the verifier independently confirms the artifact, not before.**

## Cross-references

- `~/.hermes/profiles/orchestrator/state/pins/PIN-2026-07-27-NED-WORKING-UNCONFIRMED.json` — the pin that closed
- `okf/reports/2026-07-27-agent-harness-discipline-session.md` — full session report
- `okf/standards/hermes-mechanism-probe-recipe.md` — companion standard for the "probe any documented mechanism" pattern

## Verification

The pattern is load-bearing. The next time the question "is the agent working?" comes up, do **not** answer with "yes, he's active." Answer with: "I need to see the artifact. The artifact must match a verifiable ground truth. The ground truth is provable by [recipe]. Until the artifact matches, the pin stays open."
