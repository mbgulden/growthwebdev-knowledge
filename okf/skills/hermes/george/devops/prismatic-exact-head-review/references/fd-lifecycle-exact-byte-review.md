# FD lifecycle exact-byte review pattern

Session signal: GRO-4368 Phase 2 opaque workspace review iterated through V1-V5 because independent reviewers found real descriptor-lifecycle hazards after earlier focused tests passed.

## Durable lesson

For security-sensitive filesystem traversal code, exact-head review must inspect descriptor ownership transitions, not only happy-path behavior or API output. Treat Linux `close(2)` failure semantics as security-relevant: after `close(fd)` is called, the numeric descriptor must be considered relinquished even if `close` raises, because retrying that same integer can close an unrelated reused descriptor.

## Review checklist

When reviewing `openat`/`openat2`/fallback traversal code:

1. Track every FD owner variable and sentinel value through success and every exception path.
2. Verify ownership transfer happens before any cleanup block can close the transferred FD.
3. Verify a newly opened child FD is closed exactly once if validation (`fstat`, type check, mount check, etc.) fails before ownership transfer.
4. Verify parent ownership is relinquished before calling `close(parent_fd)`; outer cleanup must not retry that descriptor number if close raises.
5. Verify empty-root or root-component fallback returns a live FD and does not close it in `finally`.
6. Verify fallback does not silently downgrade containment (`openat2` resolve flags, `NO_XDEV`/mount-ID equality, no-follow semantics).

## Deterministic tests to require

Add focused tests that monkeypatch or otherwise inject:

- child `fstat` failure after `openat` succeeds, asserting the child descriptor is closed/`EBADF` and closed once;
- child type-validation failure, asserting the child descriptor is closed once;
- parent close that actually closes the FD and then raises `EINTR`/`OSError`, asserting cleanup does not retry the parent FD number;
- forced fallback empty-root success, asserting the returned root FD remains usable;
- syscall-layer `openat2` resolve-mask capture, asserting the complete mask and no fallback downgrade.

## Evidence boundary

These are ad-hoc/focused security regressions. They support exact-head candidate acceptance only when paired with:

- exact manifest/path hashes;
- clean reconstruction from base plus authorized files;
- package/wheel install proof when packaging is in scope;
- canonical base-equivalence or canonical green, clearly separated;
- independent read-only review bound to the exact packet/manifest SHA.
