---
type: Report
title: Prismatic OKF treasure hunt Phase 1–6 reconciliation
description: Inventory, priority extraction, dedupe, classification, canonical structure proposal, and promotion plan for stranded Prismatic Engine OKF/documentation sources.
resource: okf/reports/prismatic-okf-treasure-hunt-2026-07-15.md
tags: [report, prismatic-engine, okf, documentation, treasure-hunt, reconciliation]
timestamp: 2026-07-15T00:45:41Z
linear_issue: GRO-3721
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/reports/prismatic-okf-treasure-hunt-2026-07-15.md
last_verified: 2026-07-15
verified_by: fred
status: current
---

# Prismatic OKF Treasure Map — Phase 1–6 Reconciliation

Generated: 2026-07-15T00:45:41.488384+00:00

## 1. Executive summary

Prismatic documentation is not gone; it is fragmented. Current `deploy-fresh` has a breadcrumb map but no first-class `okf/` tree, while priority backup/Ned/knowledge-hub branches contain thousands of candidate docs and repeated full OKF trees. This phase inventories sources, extracts priority hidden docs without checkout pollution, groups duplicate families, classifies documents, and proposes the canonical OKF structure before any cleanup.

## 2. Source inventory counts

| Source | Branch/ref records | Branch-summed OKF files | Notes |
|---|---:|---:|---|
| `prismatic-engine` | 1785 | 13995 | Includes local, origin, dev-repo/stale refs where locally inspectable. |
| `growthwebdev-knowledge` | 102 | 17285 | Includes local, origin, dev-repo/stale refs where locally inspectable. |
| local `/home/ubuntu/work/**/okf` dirs | 52 | 1337 files | Includes archived worktree cleanup directories. |

## 3. Hidden branches/worktrees with OKF docs

| Repo | Branch/ref | OKF files | MD files | Prismatic-ish MD | Reachable from remote | Notes |
|---|---|---:|---:|---:|---|---|
| `prismatic-engine` | `backup/gro-3522-inlane-disconnected` | 301 | 901 | 485 | True |  |
| `prismatic-engine` | `dev-repo/backup/gro-3522-inlane-disconnected` | 301 | 901 | 485 | False | dev-repo ref; fetch may be stale or remote may be unavailable; local-only or stale local ref; no matching origin/dev-rep |
| `prismatic-engine` | `dev-repo/ned/GRO-3509` | 301 | 901 | 485 | False | dev-repo ref; fetch may be stale or remote may be unavailable; local-only or stale local ref; no matching origin/dev-rep |
| `prismatic-engine` | `ned/GRO-3509` | 301 | 901 | 485 | True |  |
| `prismatic-engine` | `backup/gro-3515-full-okf-blocked` | 301 | 900 | 484 | True |  |
| `prismatic-engine` | `backup/gro-3522-full-okf-blocked` | 301 | 900 | 484 | True |  |
| `prismatic-engine` | `dev-repo/backup/gro-3515-full-okf-blocked` | 301 | 900 | 484 | False | dev-repo ref; fetch may be stale or remote may be unavailable; local-only or stale local ref; no matching origin/dev-rep |
| `prismatic-engine` | `dev-repo/backup/gro-3522-full-okf-blocked` | 301 | 900 | 484 | False | dev-repo ref; fetch may be stale or remote may be unavailable; local-only or stale local ref; no matching origin/dev-rep |
| `prismatic-engine` | `dev-repo/feature/GRO-3781-meridian-asset-curation` | 301 | 900 | 484 | False | dev-repo ref; fetch may be stale or remote may be unavailable; local-only or stale local ref; no matching origin/dev-rep |
| `prismatic-engine` | `dev-repo/feature/distribution-requirements-txt` | 301 | 900 | 484 | False | dev-repo ref; fetch may be stale or remote may be unavailable; local-only or stale local ref; no matching origin/dev-rep |
| `prismatic-engine` | `dev-repo/feature/gro-3258-terraform-cloud-deploy` | 301 | 900 | 484 | False | dev-repo ref; fetch may be stale or remote may be unavailable; local-only or stale local ref; no matching origin/dev-rep |
| `prismatic-engine` | `dev-repo/feature/gro-3260-example-lane` | 301 | 900 | 484 | False | dev-repo ref; fetch may be stale or remote may be unavailable; local-only or stale local ref; no matching origin/dev-rep |
| `prismatic-engine` | `dev-repo/feature/gro-3297-visual-verification` | 301 | 900 | 484 | False | dev-repo ref; fetch may be stale or remote may be unavailable; local-only or stale local ref; no matching origin/dev-rep |
| `prismatic-engine` | `dev-repo/feature/gro-3524-command-plane-hardening` | 301 | 900 | 484 | False | dev-repo ref; fetch may be stale or remote may be unavailable; local-only or stale local ref; no matching origin/dev-rep |
| `prismatic-engine` | `dev-repo/feature/gro-3781-meridian-asset-curation` | 301 | 900 | 484 | False | dev-repo ref; fetch may be stale or remote may be unavailable; local-only or stale local ref; no matching origin/dev-rep |
| `prismatic-engine` | `dev-repo/feature/pwp-phase0-contract-compat-review` | 301 | 900 | 484 | False | dev-repo ref; fetch may be stale or remote may be unavailable; local-only or stale local ref; no matching origin/dev-rep |
| `prismatic-engine` | `dev-repo/feature/pwp-system-website-build-orchestration` | 301 | 900 | 484 | False | dev-repo ref; fetch may be stale or remote may be unavailable; local-only or stale local ref; no matching origin/dev-rep |
| `prismatic-engine` | `dev-repo/merge/pipeline-v2` | 301 | 900 | 484 | False | dev-repo ref; fetch may be stale or remote may be unavailable; local-only or stale local ref; no matching origin/dev-rep |
| `prismatic-engine` | `dev-repo/ned/GRO-2445-okf-drive-drift-check` | 301 | 900 | 484 | False | dev-repo ref; fetch may be stale or remote may be unavailable; local-only or stale local ref; no matching origin/dev-rep |
| `prismatic-engine` | `dev-repo/ned/GRO-2445-okf-drive-drift-refresh` | 301 | 900 | 484 | False | dev-repo ref; fetch may be stale or remote may be unavailable; local-only or stale local ref; no matching origin/dev-rep |
| `prismatic-engine` | `dev-repo/ned/GRO-3519` | 301 | 900 | 484 | False | dev-repo ref; fetch may be stale or remote may be unavailable; local-only or stale local ref; no matching origin/dev-rep |
| `prismatic-engine` | `dev-repo/test-merge-rate-limits` | 301 | 900 | 484 | False | dev-repo ref; fetch may be stale or remote may be unavailable; local-only or stale local ref; no matching origin/dev-rep |
| `prismatic-engine` | `feature/GRO-3781-meridian-asset-curation` | 301 | 900 | 484 | True |  |
| `prismatic-engine` | `feature/distribution-requirements-txt` | 301 | 900 | 484 | True |  |
| `prismatic-engine` | `feature/gro-3258-terraform-cloud-deploy` | 301 | 900 | 484 | True |  |
| `prismatic-engine` | `feature/gro-3260-example-lane` | 301 | 900 | 484 | True |  |
| `prismatic-engine` | `feature/gro-3297-visual-verification` | 301 | 900 | 484 | True |  |
| `prismatic-engine` | `feature/gro-3524-command-plane-hardening` | 301 | 900 | 484 | True |  |
| `prismatic-engine` | `feature/gro-3781-meridian-asset-curation` | 301 | 900 | 484 | True |  |
| `prismatic-engine` | `feature/pwp-phase0-contract-compat-review` | 301 | 900 | 484 | True |  |
| `prismatic-engine` | `feature/pwp-system-website-build-orchestration` | 301 | 900 | 484 | True |  |
| `prismatic-engine` | `merge/pipeline-v2` | 301 | 900 | 484 | True |  |
| `prismatic-engine` | `ned/GRO-2445-okf-drive-drift-check` | 301 | 900 | 484 | True |  |
| `prismatic-engine` | `ned/GRO-2445-okf-drive-drift-refresh` | 301 | 900 | 484 | True |  |
| `prismatic-engine` | `ned/GRO-3519` | 301 | 900 | 484 | True |  |

### Local archived OKF directories

| Path | Files | Prismatic-ish | Archived? |
|---|---:|---:|---|
| `/home/ubuntu/work/growthwebdev-knowledge/okf` | 323 | 323 | False |
| `/home/ubuntu/work/okf` | 397 | 104 | False |
| `/home/ubuntu/work/aot-seo-knowledge/okf` | 88 | 58 | False |
| `/home/ubuntu/work/belief-deprogrammer/okf` | 27 | 26 | False |
| `/home/ubuntu/work/darius-star-gro-2165/okf` | 25 | 25 | False |
| `/home/ubuntu/work/darius-star/okf` | 25 | 25 | False |
| `/home/ubuntu/work/active-oahu-business/okf` | 20 | 19 | False |
| `/home/ubuntu/work/active-oahu-tours-mirror-1251/okf` | 50 | 18 | False |
| `/home/ubuntu/work/aot-business-gameplan-2026-07-08/okf` | 20 | 18 | False |
| `/home/ubuntu/work/aot-business-kba-countercontent/okf` | 19 | 18 | False |
| `/home/ubuntu/work/active-oahu-tours-mirror/okf` | 49 | 17 | False |
| `/home/ubuntu/work/aot-governance-watchdog-worktree/okf` | 49 | 17 | False |
| `/home/ubuntu/work/worktree-cleanup-20260712T033423Z/tmp-git-dirs-moved/aot-business-seo-report/okf` | 18 | 17 | True |
| `/home/ubuntu/work/aot-gro3718-best-practices/okf` | 15 | 9 | False |
| `/home/ubuntu/work/worktree-cleanup-20260712T033423Z/tmp-git-dirs-moved/aot-gro3640-console-fix/okf` | 12 | 9 | True |
| `/home/ubuntu/work/worktree-cleanup-20260712T033423Z/tmp-git-dirs-moved/aot-pr77-verify/okf` | 12 | 9 | True |
| `/home/ubuntu/work/active-oahu-tours-mirror-2529/okf` | 8 | 8 | False |
| `/home/ubuntu/work/aot-gro-558/okf` | 8 | 8 | False |
| `/home/ubuntu/work/aot-gro3640-booking-mobile-conversion/okf` | 8 | 8 | False |
| `/home/ubuntu/work/aot-gro3645-booking-intent/okf` | 8 | 8 | False |
| `/home/ubuntu/work/aot-gro3665-csp-console-hotfix/okf` | 8 | 8 | False |
| `/home/ubuntu/work/aot-gro3649-lanikai/okf` | 7 | 7 | False |
| `/home/ubuntu/work/aot-gro3665-fonts/okf` | 7 | 7 | False |
| `/home/ubuntu/work/meridian-static-site/okf` | 6 | 6 | False |
| `/home/ubuntu/work/hd-platform/okf` | 106 | 5 | False |
| `/home/ubuntu/work/sentinel-it-asset-logistics/okf` | 5 | 5 | False |
| `/home/ubuntu/work/beyondsaas-site/okf` | 3 | 3 | False |
| `/home/ubuntu/work/hd-platform-staging/okf` | 3 | 3 | False |
| `/home/ubuntu/work/homelab/okf` | 3 | 3 | False |
| `/home/ubuntu/work/active-oahu-static/okf` | 2 | 2 | False |

## 4. Top 20 high-value hidden docs

| Class | Family | Repo | Branch | Path | Title | Recommendation |
|---|---|---|---|---|---|---|
| hidden-historical | AGY audit | `prismatic-engine` | `backup/gro-3515-full-okf-blocked` | `docs/agy-night/directory-indexes/prismatic-agents.md` | Directory Index: `prismatic/agents` | archive/index as historical after summary |
| hidden-historical | AGY audit | `prismatic-engine` | `backup/gro-3515-full-okf-blocked` | `docs/agy-night/directory-indexes/prismatic-api-routers.md` | Directory Index: `prismatic/api/routers` | archive/index as historical after summary |
| hidden-historical | AGY audit | `prismatic-engine` | `backup/gro-3515-full-okf-blocked` | `docs/agy-night/directory-indexes/prismatic-core.md` | Prismatic Core Directory Index | archive/index as historical after summary |
| hidden-historical | AGY audit | `prismatic-engine` | `backup/gro-3515-full-okf-blocked` | `docs/agy-night/directory-indexes/prismatic-interface.md` | Prismatic Interface Directory Index | archive/index as historical after summary |
| hidden-historical | AGY audit | `prismatic-engine` | `backup/gro-3515-full-okf-blocked` | `docs/agy-night/directory-indexes/prismatic-network.md` | Directory Index: `prismatic/network` | archive/index as historical after summary |
| hidden-historical | AGY audit | `prismatic-engine` | `backup/gro-3515-full-okf-blocked` | `docs/agy-night/directory-indexes/prismatic-providers-tasks.md` | Directory Index: `prismatic/providers/tasks` | archive/index as historical after summary |
| hidden-historical | AGY audit | `prismatic-engine` | `backup/gro-3515-full-okf-blocked` | `docs/agy-night/directory-indexes/prismatic-providers.md` | Directory Index: `prismatic/providers` | archive/index as historical after summary |
| hidden-historical | AGY audit | `prismatic-engine` | `backup/gro-3515-full-okf-blocked` | `docs/agy-night/module-cards/prismatic-agent-cards-py.md` | Module Card: `prismatic/agent_cards.py` | archive/index as historical after summary |
| hidden-historical | AGY audit | `prismatic-engine` | `backup/gro-3515-full-okf-blocked` | `docs/agy-night/module-cards/prismatic-agents-base-py.md` | Module Card: `prismatic/agents/base.py` | archive/index as historical after summary |
| hidden-historical | AGY audit | `prismatic-engine` | `backup/gro-3515-full-okf-blocked` | `docs/agy-night/module-cards/prismatic-agents-hermes-py.md` | Module Card: prismatic/agents/hermes.py | archive/index as historical after summary |
| hidden-historical | AGY audit | `prismatic-engine` | `backup/gro-3515-full-okf-blocked` | `docs/agy-night/module-cards/prismatic-agents-init-py.md` | Module Card: `prismatic/agents/__init__.py` | archive/index as historical after summary |
| hidden-historical | AGY audit | `prismatic-engine` | `backup/gro-3515-full-okf-blocked` | `docs/agy-night/module-cards/prismatic-agy-live-parser-py.md` | Module Card: `prismatic/agy_live_parser.py` | archive/index as historical after summary |
| hidden-historical | AGY audit | `prismatic-engine` | `backup/gro-3515-full-okf-blocked` | `docs/agy-night/module-cards/prismatic-api-init-py.md` | Module Card: prismatic/api/__init__.py | archive/index as historical after summary |
| hidden-historical | AGY audit | `prismatic-engine` | `backup/gro-3515-full-okf-blocked` | `docs/agy-night/module-cards/prismatic-api-main-py.md` | Module Card: prismatic/api/main.py | archive/index as historical after summary |
| hidden-historical | AGY audit | `prismatic-engine` | `backup/gro-3515-full-okf-blocked` | `docs/agy-night/module-cards/prismatic-api-routers-credits-py.md` | Module Card: `prismatic/api/routers/credits.py` | archive/index as historical after summary |
| hidden-historical | AGY audit | `prismatic-engine` | `backup/gro-3515-full-okf-blocked` | `docs/agy-night/module-cards/prismatic-api-routers-init-py.md` | Module Card: prismatic/api/routers/__init__.py | archive/index as historical after summary |
| hidden-historical | AGY audit | `prismatic-engine` | `backup/gro-3515-full-okf-blocked` | `docs/agy-night/module-cards/prismatic-api-routers-jobs-py.md` | Module Card: prismatic/api/routers/jobs.py | archive/index as historical after summary |
| hidden-historical | AGY audit | `prismatic-engine` | `backup/gro-3515-full-okf-blocked` | `docs/agy-night/module-cards/prismatic-api-server-py.md` | Module Card: `prismatic/api/server.py` | archive/index as historical after summary |
| hidden-historical | AGY audit | `prismatic-engine` | `backup/gro-3515-full-okf-blocked` | `docs/agy-night/module-cards/prismatic-billing-cost-attribution-py.md` | Implementation Card: Client Cost Attribution Engine (`prismatic/billing/cost_att | archive/index as historical after summary |
| hidden-historical | AGY audit | `prismatic-engine` | `backup/gro-3515-full-okf-blocked` | `docs/agy-night/module-cards/prismatic-billing-credit-ledger-py.md` | Module Card: `prismatic/billing/credit_ledger.py` | archive/index as historical after summary |

## 5. Duplicate families

| Family | Canonical candidate | Duplicates | Action |
|---|---|---:|---|
| Ned scan-triage OKF | `growthwebdev-knowledge:origin/feature/fred-okf-gap13-sync:okf/audits/ned-scan-triage-2026-06-27-r2.md` | 412 | summarize/archive as historical; do not promote every per-run file |
| Plugin ecosystem | `growthwebdev-knowledge:origin/feature/fred-okf-gap13-sync:okf/standards/ui-ux-plan.md` | 364 | merge useful evidence into one current report |
| Governance dashboard | `growthwebdev-knowledge:origin/feature/fred-okf-gap13-sync:okf/standards/pwp-ingest-spec.md` | 344 | merge current dashboard proof/history into project records |
| Other Prismatic docs | `growthwebdev-knowledge:origin/feature/fred-okf-gap13-sync:okf/reports/index.md` | 219 | merge useful evidence into one current report |
| AGY audit | `growthwebdev-knowledge:origin/feature/fred-okf-gap13-sync:okf/standards/agy-peer-review.md` | 171 | merge useful evidence into one current report |
| Webhook / Linear security | `growthwebdev-knowledge:origin/feature/fred-okf-gap13-sync:okf/standards/webhook-security.md` | 155 | merge useful evidence into one current report |
| Dispatcher incident | `growthwebdev-knowledge:origin/feature/fred-okf-gap13-sync:okf/decisions/event-driven-dispatch.md` | 117 | merge useful evidence into one current report |
| OKF drift / recovery | `growthwebdev-knowledge:origin/feature/fred-okf-gap13-sync:okf/audits/ned-scan-triage-2026-06-27-r1.md` | 40 | create OKF drift and recovery history record |
| Tier 7 hardening | `growthwebdev-knowledge:origin/feature/fred-okf-hde-cron-closeouts-20260713:okf/standards/prismatic-staging-governance.md` | 15 | promote/update hub project index for Tier 7 journey and architecture |
| Canonical merge winner maps | `prismatic-engine:backup/gro-3515-full-okf-blocked:okf/audits/canonical-merge-winner-map-2026-07-06.md` | 3 | preserve one canonical map; record duplicates as superseded |

Exact content duplicate groups among priority docs: **402**.

## 6. Document classification summary

| Class | Count | Meaning / action |
|---|---:|---|
| `duplicate-superseded` | 1138 | Same path/content or obsolete version; do not promote directly. |
| `hidden-historical` | 549 | Useful as history/provenance only; archive/index as historical. |
| `hidden-useful` | 155 | Not indexed/current, contains still-useful facts; promote or merge. |
| `unsafe/private` | 8 | Potential secret/private marker; quarantine. |

## 7. Recommended canonical structure

Proposed hub project structure:

```text
growthwebdev-knowledge/okf/projects/prismatic-engine/index.md
growthwebdev-knowledge/okf/projects/prismatic-engine/ingestion-queue-repair-2026-07-14.md
growthwebdev-knowledge/okf/projects/prismatic-engine/tier-7-journey.md
growthwebdev-knowledge/okf/projects/prismatic-engine/tier-7-architecture.md
growthwebdev-knowledge/okf/projects/prismatic-engine/dispatcher-incident-history.md
growthwebdev-knowledge/okf/projects/prismatic-engine/governance-dashboard-history.md
growthwebdev-knowledge/okf/projects/prismatic-engine/okf-drift-and-recovery-history.md
```

Proposed standards/decisions/reports:

```text
growthwebdev-knowledge/okf/standards/prismatic-staging-governance.md
growthwebdev-knowledge/okf/standards/prismatic-dashboard-live-proof.md
growthwebdev-knowledge/okf/standards/okf-worktree-reconciliation.md
growthwebdev-knowledge/okf/decisions/prismatic-okf-hub-and-spoke-map.md
growthwebdev-knowledge/okf/reports/prismatic-okf-treasure-hunt-2026-07-15.md
```

Repo-local spoke map remains:

```text
prismatic-engine/docs/okf-map.md
```

## 8. Promotion plan

1. **Batch 1 — Inventory + treasure map:** landed/maintain this report plus reports/project indexes.
2. **Batch 2 — Canonical project index/current records:** create `okf/projects/prismatic-engine/index.md`; promote Tier 7, dispatcher, governance dashboard, webhook/Linear, and OKF drift current records.
3. **Batch 3 — Historical/archive docs:** summarize Ned scan-triage and AGY audit families instead of promoting every per-run file.
4. **Batch 4 — Repo-local breadcrumb update:** update `prismatic-engine/docs/okf-map.md` after hub structure is landed.

## 9. Risks/blockers

- Branch-summed OKF counts include duplicated trees across refs; do not treat them as unique docs.
- Some dev/sandbox remotes are stale or broken; local refs were inspected when fetch was unreliable.
- `growthwebdev-knowledge` primary checkout is dirty/on a feature branch; use clean worktrees for PRs.
- Potential unsafe/private markers must be quarantined before publication.
- Do not delete backup branches or archived worktrees until promotion batches land and cleanup candidates are reverified.

## 10. Exact cleanup candidates safe after promotion

No cleanup candidate is safe **now**. After promotion, review:

| Candidate | Reason | Safe now? |
|---|---|---|
| `dev-repo/backup/gro-3522-inlane-disconnected` | dev-repo duplicate/stale ref with full OKF tree; safe only after canonical docs promoted and branch ref backed up | False |
| `dev-repo/ned/GRO-3509` | dev-repo duplicate/stale ref with full OKF tree; safe only after canonical docs promoted and branch ref backed up | False |
| `dev-repo/backup/gro-3515-full-okf-blocked` | dev-repo duplicate/stale ref with full OKF tree; safe only after canonical docs promoted and branch ref backed up | False |
| `dev-repo/backup/gro-3522-full-okf-blocked` | dev-repo duplicate/stale ref with full OKF tree; safe only after canonical docs promoted and branch ref backed up | False |
| `dev-repo/feature/GRO-3781-meridian-asset-curation` | dev-repo duplicate/stale ref with full OKF tree; safe only after canonical docs promoted and branch ref backed up | False |
| `dev-repo/feature/distribution-requirements-txt` | dev-repo duplicate/stale ref with full OKF tree; safe only after canonical docs promoted and branch ref backed up | False |
| `dev-repo/feature/gro-3258-terraform-cloud-deploy` | dev-repo duplicate/stale ref with full OKF tree; safe only after canonical docs promoted and branch ref backed up | False |
| `dev-repo/feature/gro-3260-example-lane` | dev-repo duplicate/stale ref with full OKF tree; safe only after canonical docs promoted and branch ref backed up | False |
| `dev-repo/feature/gro-3297-visual-verification` | dev-repo duplicate/stale ref with full OKF tree; safe only after canonical docs promoted and branch ref backed up | False |
| `dev-repo/feature/gro-3524-command-plane-hardening` | dev-repo duplicate/stale ref with full OKF tree; safe only after canonical docs promoted and branch ref backed up | False |
| `dev-repo/feature/gro-3781-meridian-asset-curation` | dev-repo duplicate/stale ref with full OKF tree; safe only after canonical docs promoted and branch ref backed up | False |
| `dev-repo/feature/pwp-phase0-contract-compat-review` | dev-repo duplicate/stale ref with full OKF tree; safe only after canonical docs promoted and branch ref backed up | False |
| `dev-repo/feature/pwp-system-website-build-orchestration` | dev-repo duplicate/stale ref with full OKF tree; safe only after canonical docs promoted and branch ref backed up | False |
| `dev-repo/merge/pipeline-v2` | dev-repo duplicate/stale ref with full OKF tree; safe only after canonical docs promoted and branch ref backed up | False |
| `dev-repo/ned/GRO-2445-okf-drive-drift-check` | dev-repo duplicate/stale ref with full OKF tree; safe only after canonical docs promoted and branch ref backed up | False |
| `dev-repo/ned/GRO-2445-okf-drive-drift-refresh` | dev-repo duplicate/stale ref with full OKF tree; safe only after canonical docs promoted and branch ref backed up | False |
| `dev-repo/ned/GRO-3519` | dev-repo duplicate/stale ref with full OKF tree; safe only after canonical docs promoted and branch ref backed up | False |
| `dev-repo/test-merge-rate-limits` | dev-repo duplicate/stale ref with full OKF tree; safe only after canonical docs promoted and branch ref backed up | False |
| `dev-repo/ned/GRO-3508-dashboard-fix` | dev-repo duplicate/stale ref with full OKF tree; safe only after canonical docs promoted and branch ref backed up | False |
| `dev-repo/ned/GRO-3516` | dev-repo duplicate/stale ref with full OKF tree; safe only after canonical docs promoted and branch ref backed up | False |

## 11. Verification evidence

Phase 2–6 generated metrics:

```json
{
  "priority_candidate_docs": 1850,
  "exact_duplicate_groups": 402,
  "concept_families": 10,
  "classification_counts": {
    "duplicate-superseded": 1138,
    "hidden-historical": 549,
    "hidden-useful": 155,
    "unsafe/private": 8
  }
}
```

Manifest/report generation wrote:

- `/tmp/prismatic-okf-treasure-hunt/manifests/prismatic-engine-branches.json`
- `/tmp/prismatic-okf-treasure-hunt/manifests/growthwebdev-knowledge-branches.json`
- `/tmp/prismatic-okf-treasure-hunt/manifests/local-okf-directories.json`
- `/tmp/prismatic-okf-treasure-hunt/manifests/priority-candidate-docs.json`
- `/tmp/prismatic-okf-treasure-hunt/manifests/priority-candidate-docs.csv`
- `/tmp/prismatic-okf-treasure-hunt/manifests/priority-exact-duplicate-groups.json`
- `/tmp/prismatic-okf-treasure-hunt/manifests/priority-concept-families.json`
- `/tmp/prismatic-okf-treasure-hunt/manifests/cleanup-candidates-after-promotion.json`
- `/tmp/prismatic-okf-treasure-hunt/manifests/phase2-6-summary.json`

Boundary: ad hoc targeted verification only — not full docs-suite green.
