# PR #33 — Phase 1 Quality Gates: Code Review

**Branch**: `ned/phase1-quality-gates`
**Files reviewed**: `prismatic/quality/__init__.py`, `prismatic/quality/gates.py` (714 lines), `prismatic/quality/test_gates.py` (528 lines, 49 tests)
**Test run**: `49 passed in 0.16s` ✅
**Reviewer**: AGY (agy-as-reviewer lane)
**Date**: 2026-06-28

---

## Review Verdict: REQUEST_CHANGES

The foundations are good — the layered architecture is clean, `VerificationVerdict` is ergonomic, the API surface is well-curated, and all 49 tests pass. However, **two security bugs** and **one misleading test** are production blockers that must be fixed before merge.

---

### Strengths

- **Architecture is correct.** Splitting `agent:needs-human-review` into `task:shape-violation` + `output:requires-verification` with explicit SLA hours (24h vs 12h) is the right model. `ShapeRouter` is self-documenting.
- **Dependency injection done right.** `check_linked_pr`'s `pr_check_fn: Callable | None` makes the layer testable without mocking network I/O. Mature API design.
- **`VerificationVerdict.to_markdown()` is production-ready.** The Linear-comment format is immediately usable. Fail reasons cascade correctly through `failed_layers`.
- **`__init__.py` re-exports are explicit and well-structured.** `__all__` is correctly maintained. Individual layer functions exposed for unit testing is a good ergonomic choice.
- **No ReDoS risk.** All 7 regex patterns in `SHAPE_VIOLATION_PATTERNS` and `route_nhr_task` run in sub-millisecond time on adversarial 5000-character inputs.
- **Performance is acceptable.** A 50MB git diff processes in ~70ms. A 50k-word task body in `check_goal_match` takes ~18ms. No O(n²) patterns detected.
- **`check_basic_syntax` gracefully degrades.** Missing PyYAML is caught and skipped. Deleted files are skipped correctly.

---

### Issues Found

#### CRITICAL — Path traversal bypasses workdir enforcement in `check_workdir` and `check_drift`

**File**: `gates.py` lines 158–164, 547–550. **Confirmed by probe.**

```python
# gates.py L160-163
normalized = f.lstrip("./")
if not normalized.startswith(workdir):
    if not normalized.startswith(workdir.lstrip("./")):
        out_of_workdir.append(f)
```

`lstrip("./")` does NOT resolve `..` components. A path like `prismatic/quality/../../etc/passwd` after `lstrip("./")` is still `prismatic/quality/../../etc/passwd`, which passes `startswith("prismatic/quality")`.

**Reproduction**:
```
check_workdir(['prismatic/quality/../../etc/passwd'], 'prismatic/quality')
→ passed=True   # BUG: should be False
```

**Fix** — use `Path.relative_to` after `os.path.normpath`:
```python
def _is_within(filepath: str, workdir: str) -> bool:
    norm_file = Path(os.path.normpath(filepath))
    norm_work = Path(os.path.normpath(workdir))
    try:
        norm_file.relative_to(norm_work)
        return True
    except ValueError:
        return False
```

The identical bug exists in `check_drift` (line 549).

---

#### CRITICAL — Prefix collision: `check_workdir` and `check_drift` treat `docs_extra/` as inside `docs/`

**File**: `gates.py` lines 161, 163, 549. **Confirmed by probe.**

```
check_workdir(['docs_extra/bad.py'], 'docs')
→ passed=True   # BUG: should be False
```

`"docs_extra/bad.py".startswith("docs")` is `True`. The `Path.relative_to` fix above also resolves this — `docs_extra` is not relative to `docs`.

---

#### HIGH — `test_verdict_persists_to_disk` does not test disk persistence

**File**: `test_gates.py` lines 403–411

```python
def test_verdict_persists_to_disk(self, tmp_path):
    verdict = VerificationVerdict(...)
    path = verdict.to_dict()        # calls to_dict(), NOT save_verdict()
    assert path["passed"] is True   # path is a dict, not a filepath
```

`save_verdict()` has **zero test coverage**. A filesystem error (permissions, disk full, `/` in identifier) would not be caught in CI.

**Fix**: rename to `test_verdict_to_dict_schema` and add a real `test_verdict_save_to_disk` that calls `save_verdict(verdict, base_dir=str(tmp_path))` and asserts the file exists with valid JSON.

---

#### HIGH — `_count_lines_per_file` silently drops filenames with spaces

**File**: `gates.py` line 584

```python
m = re.match(r"^diff --git a/(\S+) b/\S+", line)
```

`\S+` matches non-whitespace only. Files with spaces in paths (e.g., plugin paths) are silently skipped — `oversized_files` is always empty for such repos.

**Fix**:
```python
m = re.match(r"^diff --git a/(.+) b/.+$", line)
```

---

#### MEDIUM — `check_basic_syntax` has a write side-effect: `py_compile.compile()` creates `__pycache__`

**File**: `gates.py` line 343

`py_compile.compile(str(full_path), doraise=True)` without a `cfile` argument writes a `.pyc` into `__pycache__/` adjacent to the file. In a read-only or sandboxed environment this will either fail or pollute the filesystem.

**Fix** — use in-memory compile:
```python
source = full_path.read_text()
compile(source, str(full_path), "exec")   # raises SyntaxError, no file writes
```

---

#### MEDIUM — Docstring/implementation mismatch in `check_files_changed`

**File**: `gates.py` line 189

Docstring says **"(5-50)"** but the code only enforces `> 0` and `<= 50`. No lower bound of 5 is applied. Either enforce a minimum or fix the docstring — documentation lies mislead future contributors.

---

#### LOW — `check_diff_meaningful` comment-filtering logic is dead code for diff lines

**File**: `gates.py` lines 242–243

After `.strip()`, a diff addition line `+# comment` starts with `+`, not `#`, so the comment-exclusion branch never fires for `+`/`-` lines. It only triggers on context lines, which are never counted. Harmless but dead — remove or document it.

---

#### LOW — Integration hooks not wired; `prismatic.quality` is an island

`quality_gate.py` and `agent_dispatcher.py` do not exist in this PR. No production code calls `run_verification()`, `check_drift()`, or `route_nhr_task()`. Acceptable for Phase 1 scaffolding — but the PR description should explicitly state "integration deferred to Phase 2".

---

#### LOW — `save_verdict` / `save_drift_report`: identifier used unsanitized in filename

**File**: `gates.py` lines 689, 708

An identifier containing `/` causes a `FileNotFoundError`. Linear IDs are `GRO-123` and safe in practice, but harden with:

```python
safe_id = re.sub(r"[^a-zA-Z0-9_\-]", "_", identifier)
filename = f"verdict_{safe_id}_{timestamp}.json"
```

---

### Test Coverage Assessment

| Layer | Tests | Coverage Gaps |
|---|---|---|
| `check_shape` | 6 | Empty `agent_output`; violations in task body not agent output |
| `check_workdir` | 4 | **MISSING: `../` traversal, prefix collision** |
| `check_files_changed` | 4 | Docstring mismatch (1-file vs claimed 5-file minimum) |
| `check_diff_meaningful` | 3 | Comment-only diff passes (dead filter) |
| `check_linked_pr` | 4 | Good |
| `check_basic_syntax` | 6 | `__pycache__` side-effect; YAML test |
| `check_goal_match` | 5 | Adversarial high-overlap with irrelevant content |
| `run_verification` | 5 | `test_verdict_persists_to_disk` is a **false test** |
| `check_drift` | 6 | **MISSING: `../` traversal, prefix collision** |
| `route_nhr_task` | 5 | Good |

The two workdir/drift security bugs have **zero regression tests** — they are the highest-priority additions.

---

### Required Fixes Before Merge

1. **Fix `check_workdir` and `check_drift` path normalization** — use `Path.relative_to(Path(os.path.normpath(workdir)))`. Add regression tests for `../` and `workdir_extra/` prefix collision.
2. **Fix `test_verdict_persists_to_disk`** — rename and add a real `save_verdict()` disk test.
3. **Fix `py_compile.compile()` side-effect** — use in-memory `compile(source, filename, "exec")`.

### Recommended (not blocking)

4. Fix `_count_lines_per_file` regex to handle filenames with spaces.
5. Sanitize `identifier` in `save_verdict` / `save_drift_report` filenames.
6. Align `check_files_changed` docstring with implementation.
7. Remove dead comment-filtering branch in `check_diff_meaningful`.
8. Add note to PR description that integration hooks are deferred to Phase 2.

---

### Re-Review Checklist

- [ ] `check_workdir(['a/b/../../etc/passwd'], 'a/b')` returns `passed=False`
- [ ] `check_workdir(['docs_extra/x.py'], 'docs')` returns `passed=False`
- [ ] `check_drift(['a/b/../../etc/passwd'], 'a/b')` returns `passed=False`
- [ ] `test_verdict_persists_to_disk` calls `save_verdict()` and asserts file on disk
- [ ] `check_basic_syntax` does not create `__pycache__` directories
- [ ] All 3 required fixes have regression tests
