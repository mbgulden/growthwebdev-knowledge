# Gateway webhook secret rotation and runtime-truth repair

Session-derived checklist for Prismatic gateway cutovers, webhook secret rotation, and dashboard runtime-health truth. Use as an addendum to `Focused PR merge-to-operations workflow`.

## Trigger

Use when Prismatic gateway secrets appear in unit files, webhook signatures fail canaries, a gateway release is being cut over to an immutable checkout, or the dashboard reports service/runtime status that contradicts live systemd evidence.

## Secret migration from systemd

1. **Snapshot before touching services.** Preserve current unit/env/runtime state into a mode-700 deployment snapshot with file hashes and rollback notes. Do not print secret values.
2. **Move literals out of unit files.** Put webhook secrets in a protected env file, e.g. `.prismatic/env.d/gateway_webhooks.env` with mode `600`; keep the systemd unit free of literal credentials.
3. **Use a staged old/new window.** During provider rotation, support current and next secrets long enough to prove new signatures and reject invalid signatures, then remove the old secret and restart/reload.
4. **Verify the exact effective runtime environment.** A literal in a unit file may not be the process’s effective secret after quoting, env-file layering, or wrapper changes. Test against the running service, not just against file contents.
5. **Provider-side rotation is separate from local migration.** Local env migration proves secrets are no longer in systemd; it does not prove GitHub/Linear have rotated until provider API/UI evidence and real/synthetic signed requests pass.

## Signature canary matrix

For every webhook provider, prove all four states where possible:

- new valid signature accepted;
- deliberately invalid signature rejected;
- old signature rejected after the secondary/old value is removed;
- provider-signed delivery/ping accepted when the provider exposes delivery logs or ping APIs.

Boundary language: local HMAC tests are not provider proof; provider ping/delivery proof is not a full event-processing proof.

## GitHub HMAC pitfall

GitHub signs the **raw request body only** for `X-Hub-Signature-256`. Do not prefix the body with header names or signature labels when computing/verifying HMAC. Keep a regression test that rejects the former prefixed-body algorithm while accepting the official raw-body digest.

## Immutable gateway cutover

1. Build/install from the exact reviewed merge SHA into a non-editable isolated venv.
2. Scrub `PYTHONPATH`/Hermes session contamination when validating imports and installs; prove imports come from the release/venv, not the active Hermes environment.
3. Start an alternate-port release smoke before touching the live unit.
4. Cut systemd to the immutable release only after health, dashboard smoke, and signature canaries pass.
5. After restart, verify the running process working directory, executable, release SHA, health endpoint, and signature matrix.

## Dashboard runtime truth adapter

If dashboard UI says a service is offline but systemd says active, inspect the API/UI contract before changing labels:

1. Fetch the dashboard API payload and compare it to the fields the UI renders.
2. Missing booleans often coerce to false (`undefined -> false`) and create false `OFFLINE` badges.
3. Add a read-only runtime adapter that reports actual systemd/service state into the existing payload instead of inventing new dashboard cards or fallback shells.
4. Do not fabricate heartbeat truth. If the service has no heartbeat producer, report heartbeat as unavailable/missing with a clear source boundary while separately queuing the real heartbeat producer work.

## Controller and handoff boundary

Before handing a rejected AGY repair to Fred or another agent, pause/disable bounded controllers that could auto-launch another producer. Otherwise a controller tick can violate the approved “one producer / one final repair” boundary while the handoff is being prepared.

## Private-key cleanup boundary

Deleting obsolete local private-key copies is not the same as provider-side revocation. If GitHub App key administration returns 403 or requires owner UI access, report `BLOCKED_ON_GITHUB_APP_OWNER`, remove only authorized local copies without reading/pasting contents, and ask the owner to revoke/generate through GitHub App settings.
