# Ned profile response-delivery audit — July 2026

## Trigger
Michael complained that Ned did not reliably respond when sent tasks or when finishing tasks, then asked for an active profile audit: what needs fixing, optimizing, missing, refactoring, and what works.

## Durable workflow
When a Hermes profile is not responding or not reporting task completion, audit the full delivery chain before only changing memory/style:

1. Inspect the active profile config with `hermes config path/show` and the profile `config.yaml`.
2. Inspect gateway state/logs and service status:
   - `gateway_state.json`
   - `channel_directory.json`
   - `logs/gateway.log`, `logs/errors.log`
   - `systemctl status <profile>-gateway.service`
   - `hermes gateway status --profile <profile>`
3. Probe the configured default model and likely fallback model(s) with one-shot commands. A model can be authenticated but silently hang; use a bounded timeout and switch to a known-good model if the configured one stalls.
4. Audit cron/task delivery semantics. A task loop with `deliver: local` will finish locally and stay silent to Michael; use `deliver: origin` for task pickup/completion reports that Michael expects.
5. Patch the cron prompt itself so task pickup and final completion reports are explicit. Memory alone does not fix autonomous cron behavior.
6. Run the profile audit script when available and verify the specific profile is clean.
7. If changing a running gateway from inside that gateway, do not directly restart it synchronously. Stage a delayed external reload with `systemd-run` or a helper script so the current response can be delivered before the gateway is replaced.
8. Check for systemd/manual gateway conflicts. A systemd unit repeatedly starting while a manual gateway is already running creates noisy crash loops and can obscure real delivery state. Add `gateway run --replace` to the service if supervised replacement is intended.

## Evidence pattern
Report:
- exact config changes,
- cron job ID + delivery target,
- model probe result,
- profile audit result,
- gateway/service reload status or delayed-reload caveat,
- remaining warnings separated from blockers.

## Pitfalls
- Do not call a profile fixed just because the current chat received a reply; cron completion delivery may still be local-only.
- Do not restart the current gateway directly from inside the gateway process; the child command may be killed or blocked.
- Do not treat provider authentication as proof the selected model responds; bounded model probes matter.
