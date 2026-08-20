---
type: Decision
title: AOT OKF Hub Centralization — Phase 3 (remaining real spokes)
description: Phase 3 of the OKF hub consolidation migrates the three remaining real spokes — belief-deprogrammer, darius-star, agentic-swarm-ops — into the growthwebdev-knowledge hub, and establishes the all-agents OKF-MCP enablement standard.
tags: [decision, okf, hub, centralization, phase-3, kai, darius-star, belief-deprogrammer, agentic-swarm-ops]
timestamp: 2026-08-19T22:00:00Z
status: accepted
resource: okf/hubs/active-oahu/decisions/2026-08-19-aot-hub-centralization.md
git_repo: mbgulden/growthwebdev-knowledge
migrated_from_repo: mbgulden/growthwebdev-knowledge
last_verified: 2026-08-19
verified_by: kai
---

# OKF Hub Unification — Phase 3

## Context

Phase 1 (2026-08-19) centralized Active Oahu Tours knowledge into
`okf/hubs/active-oahu/`. Phase 2 scoped the four remaining Prismatic-family
spokes (hd-platform, prismatic-engine, Hermes-Research, sentinel) and found
none of them needed migration — prismatic-engine's `okf/` is load-bearing
schema infra, the others were empty scaffolds or had no okf.

A **full-branch census across every mbgulden repo** (2026-08-19, all remotes
fetched) found three spokes with **real knowledge docs that were never in
Phase 1/2 scope**:

| Repo | Real docs on default branch | Verdict |
|---|---|---|
| `mbgulden/belief-deprogrammer` | 27 (cognitive-bias catalog, 8 methodologies, case studies, ethical guardrails, ontology manifesto + profile JSON) | **MIGRATE** |
| `mbgulden/darius-star` | 25 (`okf/storyline/` narrative, character arcs, biome/audio design, mechanics) | **MIGRATE** |
| `mbgulden/agentic-swarm-ops` | 1 (`okf/fleet-watchdog-v3.md`, Active/deployed) | **MIGRATE** |

All other repos were confirmed clean: prismatic-engine (exempt — schema
infra), hd-platform / beyondsaas-site / sentinel (empty scaffolds), and
OpenHumanDesignMCP, hd-bodygraph, prismatic-web-plugin, prismatic-web-publisher,
swarmlock, beyondsaas-bot, whatanadventure-games, hermes-agent (fork),
sentinelitad.com, Hermes-Research (0 okf docs on any branch).

## Decision

- Migrate the three spokes into the hub at `okf/projects/<name>/` (the
  same hub-canonical pattern as `okf/projects/prismatic-engine/` and
  `okf/projects/human-design-engine/`), **not** `okf/hubs/` (that's for
  business entities like AOT; these are project repos).
- Every migrated doc carries `migrated_from_repo:` provenance; original
  frontmatter preserved; `resource`/`git_repo` repointed to the hub.
- A doc with **no** frontmatter (`agentic-swarm-ops/fleet-watchdog-v3.md`)
  gets a minimal canonical block prepended; body stays verbatim.
- Source repos' `okf/` dirs retired to a single pointer `README.md` (Phase 1
  pattern). The stale `okf/projects/darius-star.md` pointer stub is removed in
  favor of the real `okf/projects/darius-star/` directory.
- **Enablement standard (new in Phase 3):** all agents search the OKF MCP
  first for domain knowledge; new knowledge lands in the hub; large
  self-contained skills are slimmed into thin pointers that name their
  canonical OKF doc so the detail is fetched via MCP, not duplicated in the
  skill. See `okf/standards/okf-agent-mcp-enablement.md`.

## Scope / boundary (durable)

- `prismatic-engine/okf/` remains **exempt from retirement indefinitely**
  (schema/registry infra, not knowledge docs).
- Empty spoke scaffolds (hd-platform, beyondsaas-site, sentinel) stay in
  place as intended landing pages; populating them is the owner's work.
- **Stranded-branch follow-ups** (not Phase 3 — they land with their PRs):
  - sentinel: 2 research docs on unmerged `ned/GRO-4016-sial-closeout`
  - SovereignSentinel: 1 incident doc on `ned/GRO-2089-zfs-repair-diagnosis`
  - Sweep into the hub after those branches merge.
- `mbgulden/meridian-static-site` local checkout has a **dead remote**
  (repository not found on GitHub). No okf docs; the checkout should be
  archived/verified, not migrated.

## Verification

- Hub PR on `content/kai-okf-phase3-spokes` — 53 docs under
  `okf/projects/{belief-deprogrammer,darius-star,agentic-swarm-ops}/`
  (50 migrated content + 3 new project indices) + 1 JSON artifact.
- Post-merge: OKF MCP `search "belief deprogrammer"`, `search "darius star
  narrative"`, `search "fleet watchdog"` return hub docs (after MCP server
  restart to rebuild the index).
- Source-repo pointer PRs replace `okf/` with `okf/README.md`.

## Refs

- [AOT hub centralization — Phase 1](./2026-08-19-aot-hub-centralization.md) (includes Phase 2 addenda)
- `okf/standards/okf-agent-mcp-enablement.md` — all-agents MCP-first + slim-skill standard
- `okf/decisions/prismatic-okf-hub-and-spoke-map.md` — original hub-and-spoke pattern (GRO-3721)
- `okf/projects/{belief-deprogrammer,darius-star,agentic-swarm-ops}/index.md` — new hub-canonical project indexes
