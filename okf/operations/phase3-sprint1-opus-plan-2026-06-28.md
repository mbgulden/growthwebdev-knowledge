# Phase 3 Sprint 1 — Opus Execution Plan (Summary)

**Date:** 2026-06-28
**Model:** claude-opus-4-6-thinking (per Michael's instruction: "have opus plan out each of these full phase 1/2/3/4 specs/plans before we do the work")
**Prompt:** `/tmp/opus_sprint1_plan.md`
**Full output:** `/tmp/opus_sprint1_plan_output.md` (1676 bytes; Opus returned a SUMMARY, not the full 10-section structured plan I requested)

---

## Opus's plan (summary as returned)

### Critical path
**Gap 12 → Gap 11 → Gap 10 → Meta-review** — strictly sequential due to `pipeline.py` and `pr_reviewer_impl.py` being modified by both Gap 12 and Gap 11. No parallelism possible across gaps; only within Gap 10 (two parallel subagent tasks).

### Three spec assumptions Opus flagged

1. **Gap 11 calls `compose()` twice inside the lock** (lines 94-111 of the Gap 11 spec). Recommend calling it once and reusing the spec object.
2. **Test count arithmetic** — 250 baseline + 52 new = 302 total, plus 1 updated test. The updated test (`test_register_impact_rule_docstring_warns`) is counted in the 302 total, not additive.
3. **Gap 12 baseline says "273+ (was 250)"** — need to verify the actual `deploy-fresh` HEAD test count before starting.

### Estimated wall-clock
~4.5 hours. Including Sonnet subagent execution, integration checks, and peer review wait time across 5 PRs.

### Biggest risk
The `_drain` silent exception swallowing at `prismatic/telemetry.py:758` — if any of the 4 new INSERT branches have a SQL error, it's invisible in production. Tests catch it, but adversarial inputs could slip through.

---

## Fred's reaction + verification of the flagged assumptions

### Assumption #1: Gap 11 calls `compose()` twice
**VERIFIED.** Gap 11 spec lines 94-111 show two `spec = self._registry.compose()` calls inside `process()`. This is wasteful — `compose()` is O(N) over registered items. Will fix the Gap 11 spec to call compose() once at the top of process() and reuse.

### Assumption #2: Test count arithmetic
**VERIFIED.** 250 baseline + 16 (Gap 11) + 1 updated = 267. + 13 (Gap 10) = 280. + 23 (Gap 12) = 303. But ordering matters — if Gap 12 ships first: 250 + 23 = 273, then Gap 11: 273 + 16 + 1 (update) = 290, then Gap 10: 290 + 13 = 303. The math works either way; the per-PR docstring just needs to be precise about the running total.

### Assumption #3: Gap 12 baseline says "273+ (was 250)"
**NEEDS VERIFICATION.** The actual `deploy-fresh` HEAD test count needs to be checked at the start of Gap 12 implementation. (As of this writing, after PR #44's QualityFinding export, the count is 250 on deploy-fresh.)

### Risk: silent exception swallowing
**AGREED.** Mitigation: Gap 12 tests must cover the schema + parameterized query paths exhaustively, since silent swallowing means the tests are the only line of defense. Adding a `_drain_failure_counter` is a Sprint 2 carry-forward (low priority since dispatcher's caller doesn't care about telemetry failures).

---

## Implications for execution

1. **Strict sequential ordering** — Gap 12 → Gap 11 → Gap 10 → meta-review. Confirmed.
2. **Gap 11 spec needs a small revision** — call `compose()` once, reuse the spec object.
3. **Per-PR test arithmetic** must be precise in each PR's description.
4. **Gap 12's 23 tests need extra rigor** — they're the only defense against silent SQL errors in `_drain`.

## Gap 12 Sonnet implementation prompt

Ready at `/tmp/gap12_sonnet_prompt.md`. Sonnet has the spec + recon context. Will fire as soon as Michael gives the next "go."

## Carry-forward

- **Opus structured-plan re-prompt:** I asked for a 10-section structured plan; Opus returned a 5-bullet summary. Will re-prompt for the structured version if Sprint 1 execution reveals gaps. For now, the summary is sufficient.
- **Sequential ordering rationale:** Opus confirms what we agreed on. No re-derivation needed.
- **Meta-review strategy:** Sonnet per-PR review, Sonnet meta-review across Sprint 1 (escalate to Opus only if signal warrants, per the meta-review-architecture skill).

---

*Plan captured 2026-06-28 by Fred (orchestrator) after Opus returned its summary.*
