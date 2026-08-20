# GRO-3609 redispatch refresh: finalize unlock owner + prefixed JSON pitfall

Session: 2026-07-11 redispatch refresh for an already-finalized Ned issue.

## Durable lessons

### 1) `finalize_task.sh` can report unlock success for the wrong lock owner

Observed transcript:

```text
[finalize] STEP 2: unlocking files in swarm lock registry
[finalize]   UNLOCKED: scripts/silent_cron_detector.py ← prismatic-engine
[finalize]   UNLOCKED: prismatic/tests/test_silent_cron_detector.py ← prismatic-engine
[finalize]   UNLOCKED: scripts/ops/README.md ← prismatic-engine
```

But a follow-up lock query still showed the same paths locked by `ned`:

```text
scripts/silent_cron_detector.py                ned
prismatic/tests/test_silent_cron_detector.py   ned
scripts/ops/README.md                          ned
```

Recovery was to manually unlock with the actual owner:

```bash
node /home/ubuntu/.antigravity/swarm.js unlock scripts/silent_cron_detector.py ned
node /home/ubuntu/.antigravity/swarm.js unlock prismatic/tests/test_silent_cron_detector.py ned
node /home/ubuntu/.antigravity/swarm.js unlock scripts/ops/README.md ned
node /home/ubuntu/.antigravity/swarm.js status
```

Acceptance condition: `No active locks.` Do not trust the finalize transcript alone when the unlock owner in the arrow is not the owner you used when locking.

### 2) Re-query Linear comments with pagination when proving the fresh finalize comment

A short `comments(last: 3)` or default comment query can miss the fresh finalization comment on noisy peer-review threads. For redispatch loops with hundreds of bot comments, paginate comments and search for the timestamp/body marker from finalize output before declaring the Linear evidence missing.

The useful evidence was found by paging `comments(first: 100, after: $cursor)` and scanning for `2026-07-11T05:49:39` / `Ned finalization report`.

### 3) `silent_cron_detector.py --json` may prepend a human summary before JSON

Despite `--json`, the command emitted a banner and summary before the JSON object:

```text
═══ Silent Cron Detector — ... ═══
Loaded ... cron jobs ...
Results:
  ...
{
  "silent_failures": [],
  ...
}
```

For smoke verification, redirect to a file and parse from the first `{`:

```bash
python3 scripts/silent_cron_detector.py --json --no-telegram > /tmp/gro3609-cron.json
python3 - <<'PY'
from pathlib import Path
import json
s = Path('/tmp/gro3609-cron.json').read_text()
payload = json.loads(s[s.find('{'):])
counts = {k: len(v) for k, v in payload.items() if isinstance(v, list)}
print('counts=', counts)
assert counts.get('archived_suppressed', 0) > 0
PY
```

Avoid piping this command directly into a here-doc Python snippet (`cmd | python3 - <<'PY'`): the here-doc consumes Python's stdin, not the pipe, and the producer can hit `BrokenPipeError`. Use a temp file for this verifier shape.
