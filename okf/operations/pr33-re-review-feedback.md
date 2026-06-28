# Re-Review: PR #33 — Phase 1 Quality Gates
**Branch:** `ned/phase1-quality-gates`  
**Fix Commit:** `ec34d66b` (HEAD confirmed)  
**Reviewer:** Antigravity (Claude Sonnet 4.6 Thinking)  
**Date:** 2026-06-28

---

## Re-Review Verdict: APPROVE

---

## Evidence Summary

| Check | Result |
|---|---|
| `git log --oneline -3` | `ec34d66b` is HEAD ✅ |
| `pytest prismatic/quality/test_gates.py -v` | **54 passed in 0.11s** ✅ |
| Manual probe: `check_workdir(['prismatic/quality/../../etc/passwd'], 'prismatic/quality')` | `passed=False` ✅ |
| Manual probe: `check_drift(['prismatic/quality/../../etc/passwd'], 'prismatic/quality')` | `passed=False` ✅ |
| `__pycache__` side-effect probe | Not created ✅ |
| Filenames with spaces regex | `path with spaces/file.py` parses, `line_count=2` ✅ |
| `_safe_identifier('GRO-99/path/with/slashes')` | `'GRO-99_path_with_slashes'` ✅ |

---

## Previously-Flagged Issues

### Finding 1 — CRITICAL: `check_workdir` path traversal
**Status: FIXED**

Old code used `lstrip()` + `startswith()` — string comparison, not path-safe.  
New code (gates.py L160–180):
```python
workdir_path = Path(declared_workdir).resolve()
file_path = Path(f).resolve()
file_path.relative_to(workdir_path)  # raises ValueError if not relative
```
Manual probe confirmed: `check_workdir(['prismatic/quality/../../etc/passwd'], 'prismatic/quality')` → `passed=False`.  
Prefix-collision test (`docs_extra` vs `docs`) also caught. Regression test `test_path_traversal_in_workdir_fails` (L441) added and passes.

---

### Finding 2 — CRITICAL: `check_drift` same path traversal bug
**Status: FIXED**

Same `Path.resolve() + relative_to()` treatment applied to `check_drift` (gates.py L576–589).  
Manual probe: `check_drift(['prismatic/quality/../../etc/passwd'], 'prismatic/quality')` → `passed=False, reasons=['1 files outside workdir...']`.  
Regression test `test_path_traversal_in_drift_fails` (L473) passes.

---

### Finding 3 — MEDIUM: `test_verdict_persists_to_disk` was a false test
**Status: FIXED**

Test was rewritten (test_gates.py L408–425) to:
1. Call `save_verdict(verdict, base_dir=str(tmp_path))`
2. Assert `os.path.exists(path)`
3. Open the file and assert `data["identifier"] == "GRO-5"` and layer structure

The test now actually exercises the file-write path. Passes.

---

### Finding 4 — HIGH: `_count_lines_per_file` regex `\S+` → `.+`
**Status: FIXED**

Regex changed from `r"^diff --git a/(\S+) b/(\S+)$"` to `r"^diff --git a/(.+) b/(.+)$"` (gates.py L624).  
Manual probe with `diff --git a/path with spaces/file.py b/path with spaces/file.py`:
- Key `'path with spaces/file.py'` present in result dict
- `line_count = 2` (correctly counted `+y` and `+z`)

Regression test `test_count_lines_handles_filenames_with_spaces` (L503) passes.

---

### Finding 5 — MEDIUM: `py_compile.compile()` wrote `__pycache__/`
**Status: FIXED**

`check_basic_syntax` now uses in-memory `compile()` (gates.py L365–367):
```python
source = full_path.read_text(encoding="utf-8", errors="replace")
compile(source, str(full_path), "exec")
```
Manual probe: directory listing before/after `check_basic_syntax` call is identical — `__pycache__` not created.  
Regression test `test_check_basic_syntax_no_pycache_side_effect` (L485) passes.

---

### Finding 6 — MEDIUM: `check_files_changed` docstring said "5-50"
**Status: FIXED**

Docstring updated (gates.py L204–211):
```
Bounds enforced: 1 ≤ count ≤ MAX_FILES_CHANGED (50).
Zero files is rejected (agent did nothing).
More than MAX_FILES_CHANGED is rejected (likely drift).
Note: no minimum other than 1 — single-file edits are legitimate.
```
This accurately describes the implementation (`count == 0` → fail, `count > 50` → fail, else pass).

---

### Finding 7 — LOW: Dead comment-filter branch in `check_diff_meaningful`
**Status: FIXED**

The dead branch (`if stripped.startswith("#") and ...`) is removed (gates.py L256–267).  
A clear explanatory comment was added instead, explaining *why* the branch was dead:
```python
# Note: we intentionally skip the dead comment-filter branch — a diff line
# like '+# comment' starts with '+' (not '#') so the old filter never fired
# for added/removed lines, only for context lines which we don't count anyway.
```

---

### Finding 8 — LOW: `save_verdict`/`save_drift_report` identifier unsanitized
**Status: FIXED**

`_safe_identifier()` helper added (gates.py L720–726):
```python
def _safe_identifier(identifier: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_\-]", "_", identifier)
```
Both `save_verdict` (L739) and `save_drift_report` (L759) now call `_safe_identifier(verdict.identifier)` before constructing the filename.  
Regression test `test_save_verdict_sanitizes_identifier` (L427) passes.  
`'GRO-99/path/with/slashes'` → `'GRO-99_path_with_slashes'` confirmed.

---

### Finding 9 — LOW: Integration hooks deferred — PR description should note this
**Status: FIXED**

PR description contains an explicit "Honest caveats" section (confirmed via GitHub API):
```
1. linked_pr_ok layer not fully wired (passes pr_check_fn=None); Phase 2 will inject GitHub API
2. goal_match is keyword matching, not semantic similarity
3. No retry on Verdict FAIL — Phase 2 (Gap 7)
4. Old agy_self_review.py / prismatic_self_review.py not yet removed
```
Caveats are honest, scoped, and already in the original PR body. ✅

---

## New Issues Found

**None blocking.** One minor observation:

**Minor — `check_workdir` fallback path for non-existent files:** The two-step resolve for non-existent files (`os.path.normpath(f)` then `.resolve()`) is correct but slightly redundant since `Path.resolve()` already handles normpath internally. This is style-only; logic is sound and probes confirm the traversal is blocked in both existent and non-existent file paths.

---

## Recommendation

All 9 findings from the previous REQUEST_CHANGES verdict have been addressed correctly and completely in commit `ec34d66b`. The two CRITICAL path-traversal security bugs are closed with proper `Path.resolve() + relative_to()` semantics — both confirmed by live probes, not just tests. The 5 new regression tests (49 → 54) are real, assertive tests with disk-level and IO-level verification; none are false coverage. The dead code is cleaned up with explanatory commentary rather than silent deletion. The docstring now matches the implementation. The identifier sanitizer correctly handles edge cases. All 54 tests pass in 0.11s. **Approve and merge.**
