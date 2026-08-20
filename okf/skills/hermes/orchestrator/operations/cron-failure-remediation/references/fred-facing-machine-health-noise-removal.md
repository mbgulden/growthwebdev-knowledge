# Fred-facing machine-health noise removal

Use this when Michael rejects a monitor as cluttering Fred, especially Proxmox/PVE load or unreachable-node alerts.

## Durable lesson

When Michael says a health monitor is cluttering Fred or is not helpful, do **not** keep tuning the alert copy or thresholds in Fred's lane. Treat the monitor class as rejected for Fred-facing delivery and remove/suppress active emitters.

For Proxmox/PVE specifically, raw unreachable-node lines and load numbers like `pve6 Load HIGH: 5.8` are not useful in Fred. They belong outside Fred-facing digests unless Michael explicitly asks for a live infrastructure check.

## Remediation sequence

1. Identify active emitters, not just files containing old alert text:
   - current Hermes cron `jobs.json` / `cronjob list`
   - live processes (`ps` for `proxmox_cluster_monitor` / service name)
   - systemd unit state (`is-active`, `is-enabled`)
   - runnable script directories only (`~/.hermes/scripts`, active profile `scripts/`)
   - active aggregators/digests that might re-surface stale health rows
2. Ignore historical transcripts, archived scripts, old cron backup snapshots, and logs for emitter detection. They can contain old alert text forever without being live senders.
3. Remove or quarantine runnable stale monitor scripts and pyc files so they cannot be accidentally revived.
4. Mask/disable stale systemd units if present.
5. Patch any active aggregator to suppress the rejected health class from Fred/Michael-facing output while preserving unrelated useful failures.
6. Run a focused `/tmp/hermes-verify-*` verifier that proves:
   - changed Python compiles
   - Proxmox/PVE fixture anomaly is suppressed
   - unrelated actionable anomaly is retained
   - no active cron/process/systemd/runnable script emitter remains
   - verifier itself is cleaned up

## Fixture pattern

Use a fake cron jobs file with at least:

```json
{
  "jobs": [
    {
      "id": "prox",
      "name": "Proxmox Cluster Monitor — Node CPU/RAM alerts via Autobot",
      "script": "proxmox_cluster_monitor.py",
      "enabled": true,
      "state": "scheduled",
      "last_status": "error",
      "last_error": "pve6 Load HIGH: 5.8; pve1 UNREACHABLE"
    },
    {
      "id": "keep",
      "name": "Useful active cron failure",
      "script": "useful.py",
      "enabled": true,
      "state": "scheduled",
      "last_status": "error",
      "last_error": "actionable non-machine-health failure"
    }
  ]
}
```

Expected result: only `keep` remains in the aggregator anomaly list.

## Verification scope note

Report this as ad hoc targeted verification, not suite-green. Explicitly say historical logs/session transcripts may still contain the old alert text and are intentionally out of scope because they are not active emitters.
