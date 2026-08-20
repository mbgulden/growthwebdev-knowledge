---
name: memory-skills-boundary-discipline
description: Memory is for stable preferences and facts only; skills are for procedures the agent re-derives every session; micro-skills are for single-recipe procedures (1 page max). Audit memory once. Anything that reads like a runbook or decision tree goes to a skill, not memory. The boundary prevents the agent from re-deriving the same procedure from memory line and from the skill body, which produces "confident same-shape re-mistakes." Apply to all profiles; the boundary leak is silent until a second source documents the same procedure.
triggers:
  - memory has a line that reads like a procedure ("When correcting, do X then Y")
  - a new rule was added to memory that a skill already documents
  - cold-load memory is too large to read in one screen
  - agent re-derives the same procedure twice (memory line + skill body)
  - user asks to "remember this" — decide which layer it belongs to before saving
  - reviewing profile memory files for a boundary audit
category: agent-operations
type: skill
---

# Memory vs. Skills Boundary Discipline

## The rule (the four-layer taxonomy)

- **Memory** (`~/.hermes/profiles/<profile>/memories/USER.md`) — stable preferences and facts only. Short prose. Cold-load should fit in one screen.
- **Umbrella skills** (`skills/<category>/<skill>/`) — class-level disciplines. A class of decisions, not a single recipe. Multi-page.
- **Micro-skills** (`skills/micro/<skill>/`) — single-recipe procedures. 1 page max (~3000 bytes). One decision tree, not a class.
- **Handoff** (`state/current.json`) — transient state. What shipped this session, what's blocked, what's next. Not memory.

When adding anything durable to the agent's cold-load surface, classify it first. If it's a preference or fact → memory. If it's a class of decisions → umbrella skill. If it's a single recipe → micro-skill. If it's transient → handoff.

## The audit procedure

When auditing memory (do this once per profile, not repeatedly):

1. **Read each memory line.**
2. **Classify each line** using the four-layer taxonomy above.
3. **For runbook-style lines**: check if a skill already documents the procedure. If yes, replace the memory line with a pointer ("see skills/<path>/"). If no, write the skill.
4. **For decision-tree lines**: write as a micro-skill under `skills/micro/`.
5. **For stable preferences and facts**: keep in memory.
6. **For transient state**: move to handoff.

The audit output is a tighter memory file with skill pointers instead of inline duplication.

## How to know when a memory line is actually a runbook

A memory line is a runbook if it answers the question "what should the agent DO?" not "what is true?". Examples:

- ✅ Memory: "Michael prefers a fast/simple response path for concepts unless live state is needed." (Preference.)
- ❌ Runbook: "When correcting an agent, lead with the verification recipe, not the assertion." (Procedure.)
- ✅ Memory: "OKF/Prismatic governance requires durable evidence, source manifests before cleanup." (Governance preference.)
- ❌ Runbook: "No branch/worktree deletion without approval; manifest first, then ask, then delete." (Procedure.)

The clean test: **if removing the line would change what the agent DOES, it's a runbook.** If removing the line would only lose a fact or preference the agent references but doesn't act on, it's memory.

## Micro-skill naming

Micro-skills live under `skills/micro/<name>/SKILL.md`. The name should describe the procedure, not the session that produced it. Good names:

- `corrections-lead-with-recipe` (a procedure)
- `outbound-action-gate` (a procedure)
- `branch-deletion-approval` (a procedure)
- `post-session-review` (a procedure)

Bad names (one-off session artifacts):

- `fix-ned-kpi-collections` (one session, one fix)
- `audit-2026-07-29` (a date, not a procedure)
- `gap-6-implementation` (a gap ID, not a procedure)

If the proposed name only makes sense for today's task, the procedure is too narrow — either generalize it or fold it into an existing skill.

## Umbrella vs. micro-skill split

Don't expand umbrella skills when a single decision-tree subprocedure would do. Examples:

- A "reply shape" umbrella covers status/evidence/blocker/next-action — that's a class. Keep as umbrella.
- A "correct with verification recipe" procedure is one decision tree — that's a micro-skill, not an umbrella.
- A "post-session review" procedure has multiple steps but is one recipe — micro-skill.

If a new procedure doesn't fit any existing skill's class, decide:
- Is it a class of decisions? New umbrella skill.
- Is it a single recipe? Micro-skill.
- Is it neither (one-off observation)? Handoff, not memory or skill.

## Cross-profile adoption

When micro-skills or umbrella skills are shared across profiles, adopt via direct symlink (not the hardcoded `_adopt_shared_skills.py` which only scans `skills/agent-operations/`). Always exclude the source profile from the target set. See `prismatic-core-skill-distribution-ops/SKILL.md` "Cross-profile skill adoption: the source-profile trap" pitfall for the failure mode.

```bash
# Manual adoption loop (preferred over the broken adopter for skills/micro/)
for skill in skills/micro/*/; do
  for profile in george kai ned autobot next-step; do
    mkdir -p ~/.hermes/profiles/$profile/skills/micro
    ln -sf $(pwd)/$skill ~/.hermes/profiles/$profile/skills/micro/
  done
done
```

## Pitfalls

- **Don't put runbook-style procedures in memory.** Memory is for stable preferences and facts only. The agent will re-derive the procedure from the memory line AND find it in the skill, producing "confident same-shape re-mistakes" when the memory line drifts from the skill body. Use skill pointers ("see skills/<path>/") instead.
- **Don't bundle unrelated micro-skills under one umbrella.** A new umbrella should describe a class of decisions. If a "skill" is really a single recipe, it's a micro-skill, not an umbrella.
- **Don't name micro-skills after the session that produced them.** `gap-6-fix` or `2026-07-29-audit` are session names, not procedure names. If the procedure only matters for one session, it doesn't need a micro-skill — put it in the handoff.
- **Don't audit memory repeatedly.** The audit is once per profile. After that, the rule is "every memory write is classified at write time." Periodic re-audits are signal-noise; the discipline is the discipline, not the audit.
- **Don't accept "skill duplication" as harmless.** If a procedure is in two places (memory + skill), the next refactor will diverge them, and the agent will follow the wrong copy. Pick one source of truth.
- **Don't expand the boundary beyond four layers.** A fifth layer ("rules," "policies," "preferences") adds complexity without adding signal. The four-layer taxonomy is enough.
- **Don't fold a micro-skill into its umbrella and delete the micro in one move — gate the delete on a separate decision.** A patch that absorbs a micro's content into the umbrella is reversible (you can re-read the umbrella diff). A delete is not (the micro is gone, and its 20+ cross-references in companion skills, other profiles, memory, and OKF standards all break). The 2026-08-01 skill-consolidation-audit pass learned this: the umbrella patch landed cleanly, but `corrections-lead-with-recipe` had cross-references in `directive-then-execute`, `memory-skills-boundary-discipline`, `verifier-as-deliverable-discipline`, `kai/skills/tourism/active-oahu-operations`, `kai/skills/micro/tool-parameter-required-fields-checklist`, a USER.md memory line, and the `hermes-memory-skills-boundary-discipline` OKF standard — plus log noise across `george`, `kai`, `ned` profiles. **Default sequence:** (1) patch the umbrella with the absorbed content as a "compact form (formerly …)" pointer section, (2) surface the delete + fan-out as a separate decision, (3) wait for the user's call before destructively editing files outside the active profile or before mutating durable artifacts (memory, OKF). The "delete when you see duplication" instinct bites here because cross-references look like noise rather than live dependency edges.

## Companion skills

- `memory-selective-pruning` — when memory has grown beyond one screen, run selective pruning against this discipline.
- `post-session-review` — micro-skill that captures the post-session review procedure, including the memory-vs-skills classification step.
- `corrections-lead-with-recipe` — micro-skill that lives in `skills/micro/`. The discipline that put it there was this skill.
- `proactive-execution-discipline` — umbrella skill. A class of decisions (when to ask, when to execute silently).
- `projector-aware-communication-discipline` — umbrella skill. A class of decisions (reply shape, anti-patterns).
- `verification-recipe-vs-assertion` — umbrella skill. A class of decisions (when to lead with recipe vs assertion).
