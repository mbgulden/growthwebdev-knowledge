---
type: Report
title: Prismatic OKF treasure hunt Phase 0/1 inventory
description: Inventory report for stranded Prismatic Engine OKF and documentation sources across backup branches, Ned drift branches, knowledge-hub branches, and archived local worktrees.
resource: okf/reports/prismatic-okf-treasure-hunt-2026-07-15.md
tags: [report, prismatic-engine, okf, documentation, treasure-hunt, reconciliation]
timestamp: 2026-07-15T00:36:05Z
linear_issue: GRO-3721
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/reports/prismatic-okf-treasure-hunt-2026-07-15.md
last_verified: 2026-07-15
verified_by: fred
status: current
---

# Prismatic OKF Treasure Map — Phase 0/1 Inventory

Generated: 2026-07-15T00:36:05.126481+00:00

## Executive summary

Current `deploy-fresh` has a repo-local OKF map but no restored first-class `okf/` tree. This Phase 0/1 inventory confirms substantial historical OKF/doc material is stranded across backup branches, Ned OKF drift branches, knowledge-hub branches, and local archived worktrees.

## Source inventory counts

| Source | Branches with OKF/Prismatic docs | Sum OKF files across branches | Candidate docs extracted |
|---|---:|---:|---:|
| `prismatic-engine` | 1785 | 13995 | 2025 |
| `growthwebdev-knowledge` | 100 | 16828 | 2025 |
| local `/home/ubuntu/work/**/okf` dirs | 49 | sampled MD dirs | n/a |

## Highest-signal hidden branches

| Repo | Branch | OKF files | Prismatic-ish MD | Head |
|---|---|---:|---:|---|
| `prismatic-engine` | `backup/gro-3522-inlane-disconnected` | 301 | 454 | `239a6c59ca11` |
| `prismatic-engine` | `dev-repo/backup/gro-3522-inlane-disconnected` | 301 | 454 | `239a6c59ca11` |
| `prismatic-engine` | `dev-repo/ned/GRO-3509` | 301 | 454 | `a32575200642` |
| `prismatic-engine` | `ned/GRO-3509` | 301 | 454 | `a32575200642` |
| `prismatic-engine` | `backup/gro-3515-full-okf-blocked` | 301 | 453 | `3133a5590705` |
| `prismatic-engine` | `backup/gro-3522-full-okf-blocked` | 301 | 453 | `f5a85cd42f28` |
| `prismatic-engine` | `dev-repo/backup/gro-3515-full-okf-blocked` | 301 | 453 | `3133a5590705` |
| `prismatic-engine` | `dev-repo/backup/gro-3522-full-okf-blocked` | 301 | 453 | `f5a85cd42f28` |
| `prismatic-engine` | `dev-repo/feature/GRO-3781-meridian-asset-curation` | 301 | 453 | `5bdc62e92b95` |
| `prismatic-engine` | `dev-repo/feature/distribution-requirements-txt` | 301 | 453 | `41e2cd2a26c9` |
| `prismatic-engine` | `dev-repo/feature/gro-3258-terraform-cloud-deploy` | 301 | 453 | `5722aa66e154` |
| `prismatic-engine` | `dev-repo/feature/gro-3260-example-lane` | 301 | 453 | `5722aa66e154` |
| `prismatic-engine` | `dev-repo/feature/gro-3297-visual-verification` | 301 | 453 | `5722aa66e154` |
| `prismatic-engine` | `dev-repo/feature/gro-3524-command-plane-hardening` | 301 | 453 | `5722aa66e154` |
| `prismatic-engine` | `dev-repo/feature/gro-3781-meridian-asset-curation` | 301 | 453 | `3efc0bef8b8c` |
| `prismatic-engine` | `dev-repo/feature/pwp-phase0-contract-compat-review` | 301 | 453 | `3efc0bef8b8c` |
| `prismatic-engine` | `dev-repo/feature/pwp-system-website-build-orchestration` | 301 | 453 | `5bdc62e92b95` |
| `prismatic-engine` | `dev-repo/merge/pipeline-v2` | 301 | 453 | `5722aa66e154` |
| `prismatic-engine` | `dev-repo/ned/GRO-2445-okf-drive-drift-check` | 301 | 453 | `5bdc62e92b95` |
| `prismatic-engine` | `dev-repo/ned/GRO-2445-okf-drive-drift-refresh` | 301 | 453 | `3efc0bef8b8c` |
| `prismatic-engine` | `dev-repo/ned/GRO-3519` | 301 | 453 | `e8a6484be540` |
| `prismatic-engine` | `dev-repo/test-merge-rate-limits` | 301 | 453 | `41e2cd2a26c9` |
| `prismatic-engine` | `feature/GRO-3781-meridian-asset-curation` | 301 | 453 | `5bdc62e92b95` |
| `prismatic-engine` | `feature/distribution-requirements-txt` | 301 | 453 | `41e2cd2a26c9` |
| `prismatic-engine` | `feature/gro-3258-terraform-cloud-deploy` | 301 | 453 | `5722aa66e154` |
| `prismatic-engine` | `feature/gro-3260-example-lane` | 301 | 453 | `5722aa66e154` |
| `prismatic-engine` | `feature/gro-3297-visual-verification` | 301 | 453 | `5722aa66e154` |
| `prismatic-engine` | `feature/gro-3524-command-plane-hardening` | 301 | 453 | `5722aa66e154` |
| `prismatic-engine` | `feature/gro-3781-meridian-asset-curation` | 301 | 453 | `3efc0bef8b8c` |
| `prismatic-engine` | `feature/pwp-phase0-contract-compat-review` | 301 | 453 | `3efc0bef8b8c` |
| `prismatic-engine` | `feature/pwp-system-website-build-orchestration` | 301 | 453 | `5bdc62e92b95` |
| `prismatic-engine` | `merge/pipeline-v2` | 301 | 453 | `5722aa66e154` |
| `prismatic-engine` | `ned/GRO-2445-okf-drive-drift-check` | 301 | 453 | `5bdc62e92b95` |
| `prismatic-engine` | `ned/GRO-2445-okf-drive-drift-refresh` | 301 | 453 | `3efc0bef8b8c` |
| `prismatic-engine` | `ned/GRO-3519` | 301 | 453 | `e8a6484be540` |

## Top high-value candidate docs

| Score | Repo | Branch | Path | Title | Recommendation |
|---:|---|---|---|---|---|
| 29 | `growthwebdev-knowledge` | `feature/fred-okf-prismatic-ingestion-queue-closeout` | `okf/projects/prismatic-engine/ingestion-queue-repair-2026-07-14.md` | Prismatic Governance Dashboard Ingestion Queue repair closeout — 2026-07-14 | review |
| 29 | `growthwebdev-knowledge` | `origin/feature/fred-okf-prismatic-ingestion-queue-closeout` | `okf/projects/prismatic-engine/ingestion-queue-repair-2026-07-14.md` | Prismatic Governance Dashboard Ingestion Queue repair closeout — 2026-07-14 | review |
| 29 | `growthwebdev-knowledge` | `origin/main` | `okf/projects/prismatic-engine/ingestion-queue-repair-2026-07-14.md` | Prismatic Governance Dashboard Ingestion Queue repair closeout — 2026-07-14 | keep-index |
| 19 | `growthwebdev-knowledge` | `deploy-fresh` | `okf/plugins/prismatic-engine-core-ingestion-top-level/prism_ingest_1_code_quality___auditing.md` | PRISM_INGEST_1_Code_Quality___Auditing | keep-index |
| 19 | `growthwebdev-knowledge` | `deploy-fresh` | `okf/plugins/prismatic-engine-core-ingestion-top-level/prism_ingest_25_compliance_auditing_and_multi-store_delivery.md` | PRISM_INGEST_25_Compliance_Auditing_and_Multi-Store_Delivery | keep-index |
| 19 | `growthwebdev-knowledge` | `deploy-fresh` | `okf/plugins/prismatic-engine-core-ingestion-top-level/prism_ingest_35_memory_auditing_and_object_pooling.md` | PRISM_INGEST_35_Memory_Auditing_and_Object_Pooling | keep-index |
| 19 | `growthwebdev-knowledge` | `feature/fred-okf-gap13-sync` | `okf/plugins/prismatic-engine-core-ingestion-top-level/prism_ingest_1_code_quality___auditing.md` | PRISM_INGEST_1_Code_Quality___Auditing | review |
| 19 | `growthwebdev-knowledge` | `feature/fred-okf-gap13-sync` | `okf/plugins/prismatic-engine-core-ingestion-top-level/prism_ingest_25_compliance_auditing_and_multi-store_delivery.md` | PRISM_INGEST_25_Compliance_Auditing_and_Multi-Store_Delivery | review |
| 19 | `growthwebdev-knowledge` | `feature/fred-okf-gap13-sync` | `okf/plugins/prismatic-engine-core-ingestion-top-level/prism_ingest_35_memory_auditing_and_object_pooling.md` | PRISM_INGEST_35_Memory_Auditing_and_Object_Pooling | review |
| 19 | `growthwebdev-knowledge` | `feature/fred-okf-hde-cron-closeouts-20260713` | `okf/plugins/prismatic-engine-core-ingestion-top-level/prism_ingest_1_code_quality___auditing.md` | PRISM_INGEST_1_Code_Quality___Auditing | review |
| 19 | `growthwebdev-knowledge` | `feature/fred-okf-hde-cron-closeouts-20260713` | `okf/plugins/prismatic-engine-core-ingestion-top-level/prism_ingest_25_compliance_auditing_and_multi-store_delivery.md` | PRISM_INGEST_25_Compliance_Auditing_and_Multi-Store_Delivery | review |
| 19 | `growthwebdev-knowledge` | `feature/fred-okf-hde-cron-closeouts-20260713` | `okf/plugins/prismatic-engine-core-ingestion-top-level/prism_ingest_35_memory_auditing_and_object_pooling.md` | PRISM_INGEST_35_Memory_Auditing_and_Object_Pooling | review |
| 19 | `growthwebdev-knowledge` | `feature/fred-okf-prismatic-ingestion-queue-closeout` | `okf/plugins/prismatic-engine-core-ingestion-top-level/prism_ingest_1_code_quality___auditing.md` | PRISM_INGEST_1_Code_Quality___Auditing | review |
| 19 | `growthwebdev-knowledge` | `feature/fred-okf-prismatic-ingestion-queue-closeout` | `okf/plugins/prismatic-engine-core-ingestion-top-level/prism_ingest_25_compliance_auditing_and_multi-store_delivery.md` | PRISM_INGEST_25_Compliance_Auditing_and_Multi-Store_Delivery | review |
| 19 | `growthwebdev-knowledge` | `feature/fred-okf-prismatic-ingestion-queue-closeout` | `okf/plugins/prismatic-engine-core-ingestion-top-level/prism_ingest_35_memory_auditing_and_object_pooling.md` | PRISM_INGEST_35_Memory_Auditing_and_Object_Pooling | review |
| 19 | `growthwebdev-knowledge` | `feature/gro-2131` | `okf/plugins/prismatic-engine-core-ingestion-top-level/prism_ingest_1_code_quality___auditing.md` | PRISM_INGEST_1_Code_Quality___Auditing | review |
| 19 | `growthwebdev-knowledge` | `feature/gro-2131` | `okf/plugins/prismatic-engine-core-ingestion-top-level/prism_ingest_25_compliance_auditing_and_multi-store_delivery.md` | PRISM_INGEST_25_Compliance_Auditing_and_Multi-Store_Delivery | review |
| 19 | `growthwebdev-knowledge` | `feature/gro-2131` | `okf/plugins/prismatic-engine-core-ingestion-top-level/prism_ingest_35_memory_auditing_and_object_pooling.md` | PRISM_INGEST_35_Memory_Auditing_and_Object_Pooling | review |
| 19 | `growthwebdev-knowledge` | `feature/okf-dispatcher-incident` | `okf/plugins/prismatic-engine-core-ingestion-top-level/prism_ingest_1_code_quality___auditing.md` | PRISM_INGEST_1_Code_Quality___Auditing | review |
| 19 | `growthwebdev-knowledge` | `feature/okf-dispatcher-incident` | `okf/plugins/prismatic-engine-core-ingestion-top-level/prism_ingest_25_compliance_auditing_and_multi-store_delivery.md` | PRISM_INGEST_25_Compliance_Auditing_and_Multi-Store_Delivery | review |
| 19 | `growthwebdev-knowledge` | `feature/okf-dispatcher-incident` | `okf/plugins/prismatic-engine-core-ingestion-top-level/prism_ingest_35_memory_auditing_and_object_pooling.md` | PRISM_INGEST_35_Memory_Auditing_and_Object_Pooling | review |
| 19 | `growthwebdev-knowledge` | `feature/phase2-quality-gates-plan` | `okf/plugins/prismatic-engine-core-ingestion-top-level/prism_ingest_1_code_quality___auditing.md` | PRISM_INGEST_1_Code_Quality___Auditing | review |
| 19 | `growthwebdev-knowledge` | `feature/phase2-quality-gates-plan` | `okf/plugins/prismatic-engine-core-ingestion-top-level/prism_ingest_25_compliance_auditing_and_multi-store_delivery.md` | PRISM_INGEST_25_Compliance_Auditing_and_Multi-Store_Delivery | review |
| 19 | `growthwebdev-knowledge` | `feature/phase2-quality-gates-plan` | `okf/plugins/prismatic-engine-core-ingestion-top-level/prism_ingest_35_memory_auditing_and_object_pooling.md` | PRISM_INGEST_35_Memory_Auditing_and_Object_Pooling | review |
| 19 | `growthwebdev-knowledge` | `fred/north-star-and-portability-core-spec` | `okf/plugins/prismatic-engine-core-ingestion-top-level/prism_ingest_1_code_quality___auditing.md` | PRISM_INGEST_1_Code_Quality___Auditing | review |
| 19 | `growthwebdev-knowledge` | `fred/north-star-and-portability-core-spec` | `okf/plugins/prismatic-engine-core-ingestion-top-level/prism_ingest_25_compliance_auditing_and_multi-store_delivery.md` | PRISM_INGEST_25_Compliance_Auditing_and_Multi-Store_Delivery | review |
| 19 | `growthwebdev-knowledge` | `fred/north-star-and-portability-core-spec` | `okf/plugins/prismatic-engine-core-ingestion-top-level/prism_ingest_35_memory_auditing_and_object_pooling.md` | PRISM_INGEST_35_Memory_Auditing_and_Object_Pooling | review |
| 19 | `growthwebdev-knowledge` | `main` | `okf/plugins/prismatic-engine-core-ingestion-top-level/prism_ingest_1_code_quality___auditing.md` | PRISM_INGEST_1_Code_Quality___Auditing | keep-index |
| 19 | `growthwebdev-knowledge` | `main` | `okf/plugins/prismatic-engine-core-ingestion-top-level/prism_ingest_25_compliance_auditing_and_multi-store_delivery.md` | PRISM_INGEST_25_Compliance_Auditing_and_Multi-Store_Delivery | keep-index |
| 19 | `growthwebdev-knowledge` | `main` | `okf/plugins/prismatic-engine-core-ingestion-top-level/prism_ingest_35_memory_auditing_and_object_pooling.md` | PRISM_INGEST_35_Memory_Auditing_and_Object_Pooling | keep-index |

## Exact duplicate groups

Exact duplicate content groups among extracted candidates: **94**.

| Count | Hash prefix | Sample path |
|---:|---|---|
| 87 | `c4dfba3b9793` | `growthwebdev-knowledge:deploy-fresh:okf/plugins/prismatic-engine-core-ingestion-top-level/prism_ingest_1_code_quality___auditing.md` |
| 87 | `ed236b8daedc` | `growthwebdev-knowledge:deploy-fresh:okf/plugins/prismatic-engine-core-ingestion-top-level/prism_ingest_25_compliance_auditing_and_multi-store_delivery.md` |
| 87 | `8ebcf51ece78` | `growthwebdev-knowledge:deploy-fresh:okf/plugins/prismatic-engine-core-ingestion-top-level/prism_ingest_35_memory_auditing_and_object_pooling.md` |
| 87 | `c7cca65483dc` | `growthwebdev-knowledge:deploy-fresh:okf/plugins/prismatic-engine-core-ingestion-business-and-licensing/3d-training-deep-dive-+-asset-forge-3d-feature-implementation-map.md` |
| 87 | `4f58f38ac926` | `growthwebdev-knowledge:deploy-fresh:okf/plugins/prismatic-engine-core-ingestion-business-and-licensing/3d-training-efficiently-training-models-using-google-ai-ultra-benefits.md` |
| 87 | `23b206ec5d1d` | `growthwebdev-knowledge:deploy-fresh:okf/plugins/prismatic-engine-core-ingestion-business-and-licensing/architecture-low-latency-on-the-fly-3d-generati....md` |
| 87 | `b28e6477bcb3` | `growthwebdev-knowledge:deploy-fresh:okf/plugins/prismatic-engine-core-ingestion-business-and-licensing/assetforge3d-tokenomics-and-technical-blueprint.md` |
| 87 | `02a0bbde7ea3` | `growthwebdev-knowledge:deploy-fresh:okf/plugins/prismatic-engine-core-ingestion-business-and-licensing/business-plan-asset-forge-3d-.md` |
| 87 | `1600b948c0af` | `growthwebdev-knowledge:deploy-fresh:okf/plugins/prismatic-engine-core-ingestion-business-and-licensing/execution-blueprint-assetforge3d.com.md` |
| 87 | `953edd8a67d6` | `growthwebdev-knowledge:deploy-fresh:okf/plugins/prismatic-engine-core-ingestion-business-and-licensing/index.md` |
| 87 | `7625df943561` | `growthwebdev-knowledge:deploy-fresh:okf/plugins/prismatic-engine-core-ingestion-business-and-licensing/part-2-asset-forge-3d.md` |
| 87 | `4cf0691e4267` | `growthwebdev-knowledge:deploy-fresh:okf/plugins/prismatic-engine-core-ingestion-business-and-licensing/part-3-asset-forge-3d.md` |
| 87 | `03f5be4ee160` | `growthwebdev-knowledge:deploy-fresh:okf/plugins/prismatic-engine-core-ingestion-business-and-licensing/part-4-asset-forge-3d.md` |
| 87 | `f5d45b826a76` | `growthwebdev-knowledge:deploy-fresh:okf/plugins/prismatic-engine-core-ingestion-business-and-licensing/part-5-asset-forge-3d---executive-summary.md` |
| 87 | `372135358263` | `growthwebdev-knowledge:deploy-fresh:okf/plugins/prismatic-engine-core-ingestion-top-level/index.md` |
| 87 | `ab44c7e61260` | `growthwebdev-knowledge:deploy-fresh:okf/plugins/prismatic-engine-core-ingestion-top-level/platform-gaps.md` |
| 87 | `959a3aaaf8d1` | `growthwebdev-knowledge:deploy-fresh:okf/plugins/prismatic-engine-core-ingestion-top-level/prism_ingest_10_engine_ingestion_unreal_unity_v2.md` |
| 87 | `1321f8d08c2d` | `growthwebdev-knowledge:deploy-fresh:okf/plugins/prismatic-engine-core-ingestion-top-level/prism_ingest_15_local_hardware_and_vram_optimization.md` |
| 87 | `43c6f0fff9e9` | `growthwebdev-knowledge:deploy-fresh:okf/plugins/prismatic-engine-core-ingestion-top-level/prism_ingest_18_physics_colliders_and_joint_rigging.md` |
| 87 | `e990cdcbbdf1` | `growthwebdev-knowledge:deploy-fresh:okf/plugins/prismatic-engine-core-ingestion-top-level/prism_ingest_22_master_build_orchestration_and_telemetry.md` |

## Local OKF directories with Prismatic signal

| Path | Sampled MD | Prismatic-ish sampled | Archived? |
|---|---:|---:|---|
| `/home/ubuntu/work/growthwebdev-knowledge/okf` | 323 | 323 | False |
| `/home/ubuntu/work/okf` | 104 | 104 | False |
| `/home/ubuntu/work/aot-seo-knowledge/okf` | 58 | 58 | False |
| `/home/ubuntu/work/belief-deprogrammer/okf` | 26 | 26 | False |
| `/home/ubuntu/work/darius-star-gro-2165/okf` | 25 | 25 | False |
| `/home/ubuntu/work/darius-star/okf` | 25 | 25 | False |
| `/home/ubuntu/work/active-oahu-business/okf` | 19 | 19 | False |
| `/home/ubuntu/work/active-oahu-tours-mirror-1251/okf` | 18 | 18 | False |
| `/home/ubuntu/work/aot-business-gameplan-2026-07-08/okf` | 18 | 18 | False |
| `/home/ubuntu/work/aot-business-kba-countercontent/okf` | 18 | 18 | False |
| `/home/ubuntu/work/active-oahu-tours-mirror/okf` | 17 | 17 | False |
| `/home/ubuntu/work/aot-governance-watchdog-worktree/okf` | 17 | 17 | False |
| `/home/ubuntu/work/worktree-cleanup-20260712T033423Z/tmp-git-dirs-moved/aot-business-seo-report/okf` | 17 | 17 | True |
| `/home/ubuntu/work/aot-gro3718-best-practices/okf` | 9 | 9 | False |
| `/home/ubuntu/work/worktree-cleanup-20260712T033423Z/tmp-git-dirs-moved/aot-gro3640-console-fix/okf` | 9 | 9 | True |
| `/home/ubuntu/work/worktree-cleanup-20260712T033423Z/tmp-git-dirs-moved/aot-pr77-verify/okf` | 9 | 9 | True |
| `/home/ubuntu/work/active-oahu-tours-mirror-2529/okf` | 8 | 8 | False |
| `/home/ubuntu/work/aot-gro-558/okf` | 8 | 8 | False |
| `/home/ubuntu/work/aot-gro3640-booking-mobile-conversion/okf` | 8 | 8 | False |
| `/home/ubuntu/work/aot-gro3645-booking-intent/okf` | 8 | 8 | False |
| `/home/ubuntu/work/aot-gro3665-csp-console-hotfix/okf` | 8 | 8 | False |
| `/home/ubuntu/work/aot-gro3649-lanikai/okf` | 7 | 7 | False |
| `/home/ubuntu/work/aot-gro3665-fonts/okf` | 7 | 7 | False |
| `/home/ubuntu/work/meridian-static-site/okf` | 6 | 6 | False |
| `/home/ubuntu/work/hd-platform/okf` | 5 | 5 | False |
| `/home/ubuntu/work/sentinel-it-asset-logistics/okf` | 5 | 5 | False |
| `/home/ubuntu/work/beyondsaas-site/okf` | 3 | 3 | False |
| `/home/ubuntu/work/hd-platform-staging/okf` | 3 | 3 | False |
| `/home/ubuntu/work/homelab/okf` | 3 | 3 | False |
| `/home/ubuntu/work/active-oahu-static/okf` | 2 | 2 | False |
| `/home/ubuntu/work/agentic-swarm-ops/okf` | 1 | 1 | False |

## Initial classification read

- `hidden-useful`: docs in backup/Ned/feature branches not present on current base; needs review-promote decisions.
- `duplicate-or-current-path`: same path already exists on current base; compare content before promotion.
- `canonical-current`: current base docs; keep/index if still accurate.
- `unsafe-review`: possible credential/secret markers; quarantine before publishing.

## Recommended next batches

1. Land this treasure-map report in `growthwebdev-knowledge` as an indexed OKF report.
2. Deep-diff duplicate families from `backup/gro-3515-full-okf-blocked`, `backup/gro-3522-full-okf-blocked`, and `backup/gro-3522-inlane-disconnected`.
3. Promote or merge canonical winners for Tier 7, dispatcher, governance dashboard, webhook/Linear, and OKF drift histories.
4. Create/repair `okf/projects/prismatic-engine/index.md` in the hub and update `prismatic-engine/docs/okf-map.md` only after hub structure lands.

## Risks/blockers

- Some non-origin remotes are broken/missing; this inventory fetched only `origin` and inspected existing refs.
- `growthwebdev-knowledge` primary checkout is on a feature branch; promotions need clean worktrees from `origin/main`.
- File-count sums are not unique document counts; branches share duplicated OKF trees.
- Candidate extraction is capped and heuristic; Phase 2 should inspect selected duplicate families deeply.

## Manifest files

- `/tmp/prismatic-okf-treasure-hunt/manifests/summary.json`
- `/tmp/prismatic-okf-treasure-hunt/manifests/prismatic-engine-branches.json`
- `/tmp/prismatic-okf-treasure-hunt/manifests/growthwebdev-knowledge-branches.json`
- `/tmp/prismatic-okf-treasure-hunt/manifests/local-okf-directories.json`
- `/tmp/prismatic-okf-treasure-hunt/manifests/candidate-docs.json`
- `/tmp/prismatic-okf-treasure-hunt/manifests/candidate-docs.csv`
- `/tmp/prismatic-okf-treasure-hunt/manifests/duplicate-content-groups.json`
- `/tmp/prismatic-okf-treasure-hunt/manifests/high-value-candidates.json`

## Verification boundary

Phase 0/1 inventory only. Verification should prove manifest/report existence, JSON/CSV parseability, expected high-signal branches, current OKF breadcrumb presence, and fresh `/tmp/hermes-verify-*` cleanup. This is **ad hoc targeted verification**, not full docs-suite green.
