# Runtime convergence inventory and asset-porting pattern

Use when Prismatic has a verified current main/release but production runtime still spans older immutable releases, mutable checkouts, profile scripts, or non-repository daemons.

## Core lesson

Do not equate a merged immutable release with runtime convergence. Inventory the actual running processes and their import/execution bases before proposing deployment. Production may depend on useful, unmerged operational assets that must be preserved and ported path-by-path.

## Read-only inventory checklist

1. Capture current source truth and immutable release identity:
   - `origin/main` SHA;
   - release checkout path;
   - standalone git proof, object alternates absence, `git fsck`, clean tracked status.
2. Inspect live services through direct runtime proof, not only unit files:
   - `systemctl show` for `MainPID`, timestamps, restart counts, unit properties;
   - `/proc/<pid>/cwd`, `/proc/<pid>/cmdline`, and environment keys/paths only;
   - service-specific `PYTHONPATH`, executable, working directory, state file paths, and external script paths.
3. Treat current unit declarations as intent, not proof. A long-running process may still have an old CWD/import base after a unit change.
4. Compare live code/assets against current main and dirty runtime preservation sources with hashes and path-level diffs.
5. Inventory timers/drop-ins and repository-owned unit templates. If live units are not reconstructable from source templates, convergence needs a source slice before deployment.
6. Preserve external mutable state separately: env files, SQLite DBs, cursors, logs, sandboxes, archives, merge-pipeline state, and systemd unit files.
7. Record whether any service restart observed during inventory was initiated by this work or happened independently.

## Preservation rules

- A dirty runtime checkout is a preservation source, not a reset target.
- Never `git reset --hard`, `git clean`, or copy current main over runtime/profile scripts until path-level classification is complete.
- Classify each changed/untracked runtime path as already merged, required source asset, superseded/stale, generated state, secret placeholder, or external config.
- Secrets and state remain outside repository/release trees; version only secret-free templates/manifests.
- If a live service executes a Hermes profile script, treat it as a temporary operational bridge. Port required behavior into source; do not make the profile script the durable dependency.
- Non-git daemons need separate packaging/release ownership or explicit exclusion; they cannot be declared converged by repointing Engine services alone.

## Convergence plan shape

Report a table with component → live execution base → state → source/main gap. Include exact hashes and paths for gateway, consumer, supervisor, curator, watchdog/webhook timers, merge daemon, current main, and immutable release.

Then split recommendations:

1. **Allowed read-only work now:** semantic diffs, clean source branches/PRs, missing unit templates, runtime manifests, backup/rollback script drafting, alternate-port dry-run planning.
2. **Separately authorized work:** editing `/etc/systemd/system`, daemon reload, live unit repoint, stop/start/restart, state migration, Linear writes, generic dispatch/cap increase.
3. **First bounded source slice:** usually secret-free unit/runtime manifest templates or semantic port of one live operational script. Keep target changed paths small and tests explicit.
4. **Later slices:** larger supervisor behavior ports, dirty runtime checkout reconciliation, non-git daemon packaging, clean-room/alternate-port proof, then staged component restart.

## Supervisor semantic-diff reviewer prompt pattern

Use a read-only delegated reviewer when live/current/dirty supervisor scripts differ materially. The reviewer may inspect and classify but must not edit, deploy, restart, mutate state, or dispatch agents.

Ask for:

- capability matrix: live external vs current main vs dirty runtime;
- function names and line ranges for absent/stale/superseded behavior;
- behavior current main has that live lacks and vice versa;
- dependencies on external profile scripts or machine paths;
- first bounded source-port recommendation with allowed changed paths, tests, and non-claims;
- explicit answer to whether current main can safely replace live now.

Priority capabilities to classify:

- exact task lookup;
- result packet/writeback;
- failure, cancellation, and completion fail-closed behavior;
- raw output queue;
- completion ledger;
- promotion checks;
- recovery/DLQ;
- locks/admission leases;
- sandbox/archive policy;
- subprocess timeout and cleanup;
- secrets/path handling.

## Read-only reviewer to queued writer handoff

If a semantic-diff reviewer returns `CLEAN_FOR_BOUNDED_PORT`, do **not** immediately admit a second writer while another runtime-convergence producer is active. Convert the reviewer result into a verified queue brief instead:

1. Reproduce the key finding locally against current main and the live preservation source before trusting the reviewer.
2. Write `QUEUE_BRIEF.md` under the agent bus for the successor slice with:
   - `STATUS=QUEUED_NOT_DISPATCHED`;
   - predecessor task id;
   - `BASE_SHA=DEFER_UNTIL_PREDECESSOR_CLOSES`;
   - exact allowed changed paths;
   - source/live hashes and preservation-source classification;
   - required behavior, acceptance tests, and non-claims.
3. Hash and read back the queue brief before recording it in handoff/control state.
4. Keep the queued slice inactive until the active producer closes and current main advances; then bind the then-current base SHA, create a clean workspace/branch, write/hash `AGY_TASK.md`, prove no producer is active, and only then dispatch.
5. Report the distinction explicitly: `QUEUED_NOT_DISPATCHED` does not consume a producer slot and does not authorize deployment/restart/live path switching.

## AGY supervisor launch-transport port pattern

When current main still uses a stale signed-stdin AGY supervisor transport but production uses filesystem-scoped AGY CLI launch/relaunch, make the first port narrow and source-only:

- Allowed paths should usually be exactly `scripts/agy_sandbox_event_supervisor.py` and its focused control-plane test.
- Replace the stale transport with `AGY_BIN --dir <sandbox> --print <bounded task prompt>` for both initial launch and relaunch.
- Pass the bounded task prompt as one exact command argument; do not write task payloads to stdin. Use `stdin=None` or `subprocess.DEVNULL`, never a writable pipe for the task payload.
- Remove transport-only signing artifacts such as `INJECTED_VIA_STDIN`, `AGY_TASK_SIGNING_SECRET`, insecure `default_secret` fallback, and HMAC payload/signature construction.
- Preserve the canonical child-environment helper such as `agy_cli_child_env()` for backend preflight, launch, and relaunch instead of copying live profile-script environment assembly wholesale.
- Preserve exact-task lookup, repair-seed protections, fail-closed `RESULT.md` semantics, rejected completion topics, sandbox root policy, cleanup, and unrelated behavior.
- Tests must prove exact command shape, relaunch identity, no writable stdin/no payload write, marker removal, child-env use in all three places, completion-signal requirements, non-promotable false/partial packets, no mutable-cache fallback, and import-time side-effect absence.
- Non-claims must include full supervisor convergence, live supervisor switch, deployment/restart, result-packet integration, raw-output queue, completion ledger, assigned-agent writeback, promotion durability, DLQ/cancellation, admission leases, orphan recovery, sandbox archival, publishability, clean-room portability, and cap increase.

## Proof packet

```text
RESULT=<INVENTORY_PASS_TOPOLOGY_SPLIT|CONVERGED|BLOCKED>
CURRENT_MAIN=<sha>
RELEASE=<path>
LIVE_BASES=<component:path-or-sha summary>
DIRTY_RUNTIME=<path/head/dirty_count>
EXTERNAL_STATE=<paths summarized, no secrets>
REPORT=<path>
DEPLOYMENT=<NOT_PERFORMED|AUTHORIZED_AND_PERFORMED>
RESTART=<NOT_PERFORMED_BY_THIS_WORK|component list>
NEXT=<bounded port/convergence slice>
NOT_CLAIMING=<runtime parity/deploy/cap/portability/etc.>
```
