# OKF Phase 4 — adoption plan + verified recon (2026-08-20)

Phase 3 (PR #32) merged to `origin/main` (`8f8d74e`) on 2026-08-20. Phase 4 is not
"migrate more" — the real spokes are done. Phase 4 = **adoption**: make the hub the
live source of truth agents actually use. This file records the recon state (so a
future session does NOT re-census) and the proposed sub-phase plan with gates.

## Verified recon state (2026-08-20, do not re-derive)

- **All three real spokes fully migrated.** belief-deprogrammer, darius-star,
  agentic-swarm-ops branch copies are **path-identical** to the hub (zero new
  knowledge left to migrate). Verified via `comm -23` of branch-vs-hub path sets.
- **MCP index is stale at 421 docs** (`mcp_okf_status.head = d5deaa4`), i.e. it does
  NOT yet include Phase 3's 53 spoke docs. Reindex (restart per-profile server or new
  session) is Phase 4.0 and closes the Phase 3 loop.
- **Deferred gaps still unmerged** (peer-review as of 2026-08-20):
  - SIAL ×2 research docs on `sentinel-it-asset-logistics` branch `ned/GRO-4016-sial-closeout`
    (`okf/research/sentinel-itad-existing-content-map-2026-07-07.md`, `...operating-brief-2026-07-07.md`).
  - SovereignSentinel ×1 incident doc on `SovereignSentinel` branch `ned/GRO-2089-zfs-repair-diagnosis`
    (`okf/incidents/gro-2089-pve6-local-zfs-degraded-2026-06-23.md`).
  Both consolidate ONLY after their PRs land.
- **~480 redundant `okf/` doc-copies** on the spokes' non-default branches (cleanup
  target, all other agents' branches):
  | repo | redundant copies | remote branches |
  |---|---:|---:|
  | belief-deprogrammer | 139 | 8 |
  | darius-star | 250 | 40 |
  | agentic-swarm-ops | 91 | 620 |
- **darius-star pointer/legacy split (the gotcha):** default `main` = one-line pointer
  README; legacy `master` = full 25 docs. Retirement completeness must be checked
  across ALL branches, not just the default.

## Phase 4 sub-phase plan (proposed — Michael had NOT yet approved at session end)

| # | What | Lane / gate |
|---|---|---|
| 4.0 | Reindex MCP → verify `search "fleet watchdog" / "darius star narrative" / "belief deprogrammer"` return hub docs | kai, low-risk |
| 4.1 | Fleet enablement audit: every wired profile → okf MCP enabled + `OKF_ROOT` correct; pass/fail table | kai, read-only |
| 4.2 | Skill slimming: flag skills duplicating a canonical OKF doc → slim to pointer. THE payoff | **scoped** — see gate |
| 4.3 | Freshness guardrail: (A) cron reindex after `main` merge, or (B) scheduled `OKF_ALLOW_UPDATE=1` | kai, needs Michael's pick |
| 4.4 | Redundant-branch sweep (~480 copies) → spokes become pointers on every branch | **needs explicit Michael go** |
| 4.5 | Deferred-gap sweep (SIAL ×2 + SS ×1) — only on GRO-4016 / GRO-2089 merge | track, act on merge |

### Open decisions (asked to Michael, unanswered at session end)
1. **4.2 cross-profile boundary** — kai slims kai's skills directly; Fred/George/Ned skills
   are cross-profile-locked. Need (a) their own agent, or (b) explicit cross-profile auth.
2. **4.3 mechanism** — cron reindex (A) vs scheduled `OKF_ALLOW_UPDATE` (B). Lean = A.
3. **4.4 branch sweep** — other agents' branches; per-branch verify-then-retire, no blanket
   delete, needs explicit go.

## Notes for the executor
- Recommended first action on approval: **4.0 reindex now** (closes Phase 3 loop) + optionally
  draft `okf/decisions/2026-08-20-okf-phase4-adoption.md` so the plan is reviewable in-repo.
- 4.2 should cite `okf/standards/okf-agent-mcp-enablement.md` as the canonical standard.
- Do NOT treat the ~480 copies or the deferred-gap status as stale without re-checking Linear
  (GRO-4016 / GRO-2089 may have merged since).
