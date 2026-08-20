---
name: post-session-review
description: "The post-session review procedure for George: update memory + class-level umbrella skills for reusable corrections; no-op reviews are rare and must be justified."
---

# post-session-review

Use this when Michael asks to review the prior conversation and save durable learning.

## Required review dimensions

1. **Memory** — save only stable facts about Michael: persona, durable preferences, expectations, personal details, and how he wants agents to behave. Do not save task progress, ticket state, artifact hashes, or anything likely stale in a week.
2. **Skills** — save reusable procedure/approach lessons. Most substantive sessions should patch at least one skill; a no-op is a miss when there was a correction, non-trivial technique, workaround, or outdated skill.

## Skill update priority

Prefer class-level umbrellas over one-session artifacts:

1. Patch a skill loaded/consulted in the session if it covers the lesson.
2. Otherwise patch an existing umbrella skill found by `skills_list`/`skill_view`.
3. For session-specific details, condensed knowledge banks, API excerpts, or exact examples, add `references/<topic>.md` under the umbrella and add a pointer in `SKILL.md`.
4. Create a new skill only when no class-level umbrella exists; name it for the recurring task class, not a ticket, PR, error string, codename, or one-off outcome.

If the right governing skill exists only in another profile and Michael has not explicitly authorized cross-profile editing, do not edit it; create or patch the active profile's governing umbrella and mention the overlap.

## User-preference embedding

When Michael corrects style, format, verbosity, legibility, tone, sequencing, or approach, save it twice when appropriate:

- memory = who Michael is / what he prefers;
- skill = how this class of task should be performed next time.

Frustration is a first-class skill signal. `Stop doing X`, `don't format like this`, or `I hate when you Y` belongs in the skill that governs the task, not only in memory.

## Do not capture

- Environment-dependent setup failures as durable negative rules.
- Negative claims about tools/features that may be fixed later.
- Transient errors that resolved; capture the retry/fix pattern if it is reusable.
- One-off task narrative, issue numbers, PR numbers, commit SHAs, or completed-work logs.

## Final report

Report exactly what changed:

```text
MEMORY=<added|updated|none + reason>
SKILLS=<patched/created files or none + reason>
OVERLAP=<existing overlapping skill if any>
```
