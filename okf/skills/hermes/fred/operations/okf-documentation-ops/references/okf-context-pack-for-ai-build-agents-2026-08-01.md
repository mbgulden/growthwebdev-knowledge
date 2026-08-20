# OKF Context Pack for AI Build Agents — Second Worked Example (2026-08-01)

This is a delta reference. The base pattern is in `references/okf-context-pack-for-ai-build-agents-2026-07-31.md`. Read that first.

This file documents what changed when the Context Pack pattern was applied to a second OKF (`okf-docs-workspace-deploy-v1.md`), the gaps the first application surfaced, and the rules that emerged from the second application.

## What the second OKF validated

The pattern documented in the 2026-07-31 reference is class-level, not one-off. The docs/workspace/deploy OKF was written on 2026-08-01 using the same 12-sub-section shape, the same frontmatter pattern, the same path-verification step, and the same quick-reference card. The second OKF shipped with 11 anti-patterns (one more than RF), 13 verified paths, 13 API endpoints, and 4 git SHAs — and the build-ready shape held. The pattern scales.

## What the second OKF added (new patterns)

### 1. Wrap-don't-replace anti-pattern (recurring)

When an OKF's workstreams must extend existing code (e.g., `prismatic.integrate.IntegratePhase` for the deploy hook), the anti-pattern is "wrap, don't replace." The new code is a thin adapter that calls the existing class as the preliminary heuristic; the existing class is the canonical runner.

Concrete shape (from the workspace/deploy OKF §16.8):

```markdown
11. ❌ Do NOT replace `prismatic.integrate.IntegratePhase`. WB-3 wraps it; the existing class is the canonical integration runner.
```

The first OKF (RF) had a similar anti-pattern ("Do NOT replace `pr_reviewer.py`"). The pattern is recurring across both OKFs.

**Capture rule:** when an OKF wraps an existing class, add a wrap-don't-replace anti-pattern. Each wrap target earns its own row in §16.8.

### 2. Sibling OKF frontmatter field

When an OKF supersedes or extends a prior OKF, add a `sibling:` field to the frontmatter. The second OKF's frontmatter:

```yaml
---
type: OKF
title: OKF — Docs/Workspace/Linear→PR→Prod Workstream V1
...
sibling: okf-review-factory-v1.md
status: proposed
---
```

The sibling pointer is the disambiguation mechanism when an OKF references concepts defined elsewhere. The agent reads the sibling first to get the context, then reads the current OKF for the new work.

Without the sibling pointer, the agent has to guess which OKF is the predecessor. The cost is re-derivation of the prior context, which is exactly what the Context Pack is trying to prevent.

### 3. Verify-paths-before-citing discipline

The docs/workspace/deploy OKF initially cited `scripts/rebuild-and-deploy.sh` as the deploy runner target for WB-3. The actual runner is `prismatic/integrate.py` (class `IntegratePhase`). The path verification step caught it; the OKF was patched to point at the real location.

The lesson: when you're about to cite a path in an OKF, verify it with `os.path.exists` or `ls` BEFORE writing the citation. The post-hoc path verification step is a safety net, but the right discipline is to verify inline as you write each citation.

This is a real failure mode, not a hypothetical. The 2026-08-01 OKF had to be patched mid-draft because the assumed path didn't exist. The patch was clean (3 entries to update), but the timeout could have been avoided.

### 4. Two-OKF continuity discipline

When the OKF replaces a manual workflow (e.g., PR merges that took 8 days), include a "Legacy baseline" sub-section. From the Review Factory OKF §12.1:

- Documents the cost (days, commits, agents) so the new system has a clear SLT to beat
- Names the inefficiencies the new system eliminates
- Gives the builder a "this is what we're replacing" anchor

The second OKF (docs/workspace/deploy) did not have a legacy-baseline section because its workstreams weren't replacing a specific prior protocol. The RF OKF's legacy baseline was high-value because PR #382 was a concrete, documentable 8-day example. Use the legacy baseline selectively — when the prior protocol is concrete and measurable.

### 5. Anti-pattern count scales with wrap-don't-replace

The first OKF (RF) had 10 anti-patterns. The second (Workspace/Deploy) had 11. The +1 was the wrap-don't-replace row for `IntegratePhase`. When counting anti-patterns during OKF design, plan for 10 + 1-per-wrap-target.

## Concrete additions to the 2026-07-31 reference

The 2026-07-31 reference should be patched with these updates (if you have write access):

1. **Worked examples** — add a second example link to the docs/workspace/deploy OKF.
2. **Recurring patterns** — add a new sub-section after "Worked example" with the five patterns above.
3. **Pitfalls** — add two new rows: "Don't cite a path from memory" and "Don't forget the sibling OKF frontmatter field."
4. **Wrap-don't-replace** — call out that this is a recurring pattern across OKFs, not a one-off.

## Worked example

`/home/ubuntu/.hermes/profiles/orchestrator/state/okf-docs-workspace-deploy-v1.md` §16 (2026-08-01). 12 subsections, 13 verified file paths, 13 API endpoints, 4 git SHAs, 11 anti-patterns (the +1 is the wrap-don't-replace for `IntegratePhase`), 16-item checklist (5 items added beyond RF), 2 acceptance-marker commands.

The OKF verified paths in two passes: draft pass (cited "scripts/rebuild-and-deploy.sh"), then verification pass (caught the missing path, fixed to "prismatic/integrate.py"). Both passes are documented in the OKF git history.

## Pitfalls (delta from 2026-07-31)

- **Don't assume the deploy script exists at the obvious path.** When in doubt, `find` for the actual runner class before citing it. The deeper-runnable-class pattern (`prismatic/integrate.py`'s `IntegratePhase`) is more common than the shell-script pattern (`scripts/rebuild-and-deploy.sh`). When you see evidence of a class-based runner, prefer that.
- **Don't cite paths from session memory.** Mem-cited paths are 60-80% accurate at best. The verification step is the safety net, but the inline-verification discipline catches errors before they reach the OKF.
- **Don't forget the frontmatter sibling field.** It's a one-line addition that prevents the agent from re-deriving the prior OKF's context. The cost of forgetting is high (the agent will guess); the cost of adding is low (one line of YAML).
- **Don't add anti-patterns just to reach a round number.** The +1 in the workspace/deploy OKF was earned by the wrap-don't-replace for `IntegratePhase`. If your OKF has 10 anti-patterns and no wrap targets, stop at 10. If it has 11 wrap targets, you have 21 anti-patterns — that's fine too.

## Related references

- `references/okf-context-pack-for-ai-build-agents-2026-07-31.md` — the base pattern. Read first.
- `linear-handoff-build-out` — the Linear tree shape that complements the Context Pack.
- `okf-documentation-ops` SKILL.md §25 — the one-liner in the umbrella skill that points at this reference.
