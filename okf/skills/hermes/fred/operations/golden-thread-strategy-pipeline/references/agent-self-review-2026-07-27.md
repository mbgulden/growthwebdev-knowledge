# Agent self-review — 2026-07-27

Session-derived reference for the class of "what gaps are there in your profile / what can you optimize?" question Michael asks. Produces a structured 8–10 axis critique of the agent's own operating surface, with concrete fixes and a top-3 priority order.

## When the user asks "what gaps are there in your profile?" or "what can you optimize?"

Use this shape. Output in chat (no artifact file needed; the deliverable is the analysis itself):

1. **Numbered list of 8–12 axes.** Common axes:
   - Live state vs memory drift
   - Proactive execution vs reactive waiting
   - Tone/format vs user preference (Projector awareness, brevity, link-first)
   - Tool/runtime dependency fragility
   - Evidence/verification hygiene
   - Skill/memory boundary leaks
   - Digest/notification contract clarity
   - Source-of-truth single-writer
   - Reading cost (Telegram, mobile, scan-time)
   - Energy/load awareness
   - Decision-routing transparency
2. **For each axis: gap, fix, verification step.** Three lines max per axis. Don't elaborate.
3. **Top-3 priority table** at the end. P0 / P1 / P2 only.
4. **End with: "Want me to start the first one now?"** If Michael has asked the question, the implicit ask is "and fix them." Don't wait for a second prompt.

## Why this shape works for self-review

- Numbered axes give Michael a **scan frame**. He can pick the one that resonates without reading the whole critique.
- Each axis carrying gap + fix + verification means Michael can pick ONE and ask me to do it; the others are deferred but visible.
- The top-3 priority table forces a single starting point. A self-review without a top-3 is just a complaint list.
- "Want me to start the first one now?" turns the analysis into execution. Without it, the analysis becomes theater.

## Worked example: 2026-07-27

Michael asked "What gaps are there in your profile? What can you optimize?" — the response was a 10-axis critique:

1. Live state vs memory drift → maintain session-state handoff file
2. Proactive execution still too gentle → hard rule, daily execution counts
3. Projector awareness has slipped → default reply shape change
4. Linear work depends on one machine → codify minimum runtime surface
5. OKF/evidence hygiene good, verification sometimes lazy → verifier co-produced with artifact
6. Skills/memory boundary leak → audit once
7. Telegram digests too chatty → strict active-problems-only contract
8. "What ships next" gate is manual → weekly reconcile registry ↔ Linear
9. Reading cost too high → lead with link, 70-char visual line
10. Energy/crash detected late → energy check on first response line

Top-3 priority:
| Priority | Fix | Impact |
|---|---|---|
| 1 | Session-state handoff file | Cold start honors work already done |
| 2 | Pre-written verifiers | Stops verification nudges firing |
| 3 | Energy check on first response line | Projector protection actually fires |

Then: "If you want, I can start the first one now: write the handoff-file format and use it on this turn."

## Distinction from `references/portfolio-gap-analysis-2026-07-27.md`

| Aspect | Portfolio gap analysis | Agent self-review |
|---|---|---|
| Scope | The user's projects | The agent's own operating surface |
| Output target | Chat or `/tmp/<name>.md` | Chat only (artifact is the analysis) |
| Sections | 4 (TL;DR, ranked table, priority block, one action) | Free-form 8–12 axes + top-3 |
| Audience | Michael's strategic decisions | Michael's expectations of the agent |
| Tone | "Here's what to work on" | "Here's where I'm underperforming" |

Use self-review when the question is about the agent. Use portfolio gap analysis when the question is about the projects.

## Pitfalls

- **Do not produce a self-review without action commitment.** If the response ends with "what do you want me to do?", the self-review failed. End with "Want me to start the first one now?"
- **Do not produce more than 12 axes.** A self-review with 20 axes is the agent avoiding commitment. Pick the most-impactful ones and present those.
- **Do not be falsely humble.** "I have no gaps" is a self-review that fails the question. Even a well-tuned agent has at least 3–5 honest critiques.
- **Do not be catastrophically self-critical.** "I fail at everything" makes the critique useless. Each axis must be paired with a realistic fix.
- **Do not name axes that the user can't act on.** "I should be smarter" is not actionable. "Memory should be audited" is actionable. State the gap in operational terms.

## Related references

- `references/portfolio-gap-analysis-2026-07-27.md` — sibling pattern for project-portfolio questions.
- `SKILL.md` §7 "Execute the top task through AGY" — when a self-review gap becomes an executable task.