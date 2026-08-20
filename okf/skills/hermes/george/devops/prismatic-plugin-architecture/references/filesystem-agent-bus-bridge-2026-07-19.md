# Filesystem agent bus bridge — 2026-07-19

Session-specific implementation notes for the interim Prismatic Kai/Fred/George coordination bridge.

## Why this exists

Telegram lane groups are useful for human/operator visibility, but Telegram bot-to-bot delivery is not reliable enough to use as the machine dispatch bus. A George bot message visible in a group may not be delivered as an inbound update to Kai/Fred bots. The interim fix is:

```text
George writes filesystem context pack
→ per-agent worker/timer claims exactly one task
→ Hermes launches target profile with a small pointer prompt
→ target writes RESULT.md
→ George audit timer detects outbox result
→ Telegram receives lifecycle/status mirrors only
```

## Active paths

```text
ROOT=/home/ubuntu/prismatic-agent-bus
SCRIPT=/home/ubuntu/prismatic-agent-bus/bin/prismatic_agent_bus.py
DOC=/home/ubuntu/prismatic-agent-bus/README.md
```

Directory shape:

```text
inbox/<agent>/      queued context packs
claimed/<agent>/    atomically claimed packs
outbox/<agent>/     RESULT.md packets
failed/<agent>/     failed claimed packs
archive/<agent>/    completed claimed packs
logs/               launcher/notification logs
state/              locks and audit seen-state
```

## Systemd timers

```text
prismatic-agent-bus-kai.timer
prismatic-agent-bus-fred.timer
prismatic-agent-bus-george-audit.timer
```

Each timer runs about every 60s. Workers are oneshot services and should be inactive/dead after a no-op pass, or activating/running while an agent LLM task is active.

## Dispatch commands

```bash
python3 /home/ubuntu/prismatic-agent-bus/bin/prismatic_agent_bus.py dispatch \
  --agent kai \
  --marker ONE_AGENT_OPERATOR_VERIFICATION_LOOP_OK \
  --task-file /home/ubuntu/prismatic-kai-dispatch-ONE_AGENT_OPERATOR_VERIFICATION_LOOP_OK-2026-07-19.md

python3 /home/ubuntu/prismatic-agent-bus/bin/prismatic_agent_bus.py dispatch \
  --agent fred \
  --marker INVALID_PACKET_REPAIR_QUEUE_OK \
  --task-file /home/ubuntu/prismatic-fred-dispatch-INVALID_PACKET_REPAIR_QUEUE_OK-2026-07-19.md
```

## Context-pack contract

Each task directory contains:

```text
TASK.md
PACKET_CONTRACT.md
CONTEXT.json
STATUS.json
```

`CONTEXT.json` defaults all real side effects to false:

```json
{
  "merge": false,
  "deploy": false,
  "linear_writeback": false,
  "github_pr_create": false,
  "auto_merge": false,
  "bulk_dispatch": false,
  "production_restart": false
}
```

Expected result path:

```text
outbox/<agent>/<task_id>/RESULT.md
```

Required packet fields:

```text
COMMAND=
RESULT=
LOG=
SCOPE=
AD_HOC_OR_CANONICAL=
NOT_CLAIMING=
MARKER=
```

## Important implementation pitfall

Systemd worker units may not have `/home/ubuntu/.local/bin` on `PATH`. The bridge script should use an absolute Hermes binary path:

```text
/home/ubuntu/.local/bin/hermes
```

Do not encode the lesson as “Hermes command not found”; the durable lesson is: systemd worker scripts should use absolute paths or explicitly set PATH.

## Verification

```bash
python3 -m py_compile /home/ubuntu/prismatic-agent-bus/bin/prismatic_agent_bus.py
python3 /home/ubuntu/prismatic-agent-bus/bin/prismatic_agent_bus.py verify
systemctl list-timers --all 'prismatic-agent-bus-*' --no-pager
```

The `verify` command performs a George-only dry-run canary and should not launch Kai/Fred LLM work. Expected marker:

```text
FILESYSTEM_AGENT_BUS_BRIDGE_OK
```

## Current boundary

This is an interim bridge, not canonical Prismatic assigned-agent dispatch. It does not itself authorize merges, deploys, real Linear/GitHub side effects, auto-merge, bulk dispatch, or production restarts.
