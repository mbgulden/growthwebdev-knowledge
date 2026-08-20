# Jules Capacity Production Bridge Checklist

Use this when a durable Jules/Resources capacity PR has merged but production still depends on live profile scripts, cron wrappers, or runtime overlays.

## Promotion shape

1. **Treat merge as necessary but not live.** A merged PR with green CI and immutable-release proof is still not production proof until runtime files and operational wrappers are updated, the importing service is restarted, and the public API/card is checked.
2. **Use a deployment packet before editing.** Capture a runtime manifest, copies of authorized runtime target files, copies of live profile scripts, and a rollback note under `.prismatic/deployments/<slice>/` before patching dispatchers/watchdogs or overlaying service code.
3. **Prefer focused overlays when runtime is dirty.** Apply only the reviewed release paths required for the slice, and verify unrelated runtime bytes remain unchanged.
4. **Keep capacity ledgers as audit evidence.** Roll back code/wrappers if needed, but do not delete the Jules capacity DB unless Michael explicitly authorizes evidence deletion.

## Live dispatcher adapter requirements

When wiring an existing synchronous Jules dispatcher into the capacity ledger:

- Add enough Linear issue fields to derive a deterministic event identity, usually issue identifier + issue uuid + updatedAt/retry/stall context.
- Pre-record launch intent before invoking `jules`; update the row with parsed session id only after success.
- Record failed lifecycle if the process exits/fails before a session id is obtained; never leave an accepted active ledger row for a failed launch.
- Distinguish independent manual retries from replay of the same event; do not collapse all launches for one issue into a single permanent identity.
- Avoid adding new Linear writes, real launches, or cron mutations while making a no-side-effect adapter proof.

## Watchdog reconciliation adapter requirements

When wiring a Jules watchdog/list poll into the ledger:

- Retain subprocess return code and stderr/stdout boundary.
- Feed the real numeric-first `jules remote list --session` table into the shared parser/reconciler.
- Persist successful polls and unavailable/auth/error polls; public capacity should expose availability, source, and stale/partial/unavailable boundaries without leaking raw rows.
- Do not change existing report/Linear side effects as part of the capacity ledger bridge unless separately authorized.

## Verification packet

Minimum proof before claiming production complete:

```text
COMMAND=<merge readback; immutable release tests; adapter compile/no-side-effect tests; runtime overlay; gateway restart; API/browser proof>
RESULT=<PASS|FAIL|PARTIAL>
LOG=<path>
SCOPE=Jules capacity ledger/API/Resources card + live dispatcher/watchdog bridge
AD_HOC_OR_CANONICAL=<GitHub CI|immutable-release local|production proof|browser proof>
NOT_CLAIMING=<no real launches, no Linear writes, no cron mutations unless explicitly performed and authorized>
MARKER=JULES_CAPACITY_PRODUCTION_BRIDGE_OK
```

## Common overclaim traps

- `PR merged` != `production API/card live`.
- `real Jules parser canary passed` != `300/day quota truth`; the visible CLI list can be capped.
- `Resources card renders` != `fresh live capacity`; verify snapshot age, availability, stale/unavailable state, and ledger permissions.
- `dispatcher code patched` != `safe launch accounting`; prove failed launch and replay identities.
- `watchdog output reported` != `ledger reconciliation`; prove the watchdog actually calls the shared reconciler and persists unavailable polls.
