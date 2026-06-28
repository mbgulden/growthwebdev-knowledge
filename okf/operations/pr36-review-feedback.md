# PR #36 Review — Gap 5 Smoke Test Layer
**Branch:** `ned/phase2-smoke-test`  
**Files reviewed:** `prismatic/quality/smoke.py` · `prismatic/quality/test_smoke.py`  
**Reviewer:** AGY (agy-as-reviewer lane)  
**Date:** 2026-06-28

---

## Review Verdict: REQUEST_CHANGES

**One medium-severity bug (false positive) and two low-severity design gaps. No blockers.**

---

## Evidence Reviewed

| Item | Result |
|---|---|
| `pytest prismatic/quality/test_smoke.py -v` | ✅ 36/36 passed (0.09 s) |
| Regex DoS (10K-char adversarial inputs ×4) | ✅ All < 2 ms — no ReDoS risk |
| Path traversal: leading `../`, `./../../`, mid-path `..`, multiple `..` | ✅ All detected |
| Path traversal: URL-encoded `%2f..%2f` | ⚠️ Not detected — expected/acceptable |
| Binary detection: null-byte threshold boundary | ⚠️ Off-by-one at exactly 1% nulls |
| Binary detection: ELF, UTF-16, latin-1 | ✅ All correctly detected as binary |
| Claim regex on real `/tmp/antigravity_*.log` files | ⚠️ Logs are launcher metadata only — not agent narrative (design gap) |
| Claim regex on real `result.md` agent output | ✅ Correctly captures backtick paths and `path:` format |
| Git commit hash false-positive from backtick pattern | ❌ Medium — `6c6ee9526...` extracted as claimed path |

---

## Findings

### 🔴 MEDIUM — Git commit hash extracted as claimed path (false positive)

**File:** `smoke.py` lines 97–99 (backtick pattern)  
**Pattern:** `` r"`((?:\.{0,2}/)?[\w./-]+)`" ``

Real agent `result.md` files contain:
```
## Commit Hash
`6c6ee9526c25862c9ad49101736cdd4fba3001ea`
```
The backtick regex captures this 40-char hex string as a claimed path. `file_exists` then misses it on disk and the smoke test **incorrectly FAILs** a legitimate, verified agent output.

**Impact:** Every agent that reports a commit SHA in backticks produces a spurious `missing` finding.

**Fix:**
```python
# In extract_claimed_paths, after the len < 4 check:
if re.match(r'^[0-9a-f]{20,}$', path):
    continue
```

**Test gap:** No test covers a commit-hash backtick edge case.

---

### 🟡 LOW — Binary detection off-by-one at exactly 1% null bytes

**File:** `smoke.py` line 190
```python
if size > 0 and null_count / size > 0.01:
```
At **exactly** 1% nulls (e.g. 1 null in 100 bytes), `> 0.01` is `False`, so the file enters the UTF-8 decode path. In practice this causes a silent text-decode on a boundary-binary file.

**Fix:** Change `> 0.01` to `>= 0.01`.

**Test gap:** `test_binary_file` uses 25% nulls. No boundary test at 1% exists.

---

### 🟡 LOW — Claim regex not wired to the correct input surface

**Probe finding:** All 25 `/tmp/antigravity_*.log` files are launcher metadata only:
```
[launcher] AGY exited after 100s
[launcher] copied: .../result.md -> /tmp/agy-dispatch-GRO-2202-result.md
```
Zero claim patterns match. The **actual agent narrative lives in `result.md`** (brain directory), not in `.log` files. Confirmed: feeding a real `result.md` to `extract_claimed_paths` correctly yields 5 matched paths.

**Implication:** If callers feed `.log` files, every run vacuous-passes silently. The PR has no docstring or README note naming the correct input surface.

**Fix required:** Add to `smoke_test()` docstring:
> The `agent_output` argument must be the agent's narrative summary (e.g. `result.md`), NOT the launcher's `.log` file, which contains only process metadata.

---

## Strengths

- **36/36 tests, 0.09 s** — fast and non-flaky.
- **No ReDoS risk.** All four CLAIM_PATTERNS are linear-time; 10K-char adversarial inputs complete in < 2 ms.
- **Path traversal end-to-end solid:** `../`, `./../../`, `foo/../../../etc/passwd`, multiple mid-path `..` — all correctly extracted *and* flagged through the full `smoke_test()` call chain.
- **Binary detection works for all practical cases:** ELF, UTF-16 (null-heavy), latin-1 non-UTF8 — all correctly identified as binary, all return `has_content=True`.
- **`to_dict()` / `to_markdown()` serialisation is clean** and tested.
- **Vacuous-pass handling** is explicit and reason string is readable.

---

## Required Fixes Before Merge

1. **[MEDIUM]** Add hex-string guard in `extract_claimed_paths` to skip git commit hashes. Add regression test.
2. **[LOW]** Change `> 0.01` → `>= 0.01` in null-byte threshold. Add boundary test at exactly 1%.
3. **[LOW]** Add docstring note to `smoke_test()` naming `result.md` (not `.log`) as the intended input.

---

## Re-review Checklist

- [ ] `re.match(r'^[0-9a-f]{20,}$', path)` guard added and tested
- [ ] Null-byte threshold is `>= 0.01`; boundary test at 1% added
- [ ] `smoke_test()` docstring explicitly names `result.md` as correct input surface
- [ ] `pytest` still 36/36 (or more) after fixes
- [ ] No new test gaps introduced
