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

## Addendum — Phase 2 scope boundary (2026-08-19, Kai)

The consolidation plan named a Phase 2 covering `hd-platform`, `prismatic-engine`,
`Hermes-Research`, and `sentinel`. Full survey of each repo's **default branch**
found that "same treatment as Phase 1" is wrong for all four — the Phase 1
pattern (migrate docs → retire `okf/` to a pointer) applies only when `okf/`
holds knowledge docs. Findings:

| Repo | `okf/` on default branch | Verdict |
|---|---|---|
| `mbgulden/prismatic-engine` | `okf/index.yaml` + `okf/schemas/okf.schema.json` — **schema infrastructure**, read directly by `scripts/validate_okf_docs.py` and `tests/test_okf_docs.py` | **DO NOT RETIRE.** Retiring to a pointer breaks the test suite. This is the machine that validates OKF docs, not knowledge docs. Canonical Prismatic knowledge already lives in the hub at `okf/projects/prismatic-engine/` (per the hub-and-spoke decision, GRO-3721). |
| `mbgulden/hd-platform` | 3 files: `index.md`, `audits/index.md`, `research/index.md` — all empty scaffolds ("No entries yet") | Nothing to migrate. Empty hub-and-spoke stubs, identical to the SIAL pattern. |
| `mbgulden/sentinel-it-asset-logistics` | same 3 empty scaffold files | Nothing to migrate. |
| `mbgulden/Hermes-Research` | 0 okf files on `main` | Nothing to do. |

Secret sweep across all four repos' default branches: **clean** — no
git-filter-repo history rewrite required in Phase 2.

**Boundary rule (durable):** before retiring any repo's `okf/` dir, verify it
contains knowledge docs, not load-bearing infrastructure (schemas, registries,
validator inputs). `prismatic-engine/okf/` is the canonical example of the
latter and is **exempt from retirement** indefinitely. Empty scaffold stubs
(hd-platform, SIAL) are left in place — they are the intended spoke landing
pages; populating them is the project owner's work, not a migration.

Coordination: George and Fred were pinged in the `Prismatic Kai` Telegram group
(2026-08-19 ~16:41 initial notice, ~17:10 course-correction) before any action.
No PRs were opened against prismatic-engine, hd-platform,
sentinel-it-asset-logistics, or Hermes-Research.

Mirrors of these findings were posted in the group; this record is the durable
source of truth.
