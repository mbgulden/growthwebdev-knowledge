---
name: timestamp-is-a-claim-not-a-fact
description: Verify staleness via mtime + date -u, not just written_at.
---

# Timestamp Is a Claim, Not a Fact

A timestamp is a **claim** stamped by its producer. The only things that are facts are what you can re-derive independently: the host wall clock, the filesystem mtime, and the content. When two of those disagree with the producer-stamped field, the field is the suspect — not the other sources.

This is the clock-twin of the git-count lesson ("branch-divergence-count is a claim, not a fact"): a number or time that lands in an artifact (a handoff, an OKF doc, a Linear comment) is the producer's assertion until you re-derive it from a machine-verifiable source.

## Why it matters (the failure mode)

Most staleness checks compute:

```
age = now (host clock) - written_at_utc (producer field)
if age > 4h: treat as stale
```

This uses **one** clock for both operands. If the host clock is skewed (NTP drift, VM clock jump, a mislabeled producer timestamp, a timezone mishap), `age` can come out **negative** or wildly small — and the `> 4h` trigger **never fires**. A genuinely stale handoff then passes as "fresh," and the next session proceeds on false premises with no warning. That is exactly the class of hidden failure the stale-handoff-recovery recipe exists to prevent, so the check that defeats it must not depend on the single clock it's trying to protect.

Observed (2026-09-12, orchestrator cold start): `date -u` returned `2026-09-12T23:22Z` while the prior run's `written_at_utc` was `2026-09-13T07:00Z` — ~8.6h *in the future* relative to the host clock. A naive subtraction would report "negative age / fresh" when the real story was "the clock (or the producer's stamp) is the liar."

## The three independent sources

Always get the freshness verdict from **three** sources, never one:

| Source | How | Role |
|---|---|---|
| Producer field | read `written_at_utc` from the JSON | the *claim* under test |
| Host wall clock | `date -u +"%Y-%m-%dT%H:%M:%S+00:00"` | independent now |
| Filesystem mtime | `stat -c %y <path>` (or `stat -c %Y` for epoch) | independent, written-by-the-OS |

The OS mtime is the strongest independent check: the kernel stamps it at write time and no producer can lie about it.

## Recipe (run on any cold start that reads a stamped record)

```bash
HAND=/home/ubuntu/.hermes/profiles/orchestrator/state/current.json

# 1. Producer claim
python3 -c "import json; print('written_at:', json.load(open('$HAND'))['written_at_utc'])"

# 2. Host wall clock (independent)
date -u +"%Y-%m-%dT%H:%M:%S+00:00"

# 3. Filesystem mtime (independent, kernel-stamped)
stat -c %y "$HAND"

# 4. Cross-check: compare all three. Any disagreement > ~1h is a clock discrepancy.
#    If written_at is IN THE FUTURE vs host date: the clock or the stamp is the suspect,
#    not necessarily the handoff. Resolve with mtime:
#      mtime ≈ host clock  -> handoff is recent; the written_at field is the mislabel.
#      mtime ≈ written_at  -> the host clock is the liar.
```

Decision rules:
- **Negative or sub-1h age** ⇒ "clock discrepancy — verify with a second source," **not** "fresh." Never let a single-clock negative age close the stale check.
- **All three agree within ~1h** ⇒ trust the verdict; proceed.
- **Two sources agree, one disagrees** ⇒ the odd one out is the suspect. The file mtime (OS-stamped) outranks the producer field; the host clock outranks neither alone but is the "now" reference.
- **Large skew confirmed** ⇒ note it in the handoff's `notes_for_next_self[]` in one line ("host clock skew detected; written_at unreliable, use mtime") so the next session doesn't re-derive it. Do **not** escalate a quiet Michael over a clock skew — the handoff note is sufficient.

## Anti-patterns

- **Single-clock staleness math.** `now - written_at_utc` from one clock is the bug. It is the timestamp analog of "branch ahead is 10" from a truncated `git log` — a confident number with no independent check.
- **Trusting `written_at_utc` because the file exists.** The field's presence proves some agent wrote it once. It does not prove the stamp is right.
- **Letting a skewed clock flip the verdict silently.** A negative age is *information* (the clocks disagree), not a "fresh" signal. Surface the discrepancy, then decide with a second source.

## What NOT to do

- Do not "fix" the producer's `written_at_utc` by rewriting the field — the producer's stamp is a historical record. If it's wrong, flag it and use mtime for the math; don't silently correct history.
- Do not treat this as "the tool is broken / timestamps don't work." It is a normal, expected failure mode (clocks drift); the fix is the cross-check, not a refusal to use timestamps.

## Where this bites

- Cold start reading `state/current.json` before greeting (the `session-state-handoff` stale-handoff-recovery recipe).
- Any "is this file/stamp still fresh?" gate (OKF `last_verified`, release-stamp checks, cron heartbeat freshness, journal `journal_freshness` gaps).
- Anywhere an agent computes an age from a stamped field and a single clock.

## Related
- `session-state-handoff` — the cold-start + stale-handoff-recovery class this complements.
- `corrections-lead-with-recipe` / the branch-divergence-count pitfall — the count-twin of this clock-twin: a value is a claim until independently re-derived.
