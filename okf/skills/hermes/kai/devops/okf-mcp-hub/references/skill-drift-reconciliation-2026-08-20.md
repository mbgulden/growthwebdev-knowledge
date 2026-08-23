# Skill drift reconciliation — session record (2026-08-20, PR #35)

Michael authorized "the drift PR and 12-way drift reconciliation" in the same breath as the portability ask.

## Census result
72 multi-copy skill names; **only 12 truly divergent** (60 byte-identical copies). Census = `rglob("SKILL.md")` under `okf/skills/`, sha256 of SKILL.md, group by skill name (dir parts: `hermes/<profile>/<category>/<name>` or `agy/<name>` or `prismatic/<name>`).

## The 12 + dispositions
| Skill | Variants | Disposition | Rationale |
|---|---|---|---|
| agent-onboarding-workflow | kai 08-18 / george 07-25 | **→ kai** | newer; adds systemd-service content |
| agy-autopilot-governance | george 08-18 / fred+orch 08-04 | **→ george** | adds AGY shared-pool section |
| compact-verification-output | kai 08-19 / george 08-18 | **→ kai** | strictly richer (+156/−34) |
| okf-mcp-hub | kai 08-20 / 6× older | **→ kai** | only copy with the skill-hub work |
| pwp-visual-qa-proof | 9× c0f4760d / fred+orch / ned | **→ c0f4760d** | clear 9/12 majority |
| tailscale-lan-access | 4 (fred+george+orch / kai / ned) | **leave** | host-specific IPs/ports/SSH quirks |
| qwen-llamacpp-reasoning-effort | kai / ned | **leave** | per-profile llama.cpp ports |
| agy-oauth-authentication | agy / prismatic | **leave** | different distribution (live vs portable) |
| autonomous-execution-discipline | agy / prismatic | **leave** | 529-line gap = different artifact |
| golden-thread | agy / prismatic | **leave** | 762-line gap = different artifact |
| daily-transit-briefing | 8× hermes / prismatic (+69 lines) | **defer** | debatable; HD-family owner review |
| hermes-agent | fred+orch 08-06 / george+ned 07-25 / kai 07-26 | **defer** | 3 substantive variants; needs owner review |

## Rules extracted
1. Majority wins ONLY when the majority is clearly the superset/newer consolidation. A 1-vote "majority" (2-way split) is a judgment call, not a default.
2. Never unify **host-specific facts** (network maps, per-profile serving config) — unifying corrupts the data.
3. Never unify **different distributions** of one concept (live tool skill vs portable reference skill) — they're different artifacts.
4. Defer genuinely debatable variants to owner review rather than guess; document why.
5. Every overwrite: backup target dir first (`/tmp/skill-reconcile-backup-<date>/<profile>/<skill>/orig`), mirror the canonical dir (wipe non-marker files then copytree), then REGEN the hub (the hub mirrors live profiles, not vice versa) and confirm the `divergent=` count in the generator output dropped.
6. Cross-profile writes to OTHER agents' live skill dirs: back up + report exact list; reversible = acceptable. (No per-profile lock blocked these — the Phase-4 "cross-profile-locked" note applies to lane-hooked REPO pushes, not live-skill edits on the shared box.)
7. Decision doc in `okf/decisions/` with the full table + follow-ups; lands in the same PR as the hub regen.

## Execution notes
- Synced 13 target dirs (5 skills) via Python; regen → `OK: 2422 files, 176 skills, divergent=7`.
- Verification: 19-check suite = 18 substantive PASS + 1 false FAIL (verifier hardcodes the branch name `content/kai-skill-hub-stable-regen` — make branch asserts prefix/regex-based, not exact-match).
- The PR also carried the auto-regen drift (19 files: new reference docs, 1 rename, content edits) — combined drift+reconciliation PR is fine as long as the diff is audited lane-by-lane.
- Two shared-checkout race incidents occurred during this work — see `references/okf-standalone-service-portability-2026-08-20.md` §Collateral and SKILL.md Phase-3 item 15.
- Backups: `/tmp/skill-reconcile-backup-2026-08-20/` (reversible).
