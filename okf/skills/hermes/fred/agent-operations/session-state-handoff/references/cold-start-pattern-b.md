# Pattern B — Provider-Agnostic Cold-Start Wiring

**Status: deferred. Adopt Pattern A today. Revisit this when the documented hooks land.**

This document captures the design and triggers for Pattern B so we can pick it up later without re-deriving the trade-offs.

## Why Pattern A is the right choice right now

Pattern A wires the handoff into Hermes via the `prefill_messages_file` config key. That key is real, documented, and verified by `hermes config check`. It works today on every running profile (DORMANT — see critical finding in cold-start-integration.md).

The downside: it depends on Hermes injecting the prefill messages file at every LLM call. If a future Hermes version drops the key, every profile silently regresses.

## Why Pattern B is the future-facing choice

Pattern B is provider-agnostic at the runtime layer: it doesn't depend on any Hermes-specific config key. It uses Hermes's documented plugin hook system (`pre_llm_call`) to inject context.

The current blocker: [NousResearch/hermes-agent#2817](https://github.com/NousResearch/hermes-agent/issues/2817) — "`pre_llm_call`, `post_llm_call`, `on_session_start`, `on_session_end` are documented but never invoked." Until that issue closes, Pattern B is a no-op.

## Pattern B design (when #2817 lands)

### Plugin layout

```
~/.hermes/plugins/session-state-handoff-cold-start/
├── plugin.yaml          # manifest: name, version, hooks
├── __init__.py          # register(ctx)
└── coldstart.py         # the actual callback
```

### plugin.yaml

```yaml
name: session-state-handoff-cold-start
version: "1.0"
description: "Injects the active session handoff's current_state.one_line into every cold turn."
hooks:
  - pre_llm_call
  - on_session_start
```

### __init__.py

```python
import json, os, subprocess
from pathlib import Path

HAND = "/home/ubuntu/.hermes/profiles/orchestrator/skills/agent-operations/session-state-handoff/scripts/handoff.py"

def _profile_from_kwargs(kwargs) -> str:
    return (
        kwargs.get("profile")
        or os.environ.get("HERMES_PROFILE")
        or "orchestrator"
    )

def _read_one_line(profile: str) -> str:
    try:
        r = subprocess.run(
            ["python3", HAND, "read", "--profile", profile, "--one-line"],
            capture_output=True, text=True, timeout=5,
        )
        if r.returncode == 0:
            return r.stdout.strip()
    except Exception:
        pass
    return ""

def _on_session_start(kwargs):
    profile = _profile_from_kwargs(kwargs)
    one_line = _read_one_line(profile)
    if one_line:
        print(f"[session-handoff:{profile}] {one_line}", flush=True)
    return None

def _pre_llm_call(kwargs):
    profile = _profile_from_kwargs(kwargs)
    one_line = _read_one_line(profile)
    if not one_line:
        return None
    return {
        "context": (
            f"[session-handoff for profile '{profile}'] "
            f"Previous session greeting: \"{one_line}\". "
            "Open the next turn by acknowledging it briefly, then ask for the next instruction."
        )
    }

def register(ctx):
    ctx.register_hook("on_session_start", _on_session_start)
    ctx.register_hook("pre_llm_call", _pre_llm_call)
```

### Install

```bash
mkdir -p ~/.hermes/plugins/session-state-handoff-cold-start
# drop the three files above in
hermes plugins reload   # or restart the gateway
```

### Why this is better than Pattern A long-term

- Survives a `prefill_messages_file` config-key removal.
- Works with any LLM provider, including ones Hermes hasn't shipped a config key for yet.
- Single source of truth for "what context does this session start with" — visible in the plugin, not split across 6 config files.
- Hooks can ALSO write the handoff at session end (`on_session_end`), closing the loop without a separate cron or agent turn.

## Migration checklist (when we flip from A to B)

1. Confirm `gh issue NousResearch/hermes-agent 2817` is closed.
2. Install the plugin from the layout above into `~/.hermes/plugins/session-state-handoff-cold-start/`.
3. Run a controlled profile-by-profile flip (one profile at a time, not all-at-once):
   - Set its `prefill_messages_file` to empty in config.
   - Enable the plugin for that profile.
   - Verify the cold-start greeting still fires (end-to-end test above).
   - If green, move to next profile.
4. After all profiles pass, remove the wire_cold_start.py integration.
5. Land a release note in OKF (we'll create the OKF doc at that time).

## Why I'm not doing this today

I cannot prove Pattern B works without first fixing #2817. Wires that fail silently are worse than wires I can prove with `config check`. Pattern A is provable today, on every profile, with the same verifier script that already passed.

When #2817 lands, this doc becomes the migration plan.

## Triggers to revisit

Re-evaluate Pattern B when **any** of:

- #2817 is closed and the documented hooks actually fire.
- A new Hermes version drops `prefill_messages_file` from config (unlikely but possible).
- We add a third LLM provider where the prefill key has never been tested.
- A profile's cold-start greeting stops working and `hermes config check` shows no error — that's a silent regression Pattern A cannot detect, and Pattern B would surface it via a hook firing/not-firing.

## Durable storage

This document lives at:

```
~/.hermes/profiles/orchestrator/skills/agent-operations/session-state-handoff/references/cold-start-pattern-b.md
```

It is **not** auto-promoted to OKF today because Pattern B is not yet active. When we flip, copy this to OKF and replace it with a short pointer.
