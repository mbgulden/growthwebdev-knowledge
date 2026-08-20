# Cron-runtime installed authority inventory evidence

Use this pattern when reviewing a Prismatic cron/runtime-authority contract or any discovery slice that claims to enumerate live trigger authority surfaces.

## Lesson

Do not accept aggregate timer rows such as `Systemd Timers (33 active)`, a named subset of timers, or active-only listings as complete authority evidence. Installed disabled, inactive, static, and masked units are still authority surfaces because their bytes can be re-enabled or paired with other units later.

## Minimum evidence for installed Prismatic systemd timers

For every installed Prismatic timer discovered by read-only `systemctl list-unit-files --type=timer --no-pager`:

1. Record the timer unit name and triggered service name.
2. Record timer state and service state separately: enabled/static/disabled/masked, active/inactive, and load state.
3. Record exact timer and service fragment paths.
4. Record owner, group, mode, and SHA-256 for each timer/service file.
5. For masked symlink units, use `lstat` and `readlink`; record the symlink target and a digest of the link text instead of following the link to `/dev/null` as if it were an empty unit file.
6. Record execution identity and working directory from the service.
7. Inventory every absolute executable/configuration path referenced by `ExecStart` and `EnvironmentFiles`.
8. Hash non-secret referenced files. For secret-scoped files (`*.env`, OAuth material, `/secrets/`, credential-looking config), do not read or quote content; record secret-safe metadata and `[REDACTED—SECRET-SCOPED]` instead.
9. Record rollback source as both unit bytes and exact enabled/active states, plus `systemctl daemon-reload` requirement.
10. State explicitly that installed does not imply duplicate scheduling or shared `cron_id`; classification and migration remain separate future work.

## Verification shape

Use a disposable `/tmp/hermes-verify-*.py` script created with Python `tempfile` to reproduce the live inventory against the exact candidate archive:

```text
HEAD=<candidate>
TREE=<tree>
INSTALLED_PRISMATIC_TIMER_COUNT=<n>
PER_TIMER_SERVICE_EVIDENCE=PASS
REFERENCED_PATH_EVIDENCE=PASS
SECRET_SCOPED_REDACTION=PASS
ROLLBACK_EVIDENCE_COUNT=<n>
LIVE_SYSTEM_MUTATION=false
AD_HOC_OR_CANONICAL=ad-hoc targeted immutable-archive evidence-completeness verification
```

## Pitfalls

- `systemctl list-timers --all` is not enough; it is schedule/activity oriented and can miss installed disabled or masked authority bytes. Pair it with `list-unit-files --type=timer`.
- Do not hash secret-scoped env files into chat or contracts; redaction is evidence when paired with path/owner/mode/state metadata.
- Do not classify every installed timer as a PE cron duplicate. The discovery slice should require future classification before mutation.
- Preserve blocked prior heads as checkpoints when a review finds evidence incompleteness; do not rewrite history or treat the new repair as automatically accepted.