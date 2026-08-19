---
type: Index
title: Active Oahu Tours — Centralized Knowledge Hub
description: Single canonical home for all Active Oahu Tours knowledge — business ops, compliance, SEO/GEO strategy, architecture doctrine, and verification records — migrated from the per-repo OKFs on 2026-08-19.
tags: [index, hub, active-oahu, aot, tourism]
timestamp: 2026-08-19T14:30:00Z
status: current
resource: okf/hubs/active-oahu/index.md
git_repo: mbgulden/growthwebdev-knowledge
migrated_from_repo: mbgulden/growthwebdev-knowledge
last_verified: 2026-08-19
verified_by: kai
---

# Active Oahu Tours — Centralized Knowledge Hub

Canonical home for **all** Active Oahu Tours (activeoahutours.com) knowledge.
Centralized on **2026-08-19** (Phase 1 of OKF hub consolidation, decided by
Michael). Per-repo `okf/` directories in the source repositories are now
pointer stubs; this hub is the single searchable source of truth indexed by
the OKF MCP.

## Layout

| Section | Contents | Migrated from |
|---|---|---|
| [`business/`](business/index.md) | Ops playbooks, governance system, compliance, incidents, vendors, analytics, site inventory, decision log | `mbgulden/active-oahu-business` (private) |
| [`seo/`](seo/index.md) | SEO/GEO/AI-search strategy, audits, competitor profiles, keyword inventories, GA4/GSC baselines, Ubersuggest integration | `mbgulden/aot-seo-knowledge` (private) |
| [`architecture/`](architecture/astro-emdash/header-footer/README.md) | Astro em-dash header/footer migration doctrine + contract JSONs | `mbgulden/active-oahu-tours-mirror` (public) |
| [`governance/`](governance/cultural-diacritics-search-policy.md) | Cultural diacritics + search policy (Hawaiʻi) | `mbgulden/active-oahu-tours-mirror` |
| [`reports/`](reports/aot-governance-finalization-2026-07-06.md) | Governance finalization, Prismatic Web governance packages, golden-thread reports | `mbgulden/active-oahu-tours-mirror` |
| [`kai-reports/`](kai-reports/gro-3101-image-aspect-ratio-fix-20260716.md) | Kai's GRO completion reports | `mbgulden/active-oahu-tours-mirror` |
| [`audits/`](audits/branch-drift/2026-07-04-main-vs-master.md) | Branch-drift audits + sync plan | `mbgulden/active-oahu-tours-mirror` |
| [`verification/`](verification/gro-3718-remediation-20260710.md) | Lighthouse remediation evidence (GRO-3718) | `mbgulden/active-oahu-tours-mirror` |

## Provenance convention

Every doc carries `migrated_from_repo:` in its frontmatter pointing at the
source repository. Docs retain their original frontmatter fields (tags,
`linear_issue`, timestamps); the managed keys `resource:`, `git_repo:`,
`migrated_from_repo:`, `last_verified:`, `verified_by:` are maintained by the
hub (owner: kai, per PRISMATIC_ENGINE lane `okf/hubs/`).

## Ownership & maintenance

- **Lane owner:** kai (`okf/hubs/` — PRISMATIC_ENGINE.yaml)
- **Branch prefix for hub changes:** `content/`
- Per-PR work packets, verification dumps, and CI-generated reports stay in
  the originating repo's branch — they are not knowledge, they are artifacts.
