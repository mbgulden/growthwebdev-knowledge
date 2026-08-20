# Descriptor-bound SQLite and PGID cleanup hardening

## Trigger

Use this reference when reviewing or repairing a read-only Prismatic operations/health plugin that inspects live profile state, shells out to Git, or reports filesystem/SQLite findings under adversarial TOCTOU conditions.

## SQLite read-only inspection pattern

A read-only health check must not open a mutable lexical SQLite path and then report page/freelist/threshold metrics as if the inspected file were stable. Harden the check this way:

1. Open the target DB with `O_NOFOLLOW` and hold the descriptor for the whole inspection.
2. `fstat()` the held descriptor and verify it is a regular file.
3. Compare descriptor identity to the lexical path identity before reporting any path-bound evidence.
4. Connect SQLite through the held descriptor, e.g. `/proc/self/fd/<fd>`, rather than through the mutable original path.
5. After connect/query, revalidate both the held descriptor and the lexical path identity.
6. Track WAL identity before and after inspection. If the WAL appears, disappears, changes identity, or changes relevant metadata during inspection, suppress page/freelist/threshold claims and report a conservative incomplete-snapshot warning.
7. Close the descriptor in a `finally` block and add FD-leak regressions when practical.

## Race regressions to require

Add adversarial fixtures for:

- regular DB replaced by symlink before open;
- symlink swap immediately after descriptor open;
- symlink/rename swap during SQLite connect/query;
- external DB substitution that would otherwise surface page/freelist metrics;
- non-empty WAL changed or removed during inspection;
- special path characters handled without falling back to the lexical path;
- no raw host paths or sensitive IDs reflected in public findings.

## Process-group cleanup pattern

For bounded Git/helper subprocesses, success-path proof is as important as timeout/error proof. A leader process can exit 0 after forking a same-process-group descendant that closes stdout/stderr; ordinary communicate/wait success can miss the leak.

Use this lifecycle:

1. Launch the helper in a dedicated process group.
2. When output/IPC succeeds, observe leader exit without reaping it first, e.g. `waitid(P_PID, pid, WEXITED | WNOHANG | WNOWAIT)`.
3. Signal/kill the dedicated PGID while the leader PID remains reserved.
4. Then reap the leader.
5. Repeat cleanup on timeout, non-zero exit, EOF, IPC exceptions, and partial-success paths.
6. Document the boundary honestly: cleanup covers the dedicated same-process-group tree, not deliberately detached `setsid()` sessions or cgroup-level containment unless such containment is actually implemented.

## Process regressions to require

- successful leader exits 0 while a same-PG descendant attempts delayed side effects;
- non-zero leader with descendant;
- timeout/stuck enumeration helper with descendants;
- early EOF/IPC exception cleanup;
- explicit detached-session boundary test or documentation review showing no overclaim.

## Proof boundary

Report focused probes as `AD_HOC_OR_CANONICAL=ad-hoc targeted`. Do not claim canonical suite green, production proof, or cgroup containment unless those exact gates ran and passed.
