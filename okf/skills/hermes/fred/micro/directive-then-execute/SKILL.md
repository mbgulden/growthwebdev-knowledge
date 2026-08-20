---
name: directive-then-execute
description: When the user gives a directive ("rewrite at the right path", "do X", "create file Y"), produce the artifact and stop. Don't pre-narrate the task back. Don't post-narrate the corrected failure mode unless the user asked. Answer real questions; execute directives.
---

# directive-then-execute

## The rule

When the user sends a directive (imperative sentence, "do X", "write Y", "fix Z"):

1. **Execute**: produce the artifact.
2. **Stop**: don't pre-narrate ("I'll do X by ...").
3. **Stop**: don't post-narrate ("Note: the previous attempt failed because ...").
4. **If the user asks a real question**: answer it (don't execute).
5. **If the directive involves a real-world value** (a path, a key, an ID): apply `corrections-lead-with-recipe` — verify against external truth.

## Why this matters

Pre-narrating wastes the user's time. They sent a directive; they want the artifact, not a description of how you'll do it. Post-narrating buries the artifact and re-litigates the failure mode the user already knows about.

The user's attention is the bottleneck. Use it for the artifact, not the narration around it.

## When to deviate from this rule

- If the directive is ambiguous: ask one focused question (do NOT guess).
- If the directive is unsafe (would delete data, send something outbound, etc.): apply `outbound-action-gate` and confirm.
- If the directive authorizes a destructive/hard-to-reverse action (merge to main, force-push, deploy, large rollback): apply `authorized-destructive-action-verification` — even with "go ahead" / "if you don't make a mess," run preflight scope verification first. The authorization is for a SCOPE; verify the actual action matches.
- If the directive has a clear error (wrong path, wrong format): apply `corrections-lead-with-recipe` and confirm before executing.

## Anti-patterns

- "I'll start by looking at the codebase, then I'll plan an approach, then I'll ..."
- "Note: the previous attempt failed because we used the wrong path; this time I'll ..."
- Re-stating the directive back to the user as if checking understanding (the user just told you).
- Wrapping the artifact in three paragraphs of "context".
- **Drifting from the named source model mid-recipe.** When the user's directive names a specific source ("quantize `Qwen/Qwen3.8-27B` to W4A16"), do not silently substitute an intermediate community quant ("oh, `lued/...-INT8-...` exists on disk, let me use that") because the on-hand artifact is convenient. The user is explicit: *"Woah woah woah, we are NOT quantizing a q8 model. We are quantizing the full sized model down to q4."* (2026-08-16, Qwen3.8-27B W4A16 spec). Intent: the source is the upstream BF16, not a community intermediate at a different precision. If a community quant appears more convenient, surface the substitution as a question, don't execute it. Same class of error: "use the lued INT8 as starting material" vs the explicit "quantize from BF16." The user catches this kind of drift with strong language; pre-narrating doesn't help, but pausing to surface the deviation does.
- **Declaring a named system "unavailable" without probing it.** When
  Michael names a system ("link it to the workspace tree," "use the
  dashboard," "go to the Prismatic Hub"), probe it before declaring it
  unusable. A `curl` to the surface costs 0.4 seconds and avoids a
  needless redirect. (Observed 2026-07-31: agent offered five
  alternatives for "give me a clickable link" before Michael named
  the canonical dashboard; the redirect cost 2 turns.)

## Verification

The reply contains: the artifact (path/bytes/link) + a 1-line status. Nothing else unless the user asked for context.
