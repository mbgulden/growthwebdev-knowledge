---
type: Standards
title: Hermes Agent Memory vs. Skills Boundary Discipline
description: Audit memory once. Anything that reads like a runbook goes to skills; anything that's a stable preference or fact stays in memory. Recurring procedures become named micro-skills under skills/micro/ (1-page max). Stop expanding umbrella skills when a single decision-tree subprocedure would do. Applied to all profiles. The verification: cold load gets only what's useful now, with the rest reachable in one click.
resource: okf/standards/hermes-memory-skills-boundary-discipline.md
tags: [standards, hermes, memory, skills, micro-skills, boundary]
timestamp: 2026-07-29T05:00:00Z
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/standards/hermes-memory-skills-boundary-discipline.md
linear_issue: null
last_verified: 2026-07-29
verified_by: fred
status: current
---

# Hermes Agent Memory vs. Skills Boundary Discipline

## Purpose

The gap is: the boundary between memory and skills has leaked. Memory is for stable preferences and facts; skills are for procedures the agent re-derives every session. When a runbook-style procedure lives in memory, the agent either re-derives it (slow, error-prone) or follows it without the discipline of a skill (no anti-patterns, no verification). This standard codifies the boundary and the migration procedure.

## What this standard defines

1. **Memory** holds stable preferences and facts. Format: short prose, organized by category. Cold-load surface should be small enough to read in one screen.
2. **Skills** hold procedures. Format: SKILL.md with frontmatter, body, anti-patterns, verification. Each skill is independently loadable.
3. **Micro-skills** under `skills/micro/` hold single-procedure recipes. 1-page max. For decisions that are single decision trees, not class-level disciplines.
4. **Umbrella skills** stay as umbrellas when they describe a class of decisions (e.g., "reply shape" covers status, evidence, blocker, next). They get split when a sub-procedure would do.
5. **Skill pointers in memory**: when memory needs to reference a runbook, it does so via "see skills/<path>/". The pointer is the boundary.

## What this standard explicitly does NOT cover

- It does not cover the canonical test/lint/build pattern (gap-5 covers that).
- It does not cover the proactive execution discipline (covered separately).
- It does not cover the projector-aware communication discipline (covered separately).
- It does not cover which skills should exist (that's a per-profile judgment call).

## Adoption status (as of 2026-07-29)

The discipline is in effect. The orchestrator, fred, george, kai, ned, autobot, and next-step profiles all have:

- A trimmed memory file (preferences + facts + skill pointers).
- Six new micro-skills under `skills/micro/`:
  - `corrections-lead-with-recipe` — corrections lead with the verification recipe, not the assertion.
  - `post-session-review` — the post-session review procedure (memory + skills + pins + counter).
  - `outbound-action-gate` — only Michael sends/publishes/records.
  - `branch-deletion-approval` — no branch/worktree deletion without approval.
  - `prismatic-evidence-handling` — George-specific Prismatic evidence discipline.
  - `directive-then-execute` — KPI/registry/PWP "produce artifact and stop" pattern.

Each micro-skill is symlinked across profiles so a single source of truth exists in the orchestrator's `skills/micro/`.

## The audit procedure

When auditing memory:

1. Read each memory line.
2. Classify:
   - **Stable preference** (Michael said "I prefer X over Y") → memory.
   - **Stable fact** ("Active profiles: ...") → memory.
   - **Runbook-style** ("When correcting, do X then Y") → skill.
   - **Decision-tree** ("If X then Y else Z") → micro-skill.
   - **Umbrella discipline** (class of decisions with multiple procedures) → umbrella skill.
3. For each runbook-style line, check if a skill already exists. If yes, replace the line with a pointer. If no, write the skill.
4. Keep memory focused on preferences and facts.

## Umbrella-skill discipline

**Don't expand umbrella skills when a single decision-tree subprocedure would do.** Examples:

- A "reply shape" umbrella covers status/evidence/blocker/next-action — that's a class. Keep as umbrella.
- A "correct with verification recipe" procedure is one decision tree — that's a micro-skill.
- A "post-session review" procedure has multiple steps but is one recipe — micro-skill.

If a new procedure doesn't fit any existing skill's class, it's either:
- A new umbrella (if it's a class of decisions).
- A micro-skill (if it's a single recipe).

If it's neither (it's an ad-hoc observation), it goes in the handoff, not memory or skills.

## Verification

The cold-load memory file is small enough to read in one screen. The number of `skills/` (umbrella) vs `skills/micro/` (single-recipe) skills reflects the class-vs-recipe distinction. The handoff can list pointers to all relevant skills in one click.

## Honest lessons from the build

- **Memory leaks are silent.** When a runbook line was added to memory (because that's where the agent's working memory lives), it didn't show up as a problem until the skill was written and the duplication became obvious.
- **Pointers in memory are the right shape.** "See skills/micro/outbound-action-gate/" is a 1-line pointer; the rule itself lives where it can be referenced, versioned, and updated independently.
- **Micro-skills are discipline, not just docs.** A 1-page SKILL.md with anti-patterns + verification is much more load-bearing than a memory line. The same content in memory reads like a rule; in a skill, it reads like a procedure.
- **Symlinks across profiles work, but only for skills you actively curate.** The hardcoded `agent-operations/` scan in the adopter doesn't pick up `skills/micro/`. A separate symlink sweep is needed. Worth a follow-up to broaden the adopter.
- **The boundary leak is bidirectional.** Memory lines that should be skills (runbook-style); umbrella skills that should be split (single procedures pretending to be classes). Both directions need auditing.

## Related work

- [Hermes Session Handoff Discipline](hermes-session-handoff-discipline.md) — the cold-start primitive that uses memory + handoff + skills together.
- [Hermes Proactive Execution Discipline](hermes-proactive-execution-discipline.md) — an umbrella skill.
- [Hermes Projector-Aware Communication Discipline](hermes-projector-aware-communication-discipline.md) — an umbrella skill.
- [Hermes Verifier-as-Deliverable Discipline](hermes-verifier-as-deliverable-discipline.md) — covers the verifier side.
- [Hermes Runtime Requirements](hermes-runtime-requirements.md) — covers the runtime surface.
