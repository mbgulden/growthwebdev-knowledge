# Public-safe runtime inventory and doctor declarations

## Trigger

Use this when a Prismatic slice changes runtime inventory, doctor/runtime readiness checks, event-consumer convergence, systemd service detection, or source declarations that may be scanned by public-security tooling.

Related evidence reference: `references/runtime-authority-discovery-contract.md` covers cron/systemd authority-discovery contracts, installed timers, managed user-crontab entries, referenced executables/configs, raw-command digest binding, and immutable exact-head proof.

## Lessons

1. **Do not put private launcher/secret paths in public source inventory.** Public config such as `config/runtime-services.json` and default doctor declarations may be scanned by public-readiness checks. Even non-content path literals under `/secrets/` can be treated as high-confidence secret-like values.
2. **Separate public runtime inventory from private launch coordinates.** Public inventory may declare durable non-secret state dependencies (for example an event DB, an admission policy file, and a non-secret environment-file boundary). Private launcher registry paths, AGY runtime registry paths, one-time credentials, and task-specific secret coordinates should remain runtime-injected control inputs rather than hard-coded source inventory.
3. **Do not weaken the operational claim.** If a source inventory excludes private launcher coordinates, the handoff/review packet must explicitly say that those coordinates are verified through invocation-time bindings such as `--launcher-config` and `PRISMATIC_TASK_ADMISSION_AGY_CONFIG`, not through the public inventory manifest.
4. **Exact-head verification should include public-security after inventory repairs.** After changing source inventory/doctor declarations, run the public-security readiness test or equivalent secret scan as part of focused proof, in addition to runtime-service schema validation and behavior tests.
5. **Installed-wheel proof needs external inventory override.** For packaged/installed behavior from an empty CWD, prove that the installed package fails closed without the external runtime inventory and passes with the explicit runtime inventory override. This catches accidental source-tree dependence.
6. **Doctor/service containment must parse real runtime structures.** For systemd `ExecStart`, parse the actual argv / structured assignment and reject substring, suffix, module-name, or label counterfeits. Do not rely on permissive string containment.

## Minimal proof packet

```text
COMMAND=<focused tests + runtime validator + public-security scan + installed/empty-CWD probe>
RESULT=PASS|FAIL
LOG=<path>
SCOPE=runtime inventory/doctor declaration changed behavior
AD_HOC_OR_CANONICAL=ad-hoc targeted|canonical suite|clean-room installed-wheel targeted
NOT_CLAIMING=<PR/merge/deploy/independent-review if not done>
MARKER=PUBLIC_SAFE_RUNTIME_INVENTORY_OK
```

## Review checklist

- Changed paths are limited to the authorized inventory/doctor/test scope.
- `git rev-parse HEAD`, tree, and clean status bind the proof to the exact candidate.
- Public source inventory contains no `/secrets/` path literals or token-like values.
- Every declared public state/env path exists as a regular non-symlink file on the live host when live path truth is being claimed.
- Private launcher/AGY coordinates are verified as runtime-injected bindings, not published as public inventory.
- Canonical suite and clean-room installed-wheel proof are reported separately from detector-facing ad-hoc verification.
