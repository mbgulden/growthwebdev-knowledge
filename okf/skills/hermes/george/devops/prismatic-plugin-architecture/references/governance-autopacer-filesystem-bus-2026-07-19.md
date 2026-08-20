# Governance autopacer over filesystem agent bus — 2026-07-19

## Class lesson

When Michael asks George to “keep going,” “always on,” or continue issuing boring governance prompts until Kai/Fred finish a governance system, do not interpret that as permission for uncontrolled bulk/autonomous side effects.

Use a conservative autopacer over the filesystem agent bus:

```text
North Star backlog
→ one active marker per agent lane
→ filesystem context pack dispatch
→ agent worker writes RESULT.md
→ George auditor writes GEORGE_AUDIT.md
→ autopacer advances only after accepted audit state
→ stop/pause lane on FAIL/BLOCKED
```

Telegram remains a status mirror. The filesystem bus is the machine handoff channel.

## Implementation shape used

Files:

```text
/home/ubuntu/prismatic-agent-bus/state/governance-backlog.json
/home/ubuntu/prismatic-agent-bus/state/governance-autopacer-state.json
/home/ubuntu/prismatic-agent-bus/bin/prismatic_governance_autopacer.py
/etc/systemd/system/prismatic-governance-autopacer.service
/etc/systemd/system/prismatic-governance-autopacer.timer
/home/ubuntu/prismatic-agent-bus/logs/governance-autopacer.log
/home/ubuntu/prismatic-agent-bus/prompts/governance/*.md
```

Systemd cadence used:

```text
OnBootSec=2min
OnUnitActiveSec=5min
AccuracySec=30s
```

Core safety rules:

- one active task per agent lane;
- dispatch only when `inbox/<agent>` and `claimed/<agent>` are empty;
- continue only from backlog entries, not model improvisation;
- require previous historical marker/audit before starting the next governance marker;
- record dispatched markers in state to avoid duplicate dispatch;
- pause a lane on `FAIL` or `BLOCKED` audit;
- keep real side effects false in the context pack: merge/deploy/Linear/GitHub/auto-merge/bulk/production restart all false;
- notify Telegram with exact handles, but do not rely on Telegram bot-to-bot wake-up.

## North Star backlog pattern

The backlog should be boring governance work that compounds toward dashboard-visible operator decisions:

```text
agent output / plugin action
→ packet / policy / proof / artifact / audit event
→ dashboard-visible operator decision
→ no real side effects without approval
```

Useful lane split from this session:

Kai lane — golden-path governance spine:

```text
GOVERNANCE_PROMOTION_DECISION_READ_MODEL_OK
DASHBOARD_GOVERNANCE_DECISION_QUEUE_OK
GOVERNANCE_EVIDENCE_LEDGER_API_OK
GOVERNANCE_POLICY_APPROVAL_GATE_OK
GOVERNANCE_SYSTEM_STITCHING_SMOKE_OK
```

Fred lane — adjacent boring hardening:

```text
INVALID_PACKET_REPAIR_DASHBOARD_VISIBILITY_OK
HANDOFF_PACKET_CONTRACT_HARDENING_OK
GOVERNANCE_NO_SECRET_POLICY_GATES_OK
GOVERNANCE_AUDIT_EVENT_HISTORY_OK
GOVERNANCE_DASHBOARD_CONTROL_GUARDRAILS_OK
```

## Prompt contract

Each autopaced prompt should include:

- exact agent handle (`@KaiactiveOahu_bot` or `@FredTheBotFredTheBot`);
- owner/lane/marker/title;
- North Star alignment;
- OKF table: Objective, Key Result, Function, Evidence, Promotion Decision;
- allowed and forbidden side effects;
- dashboard-first and no-secret expectations;
- compact verification packet requirement;
- artifact writeback requirement so George can audit via filesystem.

## Verification pattern

After installing or changing the autopacer, verify:

```bash
python3 -m py_compile /home/ubuntu/prismatic-agent-bus/bin/prismatic_governance_autopacer.py
systemctl is-active prismatic-governance-autopacer.timer
systemctl list-timers --all 'prismatic-governance-autopacer.timer' --no-pager
python3 /home/ubuntu/prismatic-agent-bus/bin/prismatic_governance_autopacer.py
```

Then inspect queue state:

```text
inbox/<agent>
claimed/<agent>
outbox/<agent>
archive/<agent>
audits/<agent>
```

Expected marker for the operational proof:

```text
GOVERNANCE_ALWAYS_ON_AUTOPACER_OK
```

Report boundary explicitly: this is ad-hoc targeted process proof, not canonical full-suite green, PR creation, merge, deploy, or writeback.

## Pitfalls

- Do not dispatch the whole backlog at once. “Always on” means paced, not bulk.
- Do not advance only from agent self-report; require filesystem outbox and George audit artifact.
- Do not rely on Telegram messages from George to wake Kai/Fred; Telegram bot-to-bot delivery may be invisible to receiving bots.
- Do not let the autopacer invent new tasks after the backlog is exhausted. Mark lane complete and ask for/derive the next backlog from North Star docs.
- Do not turn a `PARTIAL`, `FAIL`, or `BLOCKED` audit into forward progress without an explicit recovery prompt or Michael authorization.
