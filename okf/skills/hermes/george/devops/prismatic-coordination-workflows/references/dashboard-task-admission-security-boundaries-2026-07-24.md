# Dashboard task-admission security-boundary review pattern (2026-07-24)

Use when coordinating Prismatic dashboard/control-plane task admission or reviewing a candidate that accepts operator-submitted work into a durable queue.

## Durable lesson

A task-admission slice is not ready just because schema/API/UI tests pass. Review the boundary as a control-plane input surface:

1. **Policy/config file reads must be bounded before content read**
   - Open with no-follow semantics where available (`O_NOFOLLOW`).
   - Use nonblocking open (`O_NONBLOCK`) so a FIFO or special file cannot stall a worker.
   - Validate descriptor metadata before reading: regular file, owner, mode/privacy, max byte size.
   - Read in bounded chunks under an explicit maximum.
   - Re-check descriptor identity/metadata after reading to catch path or descriptor instability.
   - Add regressions for FIFO, symlink, device/special file, and oversized policy.

2. **HTTP request bodies must be bounded while streaming**
   - Do not rely on a post-hoc length check after `await request.body()` has buffered the whole entity.
   - Precheck declared `Content-Length` when present.
   - Consume `request.stream()` with a running byte cap.
   - Return a clear 413/invalid-size response once the cap is crossed.
   - Add a regression with an oversized request body that proves the route rejects it.

3. **Exact-head review discipline**
   - Treat every late independent `REPAIR` verdict as superseding previous acceptance, even if previous canonical/local proof passed.
   - After repair, bind proof to the new exact commit and tree.
   - Push the repaired head before asking for final independent review.
   - Do not merge until the independent verdict explicitly names the repaired head/tree.

4. **Verification language**
   - Label focused policy/body checks as `AD_HOC_OR_CANONICAL=ad-hoc targeted`, even when combined with py_compile, focused pytest, Ruff, build check, and security audit.
   - Keep canonical-suite claims separate from same-turn detector-rerun proof.

## Compact proof fields to preserve

```text
HEAD=<exact commit>
TREE=<exact tree>
POLICY_BOUNDARY=nonblocking no-follow descriptor open; pre-read fstat; bounded chunked read; descriptor stability
REQUEST_BOUNDARY=Content-Length precheck + streamed running byte cap
CANONICAL=<if full suite actually ran>
FOCUSED_REPAIR=<ad-hoc targeted>
FINAL_INDEPENDENT_REVIEW=<pending|clean|repair|blocked, bound to exact head/tree>
NOT_CLAIMING=merge, deployment, runtime producer execution, or independent acceptance unless actually proven
```

## Pitfalls

- A size check after reading is too late for FIFOs/devices/oversized files.
- `await request.body()` before enforcing the cap is too late for public HTTP admission routes.
- Existing canonical green does not close a later exact-head independent `REPAIR` finding; repair and rerun on the new head.
- A repeated Hermes verification guard after one compliant same-turn rerun may be detector nonrecognition, but only after the fresh current-turn proof is visible; do not use detector nonrecognition to skip the first requested rerun.
