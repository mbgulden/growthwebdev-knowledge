# Runtime authority discovery contract evidence

## Trigger

Use this when a Prismatic slice designs or reviews cron/systemd/runtime authority migration, rollback, or discovery contracts before implementation. The common failure mode is proving only an aggregate count or spool hash while missing the actual installed authority surfaces and referenced executables.

## Evidence shape

For installed runtime authority claims, inventory concrete live surfaces rather than broad summaries:

1. **Systemd timers/services**
   - Include every installed Prismatic timer unit, even disabled/inactive/masked units.
   - Record timer unit bytes/digest and corresponding service unit bytes/digest.
   - For masked services, capture `lstat` metadata and symlink target (for example `/dev/null`) instead of following the symlink and treating it as an empty regular file.
   - Record referenced executable/config paths only when public-safe; redact secret-scoped values while proving the redaction boundary.
   - Include rollback source for each installed unit.

2. **User crontab managed blocks**
   - Parse the live `crontab -l` managed block and record a byte-for-byte whole-export SHA256 for rollback.
   - Count entries and referenced workloads separately. One session found ten managed entries resolving to nine Python workload scripts plus one wrapper; future slices should not assume entry count equals workload count.
   - Record per-entry schedule and SHA256 of exact raw command bytes, but do **not** reproduce raw command/environment bytes in public docs.
   - Resolve `cd` working directory, interpreter path, interpreter symlink link-text digest, resolved interpreter digest, and every referenced script/wrapper absolute path with owner/group/mode/SHA256.
   - Treat shared mutable cwd/interpreter as authority dependencies, not harmless context.

3. **Release/config pinning**
   - Do not use semantic aliases like `/releases/v1.0.0` as production authority unless a real immutable manifest binding exists.
   - If the slice is design-only and no runtime hook artifact exists yet, use explicitly non-production fixture digests and a fail-closed algorithm for future real artifact/config bytes rather than inventing production digests.

## Verification pattern

Use an OS-safe `/tmp/hermes-verify-*` script that:

- binds `git rev-parse HEAD`, `HEAD^{tree}`, base merge-base, and exact changed path list;
- re-reads live timer/service and crontab surfaces read-only;
- asserts every live digest/path/count appears in the contract;
- asserts raw command bytes and secret-like values are not disclosed;
- asserts rollback coverage and prior repair constraints remain present;
- labels output as ad-hoc targeted unless the canonical suite was actually run.

## Proof packet fields

```text
COMMAND=<immutable archive + live authority parse>
RESULT=PASS|FAIL
LOG=<path>
SCOPE=runtime authority discovery/contract evidence
AD_HOC_OR_CANONICAL=ad-hoc targeted immutable-archive verification
NOT_CLAIMING=cron/timer mutation, migration, PR, merge, Linear write, or independent acceptance
MARKER=RUNTIME_AUTHORITY_DISCOVERY_CONTRACT_OK
```

## Pitfalls

- Do not treat a spool hash alone as evidence completeness; reviewers can and should ask for the referenced executables/configurations.
- Do not follow masked systemd-service symlinks and hash `/dev/null` as if it were the service body.
- Do not paste raw crontab commands or exported environment assignments into public contracts; use digest binding plus structured, non-secret metadata.
- Preserve blocked checkpoints by exact hash. A repair head supersedes them only after reproducing the first finding and proving the repaired archive.
