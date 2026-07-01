---
type: Reference
title: Prismatic Engine vs The Landscape — Competitive & Comparative Map
description: External landscape map. Compares Prismatic Engine to LangGraph / Temporal / OpenClaw / Manus / Dust / etc., positions the engine against its North Star (general-purpose autonomous production factory), and identifies the 40% Prismatic already owns vs the 60% it shares with competitors.
resource: okf/research/prismatic-vs-the-landscape.md
tags: [research, prismatic, competitive-analysis, north-star, comparison, langgraph, temporal, openclaw, factory]
timestamp: 2026-06-30T18:30:00Z
linear_issue: GRO-3083
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/research/prismatic-vs-the-landscape.md
last_verified: 2026-06-30
verified_by: ned
status: draft — pending AGY/Opus deep-dive
---

# Prismatic Engine vs The Landscape

> *Drafted 2026-06-30 by Ned. Intended as the seed for an AGY/Opus deep-dive that compares Prismatic Engine against the North Star (`okf/vision/prismatic-north-star.md`) and the broader competitor landscape. See Linear issue (pending) for the deep-dive task.*

---

## Why This Document Exists

The North Star defines what Prismatic Engine **must become** (a general-purpose autonomous production factory spanning five horizons — Coding → Business → Creative → Knowledge → Dream). It does not define what already exists outside that vision. To plan an honest roadmap, you need three layers of context:

1. **The North Star** — what Prismatic is trying to be (`okf/vision/prismatic-north-star.md`).
2. **The Landscape** — what other products are building, and where they overlap with Prismatic.
3. **The Gap** — the specific work that moves Prismatic from today to the North Star.

This document covers layer 2 and a first cut at layer 3. Layer 1 is the North Star itself; the AGY/Opus task below is the work to align layer 3 against layer 1.

---

## Honest Framing: How "Different" Is Prismatic From Wrapping LangGraph?

**It is not strictly better. It is different.** If you wrap LangGraph well, you cover roughly 60% of what Prismatic does. The 40% Prismatic does that LangGraph does not is concentrated in three areas: **governance, durability, and kernel/harness separation**.

### Component-by-Component Comparison

| Capability | LangGraph (2026) | Prismatic Engine | Verdict |
|---|---|---|---|
| Graph-based agent orchestration | Native (`StateGraph`, sub-graphs, `Send()`, conditional edges) | Lane discipline + lane YAMLs + manual graph wiring | LangGraph wins on ergonomics |
| Persistent state / checkpointing | Native checkpointer (MemorySaver, Postgres, Redis); thread-scoped | `prismatic/sessions` + journal continuity + artifact publisher | Tied — different shapes, similar outcomes |
| Streaming + tokens | First-class (`astream_events`, async iterators) | Whatever the harness emits | LangGraph wins on DX |
| Human-in-the-loop | `interrupt()` + `Command(resume=...)` + time-travel debugging | Lane review queues + Linear PR flow | LangGraph wins for inline interrupts; Prismatic wins for cross-process async review |
| Multi-agent / sub-agent delegation | Sub-graphs + `Send()` | Lane discipline + lane YAML + locks + heartbeat + `[Ned]` commit prefix | Tied at small scale; Prismatic wins at >5 concurrent agents where contention matters |
| Memory + semantic search | `langgraph-checkpoint` + bring-your-own vector store | Memory engines + `memory-grooming` cron + per-profile `~/.hermes/profiles/<name>/memories/` | Tied |
| Tool registration / MCP | `@tool` decorator + `langchain-mcp-adapters` | Skill loader + `hermes` plugin system | Tied |
| Long-running durability | Checkpointer + thread resume; assumes process can resume | Engine kernel + file locks + 60s heartbeat + atomic `finalize_task.sh` + journal continuity | **Prismatic wins here** — Prismatic is built for hours-to-days; LangGraph is built for minutes-to-hours |
| Governance / least-privilege lanes | Bring-your-own; no native role/lane concept | First-class: `prismatic/lanes/ned/config.yaml` with `[Ned]` writes on `scripts/`, read-only on `content/`, lane validator | **Prismatic wins decisively** — this is the gap that does not close via wrap-LangGraph |
| Audit / observability | LangSmith + OpenTelemetry | Profile-audit cron + watchdog scripts + Linear issue journal as audit trail | LangGraph+LangSmith wins on traces; Prismatic wins on "what did the agent actually change in the repo" |
| Cross-host deployment | LangGraph Platform (commercial) | `prismatic` CLI on any host with a harness | Prismatic wins on portability without a vendor lock-in |
| Cron + scheduled tasks | Bring-your-own (Celery, APScheduler) | First-class with heartbeat and silent-on-clean watchdogs | Prismatic wins |
| Linear / external system integration | Bring-your-own | `linear-agent-operations` skill as a contract; cron + journal as durability | Prismatic wins on speed-to-working because the skill already exists |

### The Honest 60% / 40% Split

**You can replicate ~60% of Prismatic on top of LangGraph in roughly 2–3 weeks** (state, tools, memory, streaming, sub-agents). That is the *agent* part.

The **40% Prismatic does that LangGraph does not** is the part that matters most for production swarm operation:

1. **Lane governance as a contract** — `ned/` writes, `content/` read-only, validated by `prismatic-lane-validator`, with `[Ned]` commit prefix enforced. This is a *product* decision baked into the kernel. Wrapping LangGraph means re-deciding this every project.
2. **Cross-process durability with locks + heartbeat** — `swarm_locks.json` + 60s heartbeat + atomic `finalize_task.sh`. This is what makes 24/7 production swarms safe. LangGraph's checkpointer is process-scoped; process death means thread loss unless you build the restart layer yourself.
3. **Harness-agnostic kernel** — your doctrine says "Prismatic is the kernel, Hermes/OpenClaw/whatever is the harness." LangGraph is a graph runtime, not a kernel — wrapping it does not give you kernel/harness separation, it just moves the seam.

### Where LangGraph Actually Beats Prismatic

- **Speed to first agent.** 30-minute time-to-running-agent. Prismatic's governance overhead has costs.
- **Ecosystem.** LangGraph inherits LangChain's ~1000 integrations. Prismatic's skill list is small.
- **Visualizer.** LangGraph Studio is real. Prismatic's diagrams are ASCII.
- **Typed state.** StateGraph's typed channels are good DX.
- **Talent / community.** Every AI engineer knows LangChain. Almost nobody knows Prismatic.

---

## The Landscape: Who Else Is Building What

Eight distinct categories, each overlapping Prismatic on different axes.

### Category 1 — Orchestrators (closest to Prismatic kernel)

| Product | Shape | Prismatic overlap |
|---|---|---|
| **LangGraph / LangChain** | StateGraph + checkpointer + LangSmith | High overlap on agent part; low on governance |
| **CrewAI** (IBM, 2024) | Role-based multi-agent | Closer to Prismatic's swarm model than a generic graph; lighter on governance |
| **AutoGen** (Microsoft) | Multi-agent conversation framework | Research-grade; less productionized |
| **Temporal + custom agent SDK** | Durable workflow engine | Closest analog to Prismatic's cross-process-durability story |
| **Inngest** | Durable functions, `step.ai.infer()` native | Closest direct competitor in "long-running agent with crash recovery" |
| **Restate** | Durable execution in Rust | Same pattern, sharper engineering |
| **Trigger.dev / Hatchet** | Task queues with cron + retries | Less agent-shaped, more infra-shaped — used as substrate under agent swarms |

### Category 2 — Agent OS / Personal Agent Platforms

| Product | Notes |
|---|---|
| **OpenClaw** | Gateway + channels + agent runtimes + memory engines + ClawHub. Has `parallel specialist lanes` natively — mirrors Prismatic lanes. |
| **Hermes Agent** (Nous Research) | Profile-based + gateway-driven + skills-pluggable. Your current harness. |
| **Claude Code + Claude Agent SDK** | Anthropic's harness. Sub-agents + MCP + hooks. De facto standard for terminal agent work. |
| **Codex CLI** (OpenAI) | Similar shape to Claude Code. App-server model. |
| **Letta** (formerly MemGPT) | Long-context memory-first agent runtime. Different philosophy than Prismatic's governance-first, architecturally similar. |

### Category 3 — AI Workforce / "Factory" Products

Closest to your stated North Star vision.

| Product | Notes |
|---|---|
| **Manus AI** | Autonomous AI worker that completes multi-step tasks. Closest analog in marketing positioning. Closed SaaS. |
| **Devin** (Cognition Labs) | Autonomous SWE agent. Software-specific. |
| **Factory / Codegen / SWE-Agent variants** | Multiple startups in the "AI agent fleet for software engineering" space. |
| **Roo Code / Cline / Continue.dev** | IDE-side agents. Ripe for being wrapped under your Prismatic layer. |
| **Bourbon / Lindy.ai / Cognosys** | Agent platforms that wrap LangGraph + add SaaS UX. |

### Category 4 — Engine / Kernel Layer (rare + aligned with Prismatic doctrine)

| Product | Notes |
|---|---|
| **Temporal** | Canonical "kernel" for long-running workflows. Used as agent substrate. |
| **Inngest** | Same. With `step.ai` native agent primitives. |
| **Restate** | Same pattern, smaller community. |
| **Modal** | Serverless compute for AI. Lower-level. |
| **Ray / Anyscale** | Distributed compute substrate. |

### Category 5 — Agent Observability / Governance

| Product | Notes |
|---|---|
| **LangSmith** | Closed. Observability + evals + prompt versioning. |
| **Langfuse** | OSS self-host or closed SaaS. Open-source LangSmith alt. |
| **Helicone** | Observability proxy. |
| **Comet / W&B** | Generic ML observability applied to agents. |
| **Arize Phoenix** | Tracing + eval. |
| **Dust.tt** | Agent platform with explicit governance UI. |

### Category 6 — Knowledge / Memory Layers

| Product | Notes |
|---|---|
| **Letta / MemGPT** | Long-context memory-first agent runtime. |
| **Honcho** | Memory layer for AI agents. |
| **QMD** | Memory engine referenced in OpenClaw ecosystem. |

### Category 7 — Creative / Media Agents

Relevant for Horizen 3 of the North Star.

| Product | Notes |
|---|---|
| **ComfyUI** | Generative media workflows — image / video / audio. |
| **Suno / Udio** | Music generation. |
| **ElevenLabs** | Voice synthesis. |
| **Runway / Pika / Sora** | Video generation. |

### Category 8 — Deployment & Sandbox Infrastructure

Relevant if Prismatic-on-OpenClaw narrative becomes real.

| Product | Notes |
|---|---|
| **Docker / gVisor / Firecracker** | Sandbox primitives. |
| **E2B / Fly / Modal** | Cloud sandbox-as-a-service for agents. |
| **Brev** | Remote GPU instance deployment (referenced in NemoClaw docs). |

---

## Specific Overlap Mapping (Prismatic North Star Capability × Landscape)

The North Star defines six permanent principles for every agent decision. Map each against the landscape:

| North Star Principle | Closest Landscape Match |
|---|---|
| 1. The engine must run without you | **Inngest / Temporal / Restate** (durable functions); **OpenClaw** (harness) — but none ship "factory-without-owner" as a feature |
| 2. Every component must be swappable | **OpenClaw** (harness-plugin contract); **LangGraph** (provider abstraction) — Prismatic's doctrine is more rigorous than either |
| 3. The overnight factory is the core product | **Manus** (closed); **Inngest** (open-ish) — no one ships this as a turnkey |
| 4. Governance is not optional | **Dust.tt** (closed); **Temporal** (sandbox primitives); **OpenClaw** (network policy) — Prismatic's lane-governance is more product-shaped |
| 5. The factory builds more than code | **ComfyUI** (media); **CrewAI** (generic roles) — only **Letta** is arguably kernel-shaped for non-code |
| 6. Help others build their dreams | **LangGraph / AutoGen** (open-source); **OpenClaw** (open-source) — but none ship "frictionless onboarding" as an outcome, only as a goal |

**Verdict:** The synthesis Prismatic is building does not exist as a single product. Each piece exists somewhere. The synthesis is the bet.

---

## Cross-Cutting Landscape Trends (to inform Horizon Planning)

1. **Durable execution is becoming table stakes.** Inngest, Temporal, Restate all raised the bar in 2024–2026. Prismatic's lock+heartbeat story is the in-house version of this. Be aware that closed competitors may ship better primitives than custom code.
2. **Closed products out-UX the open alternatives.** Manus and Dust have nicer UX than OpenClaw + Prismatic. The North Star's "frictionless onboarding" is hard, and the open stack has a deficit here.
3. **Memory engines are commoditizing.** Letta, Honcho, QMD, Builtin — the 2026 question is not "which memory engine" but "what does memory mean in a session graph." Prismatic's memory-grooming cron is honest but old-school.
4. **Agent platforms are moving toward "swarms of specialists" as the default unit.** CrewAI, OpenClaw's parallel-lanes, AGY's worker lanes, Prismatic's lanes — this convergence is real. Treat Prismatic's lane as a moderately crowded design space, not a unique insight.
5. **Kernel/harness separation is rare.** No product explicitly markets it. Temporal + custom SDK is the closest. The Prismatic doctrine is ahead of the market here, but only if you actually ship the harness-agnostic seams.
6. **Governance is a market gap.** Dust.tt is the most-aligned closed product. Langfuse is OSS but focused on traces, not lane policy. The product gap here is real and Prismatic is closer to closing it than any open-source competitor.

---

## Recommended Competitive Position (if Prismatic becomes external)

| If competing on | Against | Likely outcome |
|---|---|---|
| Governance + durability + kernel/harness split | Temporal + LangGraph + Inngest | Win on differentiation, lose on adoption |
| "Agent factory on OpenClaw" | Manus + Devin + LangGraph Platform | Win on openness + composability, lose on out-of-box UX |
| "Lane discipline for AI coders" | Claude Code sub-agents + Roo Code | Win on rigor, lose on consumer polish |
| "Open-source kernel for agents" | LangGraph (OSS) + AutoGen (OSS) + CrewAI (OSS) | Lose on ecosystem; win only if kernel/harness separation is genuine and docs are first-class |

**Honest positioning:** Prismatic is a research-quality kernel with governance-quality decisions, not yet a marketable product. To become one, it needs packaging, adapters, default lane templates, parity tests, and onboarding docs. The product is real. The product-market fit is not yet.

---

## Open Questions for the AGY/Opus Deep-Dive

The AGY/Opus deep-dive (Linear task pending) should answer these against the North Star:

1. **Mapping check.** Where does each of the six North Star principles map to a landscape capability? Where is Prismatic ahead? Where is Prismatic lagging?
2. **Horizon feasibility recheck.** The North Star's five horizons (Coding → Business → Creative → Knowledge → Dream) were written on 2026-06-27. Has the landscape shifted in 3 days in a way that changes the horizon ordering or timing?
3. **Open-source vs closed-source analysis.** Where will the "frictionless onboarding" (North Star principle 6) come from? Which landscape trend (open vs closed) actually serves the dream-factory horizon?
4. **Risk register.** What landscape product, if it ships a particular feature in the next 6 months, would invalidate a specific Prismatic horizon? E.g., if OpenClaw ships kernel/harness separation natively, does that change the Prismatic-on-OpenClaw bet?
5. **Prismatic-on-OpenClaw feasibility.** Does the synthesis of (a) Prismatic kernel + (b) OpenClaw harness actually deliver a "frictionless 2-minute install to factory-running" experience that lands at Horizon 1? Or does it still require bespoke setup per project?
6. **"Factory spewing out high-quality results"** (Michael's exact phrasing). Which landscape product actually demos this today? What is missing from their demos that Prismatic would need to ship?
7. **Decision criteria.** Given the landscape, what is the minimum viable Prismatic that advances the North Star by 6 months? What is the cheapest experiment that de-risks the build?

---

## Status

- **Drafted 2026-06-30 by Ned** — intentionally a *seed* document, not the final answer.
- **Linear task:** [GRO-3083](https://linear.app/growthwebdev/issue/GRO-3083/agyopus-deep-dive-prismatic-engine-vs-landscape-mapped-to-north-star) — `agent:agy-opus` label; routed to the AGY/Opus dispatcher; state: Backlog; project: `📚 Prismatic Engine Docs`.

---

## References

- North Star: `okf/vision/prismatic-north-star.md`
- AGY architecture recipe: `okf/standards/agy-architecture-recipe.md`
- Dispatch architecture: `okf/standards/dispatch-architecture.md`, `okf/standards/dispatch-production-grade.md`
- Pipeline recipes: `okf/standards/kai-architecture-recipe.md`
- (For deep-dive AGY/Opus): external web research on LangGraph, Temporal, Inngest, OpenClaw, Manus, Dust, CrewAI, AutoGen, Letta.
