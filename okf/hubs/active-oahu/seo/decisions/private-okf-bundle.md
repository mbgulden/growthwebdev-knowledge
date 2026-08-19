---
type: Decision
title: Private OKF Bundle Structure for AOT SEO Initiative
description: Decision to use a private repo (mbgulden/aot-seo-knowledge) for the SEO/GEO initiative rather than the public growthwebdev-knowledge hub.
tags: [decision, okf, aot, seo, private-bundle]
timestamp: 2026-06-19T14:56:00Z
linear_issue: null
git_path: okf/decisions/private-okf-bundle.md
status: accepted
resource: okf/hubs/active-oahu/seo/decisions/private-okf-bundle.md
git_repo: mbgulden/growthwebdev-knowledge
migrated_from_repo: mbgulden/aot-seo-knowledge
last_verified: 2026-08-19
verified_by: kai
---

# Private OKF Bundle Structure for AOT SEO Initiative

## Context

The Active Oahu Tours SEO/GEO initiative generates sensitive competitive intelligence:
- Baseline SEO numbers (DA, traffic, backlinks)
- Competitor gap analysis (what KBA, HBT, Surfnsea rank for that AOT doesn't)
- 6-month strategy roadmap (specific keyword targets, content production queue)
- CRO hypotheses
- Photo-library deployment priorities

This information is operationally sensitive — if published, it would give competitors a roadmap to outflank AOT.

## Decision

Create a **dedicated private repo** at `mbgulden/aot-seo-knowledge` for the SEO initiative, separate from the public `growthwebdev-knowledge` hub.

The public hub still gets a cross-reference under "Private bundles" in `okf/projects/index.md`, but the contents stay private.

## Consequences

**Positive:**
- Competitive intelligence stays secure
- 6-month strategy can be committed to git history without leaking
- Future agents picking up AOT SEO work get the full context without manual onboarding
- Linear issue tracking + GitHub commits create a clear audit trail

**Negative:**
- Two repos to maintain (one public, one private)
- Cross-references needed between them
- The repo name "aot-seo-knowledge" leaks the existence of a separate SEO initiative

**Mitigation:** Repo name is generic enough that a casual observer wouldn't know it's sensitive. The private visibility setting prevents anonymous access.

## Alternatives considered

- **A) Put everything in the public hub** — rejected: leaks competitive intelligence
- **B) Local-only, no git** — rejected: no audit trail, no backup, no sharing
- **C) Single private repo per project (AOT, but also future SEO initiatives for other projects)** — accepted pattern for future projects too
- **D) GitHub Enterprise with SSO** — rejected: overkill for solo operator

## Implementation

- Repo created: https://github.com/mbgulden/aot-seo-knowledge
- Visibility: Private (confirmed: anonymous API access returns 404)
- Cross-reference from public hub: `okf/projects/index.md` "Private bundles" section
- Backup: same git history, just remote-only access

## Refs

- OKF spec: https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md
- Public hub: https://github.com/mbgulden/growthwebdev-knowledge
