# Multi-profile model policy rollout

Use this reference when Michael asks to set the same primary/fallback model policy across multiple running Hermes profiles.

## Durable lesson

A successful rollout requires four proofs, not just editing `config.yaml`:

1. **Config intent** — each target profile has the requested `model.provider` + `model.default` and exactly the requested top-level `fallback_providers` chain.
2. **Provider viability** — run pre-change or pre-reload exact probes for the primary and fallback model for each profile when possible.
3. **Runtime activation** — reload/restart the real gateway units safely and verify new PIDs, active/running state, zero restart counters, and cgroup ownership.
4. **Route/capacity boundary** — run default-route probes or inspect safe session metadata to prove the primary route selected; if the configured fallback is reached but quota/rate-limit fails, report capacity degraded rather than configuration failure.

## Audit before editing

For each profile:

- Resolve the real profile root. Profiles may be symlinks/aliases; e.g. a `fred` profile path can resolve to an `orchestrator` profile root and share one config file.
- Read only non-secret config fields: config path, SHA, `model.provider`, `model.default`, top-level `fallback_providers`, and whether stale nested `model.fallback_providers` exists.
- Identify the real service unit and live PID/cgroup. Do not assume profile directories are independent.
- Check `hermes fallback list` after edits; it is the user-facing parity check for the configured fallback chain.

## Safe mutation pattern

Use an atomic YAML rewrite script rather than line-oriented shell edits:

- preserve unrelated config keys;
- set `model.provider` and `model.default` exactly;
- set a top-level `fallback_providers` list with `provider` and `model` keys;
- remove malformed or stale nested fallback keys such as string-valued `model.fallback_providers`;
- remove extra fallback providers not requested by the user instead of leaving hidden rescue routes.

If a profile root is an alias to another profile, state that boundary explicitly and do not attempt to split it unless Michael explicitly asks for independent profile roots.

## Verification commands/patterns

Use exact one-turn probes for each provider/model before relying on a config change:

```bash
hermes --profile <profile> --provider openai-codex --model gpt-5.6-terra -z 'Reply exactly: <PROFILE>_TERRA_OK'
hermes --profile <profile> --provider minimax --model MiniMax-M3 -z 'Reply exactly: <PROFILE>_MINIMAX_M3_OK'
```

After reload, verify service and ownership:

```bash
systemctl show hermes-gateway-<profile>.service -p ActiveState -p SubState -p MainPID -p NRestarts -p ExecMainStatus --no-pager
# inspect /sys/fs/cgroup/system.slice/<unit>/cgroup.procs and /proc/<pid>/cmdline for --profile <profile>
```

Then verify effective policy:

```bash
hermes --profile <profile> fallback list
hermes --profile <profile> -z 'Reply exactly: <PROFILE>_DEFAULT_TERRA_OK'
```

If the default-route command exits nonzero or returns no marker, inspect bounded logs and safe session metadata before claiming failure. A final MiniMax `Token Plan usage limit`/429 after a Codex primary rate limit can mean fallback activation worked but the fallback provider is currently capacity-exhausted.

## Report shape

```text
STATUS=PASS_CONFIG_AND_RELOAD/CAPACITY_DEGRADED|PASS|PARTIAL|BLOCKED
PRIMARY=<provider:model>
FALLBACKS=<ordered provider:model list>
CONFIG_SHA=<per profile>
SERVICES=<unit PID active/substate restarts cgroup profile>
PROBES=<primary/fallback exact probes and logs>
DEFAULT_ROUTE=<session model or exact marker>
CAPACITY_BOUNDARY=<quota/rate-limit/auth if any>
NOT_CLAIMING=<e.g. provider quota availability>
```

## Pitfalls

- Do not claim default-route proof from exit code alone. Read the output log and marker count.
- Do not silently add an extra third fallback provider when the user asked for a single fallback.
- Do not treat fallback provider quota exhaustion as a reason to revert the requested configuration.
- Do not print secrets while proving provider availability; use markers, hashes, counts, and safe config fields only.
- Be explicit when a profile alias causes another profile name to show the same model in `hermes profile list`.
