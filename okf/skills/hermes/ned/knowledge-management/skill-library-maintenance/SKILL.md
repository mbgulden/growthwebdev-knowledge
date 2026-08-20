---
name: skill-library-maintenance
description: Actively update the skill library after sessions, especially when Michael corrects style/workflow or a reusable technique emerges. Use for end-of-session learning passes, skill-library review requests, or anytime a loaded skill was missing a step/pitfall.
---

# Skill Library Maintenance

## When to use

Use this skill when Michael asks to review a conversation and update the skill library, or when a session produced a reusable technique, workflow correction, style correction, or skill gap.

## Core rule

Be active. A no-op pass is not neutral when the session contained learning signals. Prefer improving an existing class-level skill over creating narrow one-off skills.

## Decision order

1. **Patch a currently loaded skill first**
   - If a skill was loaded/consulted during the session and covers the new learning, patch that skill.
   - Add missing steps, pitfalls, verification requirements, or pointers to support files.

2. **Patch an existing umbrella skill**
   - If no loaded skill fits, update a class-level umbrella that governs the task type.
   - Avoid adding long one-session narratives to `SKILL.md`; keep it procedural and reusable.

3. **Add a support file under an umbrella**
   - `references/` for session-specific transcripts, reproduction recipes, provider/API quirks, or condensed knowledge banks.
   - `templates/` for starter files meant to be copied and modified.
   - `scripts/` for deterministic probes or verification helpers future agents should run.
   - After adding a support file, patch `SKILL.md` with a one-line pointer so future agents know it exists.

4. **Create a new umbrella skill only when necessary**
   - The name must be class-level, not a PR number, issue number, error string, temporary codename, or one-session artifact.

## What counts as a learning signal

- Michael corrects style, tone, format, legibility, verbosity, result-linking, or reporting shape.
- Michael corrects workflow, sequencing, ownership, safety boundaries, or verification depth.
- A non-trivial fix, workaround, debugging path, guardrail, or tool pattern emerged.
- A loaded skill was wrong, stale, incomplete, or missing a pitfall.

## What not to save

Do not encode durable negative claims about tools, transient setup failures, missing binaries, one-off task narratives, or stale task progress. If a setup issue occurred, capture the fix/configuration pattern under a relevant setup/troubleshooting skill — not “tool X is broken.”

## Final response shape

Report exactly what changed:

```md
✅ Skill library updated

**Updated**
- `<skill>` — <what changed>
- `<skill>` — <support file added / pointer patched>

**Skipped**
- <anything intentionally not captured, if relevant>
```

If genuinely nothing was learned, say only:

```md
Nothing to save.
```

## Pitfalls

- Do not create one skill per session. Use class-level umbrellas and support files.
- Do not only write a support file and forget to patch `SKILL.md` with a pointer.
- Do not save task outcomes, PR numbers, commit SHAs, or “we completed X” as durable knowledge unless they illustrate a reusable procedure.
- User preference corrections belong in the governing skill body, not only in memory.
