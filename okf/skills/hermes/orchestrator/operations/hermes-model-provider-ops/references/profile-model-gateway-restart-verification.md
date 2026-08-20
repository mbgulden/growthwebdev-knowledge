# Profile Model Change + Gateway Restart Verification

Use when a Hermes profile is moved to a new model/provider, especially an OAuth-backed Codex/ChatGPT route.

## Lesson

Config readback and a one-off CLI smoke are not enough to prove a live Telegram bot has loaded a model. The target profile gateway may still be running with old config, or the gateway/session path may fail even after a forced CLI smoke succeeds. Always restart the target gateway and inspect live logs/state.

## Workflow

1. Confirm target profile and current config:
   - `hermes profile list | grep <profile>`
   - read `~/.hermes/profiles/<profile>/config.yaml` for `model.provider` and `model.default`.
2. Refresh authenticated provider model list before choosing a target. For `openai-codex`, only use models returned for that authenticated account.
3. If the requested model is absent or gateway logs show unsupported model errors, do not leave the bot broken. Move the profile to the highest supported model in the same requested provider family and state the blocker plainly.
4. Restart the gateway from outside the gateway process. If the active session cannot directly restart because SIGTERM would kill child commands, run a one-shot no-agent cron/script that performs the restart and prints proof.
5. Prefer `hermes --profile <profile> gateway restart --system` over raw `systemctl restart` because it refreshes stale units. Verify `TimeoutStopUSec` is at least the profile drain timeout plus buffer.
6. Read proof after restart:
   - `systemctl show hermes-gateway-<profile>.service -p ActiveState -p MainPID -p TimeoutStopUSec`
   - `~/.hermes/profiles/<profile>/gateway_state.json` has `gateway_state=running` and `platforms.telegram.state=connected`.
   - `journalctl -u hermes-gateway-<profile>.service --since ...` has no repeated unsupported-model errors for the final model.
7. Run a live smoke on the final supported route:
   - `hermes --profile <profile> -z 'Reply with exactly <MARKER> and nothing else.' --provider <provider> -m <model>`
8. Clean temporary one-shot restart scripts after use.
9. If any files/config changed, run a `/tmp/hermes-verify-*` verifier that checks config YAML, gateway state, systemd PID match, one-shot cleanup, and live smoke. Label it ad hoc targeted verification, not suite green.

## Pitfalls

- Do not claim “updated” from config-only proof; Michael expects the running bot to actually load it.
- Do not trust public model names over authenticated provider availability.
- Do not leave a profile on an unsupported requested model if the gateway logs prove it fails.
- Do not run raw restart commands from inside the same gateway process when Hermes blocks SIGTERM-propagating child commands; use a scheduler/cron one-shot or external shell path.
- Do not leave one-shot restart helper scripts behind as active changed artifacts.
