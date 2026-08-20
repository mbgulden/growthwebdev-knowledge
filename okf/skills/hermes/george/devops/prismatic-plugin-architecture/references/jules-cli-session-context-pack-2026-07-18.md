# Jules CLI Session Context Pack — 2026-07-18

## Why this matters

Jules dispatch should use the installed Jules CLI contract, not AGY's print-mode contract. During the session, live `jules new --help` showed Jules is async/session-based:

```text
jules new "task"
jules new --repo owner/repo "task"
jules remote list --session
jules remote pull --session <session_id>
```

The dispatcher previously used an unsupported shape:

```text
jules --issue <id> --task <task>
```

That is the wrong class of launch for this CLI.

## Recommended implementation shape

```text
assigned-agent event
→ write Jules context directory
→ CONTEXT_PACK.md + WORK_PACKET.md + PACKET_CONTRACT.md
→ launch tiny `jules new <compact prompt>`
→ optional PRISMATIC_JULES_REPO maps to `jules new --repo owner/repo <prompt>`
→ capture stdout/stderr to a durable session log
→ store context-pack paths + session log + reconcile hint in launch_records.execution_context
→ later reconcile with `jules remote list --session` and `jules remote pull --session <id>`
→ normalize pulled result into completed-work packet contract
```

## Context files

- `CONTEXT_PACK.md` explains that Jules uses `jules new` and must not use unsupported AGY-style flags.
- `WORK_PACKET.md` contains the bounded review/test scope, skill-pack state, expected/blocked markers, compact proof shape, and non-claims.
- `PACKET_CONTRACT.md` maps Jules async session output into the shared Prismatic completed-work contract.

## Launch-record metadata

Store JSON in `launch_records.execution_context` with at least:

```json
{
  "agent": "jules",
  "identifier": "GRO-...",
  "context_pack_dir": "/tmp/prismatic-agent-runs/jules-...-context",
  "context_pack": {
    "context_pack": ".../CONTEXT_PACK.md",
    "work_packet": ".../WORK_PACKET.md",
    "packet_contract": ".../PACKET_CONTRACT.md"
  },
  "session_capture_log": "/tmp/prismatic-agent-runs/jules-...log",
  "expected_marker": "JULES_ASSIGNED_AGENT_<ID>_OK",
  "blocked_marker": "JULES_ASSIGNED_AGENT_<ID>_BLOCKED",
  "reconcile_hint": "jules remote list --session && jules remote pull --session <session_id>",
  "marker": "JULES_CLI_SESSION_CONTEXT_PACK_OK"
}
```

## Verification pattern

Use a fake Jules binary that exits nonzero if unsupported flags appear. Assert:

- command uses `jules new`;
- command does not include `--issue`, `--task`, `--print`, `--log-file`, or `--model`;
- session capture log includes `JULES_SESSION_CAPTURE_STARTED`, context/work packet paths, skill-pack state, and fake session output;
- context files exist and include `JULES_CLI_SESSION_CONTEXT_PACK_OK`, `jules new <compact prompt>`, and unsupported flag warnings;
- token-like assignment text is redacted from all context files.

## Reporting boundary

A fake Jules verifier proves dispatcher command shape and capture/reconcile metadata. It does **not** prove a live Google Jules remote session, production deploy, live Linear mutation, auto-merge, or canonical full-suite green.
