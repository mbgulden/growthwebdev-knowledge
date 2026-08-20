---
type: Decision
title: Skill drift reconciliation — 12 divergent names (Phase A closeout)
date: 2026-08-20
owner: kai
status: accepted
---

# Decision: skill drift reconciliation (2026-08-20)

## Context
The `okf/skills/` hub (PR #33/#34) surfaced **72 multi-copy skill names, of
which 12 were truly content-divergent** (60 were byte-identical copies — no
action). Michael approved reconciliation. No user pick was made within the
decision window, so the conservative default was executed: **unify the 5
unambiguous names, leave the 7 genuinely-ambiguous ones divergent by design.**
All 13 overwritten live skill dirs backed up to
`/tmp/skill-reconcile-backup-2026-08-20/<profile>/<skill>/orig` (reversible).

## Canonicals applied (live profiles updated, hub re-mirrored)

| Skill | Canonical | Synced to | Rationale |
|---|---|---|---|
| `agent-onboarding-workflow` | kai (08-18) | george | newer; adds systemd-service content |
| `agy-autopilot-governance` | george (08-18) | fred, orchestrator | adds AGY shared-pool section |
| `compact-verification-output` | kai (08-19) | george | strictly richer (+156 lines) |
| `okf-mcp-hub` | kai (08-20) | autobot, fred, george, ned, next-step, orchestrator | only copy with the skill-hub work |
| `pwp-visual-qa-proof` | `c0f4760d` (kai) | fred, orchestrator, ned | 9/12 majority |

## Left divergent BY DESIGN (not drift)

- **`tailscale-lan-access`** (4 variants) — per-host facts (IPs, ports, SSH
  quirks differ per machine). Unifying would corrupt the data.
- **`qwen-llamacpp-reasoning-effort`** (2 variants) — per-profile serving
  config (different llama.cpp ports/profiles).
- **`agy-oauth-authentication`**, **`autonomous-execution-discipline`**,
  **`golden-thread`** — AGY live store vs prismatic portable store: different
  *distributions* (live vs reference), not copies of one thing.
- **`daily-transit-briefing`** — 8-profile hermes majority vs prismatic
  variant with +69 unique lines; needs HD-family owner review.
- **`hermes-agent`** — 3 substantive variants; kai's most maintained but
  Fred's newer by date; needs owner review before unifying.

## Follow-ups
- [ ] Owner review of `daily-transit-briefing` + `hermes-agent` variants
      (2 names) → can drop to 5 divergent.
- [ ] Prismatic portable store (`prismatic/portable-skills/`) should be
      regenerated FROM the hub (Phase B / GRO-4817), not hand-maintained —
      this retires 3 of the "distribution" divergences at the source.

## Evidence
- Census script + full table: this session (72 multi-copy, 12 divergent).
- Post-sync hub regen: `OK: 2422 files, 176 skills, divergent=7`.
- Landed in PR #35 (drift + reconciliation together).
