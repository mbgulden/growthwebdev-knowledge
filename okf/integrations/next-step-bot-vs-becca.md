---
type: Decision
title: next-step-bot and next-step-becca are distinct bots, archive duplicate/dormant Hermes profile
description: GRO-2238 archive-vs-keep call. The two profiles serve different users (Michael vs Becca) with distinct SOULs, services, databases, and active systemd units. The dormant profile inventory (GRO-2218) mis-classified the bots as duplicates, but the `becca` Hermes profile itself is redundant/dormant and was archived.
resource: okf/integrations/next-step-bot-vs-becca.md
tags: [decision, adr, agent-profiles, next-step-bot, next-step-becca, jeff, sage, hermes]
timestamp: 2026-06-25T03:40:00Z
linear_issue: GRO-2238
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/integrations/next-step-bot-vs-becca.md
last_verified: 2026-06-25
verified_by: antigravity
status: current
---

# next-step-bot vs next-step-becca: keep both bots, archive duplicate profile

## Status

Accepted (Jun 25 2026, GRO-2238). The dormant profile inventory (GRO-2218) flagged `becca` as a duplicate. We confirmed that the bots themselves are distinct and must both be kept running, but the Hermes profile `becca` was dormant/redundant and has been archived.

## Context

GRO-2218 (P1: profile inventory + decision matrix, owner Fred) catalogued 22 Hermes profiles and called out "duplicates" needing a keep-or-archive decision. GRO-2238 spawned from that workstream with this acceptance:

> - [ ] Confirm with user which profile is canonical
> - [ ] Archive the duplicate (move out of `~/.hermes/profiles/`)
> - [ ] Update the agent profile inventory in OKF
> - [ ] Document the decision rationale

The suspicion was that `next-step-bot` and `next-step-becca` were two shells for the same bot.

## Investigation (2026-06-24, Ned & 2026-06-25, Antigravity)

Inspected both profiles on Hermes VM (`/home/ubuntu/.hermes/profiles/` and `~/work/`):

| Signal | `next-step-bot` | `next-step-becca` |
| --- | --- | --- |
| SOUL identity | **Jeff** — Michael's personal assistant, AuDHD + HD coaching, executive function | **Sage** — Becca's Human Design companion, 6/2 Role Model Hermit |
| Telegram handle | `@TheNextNextStepBot` (per `next-step-bot/README.md`) | (separate bot token, not in repo) |
| Service file | `next-step-bot.service` (systemd, **active running**, PID 1173) | `becca-sage.service` (systemd, **active running**, PID 1197) |
| Database | `next_step.db` (98 KB, last touched Jun 12) | `next_step.db` (36 KB, last touched Jun 3) |
| Journals | none on disk | `journals/2026/06/25.md` (active) |
| Provider | DeepSeek API (per README) | Standalone python bot (per service ExecStart) |
| Designed for | Michael Gulden (3/5 Projector, Splenic) | Becca (6/2 Splenic Projector, HD-certified practitioner) |

The SOUL.md files are written in completely different voices with different core philosophies, different coaching frameworks, and explicitly different target users. There is **zero functional overlap** between the bot directories. They are not duplicates.

However, the Hermes profile folder `~/.hermes/profiles/becca` was completely stopped and not referenced by the running `becca-sage.service` (which executes the standalone python code directly without `hermes --profile becca gateway run`). Thus, while the **bot** is active and must be kept, the **Hermes profile** `becca` was a dormant/redundant duplicate namespace and can be safely archived.

## Decision

1. **Keep both bot directories/services running in production:** Jeff (`next-step-bot`) and Sage (`becca-sage` / `next-step-becca`) both remain active.
2. **Archive the duplicate `becca` Hermes profile:** Moved `/home/ubuntu/.hermes/profiles/becca` to `/home/ubuntu/.hermes/retired-profiles/becca-20260625T034252Z` to clean up the `~/.hermes/profiles/` namespace.
3. **Canonical profile:** The `next-step` Hermes profile remains the canonical profile running the `next-step-bot` (Jeff) gateway.

### Rationale

1. **Distinct users.** Michael and Becca are different people with different Human Design profiles, different coaching needs, and different communication preferences. Conflating them would degrade both experiences.
2. **Distinct infrastructure.** Each bot has its own systemd unit, SQLite DB, journals, and Telegram token.
3. **Clean profiles namespace.** Since the Sage bot runs standalone and does not utilize the Hermes `becca` profile gateway, keeping `/home/ubuntu/.hermes/profiles/becca` active only introduces confusion. Archiving it satisfies the GRO-2238 requirement to clean up duplicate profile directories.

## Consequences

### Positive

- Active production bots remain fully functional.
- The `~/.hermes/profiles/` namespace is cleaned of the unused `becca` profile.
- Inventory documentation is updated to match the active system state.

### Negative

- Operationally, we still monitor two separate bot repos.

## Follow-ups

- [x] **GRO-2238 close-out:** Mark GRO-2238 as Done with this ADR as the rationale.
- [x] **Archive profile:** Move `/home/ubuntu/.hermes/profiles/becca` to retired profiles (Done).
- [x] **Update OKF inventory:** Regenerate and write `okf/integrations/agent-profile-inventory.md` to reflect the active profile distribution (Done).

## References

- GRO-2218 — parent profile inventory (Fred, 2026-06-23)
- GRO-2238 — this task
- `~/work/next-step-bot/SOUL.md` (Jeff identity)
- `~/work/next-step-becca/SOUL.md` (Sage identity)
- `~/work/next-step-bot/README.md` (bot handle, provider)
- `~/work/next-step-bot/next-step-bot.service` and `~/etc/systemd/system/becca-sage.service`