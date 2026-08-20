# Codex GPT-5.6 explicit slugs and live-gateway verification

## When this applies

Use this when Michael asks whether Hermes/Codex can use GPT-5.6, or asks to switch a live profile/bot to GPT-5.6.

## Durable lesson

The Codex/OAuth picker or `list_authenticated_providers()` can lag behind working model access. Do **not** conclude GPT-5.6 is unavailable from the picker/catalog alone. Test exact slugs directly through the same Hermes route that the target profile will use.

Known useful slugs:

```text
gpt-5.6-sol
gpt-5.6-terra
gpt-5.6-luna
```

For live bot defaults, prefer the explicit variant slug, especially `gpt-5.6-sol`, rather than bare `gpt-5.6` unless gateway logs prove the bare slug is stable for that profile.

## Verification pattern

1. Run direct smokes for the exact slugs:

```bash
for m in gpt-5.6-sol gpt-5.6-terra gpt-5.6-luna; do
  hermes --profile <profile> -z "Reply with exactly ${m}_OK" --provider openai-codex -m "$m"
done
```

2. Update profile config only after a slug responds cleanly:

```yaml
model:
  provider: openai-codex
  default: gpt-5.6-sol
```

3. Restart the target gateway and verify runtime state, not just config:

```bash
sudo hermes --profile <profile> gateway restart --system
systemctl show hermes-gateway-<profile>.service -p ActiveState -p MainPID -p TimeoutStopUSec --no-pager
python3 - <<'PY'
from pathlib import Path
import json, yaml
profile='<profile>'
cfg=yaml.safe_load(Path(f'/home/ubuntu/.hermes/profiles/{profile}/config.yaml').read_text())
state=json.loads(Path(f'/home/ubuntu/.hermes/profiles/{profile}/gateway_state.json').read_text())
print(cfg['model'])
print(state['gateway_state'], state.get('platforms',{}).get('telegram',{}).get('state'))
PY
```

4. Inspect recent gateway logs for rejection strings after restart:

```bash
journalctl -u hermes-gateway-<profile>.service --since '<restart timestamp>' --no-pager \
  | grep -E 'model is not supported|BadRequest|ERROR|WARNING|gpt-5\.6' || true
```

5. Create a `/tmp/hermes-verify-*` ad hoc verifier that checks config parse, gateway state, Telegram connected, one-shot helper cleanup, live smoke, and absence of unsupported-model errors. Report it as ad hoc targeted verification only.

## Slowness diagnosis after switching to GPT-5.6 Sol

If the user says the bot is slow after the switch, first separate model slowness from system/cron problems:

- Check `gateway_state.json` and systemd active/PID.
- Check `agent.log` for context size and model latency lines. Large active sessions may show `context=~190,000 tokens` and disabled no-byte TTFB watchdog; this is a context-size bottleneck, not necessarily a broken model.
- Check recent tool calls; repeated broad `search_files` or browser work can dominate latency.
- Check Telegram flood-control warnings separately from model latency.
- Inspect profile cron jobs, but do not assume a silent no-agent watcher is the cause.

If needed, recommend one bounded mitigation: fresh session/reset for that bot task, or switch from `gpt-5.6-sol` to `gpt-5.6-terra` for daily-driver speed.