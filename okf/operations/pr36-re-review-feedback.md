# Re-Review: PR #36 — Gap 5 Smoke Test
**Branch**: `ned/phase2-smoke-test`  
**Tip commit**: `f7780fdc` — "Address PR #36 review findings (Gap 5 smoke test)"  
**Date**: 2026-06-28  
**Reviewer**: AGY (automated re-review)

---

## Re-Review Verdict: APPROVE ✅

All three previously-flagged issues are resolved. All 40 tests pass.

---

## Issue-by-Issue Confirmation

### 1. MEDIUM (commit f7780fdc) — Git SHA false-positive ✅ FIXED

**Test run:**
```
python3 -c "from prismatic.quality.smoke import extract_claimed_paths; \
  print(extract_claimed_paths('Committed at \`6c6ee9526abc123def456789012345678901234\`'))"
```

**Result:** `[]`

The 40-hex-character SHA is now correctly filtered out. `extract_claimed_paths` returns an empty list, so no spurious MISSING findings will fire on commit hash mentions in agent output.

Also confirmed by the dedicated regression test:
```
prismatic/quality/test_smoke.py::TestExtractClaimedPaths::test_git_sha_filtered_out  PASSED
prismatic/quality/test_smoke.py::TestExtractClaimedPaths::test_short_hex_not_filtered PASSED
```
Short hex strings (< 40 chars) are correctly **not** filtered — the fix is appropriately scoped.

---

### 2. LOW — Binary off-by-one: exactly 1% null bytes → binary ✅ FIXED

**Test run:**
```
python3 -m pytest prismatic/quality/test_smoke.py::TestBinaryDetectionBoundary -v
```

**Result:**
```
TestBinaryDetectionBoundary::test_exactly_1_percent_nulls_is_binary   PASSED
TestBinaryDetectionBoundary::test_just_under_1_percent_is_text        PASSED
```

The boundary is now `>= 1%` (closed interval). A file at exactly the threshold is classified as binary; a file fractionally below is text. Both boundary conditions are covered by dedicated tests.

---

### 3. LOW — `smoke_test()` docstring mentions launcher log caveat ✅ FIXED

**Docstring (abridged):**
```
Args:
    agent_output: The agent's narrative output ("I created X...")
                   NOTE: This should be the agent's RESULT/WALKTHROUGH section,
                   not the launcher log file. Launcher logs contain only
                   `[launcher] ...` metadata, which produces vacuous passes.
                   See okf/operations/pr36-review-feedback.md for details.
```

The caveat is present, clear, and references the ops feedback doc. ✅

---

## Full Test Suite

```
python3 -m pytest prismatic/quality/test_smoke.py
```

```
collected 40 items

TestExtractClaimedPaths::test_creates_claim                PASSED
TestExtractClaimedPaths::test_wrote_claim                  PASSED
TestExtractClaimedPaths::test_modified_claim               PASSED
TestExtractClaimedPaths::test_backtick_path                PASSED
TestExtractClaimedPaths::test_file_colon_format            PASSED
TestExtractClaimedPaths::test_absolute_path                PASSED
TestExtractClaimedPaths::test_no_claims_returns_empty      PASSED
TestExtractClaimedPaths::test_empty_output                 PASSED
TestExtractClaimedPaths::test_urls_filtered_out            PASSED
TestExtractClaimedPaths::test_version_strings_filtered     PASSED
TestExtractClaimedPaths::test_deduplicates                 PASSED
TestExtractClaimedPaths::test_git_sha_filtered_out         PASSED  ← new regression
TestExtractClaimedPaths::test_short_hex_not_filtered       PASSED  ← new regression
TestBinaryDetectionBoundary::test_exactly_1_percent_nulls_is_binary  PASSED  ← new regression
TestBinaryDetectionBoundary::test_just_under_1_percent_is_text       PASSED
TestPathTraversal::test_clean_path_passes                  PASSED
TestPathTraversal::test_traversal_with_dotdot_slash        PASSED
TestPathTraversal::test_traversal_with_dotdot_backslash    PASSED
TestPathTraversal::test_relative_dotdot_passes             PASSED
TestFileExists::test_existing_file                         PASSED
TestFileExists::test_missing_file                          PASSED
TestFileExists::test_relative_path_against_workdir         PASSED
TestFileExists::test_directory_not_file                    PASSED
TestFileHasSubstantiveContent::test_substantive_file       PASSED
TestFileHasSubstantiveContent::test_empty_file             PASSED
TestFileHasSubstantiveContent::test_whitespace_only_file   PASSED
TestFileHasSubstantiveContent::test_comments_only_file     PASSED
TestFileHasSubstantiveContent::test_binary_file            PASSED
TestFileHasSubstantiveContent::test_missing_file           PASSED
TestSmokeTest::test_lie_detection                          PASSED
TestSmokeTest::test_empty_file_caught                      PASSED
TestSmokeTest::test_legitimate_output_passes               PASSED
TestSmokeTest::test_no_claims_is_vacuous_pass              PASSED
TestSmokeTest::test_empty_output                           PASSED
TestSmokeTest::test_path_traversal_caught                  PASSED
TestSmokeTest::test_multiple_claims_mixed_verdict          PASSED
TestSmokeTest::test_suspiciously_small_file                PASSED
TestOutputFormats::test_to_dict                            PASSED
TestOutputFormats::test_to_markdown_pass                   PASSED
TestOutputFormats::test_to_markdown_fail                   PASSED

============================== 40 passed in 0.10s ==============================
```

**40/40 PASSED. Zero failures, zero errors.**

New regression tests added: 3 (`test_git_sha_filtered_out`, `test_short_hex_not_filtered`, `test_exactly_1_percent_nulls_is_binary`).

---

## Summary

| # | Severity | Issue | Status |
|---|----------|-------|--------|
| 1 | MEDIUM | Git SHA false-positive in `extract_claimed_paths` | ✅ Fixed + regressed |
| 2 | LOW | Binary detection off-by-one at exactly 1% null bytes | ✅ Fixed + regressed |
| 3 | LOW | `smoke_test()` docstring missing launcher log caveat | ✅ Fixed |

No new issues found. PR is ready to merge.
