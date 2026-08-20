# Resource monitor normalized thresholds

Use this pattern when a cron/watchdog reports host resource alerts that may be misleading.

## Durable lesson

Raw load average is not an actionable alert threshold by itself. It must be interpreted relative to CPU capacity:

- Load `6.0` on `64` cores is roughly `0.09x/core` and should usually be quiet.
- Load `6.0` on `4` cores is `1.50x/core` and may warrant a high/critical alert.
- RAM alerts should be independent from load alerts; e.g. `41% RAM` is not memory pressure.

## Monitor contract

A good cluster resource monitor should:

1. Collect `nproc`/core count from the target node.
2. Collect 1-minute load from `/proc/loadavg` or equivalent.
3. Compute `load_ratio = load_1m / cores`.
4. Alert on the ratio, not the raw load number.
5. Include raw load, core count, and ratio in the status/alert text.
6. Label SSH/Tailscale failures as monitor connectivity state, not proof that the server is down.
7. Be event/cooldown based: once an alert key is sent (e.g. `node:load:high`), suppress repeats for a configured cooldown such as 10 minutes while the condition persists.
8. Keep cooldown state in a small state file and key it by condition, not by entire message text, so formatting changes do not reset suppression.

Example output:

```text
pve6: Load 6.0/64 cores (0.09x) | RAM 41% (154Gi/377Gi) | 3 VMs
```

This should not alert.

Example alert-worthy output:

```text
pve6: Load 6.0/4 cores (1.50x) | RAM 41% (154Gi/377Gi) | 3 VMs
Alerts:
⚠️ pve6 Load HIGH: 6.0 on 4 cores (1.50x/core)
```

## Focused verification recipe

For script-based monitors, use a `/tmp/hermes-verify-*.py` tempfile that monkeypatches the SSH/subprocess call and Telegram sender:

- fixture A: target node returns `cores=64`, `load=6.0`, `mem_used/mem_total≈41%`; assert no alert is sent.
- fixture B: target node returns `cores=4`, `load=6.0`, same RAM; assert exactly one load alert is sent and it contains `4 cores` plus `1.50x/core`.
- fixture C: repeat fixture B immediately with the same cooldown state file; assert no second alert is sent during the cooldown window.
- assert cooldown labels appear in sent alert text when applicable (for example, `cooldown 10m`).
- assert no RAM alert appears unless the RAM fixture actually crosses the RAM threshold.
- clean up the temp verifier and label the result `ad hoc targeted verification`, not full suite green.
