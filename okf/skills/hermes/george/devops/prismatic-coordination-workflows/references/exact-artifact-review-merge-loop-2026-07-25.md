# Exact-artifact review/repair/merge loop — 2026-07-25

Use this reference when coordinating a Prismatic candidate that must survive independent review, repair cycles, detector nags, and merge gates without overclaiming.

## Pattern

1. Bind every candidate to exact commit and tree before review.
2. Treat every independent reviewer finding as blocking when it is reproducible against the current exact head, even if a prior candidate had already passed local targeted checks.
3. Repair on the same focused branch when scope remains the same; after each repair, rerun the focused regression plus the broader canonical suite that can expose interaction failures.
4. Commit the repair, then request a fresh exact-head review. A `CLEAN` review only applies to the exact commit/tree reviewed.
5. If a review is provider-filtered or otherwise returns no substantive evidence, mark it as zero acceptance evidence and replace it; do not count it as pass or fail.
6. If a background canonical run started before source changes, mark it superseded. It may be useful telemetry but is not acceptance evidence for the later exact head.
7. When GitHub Actions reports failure before running any step, inspect check annotations/job JSON. `runner_id=0` and `steps=[]` with a billing/spending-limit annotation is infrastructure blockage, not candidate failure. Record the boundary and use only the already-approved provider-neutral exact-artifact fallback path if policy allows.
8. Before merge, verify remote PR head equals the independently reviewed head. After merge, verify `origin/main` equals the merge commit and that all reviewed path blobs in `origin/main` match the reviewed head exactly.
9. Preserve deployment/restart/Linear boundaries explicitly unless separately authorized.
10. Close with a compact proof packet: status, reviewed head/tree, independent review marker, local/canonical proof logs, GitHub CI boundary, PR/merge commit, path-blob equality, and non-claims.

## Detector-compatible verification

When the system warns that edited files lack fresh evidence, run an OS-created tempfile verifier and literal commands (`python -m pytest`, `ruff`, `python -m build`) against the exact head. Report log path and digest. If the same warning repeats after successful literal reruns, classify it as detector non-recognition rather than looping indefinitely.

## Acceptance boundaries

Do not claim:

- hosted CI green when Actions was blocked before steps;
- production deployment or restart unless actually performed and authorized;
- Linear/status publication unless actually written;
- acceptance from targeted proof alone when independent review found valid current-head defects.
