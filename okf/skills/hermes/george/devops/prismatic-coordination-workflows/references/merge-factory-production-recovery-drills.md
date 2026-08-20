# Merge-factory production recovery drills

Session-derived checklist for closing a Prismatic merge-factory slice after code/security recovery. Use when deciding whether cap 1 can advance toward cap 2/3, or when a production gateway rollback/recovery must be proven after an immutable cutover.

## Trigger

Use after merge-factory governance/security work has been merged, webhook/gateway runtime has been repaired, or Michael asks whether the system is production-ready/cap-ready. Historical incidents and ad-hoc rescues do **not** count as formal drills unless they were controlled, bounded, and produced reusable proof.

## Cap-promotion boundary

Keep producer cap at 1 until both formal drills pass:

1. stale-worker recovery drill;
2. gateway rollback/recovery drill.

A merged PR, green CI, browser proof, or successful real rescue is not enough to raise cap by itself. Report cap status separately from code status.

## Formal stale-worker recovery drill

Build the drill against temporary state and exact current-main code. Avoid real AGY launches, Linear writebacks, provider mutations, or uncontrolled dispatch.

Minimum proof matrix:

1. Acquire a lease for a fixture issue under principal A.
2. Prove a concurrent producer cannot acquire while A's lease is active.
3. Heartbeat A's lease and prove it renews before expiry.
4. Force/advance expiry in fixture state.
5. Prove a new principal B can acquire only after expiry/stale recovery rules allow it.
6. Prove stale principal A cannot heartbeat, release, or overwrite B's new lease.
7. Prove issue/task identity fencing: wrong issue, wrong lease id, wrong owner, wrong stage/cap should fail closed.
8. Capture exact commands, log path, digest, state-db path, source SHA, and cleanup status.

Explicit non-claims: this drill proves lease/recovery control-plane behavior, not real AGY quality, not Linear writeback, not provider webhook delivery, and not cap increase unless the paired rollback drill also passes.

## Gateway rollback/recovery drill

After an immutable release cutover, preserve and test both rollback and roll-forward paths. This is operational proof, not just file existence.

Minimum proof matrix:

1. Identify current live release SHA/venv/unit paths and preserved rollback release SHA/venv/unit paths.
2. Snapshot the current unit/env without printing secrets.
3. Roll back to the preserved prior release only if authorized and scoped.
4. Verify service active, health endpoint, gateway API prefix, and webhook valid/invalid canaries on rollback.
5. Roll forward to the intended current release.
6. Reverify service active, health endpoint, dashboard runtime-truth payload/browser proof, and webhook valid/invalid canaries.
7. Record rollback and roll-forward commands/logs/digests plus the exact systemd unit/environment paths.

Explicit non-claims: provider-side key revocation, branch protection, mobile dashboard proof, and cap increase remain separate unless independently proven.

## Abandonment-guard portability trap

Do not treat an operational profile-script hotfix as a durable repository repair. If the orchestrator/profile script has an absolute `AGY_ABANDONMENT_GUARD` path fix but current-main still defaults to another profile or stale path, port and test the durable repository path before formal stale-worker recovery claims.

Repository portability gates may correctly reject a literal host path such as `/home/<user>`. Do not bypass that guard. Derive the stable service-account home from the OS account database (for example `pwd.getpwuid(os.getuid()).pw_dir`) rather than mutable `HOME`, append the orchestrator profile guard path, and preserve an explicit `AGY_ABANDONMENT_GUARD` environment override. Test with a foreign Hermes profile `HOME` and with an explicit override.

## Reporting block

```text
COMMAND=<grouped drill command summary>
RESULT=<PASS|FAIL|BLOCKED>
LOG=<path>
LOG_SHA256=<sha256>
SOURCE_SHA=<current-main or release sha>
STATE=<temp state/db path or release paths>
SCOPE=<stale-worker recovery|gateway rollback/recovery>
AD_HOC_OR_CANONICAL=formal drill
NOT_CLAIMING=<cap increase, provider revocation, real dispatch, etc.>
MARKER=<DRILL_MARKER>
```
