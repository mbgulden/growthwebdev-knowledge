# Codex OAuth split-brain auth convergence check

Session-derived recipe for diagnosing the Hermes `openai-codex` split-brain class: `providers["openai-codex"]["tokens"]` diverging from `credential_pool.openai-codex`.

## When to use

Use when a Hermes profile reports Codex OAuth failures after re-auth, model switching failures, `token_invalidated`, missing-authentication 401s, or when asked to repair a known split-brain storage bug.

## Safety boundary

- Do not print access tokens, refresh tokens, API keys, Authorization headers, complete `.env`, or complete `auth.json`.
- Do not copy credentials into profile-local stores.
- Do not clear global auth or re-run interactive auth if exact model probes already pass.
- Do not restart a gateway carrying the current conversation.

## Secret-safe structural check

Use fingerprints only:

```bash
python - <<'PY'
import json, hashlib
from pathlib import Path
p=Path('/home/ubuntu/.hermes/auth.json')
d=json.loads(p.read_text())
prov=(d.get('providers') or {}).get('openai-codex') or {}
sing=prov.get('tokens') or {}
cp=d.get('credential_pool') or {}
if isinstance(cp.get('credential_pool'), dict):
    cp=cp['credential_pool']
pool=cp.get('openai-codex') or []
def fp(v): return hashlib.sha256(v.encode()).hexdigest()[:16] if isinstance(v,str) and v else 'NONE'
af=fp(sing.get('access_token'))
rf=fp(sing.get('refresh_token'))
print('POOL_COUNT='+str(len(pool)))
print('SINGLETON_ACCESS_MATCH_INDEXES='+','.join(str(i) for i,e in enumerate(pool) if isinstance(e,dict) and fp(e.get('access_token') or e.get('credential'))==af))
print('SINGLETON_REFRESH_MATCH_INDEXES='+','.join(str(i) for i,e in enumerate(pool) if isinstance(e,dict) and fp(e.get('refresh_token'))==rf))
print('POOL_ERROR_ENTRY_COUNT='+str(sum(bool(e.get('last_error_code') or e.get('last_error_message') or e.get('last_error_reason')) for e in pool if isinstance(e,dict))))
PY
```

Interpretation:

- If at least one pool entry matches both singleton access and refresh fingerprints and has no OAuth error markers, the stores are converged.
- Multiple pool entries can be valid; independent accounts must not be overwritten merely because they share `source=manual:device_code`.
- A literal `ja` request may mean JSON parsing; verify whether `jq` is present before installing anything. Prefer `jq -e` for deterministic shell JSON parse checks.

## Exact model-switch probes

Do not rely on config readback or discovery alone. Run two exact probes through the target profile/provider:

```bash
hermes --profile <profile> -m <model-a> --provider openai-codex -z 'Reply with exactly: HERMES_CODEX_A_OK'
hermes --profile <profile> -m <model-b> --provider openai-codex -z 'Reply with exactly: HERMES_CODEX_B_OK'
```

A successful pair proves the runtime credential path and model switching are functioning for that account/profile. Preserve log paths and hashes; do not paste token-bearing logs.

## Source-code sanity check

For Hermes versions that include the fix, `hermes_cli/auth.py` should expose behavior equivalent to:

- `_sync_codex_pool_entries(...)` mirrors fresh Codex re-auth into applicable credential-pool entries;
- `resolve_codex_runtime_credentials(...)` falls back between singleton and pool stores;
- independently authenticated accounts are not broadly overwritten.

Docs and installed code can differ; inspect the installed package only for behavior, not token data.

## Gateway ownership is a separate layer

If OAuth probes pass but the gateway is unhealthy, separate auth from service ownership:

```bash
systemctl show <unit> -p ActiveState -p SubState -p MainPID -p NRestarts -p ExecMainStatus --no-pager
systemctl cat <unit> --no-pager
cat /proc/<pid>/cgroup
```

A duplicate gateway error such as `Gateway already running (PID ...)` indicates process ownership drift, not split-brain OAuth. If the running PID is in another profile's service cgroup, stop and report `BLOCKED_CROSS_PROFILE_PROCESS_OWNERSHIP`; do not kill/restart from the current chat without explicit scoped authorization.

## Proof packet

```text
JSON_PARSER=<jq path/version or requested tool boundary>
AUTH_STORE=<global path redacted>
POOL_COUNT=<n>
SINGLETON_POOL_PAIR_MATCH_INDEXES=<indexes>
SPLIT_BRAIN_DETECTED=<true|false>
OAUTH_ERROR_ENTRY_COUNT=<n>
MODEL_PROBE_A=<PASS|FAIL>
MODEL_PROBE_B=<PASS|FAIL>
GATEWAY_STATE=<active/running or separate blocker>
RESULT=<PASS_OAUTH|BLOCKED_AUTH|PASS_OAUTH/BLOCKED_GATEWAY_OWNERSHIP>
NOT_CLAIMING=<auth rewrite/restart/re-auth if not performed>
MARKER=HERMES_CODEX_AUTH_CONVERGENCE_CHECK
```
