# User-systemd poll dispatcher Linear request burn

Session learning from the July 2026 Linear API limit incident.

## Symptom

Linear request-count quota can be exhausted even when the system-level `prismatic-dispatcher.service` appears inactive. The active poller may be a **user-systemd** service under `user@1000.service`:

```text
/home/ubuntu/.prismatic/venv_stable/bin/prismatic-engine serve
PRISMATIC_POLL_INTERVAL=30
LINEAR_API_KEY=present
```

The process can remain active while `systemctl is-active prismatic-dispatcher.service` reports inactive because the unit is installed under:

```text
/home/ubuntu/.config/systemd/user/prismatic-dispatcher.service
```

## Emergency stop pattern

1. Find the real poller, not just the system unit:

```bash
pgrep -af 'prismatic-engine serve|prismatic.dispatcher|dispatcher.py'
ps -o pid,ppid,lstart,etime,stat,cmd -p <PID>
tr '\0' '\n' < /proc/<PID>/environ | grep -E 'PRISMATIC|POLL|LINEAR'
```

2. Stop the exact process if it is the poll-driven dispatcher:

```bash
kill -TERM <PID>
# wait briefly, then kill -KILL only if still alive
```

3. Manage the user service with an explicit user bus:

```bash
export XDG_RUNTIME_DIR=/run/user/1000
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus
systemctl --user stop prismatic-dispatcher.service || true
systemctl --user disable prismatic-dispatcher.service || true
```

4. If masking fails because the unit file already exists, add a reversible condition drop-in instead of deleting the unit:

```ini
# ~/.config/systemd/user/prismatic-dispatcher.service.d/10-linear-budget-kill-switch.conf
[Unit]
ConditionPathExists=/home/ubuntu/.prismatic/allow-poll-dispatcher
```

Then:

```bash
rm -f /home/ubuntu/.prismatic/allow-poll-dispatcher
systemctl --user daemon-reload
```

This makes even a manual start skip unless an operator intentionally creates the allow-file after replacing the poller with a budgeted/event-driven path.

## Verification

Use a fresh `/tmp/hermes-verify-*` tempfile and make **no Linear API calls**. Assert:

- user unit is disabled
- condition gate is present
- allow-file is absent
- no exact `prismatic-engine serve` / `PRISMATIC_POLL_INTERVAL=30` poller process remains
- `/home/ubuntu/.prismatic/logs/dispatcher.log` does not grow over ~35s
- core local services remain active: `prismatic-gateway.service`, `prismatic-consumer.service`, `prismatic-merge.service`

Use marker:

```text
LINEAR_POLL_BURN_STOP_OK
```

## Pitfall

Do not over-match every process containing `dispatcher.py`. A one-shot helper such as `jules_dispatcher.py` may have Linear credentials and an active HTTPS connection but is not the 30-second full-queue poller. Inspect loop shape before killing it.

## Non-claims

Stopping/gating the poller is emergency mitigation only. It does **not** mean:

- dispatcher architecture is fixed
- Linear quota has recovered before reset
- Linear mutations were applied
- event-driven/budgeted dispatch has been implemented
