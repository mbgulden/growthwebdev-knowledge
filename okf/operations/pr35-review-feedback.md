# PR #35 Review — Phase 2 / Gap 7: Failure Classification with Smart Retry

**Branch:** `ned/phase2-failure-classification`  
**Files reviewed:** [`failure.py`](file:///home/ubuntu/work/prismatic-engine/prismatic/quality/failure.py), [`test_failure.py`](file:///home/ubuntu/work/prismatic-engine/prismatic/quality/test_failure.py)  
**Tests run:** 44/44 ✅ passing  
**Evidence:** Live ReDoS probe, edge-case harness, false-positive analysis, POLICIES audit

---

## Review Verdict: REQUEST_CHANGES

Two bugs need fixing before merge: a docstring that lies about `reset_after_success` behavior, and the `TRANSIENT`/`RATE_LIMIT` exhaustion label that re-queues rather than escalates. Everything else is medium-or-lower and can be addressed as follow-on issues.

---

## Strengths

- **Correct retry semantics for 5 of 5 modes.** SHAPE_VIOLATION and IMPOSSIBLE correctly set `max_attempts=0`; the `should_retry = attempt < max_attempts` guard works cleanly across the attempt spectrum, including `attempt_count=999999` (correctly returns `False`).
- **Pattern ordering discipline.** RATE_LIMIT → SHAPE_VIOLATION → IMPOSSIBLE → LOGIC_ERROR → TRANSIENT matches the right precedence: critical non-retryable signals win before broad transient defaults. The `test_first_pattern_match_wins` test validates this.
- **Fault-tolerant Linear integration.** Bare `except Exception: pass` inside `apply_failure_classification` is justified here — Linear API failures must never block classification. Confirmed by `test_linear_error_does_not_block`.
- **Counter corruption recovery.** `_load_counter` silently returns `{}` on `JSONDecodeError`/`OSError`. `test_corrupted_counter_file_recovers` covers it.
- **No ReDoS.** All 14 patterns probed with adversarial 10K-char inputs (no quantifier nesting, no catastrophic backtracking). Worst-case probe completed under 5ms per pattern.
- **`fail_open` / `fail_closed` toggle is well-designed.** The dual-mode `classify_with_policy` is a good API for callers with different risk tolerances.
- **`to_dict()` on ClassificationResult and RetryPolicy** — correct JSON serialisability for Linear comment payloads.

---

## Issues Found

### 🔴 HIGH — `TRANSIENT`/`RATE_LIMIT` exhaustion escalates to `dispatch:ready` (re-queue loop risk)

**File:** [`failure.py:73-74`](file:///home/ubuntu/work/prismatic-engine/prismatic/quality/failure.py#L73-L74)

```python
FailureMode.TRANSIENT:  RetryPolicy(max_attempts=3, backoff_seconds=5.0,  escalate_to="dispatch:ready"),
FailureMode.RATE_LIMIT: RetryPolicy(max_attempts=5, backoff_seconds=60.0, escalate_to="dispatch:ready"),
```

`dispatch:ready` is the **work-queue pickup label** — applying it when retries are exhausted will cause an agent to pick up the task again immediately, creating an infinite retry loop. There is no label-removal step before re-applying `dispatch:ready`, and no loop-break mechanism.

**Expected behaviour:** transient exhaustion should escalate to something like `output:requires-attention` or `agent:fred`, not re-enqueue. Rate-limit exhaustion might reasonably re-queue, but only with a separate cooldown mechanism not present here.

**Severity:** High — this is a correctness bug in the escalation path that can cause unbounded agent loops in production.

**Fix:** Change `escalate_to` for both modes to a human-review label, or add a loop-guard before re-adding `dispatch:ready`.

---

### 🔴 HIGH — `reset_after_success` docstring lies about label cleanup

**File:** [`failure.py:279-285`](file:///home/ubuntu/work/prismatic-engine/prismatic/quality/failure.py#L279-L285)

```python
def reset_after_success(issue_id: str, linear_api_fn: Any | None = None) -> None:
    """Reset failure counter after a task succeeds.

    Also clears the escalate_to label if it was applied during retries.
    """
    reset_failure(issue_id)
    # Note: Linear label cleanup is the caller's responsibility
```

The docstring says it **clears the escalate_to label**. The implementation does **not** — it only resets the counter. The inline comment contradicts the docstring. `linear_api_fn` is accepted but never used.

This is a documentation bug that will cause callers to rely on cleanup that doesn't happen, leaving stale `task:shape-violation` or `output:requires-attention` labels on tasks that subsequently succeeded.

**Severity:** High — silent correctness failure for any caller trusting the documented contract.

**Fix:** Either implement label removal (call `linear_api_fn` to remove the label) or remove the false claim from the docstring and drop the unused `linear_api_fn` parameter.

---

### 🟡 MEDIUM — `FileNotFoundError: No such file or directory` (POSIX standard error) is a false negative

**File:** [`failure.py:44`](file:///home/ubuntu/work/prismatic-engine/prismatic/quality/failure.py#L44)

```python
(r"does not exist|no such file.*cannot", FailureMode.IMPOSSIBLE, "missing_dependency"),
```

The pattern `no such file.*cannot` requires **both** `no such file` and `cannot` in the same line. The canonical POSIX message `No such file or directory` (Python's `FileNotFoundError`, shell commands, etc.) does **not** contain `cannot` and therefore **does not match**.

```
FileNotFoundError: [Errno 2] No such file or directory: '/path/to/file'
→ mode=TRANSIENT (falls through — wrong!)
```

**Severity:** Medium — common real-world errors mis-classified as transient and retried 3×.

**Fix:** Split into `does not exist|no such file or directory`.

---

### 🟡 MEDIUM — `retry` in `transient_signal` pattern has no word boundary

**File:** [`failure.py:56`](file:///home/ubuntu/work/prismatic-engine/prismatic/quality/failure.py#L56)

```python
(r"temporary failure|try again|retry", FailureMode.TRANSIENT, "transient_signal"),
```

The bare `retry` matches **any** substring: `retry_handler()`, `should_retry()`, `retrying...`, `don't retry`, and function names in agent code/logs. Agent logs frequently contain the word `retry` as Python identifiers.

**Example false positive confirmed:**
```
'Calling retry_handler() with exponential backoff'  → TRANSIENT (wrong)
'please retry after fixing shape'                   → TRANSIENT (wrong, if no shape pattern above)
```

**Severity:** Medium — false positives cause unnecessary retries of logs that contain the word `retry` in non-error context.

**Fix:** Use `\bretry\b` and `\btry again\b`, or tighten to `please retry|retry in \d|retry after`.

---

### 🟡 MEDIUM — `wait_for_retry` blocks the caller thread for up to 60 seconds

**File:** [`failure.py:303-315`](file:///home/ubuntu/work/prismatic-engine/prismatic/quality/failure.py#L303-L315)

```python
def wait_for_retry(error_log: str, attempt_count: int = 0) -> bool:
    should, mode, backoff = should_retry(error_log, attempt_count)
    if should and backoff > 0:
        time.sleep(backoff)   # ← blocks for RATE_LIMIT.backoff_seconds = 60s
    return should
```

This is a synchronous `time.sleep(60)` on the caller's thread. No cap, no interruptibility. In async orchestration contexts, this will deadlock or starve other tasks.

**Severity:** Medium — acceptable only if callers are always in a dedicated thread. Should be documented explicitly, or offer an async variant / accept a `max_sleep` cap parameter.

---

### 🟡 MEDIUM — `None` error log silently treated as empty (no type guard)

**File:** [`failure.py:114`](file:///home/ubuntu/work/prismatic-engine/prismatic/quality/failure.py#L114)

```python
if not error_log:
```

`not None` is `True`, so `None` passes as an empty log. No `TypeError` is raised. The type annotation says `str` but the function silently accepts `None`. In Python 3.12+ with strict type checking this would be caught statically, but at runtime it's silent.

**Severity:** Medium — masks caller bugs. Add `if not isinstance(error_log, str): raise TypeError(...)` or change the guard to `if not error_log or not isinstance(error_log, str)`.

---

### 🟡 MEDIUM — No log length cap; 10MB+ logs will scan for seconds

**File:** [`failure.py:128-140`](file:///home/ubuntu/work/prismatic-engine/prismatic/quality/failure.py#L128-L140)

Measured: ~190ms for a 400KB log (14 patterns × full scan). At 10MB that's ~4.7 seconds; at 100MB, ~47 seconds. Agent transcripts can be large.

**Severity:** Medium — no denial-of-service risk (this is internal), but latency spike is real. Fix: truncate `error_log` to last N characters (e.g., `error_log = error_log[-16_384:]`) before pattern matching — failure signals are almost always in the last few lines.

---

### 🟡 MEDIUM — `/tmp/failure_counter.json` has TOCTOU race; no file locking

**File:** [`failure.py:193-208`](file:///home/ubuntu/work/prismatic-engine/prismatic/quality/failure.py#L193-L208)

`_load_counter()` reads the file, `_save_counter()` writes it, with no exclusive lock between them. Two agents calling `increment_failure("GRO-1")` concurrently can both read `count=1`, both write `count=2`, dropping one increment.

**Severity:** Medium — real-world impact depends on how many concurrent agents share the host. Fix: use `fcntl.flock` or replace with a counter stored per-agent directory.

---

### 🟡 MEDIUM — `permission denied` pattern matches test descriptions (false positive)

**File:** [`failure.py:43`](file:///home/ubuntu/work/prismatic-engine/prismatic/quality/failure.py#L43)

```python
(r"permission denied|EACCES|EPERM|access denied", FailureMode.IMPOSSIBLE, "permission_denied"),
```

Confirmed false positive:
```
'Test: operation should return permission denied error'  → IMPOSSIBLE (wrong)
```

Agent test output often describes expected error behaviour. This incorrectly classifies a successful test run as IMPOSSIBLE.

**Severity:** Medium — add anchoring or require the error to appear at the start of a line: `r"^.*(?:permission denied|EACCES|EPERM|access denied)"` or pair with context like excluding lines starting with `Test:`.

---

### 🔵 LOW — Test count mismatch: 44 tests collected, PR description says 44 (Gap 7) + 54 (Phase 1) = 98 total

PR description claims 98 tests. The suite collects 44. Phase 1 tests presumably live in `test_gates.py`. The PR description should clarify this — reviewers may wonder if 54 tests are missing.

**Severity:** Low — cosmetic but worth correcting in the PR description.

---

### 🔵 LOW — `attempt` field in `ClassificationResult` stores input `attempt_count`, not "next attempt" number

**File:** [`failure.py:88`](file:///home/ubuntu/work/prismatic-engine/prismatic/quality/failure.py#L88)

The field is named `attempt` but contains the zero-indexed count passed in by the caller. The `to_dict()` output will show `"attempt": 0` on first failure, which could confuse consumers expecting 1-indexed attempts. Rename to `attempt_count` to match the parameter name, or document the 0-index convention.

**Severity:** Low — API readability issue.

---

### 🔵 LOW — `LOGIC_ERROR` `escalate_to="agent:fred"` is a hardcoded human name

**File:** [`failure.py:76`](file:///home/ubuntu/work/prismatic-engine/prismatic/quality/failure.py#L76)

```python
FailureMode.LOGIC_ERROR: RetryPolicy(max_attempts=1, backoff_seconds=30.0, escalate_to="agent:fred"),
```

Escalation to a specific person baked into library code will break when the responsible engineer changes. Should be a constant or config value.

**Severity:** Low — hardcoding a person's name in foundation code is poor practice.

---

## Test Coverage Assessment

**Good coverage:** enum completeness, POLICIES table, retry decision logic (within/at/beyond budget), fail-open/fail-closed, counter CRUD, Linear integration (escalation, no-escalation, error resilience), convenience helpers.

**Gaps:**

| Missing test | Risk |
|---|---|
| `None` passed as `error_log` | Medium — no `TypeError` raised; untested silent behaviour |
| `"No such file or directory"` (POSIX) classified | Medium — confirmed false negative, no test catches it |
| `retry_with_backoff()` (function name) in log → false positive TRANSIENT | Medium |
| 10MB+ log performance | Low |
| Concurrent `increment_failure` (race) | Low |
| `reset_after_success` with `linear_api_fn` (never calls it) | High — documents behaviour that doesn't exist |

---

## Required Fixes Before Merge

1. **Fix `TRANSIENT`/`RATE_LIMIT` `escalate_to`** — must not re-add `dispatch:ready` on exhaustion.
2. **Fix `reset_after_success` docstring** — remove the false claim about label cleanup, or implement it.

## Recommended Follow-Ons (non-blocking)

3. Fix `no such file.*cannot` → `no such file or directory` to catch POSIX errors.
4. Add word boundary to `retry` in `transient_signal` pattern.
5. Truncate `error_log` to last 16KB before pattern matching.
6. Add `isinstance(error_log, str)` guard with `TypeError`.
7. Add `fcntl.flock` to `_save_counter` for concurrent-agent safety.
8. Extract `"agent:fred"` to a named constant or config.

---

## Re-Review Checklist

- [ ] `TRANSIENT.escalate_to` changed to a non-re-queue label
- [ ] `RATE_LIMIT.escalate_to` reconsidered (re-queue or human escalation?)
- [ ] `reset_after_success` docstring matches implementation
- [ ] Test added for `reset_after_success` with `linear_api_fn` to confirm no label cleanup
- [ ] Test added for `None` error_log input
- [ ] Test added for `FileNotFoundError: No such file or directory` (POSIX)
- [ ] All 44 tests still pass
