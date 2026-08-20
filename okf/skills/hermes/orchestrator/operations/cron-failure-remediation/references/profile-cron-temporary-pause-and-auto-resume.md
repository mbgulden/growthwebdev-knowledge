# Temporary profile-cron pause during live bot overload

## When this applies

Use this when a Hermes profile/gateway is technically healthy but feels slow or wedged, and the user asks whether profile crons should be paused.

## Durable lesson

Do not assume crons are the cause. First prove the active bottleneck:

- gateway/service state
- profile model/provider
- recent `agent.log` API-call latency and context size
- recent tool calls with long durations
- Telegram flood-control warnings
- profile cron list and latest cron outputs
- host load/memory/processes

A no-agent cron that runs silently every 15 minutes is usually not a large model latency driver, but pausing it can still be a useful short-lived lane-clearing mitigation while a live bot handles a large context/tool-heavy task.

## Safe mitigation pattern

1. Inspect target profile crons directly:

```bash
hermes --profile <profile> cron list
python3 - <<'PY'
from pathlib import Path
import json
profile='<profile>'
p=Path(f'/home/ubuntu/.hermes/profiles/{profile}/cron/jobs.json')
print(json.dumps(json.loads(p.read_text()), indent=2))
PY
```

2. If a noncritical watcher is active and the user wants speed relief, pause the exact job:

```bash
hermes --profile <profile> cron pause <job_id>
hermes --profile <profile> cron list
```

3. Do not leave governance blind indefinitely. Create a **local no-agent one-shot resume** under the active profile `scripts/` directory:

```bash
cat > /home/ubuntu/.hermes/profiles/<active-profile>/scripts/resume_<profile>_<job>_once.sh <<'SH'
#!/usr/bin/env bash
set -euo pipefail
/home/ubuntu/.local/bin/hermes --profile <profile> cron resume <job_id> >/dev/null
/home/ubuntu/.local/bin/hermes --profile <profile> cron list | sed -n '1,80p'
SH
```

Then schedule it locally:

```python
cronjob(action='create', name='Resume <profile> <job>', schedule='2h', repeat=1,
        deliver='local', no_agent=True, script='resume_<profile>_<job>_once.sh')
```

4. Verify with `/tmp/hermes-verify-*`:

- resume script exists and passes `bash -n`
- script includes strict mode and targets the exact profile/job id
- target job is paused now
- one-shot resume cron exists, is enabled/scheduled, `no_agent=True`, `deliver=local`, `repeat.times=1`

Report this as ad hoc targeted verification only.

## Pitfalls

- Do not call this a root-cause fix unless logs prove the cron was consuming resources.
- Do not pause a critical watcher without an automatic or explicitly user-approved resume path.
- Do not use broad `cron pause` or remove jobs when the user asked only whether to relieve slowness.
- Do not leave resume helper scripts unverified; `bash -n` and job-target assertions are enough for the helper contract.