# PR #38 — Code Review: Phase 2 / Gap 4 Real PR Reviewer

**Branch:** `ned/phase2-real-pr-review-v2`  
**Files reviewed:**
- [`pr_reviewer.py`](file:///home/ubuntu/work/prismatic-engine/prismatic/review/pr_reviewer.py) — stub contract (155 lines)
- [`pr_reviewer_impl.py`](file:///home/ubuntu/work/prismatic-engine/prismatic/review/pr_reviewer_impl.py) — real implementation (496 lines)
- [`test_pr_reviewer_impl.py`](file:///home/ubuntu/work/prismatic-engine/prismatic/review/test_pr_reviewer_impl.py) — test suite (468 lines)
- [`__init__.py`](file:///home/ubuntu/work/prismatic-engine/prismatic/review/__init__.py) — public API (37 lines)

**Test run:** 35/35 passed in 0.07s ✅

---

## Review Verdict: REQUEST_CHANGES

---

### Strengths

- **Solid subprocess hygiene.** `fetch_pr_diff` uses a list form of `subprocess.run` (no `shell=True`), passes `timeout=`, and catches `TimeoutExpired`, `FileNotFoundError`, and `OSError`. No shell injection surface.
- **Clean protocol conformance.** `RealPRReviewer.review_pr(pr_url) → PRReviewResult` exactly matches the `PRReviewer` Protocol. `__post_init__` on `PRReviewResult` validates verdicts; the real reviewer only ever produces valid verdicts.
- **Well-structured secret patterns.** 10 patterns covering AWS, GitHub PAT/OAuth, Slack, Stripe, PEM private keys, DB URLs, generic API keys. The `break` after first match per line prevents duplicate findings on the same line — a deliberate and correct design.
- **`--- /dev/null` heuristic is correct.** The two-pass logic in `check_test_coverage_heuristic` correctly distinguishes new files from modifications, and the `COVERAGE_MIN_NEW_SOURCE_LINES = 10` threshold suppresses noise from trivial stubs.
- **Good test patterns.** Secrets in test fixtures are assembled via string concatenation to defeat GitHub's push-protection scanner. Tests are fast and deterministic (all mocked).
- **Security edge case handled.** `detect_secrets` only scans lines beginning with `+`, so deleted secrets (removal commits) don't trigger false positives. Confirmed by `test_only_added_lines_scanned`.

---

### Issues Found

#### 🔴 Bug 1 — `medium` severity in `SECRET_PATTERNS` is silently dropped by `compute_verdict` (severity: **critical**)

**Location:** [`pr_reviewer_impl.py:63`](file:///home/ubuntu/work/prismatic-engine/prismatic/review/pr_reviewer_impl.py#L63) (pattern) and [`pr_reviewer_impl.py:380-422`](file:///home/ubuntu/work/prismatic-engine/prismatic/review/pr_reviewer_impl.py#L380-L422) (verdict logic)

`SECRET_PATTERNS` includes a `"medium"` severity entry for generic `secret = "..."` patterns:
```python
(r"secret\s*=\s*[\"']?([A-Za-z0-9]{32,})", "secret", "medium"),
```
`compute_verdict` handles `"critical"`, `"high"`, and `"warning"` — but **not `"medium"`**. Confirmed by live probe:

```
severity=medium  →  verdict=APPROVE  (All checks passed — no issues found)
```

A diff containing `secret = "abcdef..."` (a genuine credential leak) is silently **approved**. This is a correctness and security bug — the severity tier that fires for generic secrets produces a false-safe outcome.

**Fix:** Either map `"medium"` → `NEEDS_DISCUSSION` inside `compute_verdict`, or change the pattern's severity to `"warning"` so it participates in the existing branch.

---

#### 🔴 Bug 2 — Warning detail lines are omitted from the summary when high-severity findings are also present (severity: **high**)

**Location:** [`pr_reviewer_impl.py:407-410`](file:///home/ubuntu/work/prismatic-engine/prismatic/review/pr_reviewer_impl.py#L407-L410)

In the `high` branch of `compute_verdict`, the warnings section header is appended but **the individual warning detail lines are never appended**:

```python
if warnings:
    summary_lines.append("")
    summary_lines.append(f"### Warnings ({len(warnings)})")
    # ← BUG: the actual per-finding lines are missing
return verdict, "\n".join(summary_lines)
```

Compare with the analogous block in the `critical` branch (lines 392–396), which correctly iterates and appends each finding. Confirmed by live probe — with one high + one warning, `f.py` does not appear in the summary at all. The warning section header renders but no findings beneath it. The downstream Linear comment will show a truncated, misleading review.

**Fix:** Add the missing loop:
```python
if warnings:
    summary_lines.append("")
    summary_lines.append(f"### Warnings ({len(warnings)})")
    for f in warnings[:5]:                          # add this
        summary_lines.append(f"- `{f.path}:{f.line}` — {f.message}")  # add this
```

---

#### 🟡 Bug 3 — `RealPRReviewer` is not exported from `prismatic.review.__init__` (severity: **medium**)

**Location:** [`__init__.py`](file:///home/ubuntu/work/prismatic-engine/prismatic/review/__init__.py)

`__init__.py` exports `StubPRReviewer` but not `RealPRReviewer`. The factory wiring (`GRO-2876`) that swaps in the real reviewer must import from `prismatic.review.pr_reviewer_impl` directly — a coupling the package design was trying to avoid. Confirmed:

```
has RealPRReviewer: False
__all__: ['PRReviewResult', 'PRReviewer', 'StubPRReviewer', ...]
```

**Fix:** Add `RealPRReviewer` to `__init__.py`:
```python
from .pr_reviewer_impl import RealPRReviewer
__all__ = [..., "RealPRReviewer"]
```

---

#### 🟡 Bug 4 — `check_function_length` uses diff line index (`i`) as the reported line number, not the actual source file line (severity: **medium**)

**Location:** [`pr_reviewer_impl.py:175`](file:///home/ubuntu/work/prismatic-engine/prismatic/review/pr_reviewer_impl.py#L175)

```python
for i, line in enumerate(diff.splitlines()):
    ...
    func_start_line = i   # ← diff line number, not source file line
```

`detect_secrets` has the same pattern (line `359`). The `InlineComment.line` field is documented as the PR line to annotate; using the diff-enumeration index makes inline comments land on wrong lines in the GitHub UI. The hunk headers (`@@ -N,M +P,Q @@`) are available in the diff and should be parsed to track the actual `+` line counter.

This is a correctness issue for the GitHub inline comment feature, though it doesn't affect the verdict.

---

#### 🟡 Test gap — no test for `medium` severity path through `compute_verdict` (severity: **medium**)

**Location:** [`test_pr_reviewer_impl.py:333-374`](file:///home/ubuntu/work/prismatic-engine/prismatic/review/test_pr_reviewer_impl.py#L333-L374)

`TestComputeVerdict` covers `critical`, `high`, and `warning` but has no test for `medium`. Had such a test existed it would have caught Bug 1 immediately. The `TestDetectSecrets` suite also has no test for the generic `secret = "..."` pattern (the one with `medium` severity).

---

#### 🟡 Test gap — `compute_verdict` with mixed `critical + warning` does not verify the warning section (severity: **low**)

The `test_critical_secret_blocks_merge` test asserts `verdict == REQUEST_CHANGES` and `"critical" in summary` but does not add a warning finding alongside the critical one to exercise the mixed branch at lines 392–396. This gap allowed Bug 2's analogous omission in the `high` branch to go undetected.

---

#### 🟢 Observation — `parse_pr_url` is resilient to trailing slash and whitespace (not a bug)

Probed `"https://github.com/owner/repo/pull/123/"` and `"https://github.com/owner/repo/pull/123  "` — both parse correctly via the greedy `\d+` match. No action needed.

---

#### 🟢 Observation — binary file headers handled gracefully (not a bug)

A diff containing `GIT binary patch` and `Binary files ... differ` does not produce findings because the binary marker lines don't start with `+`, and there is no `+++ b/` header that tricks the parser. Correct behavior, no action needed.

---

### Required fixes before merge

| # | Severity | Location | Fix |
|---|----------|----------|-----|
| 1 | 🔴 Critical | `compute_verdict` | Handle `"medium"` severity (map to `NEEDS_DISCUSSION`) |
| 2 | 🔴 High | `compute_verdict` high branch | Add per-finding lines to warnings section |
| 3 | 🟡 Medium | `__init__.py` | Export `RealPRReviewer` |
| 4 | 🟡 Medium | `check_function_length` / `detect_secrets` | Use hunk-based line tracking, not `enumerate` index |

Bugs 1 and 2 are blocking: Bug 1 is a silent false-safe for a security detection path; Bug 2 produces a misleading Linear comment that hides actionable findings from the human reviewer.

### Re-review checklist

- [ ] `compute_verdict` handles `"medium"` severity and a test asserts `NEEDS_DISCUSSION` (or `REQUEST_CHANGES`) for it
- [ ] The high-severity branch of `compute_verdict` includes per-finding warning detail lines in the summary
- [ ] `RealPRReviewer` added to `prismatic.review.__all__`
- [ ] `test_compute_verdict_mixed_critical_and_warning` test verifies warning details appear in summary
- [ ] `test_detect_secrets_generic_secret_medium` test added
- [ ] (Nice-to-have) Hunk-header line tracking for accurate `InlineComment.line`

### Recommendation

The core structure is clean and the 35 existing tests demonstrate good intent. Two bugs prevent a safe merge: `medium` severity secrets silently produce `APPROVE` (Bug 1 — a false safe for security), and the `high` branch of `compute_verdict` produces a summary that titles a warnings section but omits all its content (Bug 2 — misleading Linear output). Both are fixable in under 10 lines. Fix those two, export `RealPRReviewer` from `__init__.py`, and add the two missing test cases — then this is ready to merge.
