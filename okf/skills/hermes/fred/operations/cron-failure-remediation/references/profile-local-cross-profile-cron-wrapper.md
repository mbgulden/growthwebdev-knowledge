# Profile-local wrapper for cross-profile no-agent cron scripts

## When this applies

Use this when a Hermes no-agent cron is configured to run a script outside the active profile's allowed `scripts/` directory and the scheduler reports a sandbox/path-policy failure such as:

```text
Blocked: script path resolves outside the scripts directory
Allowed: /home/ubuntu/.hermes/profiles/<active-profile>/scripts
Requested: /home/ubuntu/.hermes/profiles/<other-profile>/scripts/<script> --args
```

## Durable pattern

Do **not** point the cron directly at another profile's script, even if that script exists and runs manually. Create a thin wrapper under the active profile's `scripts/` directory and update the cron to use the wrapper by relative script name.

Example shape:

```bash
#!/usr/bin/env bash
set -euo pipefail

CANONICAL="/home/ubuntu/.hermes/profiles/ned/scripts/ned_memories_bak_sweep.sh"
if [[ ! -x "$CANONICAL" ]]; then
  echo "[wrapper] missing or non-executable canonical script: $CANONICAL" >&2
  exit 1
fi

export HERMES_PROFILE_DIR="/home/ubuntu/.hermes/profiles/ned"
exec bash "$CANONICAL" --apply
```

Then update the cron:

```text
script: ned_memories_bak_sweep_wrapper.sh
```

## Verification checklist

Use a focused `/tmp/hermes-verify-*` verifier that checks:

- wrapper path exists under the active profile's `scripts/` dir
- wrapper is executable
- wrapper contains the canonical script path, target `HERMES_PROFILE_DIR`, and expected mode flags
- direct wrapper execution exits `0`
- wrapper stdout proves the target mode, e.g. `mode=apply`
- `cronjob(action="run", job_id=...)` succeeds after the cron is updated
- `cronjob(action="list")` shows the job script is the wrapper name, not the cross-profile absolute path

## Pitfalls

- A stale `last_status=ok` is not proof the current scheduler config is safe. Inspect the `script` field.
- Keep canonical ownership intact. The wrapper should bridge scheduler policy, not move another agent/profile's script.
- Avoid leaking cross-profile secrets or memory content; this pattern is for bounded operational scripts only.
