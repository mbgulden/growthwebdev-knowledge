# Journal-tail repair after revoked clean verdicts

Use this reference when reviewing or coordinating Prismatic journal/log-tail repairs where previous `CLEAN` verdicts were revoked by async reviewers.

## Durable lesson

A focused test pass and a George adversarial pass can still miss byte-tail compatibility regressions. Treat every new repair commit as a fresh exact-head candidate; prior review/CI is invalidated by any new candidate head.

## Edge classes that caught real defects

1. **Only unterminated content**
   - `b"unterminated"` and multibyte-only unterminated payloads must return no complete line.
   - Do not let a tail helper fabricate a complete record from a file with no newline.
2. **Malformed UTF-8 inside the selected window**
   - Candidate must not let one malformed byte hide later/earlier valid complete lines.
   - Preserve base-compatible tolerant decoding behavior: malformed bytes are dropped/replaced at byte granularity while valid complete lines remain visible.
   - Explicitly probe both orders:
     - `b"bad\xff\nvalid\n"`
     - `b"valid\nbad\xff\n"`
3. **Boundary slicing and partial-tail window expansion**
   - Complete-line suffix under budget.
   - Leading partial line exclusion.
   - Trailing partial line exclusion.
   - Partial-tail byte-window expansion: if the trailing unterminated record exactly fills or exceeds the initial byte window (for example `data=b"ok\n" + b"x"*(limit*4)` or malformed `b"\xff"*(limit*4)`), strip the tail and expand backward so earlier complete records that fit the decoded-character budget remain visible.
   - Tail longer than the initial window, empty complete LF records before a partial tail, multiple complete records before a long tail, and multibyte complete records before ASCII/malformed tails.
   - Oversized newest complete line returns no truncated fake line and must not be skipped for older records unless the product contract says otherwise.
   - Byte window beginning inside a multibyte sequence.
   - Decoded-character budget vs raw-byte budget.
   - Empty, zero, negative, tiny, exact-size budgets.
   - CRLF preservation.
4. **Timestamp freshness**
   - `Z`, naive UTC, and numeric offset timestamps.
   - Exact lower/upper cutoffs plus just-outside cases.
   - Freeze/inject `now` and assert only one `now` read where freshness semantics require a stable window.
5. **Git wrapper behavior**
   - Successful stdout only.
   - Successful stderr is suppressed when stdout exists or empty output is valid.
   - Failed command and exceptions preserve prior public behavior.

## Review workflow

1. Reproduce the async reviewer’s blocker on the exact old head before accepting it.
2. Compare against exact base behavior with an isolated module loader when compatibility is the claim. If base also fails but the current task contract requires the behavior, do **not** downgrade the finding to noise; classify it as an unclosed target requirement and repair the same task.
3. Revoke the prior `CLEAN` verdict and hold any PR at its old remote head; do not fast-forward until a new exact-head review is clean.
4. Dispatch a same-task repair only; no successor admission, no merge/deploy/Linear side effects.
5. Preserve the new candidate with a local ref and bundle before review.
6. Run source containment checks:
   - clean exact head;
   - path allowlist;
   - symbol/signature unchanged;
   - AST changes only in target functions;
   - byte-identical source outside target functions.
7. Run deterministic property/randomized byte-tail probes after hand-written edge probes. Search for crashes, budget violations, non-complete outputs, and malformed bytes hiding valid complete lines.
8. Require a fresh independent exact-head review after every repair commit, especially after two or more revoked candidates.

## Proof packet shape

```text
STATUS=<REPAIR_N_FINAL_EXACT_HEAD_REVIEW_PENDING|CLEAN|REPAIR>
HEAD=<candidate_sha>
PARENT=<parent_sha>
TREE=<tree_sha>
PATHS=<allowlist>
ADVERSARIAL_LOG=<path>
ADVERSARIAL_SHA256=<sha256>
CANONICAL=<pass/fail counts with inherited-failure boundary>
BASE_COMPAT_LOG=<path when applicable>
PRESERVE_REF=<local_ref>
PRESERVE_BUNDLE_SHA256=<sha256>
INDEPENDENT_REVIEW=<delegation_id>
NOT_CLAIMING=<push, merge, deploy, successor admission, cap increase>
```

## Pitfalls

- Do not describe invalid UTF-8 handling generically as “fail closed” if the base contract is tolerant complete-line preservation. The correct invariant is: malformed bytes must not crash and must not hide valid complete lines.
- Do not treat a hung helper that wrote `RESULT.md` as success. Preserve candidate, stop the task-owned process, classify the worker as failed-after-result, and review the candidate independently.
- Do not let canonical inherited failures block a source-no-regression verdict, but also do not claim canonical full-suite green.
