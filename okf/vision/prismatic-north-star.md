---
type: Vision
title: Prismatic Engine — The North Star
description: The guiding document for every architectural decision. Defines what Prismatic Engine actually is (a general-purpose autonomous production factory, not a coding tool), the five horizons (Coding → Business → Creative → Knowledge → Dream), and six permanent principles for every agent decision.
resource: okf/vision/prismatic-north-star.md
tags: [vision, north-star, prismatic, strategy, factory, autonomy]
timestamp: 2026-06-27T07:32:00Z
linear_issue: pending
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/vision/prismatic-north-star.md
last_verified: 2026-06-27
verified_by: michael
status: current
---

# Prismatic Engine: The North Star

> *"I didn't want an app that builds apps. I want a system of workers that builds, maintains, and grows businesses."*
> — Michael Gulden, June 27, 2026

---

## What Prismatic Engine Actually Is

Prismatic Engine is not a coding tool. Coding is just the first vertical it learned.

Prismatic Engine is a **general-purpose autonomous production factory**. It takes in human intent — a dream, a business idea, a creative vision — and coordinates a swarm of specialized workers to research, design, build, test, ship, maintain, and grow the thing. The human stays in the director's chair. The factory runs.

The insight that makes this not crazy: **the hard part was never the AI model**. The hard part was always the orchestration, the governance, the safety, the task decomposition, the overnight autonomy, the circuit breakers, the self-review, the plugin architecture, and the ability to swap out any component without breaking the whole. That is what you have been building. That is the engine.

---

## The Five Horizons

### Horizon 1: The Coding Factory (NOW → 3 months)
**Where we are.** The engine coordinates agents to read codebases, write code, run tests, self-review, and produce Pull Requests overnight. It works on a single VM. It uses Linear as a task tracker. It is coupled to Michael's infrastructure.

**What success looks like:**
- Anyone can `git clone` the engine, run `pip install .`, and execute a demo task on their own machine
- The JSON-file task provider works without Linear
- The engine boots on Windows, Linux, and macOS
- A 2-minute demo video exists showing the overnight factory workflow
- 10 external developers have cloned and run it

**What carries forward:** Everything built in this horizon (the supervisor, circuit breakers, task provider ABC, harness plugin contract, OKF knowledge base) becomes permanent infrastructure for every future horizon.

---

### Horizon 2: The Business Factory (3–9 months)
**The engine learns to do more than code.** A "business" is not just a repository. It is a website, a marketing strategy, customer support, content, SEO, social media, invoicing, analytics, and iteration based on real-world feedback.

**What success looks like:**
- The engine can ingest a business concept and produce a structured project plan (epics, tasks, milestones)
- Specialized worker plugins exist for: website generation, content writing, SEO auditing, social media scheduling, analytics ingestion
- The engine monitors deployed businesses (uptime, traffic, conversion) and autonomously creates improvement tasks
- Michael's own businesses (Active Oahu Tours, Growth Web Dev, etc.) are maintained and grown by the factory with minimal daily input

**What carries forward:** The plugin marketplace. The pattern of "ingest intent → decompose → execute → monitor → improve" becomes the universal loop.

---

### Horizon 3: The Creative Factory (6–18 months)
**The engine learns to create, not just engineer.** Games, art, music, stories, voice acting, SFX. The factory ingests creative vision — character arcs, art style references, narrative themes — and coordinates specialized workers (image generators, music composers, voice synthesizers, narrative engines, game engine integrators) to produce complete creative works.

**What success looks like:**
- The engine can ingest a game design document and produce a playable prototype with original art, sound, and narrative
- It can then produce 10 more games of different genres using the same pipeline
- Creative workers are plugins (Stable Diffusion for art, Suno/Udio for music, ElevenLabs for voice, Unity/Godot for game engine integration)
- A "creative brief" format exists — the equivalent of a Linear ticket but for creative intent
- The human reviews and directs; the factory produces

**What carries forward:** The understanding that "task" is not "write code." A task is any bounded unit of creative or productive work. The `TaskProvider` ABC and the `PrismaticPlugin` contract prove their generality here.

---

### Horizon 4: The Knowledge Factory (12–24 months)
**The engine learns to think, not just do.** It continuously ingests the world's knowledge — research papers, market data, news, community discussions, patent filings, scientific discoveries — and synthesizes insights that no individual human would connect.

**What success looks like:**
- The engine maintains a living knowledge graph that surfaces non-obvious connections ("this obscure materials science paper + this gaming trend + this underserved market = a product nobody has built")
- It autonomously generates "insight briefs" — short documents that say "here is something worth building, here is why, and here is how"
- The human reviews insight briefs, selects the ones worth pursuing, and the factory enters Horizon 2/3 to build them
- The engine gets smarter over time because every completed project feeds back into the knowledge graph

**What carries forward:** The OKF (Operational Knowledge Framework) you built is the seed of this. It is already a structured, indexed, machine-readable knowledge base. Scaling it to ingest external knowledge is an extension, not a reinvention.

---

### Horizon 5: The Dream Factory (2+ years)
**The engine runs continuously and helps anyone — not just Michael — realize their vision.**

**What success looks like:**
- A creator with no technical background can describe what they want ("I want a cozy farming game with hand-painted art and a story about community"), and the factory produces it
- A small business owner can say "I want to grow my bakery's online presence," and the factory builds the website, runs the SEO, manages the social media, and reports back weekly
- The factory is self-sustaining: it monitors its own health, improves its own processes, and scales its own infrastructure
- Other developers build plugins for the factory (new task providers, new creative workers, new knowledge sources, new deployment targets)
- The factory is open source. Anyone can run it on their own infrastructure. Privacy and ownership stay with the operator

---

## The Golden Path Forward

The path from Horizon 1 to Horizon 5 is not a fantasy. It is a series of concrete, incremental extensions of what already works:

```
TODAY                           HORIZON 5
  │                               │
  │  TaskProvider ABC             │  TaskProvider: anything
  │  (Linear, JSON)               │  (Linear, Jira, Notion, voice, email, chat)
  │                               │
  │  PrismaticPlugin ABC          │  Plugin marketplace
  │  (Hermes harness)             │  (code, art, music, voice, analytics, SEO, ...)
  │                               │
  │  OKF knowledge base           │  Living knowledge graph
  │  (markdown files)             │  (structured, searchable, cross-referenced)
  │                               │
  │  Overnight autonomy           │  Continuous autonomy
  │  (cron + circuit breaker)     │  (self-healing, self-scaling, self-improving)
  │                               │
  │  One operator (Michael)       │  Any operator
  │  (one VM)                     │  (any infrastructure)
  │                               │
  └───────────────────────────────┘
```

Every horizon reuses and extends the same core components. Nothing gets thrown away. The engine you are building today IS the engine that runs the dream factory. It just learns new skills over time.

---

## What "The End" Looks Like

There is no end. That is the point.

The engine is not a product you ship and walk away from. It is a living system that continuously:
1. **Ingests** — ideas, knowledge, feedback, data
2. **Decomposes** — breaks big visions into bounded tasks
3. **Executes** — coordinates specialized workers to produce real output
4. **Reviews** — self-checks quality, governance, safety
5. **Ships** — delivers real artifacts to the real world
6. **Monitors** — watches what happens after shipping
7. **Improves** — creates new tasks based on what it learned
8. **Repeats** — forever

The human's role is to **direct**: to provide vision, make value judgments, and decide what matters. Everything else is the engine's job.

Success is when you wake up in the morning, review a dashboard of what the factory accomplished overnight, approve the good work, redirect the rest, and go live your life. That is not a fantasy. You are 3 months of portability work away from Horizon 1, and everything after that is extension.

---

## Permanent Guidance for All Agents

The following principles must guide every architectural decision, every task shape, and every code change across all agents (Fred, Ned, Kai, Jules, AGY, Antigravity, and any future agent):

### 1. The Engine Must Run Without You
If Michael gets hit by a bus, the engine should still boot, still accept tasks, and still produce output. No hardcoded paths, no personal secrets in the repo, no Michael-only assumptions.

### 2. Every Component Must Be Swappable
Linear can be swapped for Jira. Hermes can be swapped for a Slack bot. Gemini can be swapped for Claude or a local model. Docker can be swapped for gVisor. If any component becomes a hard dependency, that is a bug.

### 3. The Overnight Factory Is the Core Product
The ability to queue work, close your laptop, and wake up to verified results is the thing that no competitor does well. Every feature must strengthen this loop. If a feature breaks the overnight loop, it does not ship.

### 4. Governance Is Not Optional
Circuit breakers, self-review, cost tracking, sandbox isolation, and human-in-the-loop checkpoints are not "nice to have." They are the reason the factory can run unattended. Remove any one of them and you have "fire and pray."

### 5. The Factory Builds More Than Code
Code is Horizon 1. Every architectural decision must account for the fact that future workers will produce art, music, stories, business plans, marketing campaigns, and knowledge synthesis — not just Pull Requests.

### 6. Help Others Build Their Dreams
The engine is open source. The documentation is generous. The onboarding is frictionless. The goal is not to build a SaaS that extracts rent. The goal is to give every builder — technical or not — an autonomous factory that helps them realize their vision.

---

## What to Commit to the OKF

This document should be uploaded to:
```
okf/vision/prismatic-north-star.md
```

It is the north star that every standard, every epic, every task, and every agent decision points back to. When in doubt about any architectural choice, ask: "Does this move us toward the dream factory, or away from it?"

---

*Written June 27, 2026, at 1:22 AM Mountain Time, during an overnight session where the factory was already running, already producing, and already proving that the dream is not crazy.*
