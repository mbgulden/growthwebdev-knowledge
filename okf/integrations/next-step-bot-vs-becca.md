---
type: Decision
title: next-step-bot and next-step-becca are distinct, both keep
description: GRO-2238 archive-vs-keep call. The two profiles serve different users (Michael vs Becca) with distinct SOULs, services, databases, and active systemd units. The dormant profile inventory (GRO-2218) mis-classified them as duplicates; this ADR records the corrected call.
resource: okf/integrations/next-step-bot-vs-becca.md
tags: [decision, adr, agent-profiles, next-step-bot, next-step-becca, jeff, sage, hermes]
timestamp: 2026-06-24T04:10:00Z
linear_issue: GRO-2238
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/integrations/next-step-bot-vs-becca.md
last_verified: 2026-06-24
verified_by: ned
status: current
---

# next-step-bot vs next-step-becca: keep both

## Status

Accepted (Jun 24 2026, GRO-2238). The dormant profile inventory (GRO-2218) was wrong to flag these as duplicates. Both profiles stay active.

## Context

GRO-2218 (P1: profile inventory + decision matrix, owner Fred) catalogued 22 Hermes profiles and called out "duplicates" needing a keep-or-archive decision. GRO-2238 spawned from that workstream with this acceptance:

> - [ ] Confirm with user which profile is canonical
> - [ ] Archive the duplicate (move out of `~/.hermes/profiles/`)
> - [ ] Update the agent profile inventory in OKF
> - [ ] Document the decision rationale

The suspicion was that `next-step-bot` and `next-step-becca` were two shells for the same bot.

## Investigation (2026-06-24, Ned)

Inspected both profiles on Hermes VM (`/home/ubuntu/.hermes/profiles/ned/home/work/`, which is `~/work/` in the canonical workspace):

| Signal | `next-step-bot` | `next-step-becca` |
| --- | --- | --- |
| SOUL identity | **Jeff** — Michael's personal assistant, AuDHD + HD coaching, executive function | **Sage** — Becca's Human Design companion, 6/2 Role Model Hermit |
| Telegram handle | `@TheNextNextStepBot` (per `next-step-bot/README.md`) | (separate bot token, not in repo) |
| Service file | `next-step-bot.service` (systemd, **active running**, PID 1173) | `next-step-becca.service` (systemd shows inactive/dead but Python process 1137 still alive) |
| Database | `next_step.db` (98 KB, last touched Jun 12) | `next_step.db` (36 KB, last touched Jun 3) |
| Journals | none on disk | `journals/2026/06/23.md` (active) |
| Provider | DeepSeek API (per README) | Hermes profile gateway (per service ExecStart) |
| Designed for | Michael Gulden (3/5 Projector, Splenic) | Becca (6/2 Splenic Projector, HD-certified practitioner) |

The SOUL.md files are written in completely different voices with different core philosophies, different coaching frameworks, and explicitly different target users. There is **zero functional overlap**. They are not duplicates.

## Decision

**Keep both profiles.** No archival action.

The GRO-2218 inventory entry classifying these as duplicates was a name-collision error (both files share the `next-step-` prefix and live in `~/work/`). This is a misclassification, not a duplication.

### Rationale

1. **Distinct users.** Michael and Becca are different people with different Human Design profiles, different coaching needs, and different communication preferences. Conflating them would degrade both experiences.
2. **Distinct voices.** Jeff (warm, gamified, executive-function-first) and Sage (calm, Splenic, "wait for the knock") are deliberately opposite registers. They share no prompt text, no model weights, no skill set.
3. **Distinct infrastructure.** Each has its own systemd unit, its own SQLite DB, its own journals directory, its own Telegram bot token. They can be stopped, restarted, and evolved independently.
4. **Live services.** Both are running as of 2026-06-24 04:08 UTC. Archiving either would break an active production bot.
5. **Historical naming.** The "becca" suffix was added to disambiguate from the original `next-step-bot`. The codebase preserves that history — archiving `next-step-becca` would lose that distinction.

## Consequences

### Positive

- No migration work needed.
- Each bot can iterate independently (Jeff can adopt new coaching patterns; Sage can deepen HD specificity).
- Inventory hygiene improves once the next-pass audit flags GRO-2218's classification error.

### Negative

- Two separate bots to maintain, monitor, and back up. Already the case — this decision does not change the operational load.
- The dormant inventory table is now known to contain a misclassification. Either Fred or Ned should fix the entry to remove the "duplicate" callout.

## Follow-ups

- [ ] **GRO-2238 close-out:** Mark GRO-2238 as Done with this ADR as the rationale comment on Linear.
- [ ] **GRO-2218 patch:** Open a small follow-up (suggest GRO-2239) to correct the inventory entry for `next-step-becca`. Owner: Fred (he authored GRO-2218).
- [ ] **OKF inventory refresh:** Once the OKF doc publisher auth flow is healthy again (`okf/integrations/cloudflare-access-okf-publisher.md`), rewrite `okf/integrations/agent-profile-inventory.md` to reflect this decision. Until then, this ADR is the canonical record.

## References

- GRO-2218 — parent profile inventory (Fred, 2026-06-23)
- GRO-2238 — this task (Ned, 2026-06-24)
- `~/work/next-step-bot/SOUL.md` (Jeff identity)
- `~/work/next-step-becca/SOUL.md` (Sage identity)
- `~/work/next-step-bot/README.md` (bot handle, provider)
- `~/work/next-step-bot/next-step-bot.service` and `~/work/next-step-becca/next-step-becca.service`