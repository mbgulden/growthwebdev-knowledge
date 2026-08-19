---
type: Decision
title: AOT OKF Hub Centralization — Phase 1
description: Michael authorizes centralizing all Active Oahu Tours knowledge (mirror + business + SEO repos) into the private growthwebdev-knowledge hub at okf/hubs/active-oahu/; source repos get pointer stubs.
tags: [decision, active-oahu, okf, hub, centralization, kai]
timestamp: 2026-08-19T14:35:00Z
status: accepted
resource: okf/hubs/active-oahu/decisions/2026-08-19-aot-hub-centralization.md
git_repo: mbgulden/growthwebdev-knowledge
migrated_from_repo: mbgulden/growthwebdev-knowledge
last_verified: 2026-08-19
verified_by: kai
---

# AOT OKF Hub Centralization — Phase 1

## Context

On 2026-08-19 Michael asked whether the per-repo `okf/` trees should be
centralized in the main OKF repository that the OKF MCP indexes. Audit found:

- The MCP only indexed `growthwebdev-knowledge/okf` (266 docs) — which
  contained **zero** AOT content, despite AOT being the flagship business.
- AOT knowledge was fragmented across three repos:
  - `active-oahu-tours-mirror/okf` (public repo, public-safe doctrine, 19 docs + JSON artifacts)
  - `active-oahu-business/okf` (private, 21 docs: compliance, vendors, FareHarbor, analytics)
  - `aot-seo-knowledge/okf` (private, 59 docs + baseline JSON)
- Every AOT worktree/branch checkout replicated the `okf/` directory,
  amplifying drift.

The existing [Prismatic OKF hub-and-spoke map](../../decisions/prismatic-okf-hub-and-spoke-map.md)
(GRO-3721) established hub-canonical + repo-local breadcrumbs for
Prismatic. This decision extends that pattern to AOT but goes one step
further: AOT docs are **migrated into the hub** rather than left in spokes,
because AOT has no single owning application repo — the "spokes" were
themselves the knowledge.

## Decision

- Canonical AOT home: `okf/hubs/active-oahu/` in `mbgulden/growthwebdev-knowledge` (private).
  - `business/` ← `mbgulden/active-oahu-business`
  - `seo/` ← `mbgulden/aot-seo-knowledge`
  - `architecture/`, `governance/`, `reports/`, `kai-reports/`, `audits/`, `verification/` ← `mbgulden/active-oahu-tours-mirror`
- Every migrated doc carries `migrated_from_repo:` provenance frontmatter; original fields are preserved.
- Source repos' `okf/` directories are retired to a single pointer `README.md` (content remains in their git history; mirror repo is public so its okf/ was public-safe doctrine).
- Lane: kai owns `okf/hubs/` (PRISMATIC_ENGINE.yaml); hub changes ride `content/` branches + PR + manual merge (no direct-main, per OKF commit authorization 2026-08-19).
- Per-PR work packets, verification dumps, and CI artifacts **stay in the originating repo** — they are artifacts, not knowledge.

## Phase plan

- **Phase 1 (this change):** AOT — mirror + business + SEO → hub. ✅
- **Phase 2 (pending, coordinate with George/Fred):** hd-platform, prismatic-engine, Hermes-Research, sentinel, and remaining spokes.

## Consequences

- **Positive:** one searchable index for all AOT knowledge; MCP `search`/`recent` cover AOT; worktree replication of knowledge stops; private business docs consolidated in a private repo.
- **Negative / trade-offs:** per-repo git history of the docs is left behind (mitigated by provenance frontmatter + single migration commit per repo); the public mirror loses its public-safe doctrine from its default branch (still in history; doctrine is internal, not customer-facing).
- **Privacy invariant:** `business/` and `seo/` content must never be republished to a public repo.

## Verification

- Hub PR on `content/kai-aot-hub-centralization` — 99 docs under `okf/hubs/active-oahu/` (96 migrated + 3 new indices/decision).
- Post-merge: OKF MCP `search "active oahu"` returns hub docs.
- Source-repo pointer PRs replace `okf/` with `okf/README.md`.

## Refs

- `okf/hubs/active-oahu/index.md` — hub master index
- `okf/decisions/okf-agent-commit-authorization.md` — agent commit authorization
- `okf/decisions/prismatic-okf-hub-and-spoke-map.md` — original hub-and-spoke pattern (GRO-3721)
