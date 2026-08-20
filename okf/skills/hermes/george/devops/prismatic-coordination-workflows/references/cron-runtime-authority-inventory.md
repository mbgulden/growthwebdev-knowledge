# Cron runtime authority inventory and review repair pattern

Use this when a Prismatic slice inventories cron/systemd runtime authority, migrates mutable cron workloads, or repairs reviewer findings about installed scheduler evidence.

## Scope

This is a coordination/review pattern, not permission to mutate cron, timers, services, Linear, PRs, or deployments. Keep installed state reads bounded and public-safe. Treat secret-scoped launcher/config files as redacted evidence unless the user explicitly authorizes deeper inspection.

## Required identity distinctions

1. **User crontab spool vs export are different artifacts.**
   - Spool evidence: `/var/spool/cron/crontabs/<user>` often requires `sudo stat` / `sudo sha256sum`; record owner, group, mode, type, and digest.
   - Portable rollback payload: `crontab -l` export; hash the exact exported bytes and restore with `crontab <backup>` only under separate mutation authorization.
   - Do not copy spool owner/group onto the export, and do not present the spool file as the rollback artifact.
   - Example live shape observed for ubuntu: spool file `ubuntu:crontab`, mode `0600`, regular file; export digest differed from spool digest.
2. **Installed scheduler surfaces include disabled/inactive units.** Inventory all installed Prismatic timer/service unit files, not only active timers, when the contract claims runtime authority coverage.
3. **Each managed cron entry needs executable/config evidence.** Count entries, referenced Python workload scripts, wrappers, interpreter symlinks/resolved targets, working directory, raw-command digest, and rollback binding. Redact raw command bytes or env assignments when they may expose secret-scoped configuration.
4. **Release pinning must fail closed.** Avoid reusable semantic aliases such as `/releases/v1.0.0` unless there is an existing immutable manifest/hook that binds artifact bytes. Design-only examples must use valid fixture digests and clearly state they are non-production.

## Read-only discovery commands

Use direct commands only when they are safe and bounded:

```bash
sudo stat -c 'PATH=%n OWNER=%U GROUP=%G MODE=%a TYPE=%F' /var/spool/cron/crontabs/ubuntu
sudo sha256sum /var/spool/cron/crontabs/ubuntu
crontab -l | sha256sum
```

For crontab parsing, prefer a temporary script that classifies tokens as files/directories/symlinks before hashing. Do not blindly hash checkout directories or follow masked unit symlinks to `/dev/null` as if they were empty regular files; use `lstat` and record symlink target evidence.

## Verification pattern

After each same-task repair:

1. Freeze a new exact candidate commit and preserve the blocked head with the reviewer’s first finding.
2. Run a `/tmp/hermes-verify-*` verifier from an immutable archive, not only the mutable worktree.
3. Assert exact `HEAD`, `TREE`, merge-base, one-path containment, clean tracked status, and the repaired evidence.
4. For cron runtime repairs, assert:
   - spool owner/group/mode/digest;
   - export digest and `spool_digest != export_digest`;
   - counts for managed entries, Python workloads, wrappers, timers/services;
   - no secret-like literals;
   - rollback source/digest language;
   - prior evidence repairs remain present.
5. Run a final post-handoff `/tmp/hermes-verify-*` readback if the handoff was edited after the archive proof. Include handoff candidate head/tree/log/hash and `POST_VERIFIER_MUTATION=none` when responding to repeated detector warnings.

## Reporting boundary

Use proof packets like:

```text
COMMAND=<read-only discovery or immutable-archive verifier>
RESULT=PASS|FAIL|BLOCKED
LOG=<path>
LOG_SHA256=<digest>
SCOPE=cron runtime authority inventory / specific repair
AD_HOC_OR_CANONICAL=ad-hoc targeted
NOT_CLAIMING=canonical suite green, independent acceptance, cron/timer mutation, PR, merge, Linear write, or live migration
MARKER=<specific marker>
```

If an independent reviewer finds a valid issue, accept the first finding, repair only that finding plus directly related consistency text, freeze a new head, and re-dispatch exact-head review.