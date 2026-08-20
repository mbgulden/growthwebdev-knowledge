# AGY descendant containment gate — 2026-07-25

## Trigger

Use this reference when coordinating or reviewing Prismatic AGY runtime, dashboard activity, cancellation, replay-ledger, or cap/slot-release changes.

## Session lesson

A no-wall-clock AGY runtime is not enough by itself. A successful cancellation or cleanup receipt can still be unsafe if a detached descendant survives outside the observed root process/session. One independent exact-head review found this real blocker: a `setsid()` descendant that ignored `SIGHUP` and `SIGTERM` survived while the system still wrote a successful cleanup receipt and released the cap-one slot.

## Required acceptance contract

Before accepting AGY cancellation, normal-completion cleanup, dashboard status, or cap/slot release:

1. Preserve the approved no-cap rule: do **not** add wall-clock or inactivity kills. Dashboard activity is evidence only; explicit exact-run cancel stops work.
2. Treat the process tree as the unit of containment, not only the root/tmux pane process.
3. On Linux, prefer child-subreaper adoption for exact-run supervisors so daemonizing/detached descendants remain observable.
4. Track exact process identities with PID plus start-tick or equivalent freshness identity; PID alone is insufficient because of reuse.
5. On explicit cancellation, signal exact descendants before declaring success: TERM first, then KILL if still active. Zombies must be reaped or distinguished from live survivors.
6. On normal root-child completion, run the same full-tree containment before writing final cleanup success.
7. Do not tear down tmux or release the active slot until `exact_process_tree_cleanup=true` / equivalent is proven.
8. Receipts must fail closed and include survivor identities if any exact descendant remains active.
9. Dashboard/activity APIs must not claim `running` from stale artifacts alone. If the live pane/process identity cannot be verified, classify stale/orphaned/unverified rather than active.
10. Keep no-secret discipline: receipts may include PID/start-tick/status metadata, but not projected tokens or command secrets.

## Suggested reviewer probe

A focused adversarial probe should create a child that:

- calls `os.setsid()` or otherwise detaches from the root process group/session;
- ignores `SIGHUP` and `SIGTERM`;
- remains alive long enough to test cancellation and normal-completion cleanup;
- records its PID/start identity to a fixture file;
- asserts that the exact identity is inactive before any successful cancellation receipt, tmux teardown, or slot release.

Run the probe independently against the exact candidate head. Producer logs are not acceptance evidence.

## Proof packet fields

```text
COMMAND=<focused descendant containment probe + focused AGY tests>
RESULT=<PASS|FAIL|BLOCKED>
LOG=<path>
LOG_SHA256=<sha256>
SCOPE=detached descendant containment before cleanup receipt and slot release
AD_HOC_OR_CANONICAL=ad-hoc targeted unless full project suite also ran
NOT_CLAIMING=merge, deploy, production proof, or unrelated canonical green
MARKER=PE_AGY_DESCENDANT_CONTAINMENT_<OK|FAIL>
```

## Boundary

This gate complements, but does not replace, the no-wall-clock/no-inactivity-kill rule. Do not reintroduce time caps as a cleanup substitute; containment must be exact-run/process-tree based.
