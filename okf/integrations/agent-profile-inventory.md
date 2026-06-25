---
type: Profile Inventory
title: Agent Profile Inventory & Dormant Profile Decision (2026-06-23)
description: 22 agent profiles on disk, 5 running. Decision matrix for which to keep, which to archive, which to revive.
resource: okf/integrations/agent-profile-inventory.md
tags: [profile, agent, inventory, dormant, audit, orchestration]
timestamp: 2026-06-25T13:30:00Z
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/integrations/agent-profile-inventory.md
last_verified: 2026-06-25
verified_by: antigravity
status: current
---

# Agent Profile Inventory & Dormant Profile Decision

> **Source:** Ned's orchestration audit (GRO-2206), 2026-06-23
> **Trigger:** 22 profiles on disk, 5 running → 17 dormant

## Running profiles (5)

| Profile | Purpose | Status |
|---|---|---|
| `orchestrator` | Main orchestrator (this one) | ✅ Running |
| `ned` | Code execution, infra, audit | ✅ Running |
| `kai` | Content writer, CSS/JS | ✅ Running |
| `autobot` | Generic Telegram bot | ✅ Running |
| `next-step` | Michael's "what's next" assistant | ✅ Running |

## Dormant profiles (17) — classification

### CLI-backed (intentional, not gateways)

These don't have gateways — they use the CLI directly. Not actually dormant.

| Profile | Why not a gateway |
|---|---|
| `agy` | Uses `/home/ubuntu/.local/bin/agy` CLI directly. Cron job `faf8d91da716` supervises it. |
| `jules` | Uses Google Jules CLI at jules.google.com. Cron `b7996de54e7e` watchdog. |
| `codex-5-4` | OpenAI Codex CLI. Not used in current workflows. |
| `codex-5-5` | OpenAI Codex CLI. Not used in current workflows. |

### Should-be-running (revive)

These look like they should be active. Either they crashed, were demoted, or are waiting for a task.

| Profile | Why it should run | Action |
|---|---|---|
| `fred` | The orchestrator-level agent. (I'm running as orchestrator, not fred). | Create separate "fred" gateway for orchestration tasks vs orchestrator (admin) |
| `becca` | Becca bot for next-step-bot workflows. | Duplicate of next-step. Archived to retired-profiles on 2026-06-25. |
| `hermeslocal` | Local-only Hermes variant. | Revive when running on a non-orchestrator machine |
| `qwenlocal` | Local Qwen model. | Revive if local model is in scope |

### Legacy/ambiguous (decide)

These may be from previous experiments. Need to be reviewed.

| Profile | Suspected purpose | Action |
|---|---|---|
| `kai-content` | Kai specialized for content | Defer to kai (already covers this) |
| `kai-css` | Kai specialized for CSS | Defer to kai |
| `kai-js` | Kai specialized for JS | Defer to kai |
| `deepseekv4` | DeepSeek local model | Investigate if we have GPU capacity for it |
| `hdengine` | HD engine agent | Active in `hd-platform` repo. Should be revived for HD work. |
| `beyondsaas-leads` | Lead generation agent | If leads are still a focus, revive. |
| `ai-consulting` | AI consulting workflows | If active consulting is a focus, revive. |
| `active-oahu` | AOT site agent | AOT is in production. Should be revived for content work. |
| `home` | Home assistant? | Unclear. Investigate. |

## Recommendation

| Action | Profiles |
|---|---|
| Keep (CLI-backed) | agy, jules, codex-5-4, codex-5-5 |
| Revive | hdengine (HD work is active), active-oahu (AOT is in production) |
| Document as duplicate | becca (next-step covers it; archived on 2026-06-25), kai-content/css/js (kai covers it) |
| Archive (move out of profiles/) | deepseekv4, qwenlocal, hermeslocal, home, ai-consulting, beyondsaas-leads |
| Decide: orchestrator-level split | fred vs orchestrator |

## Implementation

1. (this week) Add `hdengine` and `active-oahu` gateways to the run set
2. (this week) [COMPLETED] Document that `becca` is a duplicate of `next-step` and archive it (2026-06-25)
3. (this week) Archive 5 unambiguous-legacy profiles: `deepseekv4`, `qwenlocal`, `hermeslocal`, `home`, `ai-consulting`
4. (next week) User decision needed for: `kai-content/css/js` (archive or keep), `beyondsaas-leads` (revive or archive)
5. (next week) Decide on `fred` vs `orchestrator` split

See GRO-2218 for the Linear tracking.
