# Delegation chains (parent -> child handoff graph)

The handoff file is most useful when one agent hands work to another. The graph stays traceable because each child records its parent.

## Example: orchestrator -> AGY -> orchestrator

### Turn 1 — orchestrator decides to delegate

Orchestrator writes its own handoff with `next_action` pointing at AGY:

```json
{
  "agent": "fred",
  "current_state": {
    "one_line": "Delegating AGY Golden Thread remediation to AGY lane.",
    "energy_phase": "fresh"
  },
  "next_action": {
    "title": "Hand off AGY remediation; expect AGY handoff in 5-10 min.",
    "first_command": "agy run --from-handoff ~/.hermes/profiles/orchestrator/state/current.json"
  }
}
```

The dispatch payload to AGY includes `parent_handoff_path` so AGY can inherit.

### Turn 2 — AGY runs, writes its own handoff

AGY's profile lives at `~/.hermes/profiles/agy/state/current.json`. AGY writes:

```json
{
  "agent": "agy",
  "agent_profile": "agy",
  "extends": {
    "parent_agent": "fred",
    "parent_handoff_path": "/home/ubuntu/.hermes/profiles/orchestrator/state/current.json",
    "inherited_decisions": [
      "Use existing remediation rows from AGY Golden Thread 2026-07-27 cron output",
      "Do not create new dispatch:ready labels outside the AGY lane"
    ]
  },
  "current_state": {
    "one_line": "AGY applied 6 of 8 remediation rows; 2 blocked on Linear rate limit.",
    "energy_phase": "in_sprint"
  },
  "executed_since_last_handoff": [
    {"kind": "linear_mutation", "what": "Updated 6 Linear issues with remediation comments", "ref": "GRO-4318..GRO-4323"}
  ]
}
```

### Turn 3 — orchestrator resumes

Orchestrator reads its own handoff, sees `next_action` is done, reads AGY's handoff via `extends.parent_handoff_path` chain, and updates its own `next_action` to verify.

```bash
HAND=~/.hermes/profiles/orchestrator/skills/agent-operations/session-state-handoff/scripts/handoff.py
python3 $HAND read --profile agy --next-action
```

## Anti-patterns

- **Child writes over parent's handoff.** Each profile owns its own `current.json`. Children only reference parents via `extends`.
- **Parent writes child work into its own handoff.** The child's `executed_since_last_handoff` is the source of truth for child work. Parent's handoff only needs a one-line summary plus a reference.
- **Delegation chain without `extends`.** If you forget `extends.parent_handoff_path`, the parent cannot audit the chain. Treat `extends` as a required field for child writes that follow delegation.
- **Handoff files in source control.** They are transient. The archive is for forensic recovery only; do not commit `.hermes/profiles/*/state/` to git.

## Audit recipe

To reconstruct "what did the orchestrator hand off to AGY last Tuesday":

```bash
ls -la ~/.hermes/profiles/orchestrator/state/archive/ | grep fred
# Pick a file, open it, look at next_action and extends
ls -la ~/.hermes/profiles/agy/state/archive/ | grep agy
# Cross-reference with extends.parent_handoff_path
```

This is far cheaper than parsing Linear activity streams for "who initiated what."
