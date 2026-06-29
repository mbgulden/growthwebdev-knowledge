---
type: Project
title: Prismatic Web Plugin — Project Hub (the big project, scope corrected)
description: The "big project" Michael called out. The MVP is NOT a single example website — it's THE SYSTEM that ingests any client's Website Content Gathering Framework (5 Drive docs), synthesizes a build plan, distills it into Linear tasks, and orchestrates the agent swarm to produce the site. This is the corrected scope per Michael's 2026-06-23 direction.
resource: https://github.com/mbgulden/growthwebdev-knowledge/blob/main/okf/projects/prismatic-web-plugin/index.md
tags: [project, prismatic-web-plugin, big-project, system-builder, multi-agent-orchestration, ingestion, plan-synthesis, task-distillation, mega-task]
timestamp: 2026-06-23T06:40:00Z
linear_issue: GRO-2132 (superseded, new epic TBD)
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/projects/prismatic-web-plugin/index.md
last_verified: 2026-06-23
verified_by: fred
status: current
---

# Prismatic Web Plugin — Project Hub (the big project, scope corrected)

> **CRITICAL SCOPE CORRECTION (2026-06-23 06:35 UTC)**
>
> Per Michael's direction: "the MVP needs to be the system that can create a comprehensive website based off the website content gathering framework. You are building out the system that ingests the info and converts it into actionable plans that are distilled into tasks so that all the agents contribute in the flow/build/review and get better quality outputs that are consistently high quality and 'well thought out'."
>
> The previous scope (build one example site for "Meridian Women's Defense Academy") was **wrong**. The 5 Website Dev Drive docs are the **ingestion framework**, not example content. The MVP is a system that processes ANY client's framework responses and produces a website via the agent swarm.

## What this is

A multi-agent orchestration system for **client-driven website development**. The system:

1. **Ingests** any client's completed Website Content Gathering Framework (the 5 Drive docs)
2. **Synthesizes** an actionable website build plan from the framework responses
3. **Distills** the build plan into Linear tasks with proper agent:* labels + context
4. **Dispatches** via the existing agent workflow (AGY/Ned/Kai/Jules)
5. **Builds** the actual website via the agent swarm
6. **Reviews** via the existing review loop (Worker → AGY peer review → Fred verify → Done)
7. **Deploys** to Cloudflare Pages
8. **Documents** the build in OKF for future client onboarding

The plugin is a Prismatic-compatible manifest with hooks, skills, and tool integrations that orchestrate the entire pipeline.

## Architecture overview

```
┌────────────────────────────────────────────────────────────┐
│ INPUT: Client's filled-in 5 Website Dev docs (Drive / OKF) │
└────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────┐
│ STEP 1: INGEST                                              │
│ - Parse 5 docs into structured client data (JSON)         │
│ - Schema validation (required fields present?)             │
│ - Output: client_profile.json + content_brief.json         │
│ - Agent: AGY (LLM-based parser, handles any client input)   │
└────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────┐
│ STEP 2: SYNTHESIZE                                           │
│ - IA: page list from framework sections                   │
│ - Per-page content briefs                                 │
│ - Design tokens from brand interview                      │
│ - Tech requirements from launch kit                        │
│ - Automation workflows from post-purchase                  │
│ - Output: website_build_plan.md (the spec)                 │
│ - Agent: AGY pro (peer-reviewed)                            │
└────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────┐
│ STEP 3: DISTILL                                              │
│ - Read the build plan, create Linear issues                 │
│ - Parent epic per website build                              │
│ - Child issues per page/section                              │
│ - Each: agent:* label, OKF context, AGY_TASK.md            │
│ - Peer review issues (AGY-pro) for code tasks              │
│ - Output: Linear epic + 10-20 child issues                  │
│ - Agent: Fred (orchestrator-only, deterministic)            │
└────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────┐
│ STEPS 4-7: AGENT SWARM EXECUTION                             │
│ (existing infrastructure, mostly works)                      │
│                                                            │
│ 4. DISPATCH — AGY picks up content/design tasks             │
│             Kai picks up CSS/styling tasks                 │
│             Ned picks up infrastructure/deploy tasks        │
│             Jules CLI reviews (when code review needed)     │
│             Fred verifies (Worker → AGY → Fred → Done)     │
│                                                            │
│ 5. BUILD — Each task produces deliverable + RESULT.md        │
│                                                            │
│ 6. REVIEW — AGY pro reviews code; Fred verifies              │
│                                                            │
│ 7. DEPLOY — Cloudflare Pages deploy via Ned                  │
└────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────┐
│ OUTPUT: Deployed website + OKF handoff package              │
│ + reusable system for the next client                        │
└────────────────────────────────────────────────────────────┘
```

## MVP scope (corrected — system, not single site)

**Phase 1: The system (MVP)**
- Ingestion parser (Step 1) — accepts any client's 5 Website Dev docs
- Build plan synthesizer (Step 2) — AGY pro, produces website_build_plan.md
- Task distiller (Step 3) — Fred + Linear API, creates epic + 10-20 child issues
- A "demo run" with a fake client profile (using Meridian Women's Defense Academy as the example data) to prove the system end-to-end
- OKF docs for each step (reusable for next client)
- **Deliverable:** `meridian-womens-defense-website` epic filed in Linear with all child issues, ready for the agent swarm to execute. The system itself is the MVP, the demo build proves it works.

**Phase 2: Execute the demo (proves the system end-to-end)**
- Run the agent swarm on the demo epic
- Deploy the Meridian Women's Defense Academy site
- Total: 4-8 hours with the system + existing agent workflow

**Phase 3-7: As in master synthesis** (plugin skeleton, extraction, GRO-1497, design system, schema migration, commercialization)

## Inputs available right now (all in OKF)

| Input | Path | Status |
|---|---|---|
| Master synthesis (1-page directive) | `okf/projects/prismatic-source-plans-master-synthesis-2026-06-23.md` | published |
| AGY Golden Path (62-phase master plan) | `okf/plugins/prismatic-engine-golden-path/agy-plugin-development-golden-path.md` | mirrored |
| Research Report: Prismatic engine web blueprint (34KB Gemini DeepThink) | `okf/projects/prismatic-engine/drive-evals/Research_Report_-_Prismatic_engine_web_blueprint.md` | mirrored |
| Prismatic Web plugin (today's directive) | `okf/projects/prismatic-engine/drive-evals/Prismatic_Web_plugin.md` | mirrored |
| 4 Gemini evaluation summaries (Prism story/video gaps/image/audio) | `okf/plugins/prismatic-*/` | mirrored |
| Platform Gaps + Prismatic gaps | `okf/projects/prismatic-engine/drive-evals/` | mirrored |
| **5 Website Dev client docs (THE INGESTION FRAMEWORK)** | `okf/projects/website-dev/inputs/` | mirrored, not yet built against |
| 20 AGY architecture reports | `okf/projects/prismatic-engine/agy-reports/` | mirrored |
| 90 OKF-mirrored plugin docs | `okf/plugins/prismatic-*/` | existing |
| GRO-1497 plugin interface spec | `~/work/prismatic-engine/specs/implementation-plans/` | existing |
| Standalone command center extraction plan | `~/work/prismatic-engine/specs/implementation-plans/` | existing |
| AOT architecture template (the infra reference) | `okf/standards/active-oahu-tours-architecture-template.md` | published |
| **Existing agent dispatch architecture** | `okf/standards/agent-dispatch-architecture.md` | published |

## Process overhaul (parallel workstream)

The 11 process-overhaul tasks (GRO-2121 through GRO-2131) are in flight. **Three of them were just fixed in this session:**
- GRO-2122 (AGY GT Review dispatcher) — fixed in commit 28c4ae5
- GRO-2124 (Ned dispatcher) — fixed in commits 28c4ae5 + 3fdfa57
- GRO-2125 (Kai dispatcher) — fixed in commits 28c4ae5 + 3fdfa57

Smoke-tested: all 3 dispatchers now return real agent output. The model name was the issue (the "Claude Sonnet 4.6 (Thinking)" name silently fell back to Gemini 3.5 Flash (Medium) — the fix is to use a real AGY model name like "Gemini 3.5 Flash (High)").

## Related OKF docs
- [Master plan synthesis](../prismatic-source-plans-master-synthesis-2026-06-23.md) — the 1-page directive
- [Mega task workflow](../../standards/mega-task-workflow.md) — the workflow I'm following
- [Agent dispatch architecture](../../standards/agent-dispatch-architecture.md) — the dispatch system
- [AOT architecture template](../../standards/active-oahu-tours-architecture-template.md) — the infra reference
- [Drive evals directory](../prismatic-engine/drive-evals/) — the 7 Gemini evaluations
- [AGY reports directory](../prismatic-engine/agy-reports/) — the 20 AGY architecture docs
- [Website Dev inputs directory](../website-dev/inputs/) — the 5 ingestion framework docs

## Change log
- 2026-06-23 06:10 UTC: Hub created after Michael's "Prismatic Web plugin is the big project" + MVP direction
- 2026-06-23 06:25 UTC: Design direction updated to program-agnostic
- 2026-06-23 06:35 UTC: **SCOPE CORRECTION** — MVP is the SYSTEM (ingest → synthesize → distill → dispatch), not a single example site. 4 old MVP child issues canceled (GRO-2133 through GRO-2136). New epic filed.
- 2026-06-23 06:36 UTC: Process overhaul - 3 dispatchers fixed in commits 28c4ae5 + 3fdfa57
- 2026-06-23 06:43 UTC: **GRO-2138 DONE** — Step 1 ingestion parser built, tested, committed (ce4a561 + 8639c99). Script `pwp_ingest.py` reads any client's 5 Website Dev docs and produces `client_profile.json` + `content_brief.json` + `ingest_report.md` in ~16 seconds.
- 2026-06-23 06:47 UTC: **GRO-2139 DONE** — Step 2 synthesizer built, tested (commit 8118b46). Script `pwp_synthesize.py` uses AGY pro (Gemini 3.1 Pro High) to produce a 3,467-word `website_build_plan.md` in ~80 seconds.
- 2026-06-23 06:51 UTC: **GRO-2140 DONE** — Step 3 task distiller built, tested (commit 8118b46). Script `pwp_distill.py` parses the build plan and creates 1 epic + 13 child issues in Linear. Tested: GRO-2142 (epic) + GRO-2143-2155 (13 children for Meridian Women's Defense build).
- 2026-06-23 06:51 UTC: **PWP SYSTEM MVP COMPLETE.** All 3 steps shipped end-to-end. The system can now ingest any client's framework docs → synthesize a build plan → create a Linear epic with 10-20 child issues routed to the right agent lanes. The agent swarm picks up the children on the next cron tick (15 min) and starts the actual Meridian Women's Defense build.
- 2026-06-23 07:00-07:40 UTC: **/YOLO POC PHASE.** Built generic versions of all 3 PWP steps that work on ANY project type. Tested on 5 real Michael projects. Full pipeline proven end-to-end on 2 (Darius Star game + Belief Deprogrammer knowledge-base). 26 additional Linear issues filed (GRO-2157-2184) for real project implementation epics.

**Open follow-up work (not blocking the demo build):**
- 8 process-overhaul P1/P2 tasks still open (will be picked up by their agents on next cron tick)
- After the agent swarm builds the Meridian Women's Defense site, file follow-up issues for plugin skeleton, extraction, GRO-1497 hook stubs (Phases 3-7 of the master synthesis)
- Add JSON Schema validation to Step 1 (currently trusts AGY output)
- 2026-06-23 16:00 UTC: **PWP v0.1.0 SHIPPED** at https://github.com/mbgulden/prismatic-web-plugin. Pipeline (Steps 1-3) + Prismatic Web Builder (pwb) sub-tool + lane governance + 5 follow-up issues filed (GRO-2226 to GRO-2230). The sub-tool inside the PWP package is now called Prismatic Web Builder (pwb) — NOT orchestrator — to avoid name collision with Fred.
- 2026-06-26 22:55 UTC: **AGY fast-SSD sandbox pivot** — active AGY/PWP sandboxes moved off NAS/NFS to local fast SSD (`/archive/agy_sandboxes`; `/storage` symlink). Active logs: `/archive/agy_sandbox_logs`. NAS is now archive/evidence only. Direct `/archive` writes measure ~2.9 GB/s; NAS/NFS random I/O is latency-bound and was stalling AGY's background-tool loop.
- 2026-06-26 22:55 UTC: **AGY auto-resume safety gates (native)** — `--cron-mode` enforces storage guard (`/tmp >=10GB`, `/archive >=50GB`), Linear + AGY backend preflight, strict dispatch opt-in (`dispatch:ready` / `dispatch:priority` only), envelope (`max-concurrent=2`, `jitter=15-30`, `AGY_INACTIVITY_KILL_SEC=120`), and a 2-strike circuit breaker on `INACTIVITY_KILL` / `AGY_BACKEND_TIMEOUT` / `PARTIAL_RESULT`. Verified live; cron resumed at 22:54 UTC.
