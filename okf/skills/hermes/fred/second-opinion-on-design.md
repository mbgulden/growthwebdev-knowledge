---
name: second-opinion-on-design
description: When to get a second opinion before coding (delegate_task to subagent) and how to frame the question for maximum signal.
---

# Second Opinion on Design Questions — When and How

## When to load this skill

You're about to implement a fix to a failing test, a heuristic, or a non-trivial code change. Before writing code, ask: "Could this be a wrong-signal problem instead of a tuning problem?"

## The pattern

**Step 1: Recognize the trigger**
- Test failing on edge case
- Threshold tuning question ("what value of X?")
- Heuristic that "looks right" but produces false positives
- Multiple plausible fixes (A, B, C, D, E)

**Step 2: Write a focused design question**
- State the failing test or symptom
- Show the relevant code (or file path)
- List 4-5 candidate fixes with brief descriptions
- Ask: "Which is correct? Defend briefly. Give exact code change."

**Step 3: Delegate to a subagent**
```python
delegate_task(
    goal="Review this design question and recommend ONE fix...",
    context="<code path, file lines, exact failure>",
    toolsets=["file"]
)
```

**Step 4: Apply the fix or refute it**
- Subagent might catch a structural bug you missed (like the new-vs-modified file distinction in Phase 2 Gap 4)
- Or confirm your original fix was right (also valuable)
- Either way, you ship faster than iterating alone

## Real example: Phase 2 Gap 4

**My framing:** "Test fails because `check_test_coverage_heuristic` flags a 1-line new source file. Options: A) accept NEEDS_DISCUSSION, B) 50-line threshold, C) remove from verdict path, D) info-level, E) only flag new files."

**Subagent caught:** The heuristic conflated new files with modified files. Every diff line shows `+++ b/path` regardless of whether the file is new. Option E + 10-line threshold is the structural fix. The heuristic was lying about "new" source files.

**Result:** Saved 2+ hours of threshold-iteration that would have produced a fragile fix.

## Cost vs benefit

- **Cost:** 30-60 seconds + subagent tokens
- **Benefit:** Catches structural bugs that pure reasoning misses (subagent sees code fresh, no context pollution)

## The Recon Step (added Jun 2026)

**Before writing specs, do recon.**

Second-opinion reviews are great at catching spec-level assumptions that aren't validated against the actual codebase. But if you write a spec *before* reconning the codebase, the subagent reviewer will spend their context window finding the same missing infrastructure you'd find with a 30-min search. That's wasted review work.

**Pattern:**
1. Before writing the spec, delegate 2-3 parallel recon tasks via `delegate_task`. Each task: "Search the codebase for existing infrastructure in area X. Report what already exists, what gaps exist, what to extend vs reinvent."
2. Save the recon as a single audit-trail doc (`okf/operations/<initiative>-reconnaissance-<date>.md`).
3. Write the spec *grounded in the recon findings* — cite file paths, line numbers, and verified APIs.
4. Then run second-opinion reviews. The subagent reviewer's job is now "challenge the design + verify the recon is correct," not "find infrastructure you should have searched for."

**Cost:** 3 × 60s = 3 minutes of recon + ~6 minutes of subagent review = 9 minutes total.

**Benefit:** Second-opinion reviews focus on design quality, not infrastructure discovery. Far higher signal.

**Reference:** Phase 3 Sprint 1 (Jun 2026) — 3 specs originally written *without* recon, all 3 flagged REQUEST_CHANGES with 1 CRITICAL miss (invented parallel observability when `prismatic/telemetry.py` already exists). After 3 parallel recon tasks + spec rewrites, all 3 specs are grounded in verified reality. Audit trail: `okf/operations/phase3-reconnaissance-2026-06-28.md`.

## Anti-pattern: don't second-guess yourself into paralysis

This skill is for **non-trivial design questions** where multiple fixes are plausible. If there's only one obvious fix, just write it. Don't waste subagent calls on trivial work.

## Related skills

- `peer-review-before-merge.md` — peer review AFTER code is written
- `factory-code-audit.md` — audit factory outputs for false-completions
- `autonomous-execution-discipline.md` — when to act vs ask