---
type: Standard
title: OKF MCP-first agent enablement + slim-skill routing
description: Canonical standard for all agents to search the OKF MCP first for domain knowledge, land new knowledge in the hub, and keep skills as thin pointers to canonical OKF docs rather than duplicating detail.
tags: [standard, okf, mcp, agents, skills, knowledge, routing]
timestamp: 2026-08-19T22:00:00Z
linear_issue: null
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/standards/okf-agent-mcp-enablement.md
last_verified: 2026-08-19
verified_by: kai
status: current
---

# OKF MCP-first agent enablement + slim-skill routing

## Why

OKF unification Phase 3 (2026-08-19) moved all real project knowledge into the
`mbgulden/growthwebdev-knowledge` hub (see
`okf/decisions/2026-08-19-okf-hub-unification-phase3.md`). Every agent
(kai, george, fred, ned, orchestrator, autobot) has the `okf` MCP enabled and
points at the same `OKF_ROOT=/home/ubuntu/work/growthwebdev-knowledge`. For the
unification to pay off, agents must actually **use** the hub as the knowledge
source of truth instead of carrying detail in local skills or re-discovering
what already lives in the hub.

## The standard (all agents)

1. **Search OKF first.** Before answering a domain question or doing
   non-trivial work in a known area (AOT/tourism, Prismatic, hd-platform,
   darius-star, belief-deprogrammer, swarm-ops, infra/llama.cpp, etc.), call
   `mcp_okf_search` (and `mcp_okf_read` on hits). Do not rely on a skill or
   memory copy when a canonical OKF doc exists.
2. **Land knowledge in the hub.** Durable facts, decisions, closeouts,
   integration notes, and audit findings get written to `okf/` in the hub
   (correct category: `decisions/`, `projects/<name>/`, `standards/`,
   `integrations/`, `reports/`, `research/`, `audits/`, `incidents/`). Do not
   leave durable knowledge only in a skill, a memory entry, or a per-repo
   `okf/` spoke.
3. **Skills are thin pointers.** A skill should hold *when to act* and
   *how to start* (trigger, first commands, gotchas), and **name its canonical
   OKF doc** by path. The deep detail lives in the OKF doc and is fetched via
   `mcp_okf_read` at runtime. A skill that duplicates a whole doc is a drift
   liability — slim it.
4. **Provenance on migration.** Anything moved into the hub keeps its
   `migrated_from_repo:` frontmatter so the source is traceable.
5. **Refresh the index.** The OKF MCP builds its search index **at server
   start**. After a hub merge that adds docs, restart the relevant
   `okf-mcp-server` process (or set `OKF_ALLOW_UPDATE=1` and call
   `mcp_okf_update`) so new docs become searchable. A doc in `git` but not in
   the MCP index is not "unified" yet.

## Skill-slimming pattern

For a large self-contained skill (e.g. `active-oahu-operations`,
`okf-mcp-hub`):

- Keep: trigger conditions, the 5–10 most-used commands, hard pitfalls,
  verification steps, and a **"canonical OKF doc(s)"** section listing exact
  `okf/...` paths.
- Move: long doctrine, full step-by-step walkthroughs, reference tables that
  change — into an OKF doc. Replace the inline text with a one-line pointer:
  > Full reference: `okf/…/…md` (read via `mcp_okf_read`).
- The skill stays < ~150 lines and stable; the OKF doc carries the weight.

## Write-path (hub)

- Lane owners per `PRISMATIC_ENGINE.yaml`; hub changes ride a `content/` or
  `feature/` branch → PR → manual merge. No direct-main.
- One migration commit per repo keeps provenance clean (Phase 1/3 pattern).
- Privacy invariant: private business/SEO content must never be republished
  to a public repo.

## Verification

- `mcp_okf_search "<domain term>"` returns the canonical doc after a server
  restart.
- A slimmed skill references an OKF path that `mcp_okf_read` resolves.
- No new durable knowledge lives only in a skill or per-repo spoke.

## Refs

- `okf/decisions/2026-08-19-okf-hub-unification-phase3.md`
- `okf/decisions/2026-08-19-aot-hub-centralization.md` (Phase 1 + 2)
- `okf/standards/agent-memory-governance.md` — memory vs skill vs OKF routing
- `okf/decisions/okf-agent-commit-authorization.md` — who may commit to the hub
