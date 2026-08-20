# Hermes gateway Telegram reconnect wedge

Session pattern: user reports an agent/profile is "not responding" even though its systemd service is active.

## Durable failure contract

A Hermes gateway can be `active (running)` while the messaging platform is wedged. In the Ned case, `ned-gateway.service` was active, but journal logs showed repeated Telegram reconnect failures:

```text
Reconnect telegram error: telegram connect timed out after 30s, next retry in 300s
```

The profile was not responsive to Telegram messages until the gateway was restarted and the Telegram adapter reconnected.

## Triage sequence

1. Check the service and logs:

```bash
systemctl status <profile>-gateway.service --no-pager -l
journalctl -u <profile>-gateway.service --since '2 hours ago' --no-pager -n 220
```

2. Check the real gateway state file, not just systemd:

```bash
python3 - <<'PY'
import json
from pathlib import Path
p = Path('/home/ubuntu/.hermes/profiles/<profile>/gateway_state.json')
print(json.dumps(json.loads(p.read_text()), indent=2))
PY
```

Healthy platform evidence should look like:

```json
{
  "gateway_state": "running",
  "platforms": {
    "telegram": {
      "state": "connected",
      "error_code": null,
      "error_message": null
    }
  }
}
```

3. Smoke the model path separately so you can distinguish provider failure from gateway/platform failure:

```bash
hermes --profile <profile> -z 'Reply with exactly <PROFILE>_SMOKE_OK and nothing else.' --provider <provider> -m <model>
```

If the model smoke works but Telegram is disconnected/reconnecting, repair the gateway/platform layer.

## Repair pattern

```bash
sudo systemctl restart <profile>-gateway.service
sleep 8
systemctl status <profile>-gateway.service --no-pager -l
journalctl -u <profile>-gateway.service --since '2 minutes ago' --no-pager -n 120
```

Then inspect `gateway_state.json` and recent logs for `Connected to Telegram (polling mode)` and no fresh `telegram connect timed out` lines.

## systemd drain-timeout hardening

Hermes may warn that systemd can kill the gateway mid-drain, for example:

```text
Stale systemd unit detected: <service> has TimeoutStopSec=90s but drain_timeout=180s (expected >=210s)
```

If the installed CLI does not provide the newer `hermes gateway service install --replace` command, apply the equivalent systemd timeout directly:

```bash
sudo mkdir -p /etc/systemd/system/<profile>-gateway.service.d
printf '[Service]\nTimeoutStopSec=210s\n' | sudo tee /etc/systemd/system/<profile>-gateway.service.d/timeout.conf >/dev/null
sudo systemctl daemon-reload
sudo systemctl restart <profile>-gateway.service
systemctl show <profile>-gateway.service -p TimeoutStopUSec --no-pager
```

If Hermes' warning detector still reads the base unit and ignores drop-ins, add `TimeoutStopSec=210s` to the base unit too, reload, and restart. Verify with `systemctl show`; do not rely only on the warning text.

## Verification checklist

Use a `/tmp/hermes-verify-*` script and label the result ad hoc targeted verification. Check:

- `systemctl is-active <profile>-gateway.service` returns `active`.
- `TimeoutStopUSec=3min 30s` for a 210s timeout.
- `gateway_state.json` says `gateway_state=running`.
- Telegram platform state is `connected` with no error code/message.
- Recent logs since the final restart have no fresh `telegram connect timed out`.
- Gateway log tail includes `Connected to Telegram (polling mode)` and `Gateway running with 1 platform(s)`.
- Direct profile model smoke returns the exact sentinel string.

## Pitfalls

- Do not equate `systemctl active` with responsiveness. Check platform state.
- Do not diagnose provider/model failure until a direct profile model smoke fails.
- Do not store or print tokens while inspecting `auth.json`; redact secrets.
- Do not call this full Hermes suite green. It is a gateway/platform responsiveness smoke.
