# Phase 3 / Sprint 1 — Honest Caveats

**Date:** 2026-06-28
**Sprint:** Phase 3 / Sprint 1
**Owner:** Fred (orchestrator)
**Source:** Opus plan + my own audit

---

## Things that could derail Sprint 1

### D1 — Sonnet subagent fabrication

The single biggest risk. A Sonnet subagent could:
- Skip tests silently
- Mock the function under test instead of running real code (Lesson 10 anti-pattern)
- Report "all tests pass" when actually some failed and were ignored
- Use `lambda *a: None` indistinguishable from no hook (Gap 11 anti-pattern)

**Mitigation:** Every subagent return summary requires live REPL probes (`python3 -c "..."`). Fred runs `pytest` independently after subagent returns.

### D2 — Spec assumption collapses in implementation

Each spec makes 5-10 implicit assumptions. Some examples:
- Gap 12 assumes `LinearTaskProvider.add_comment()` exists with the documented signature
- Gap 11 assumes `PipelineOrchestrator._lock` semantics are unchanged by adding `registry` kwarg
- Gap 10 assumes `importlib.metadata.entry_points()` works on Python 3.12+ (it does, but version differences exist)

**Mitigation:** If a subagent reports "spec assumption wrong," pause, fix the spec, restart the subagent. Don't adapt the implementation to work around a wrong spec.

### D3 — Lane governance blocking pushes

Gap 12 touches `prismatic/telemetry.py` (Fred lane) but Gap 11 needs telemetry integration in `prismatic/review/*` (Ned lane). If the Sonnet subagent for Gap 12 modifies Ned lane files, the pre-push hook blocks.

**Mitigation:** Subagent prompts explicitly list out-of-scope files. Fred checks `git diff` before push.

### D4 — Meta-review reveals cross-PR drift

After all 3 gaps ship, Sonnet meta-review could surface a drift between specs and implementation. Common drift categories:
- Public symbols not exported from package __init__.py (PR #43 meta-review caught this for Phase 2)
- Docstrings contradicting the actual behavior (PR #43 caught register_impact_rule docstring)
- Dead channels (Lesson 10 — tests pass but production doesn't read the channel)

**Mitigation:** The 8-category meta-review prompt enumerates these. If Sonnet finds them, we open follow-up gaps for Sprint 2.

### D5 — Opus-only-summarized plan

Opus returned a 5-bullet summary instead of the 10-section structured plan I asked for. I wrote the remaining 5 sections myself. If those sections have gaps that I didn't notice, the sprint could miss something.

**Mitigation:** The 5 Opus-authored files are substantive (each ~7-8KB). I authored the remaining 5 based on Opus's summary + recon + specs. If Michael wants the structured Opus plan re-attempted, we can re-prompt.

## Spec assumptions to challenge

These are the assumptions I would question if I had more time:

### Gap 12 assumption: "23 tests are sufficient"

The 21 telemetry extension tests cover happy path + error cases. But:
- What about thread-safety with the daemon-thread drain loop?
- What about concurrent inserts during schema migration?
- What about cleanup_expired during high-throughput periods?

**Challenge:** Add 3 more tests for thread-safety + migration race conditions.

### Gap 11 assumption: "apply_impact_rules is pure"

The spec says `apply_impact_rules` is pure (no lock needed). But:
- What if a rule's exception is raised but not caught?
- What if the rule mutates global state (registry, file system, network)?

**Challenge:** The docstring should explicitly state: "Rules MUST be pure. Mutations are the caller's responsibility. Exceptions are caught and logged but otherwise ignored."

### Gap 10 assumption: "Reference plugin is benign"

The `prismatic-hello-world` reference plugin registers a single check for "hello" in diffs. Real plugin authors might find this trivial and copy it as a starting point. What if they accidentally ship a check that's too noisy (warning on every "hello" mention)?

**Challenge:** The reference plugin should have a "warning" severity and a clear docstring saying "for demonstration only."

## Open questions for Michael

1. **Should Gap 12's `ops_feed_target_issue_id` be a specific Linear issue (e.g., GRO-OPS) or an env var?** Spec currently uses env var (`PRISMATIC_OPS_FEED_ISSUE_ID`). If unset, falls back to stdout-only.

2. **Should Gap 11's `PipelineOrchestrator(registry=...)` be passed via constructor (current spec) or via setter (alternative)?** Constructor is more explicit but breaks if the registry needs to be swapped mid-process. Setter is more flexible but adds state. Spec uses constructor.

3. **Should Gap 10's `prismatic-hello-world` reference plugin live in `plugins/` (repo-relative) or `src/prismatic_hello_world/` (package-relative)?** Spec uses `plugins/`. This keeps the reference plugin separate from the main package, but means it's not installable via `pip install prismatic-engine`.

4. **Should the meta-review happen after each gap or after all 3 gaps?** Spec says "after all 3." Per-gap would catch issues earlier but cost more meta-review sessions. Per-sprint is cheaper but issues compound.

5. **Should the Opus plan be re-prompted for the structured 10-section version, or is the 5-bullet summary + my authored files sufficient?** Per Michael's response, Opus's failure to write files was a process bug; I've now written the missing files. If we re-prompt Opus, we might get cleaner output but burn 10 more minutes.

## "If all else fails" fallback

If Sprint 1 is partially successful (e.g., Gap 12 ships, Gap 11 fails peer review, Gap 10 never ships):

1. **Gap 12 ships alone** as a "telemetry foundation" PR. Adds value on its own.
2. **Gap 11 becomes Sprint 2 Gap 11-retry** with the fix from peer review.
3. **Gap 10 becomes Sprint 2 Gap 10-retry** with the Gap 11 dependency resolved.
4. **No Sprint 1 "complete" claim** until all 3 ship.

The factory still works without Sprint 1 — it just doesn't have observability or plugin auto-discovery. Those are improvements, not blockers.

## What we DON'T know yet (acknowledged gaps in the recon)

1. **Performance baseline** — We don't have a `pytest --durations=20` benchmark for Phase 2 deploy-fresh. Gap 11's `apply_impact_rules` could add 1-10ms per review tick; we won't know until we measure.

2. **Real third-party plugin needs** — Until Gap 14 ships the first real plugin, we're guessing at the plugin API surface. Gap 10 may need a revision after Gap 14 reveals gaps.

3. **Linear API rate limits** — We don't know how often ops_feed will be called. If it's 6 events/review × 10 reviews/hour = 60 events/hour, we're well under Linear's rate limits. But if the factory cranks up to 100 reviews/hour, we may hit limits.

4. **Reference plugin discoverability** — The reference plugin in `plugins/prismatic-hello-world/` is only installed manually (`pip install -e plugins/prismatic-hello-world`). How will real users discover it? The distribution checklist needs a "how to find plugins" section.

5. **Sprint 2 / Sprint 3 dependencies** — Sprint 2 (Gap 12-full tracing + Grafana) depends on Sprint 1's telemetry tables being stable. If Gap 12's schema changes after Sprint 2 starts, that's a backward-compat headache.

---

*Filed 2026-06-28 by Fred (orchestrator). Continuation of Opus's interrupted plan output.*
