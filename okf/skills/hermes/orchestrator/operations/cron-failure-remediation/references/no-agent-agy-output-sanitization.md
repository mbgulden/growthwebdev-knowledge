# No-agent AGY/LLM output sanitization

## When this applies

Use this pattern when a `no_agent` cron script invokes AGY/Codex/Claude or another agent CLI and the scheduler can deliver stdout directly to Telegram or another user-facing channel.

Typical symptom: the cron is technically `last_status=ok`, but the delivered message contains model scratchpad such as:

```text
I am going to check the contents of the current workspace directory...
I will view ...
Let me inspect ...
[NIGHTLY-BACKLOG] AGY exit: 0
An update was received from a background task...
Task `...` completed. Output:
```

## Durable rule

A no-agent cron stdout stream is a user-facing product surface. Never pass raw AGY/LLM/CLI output through to scheduler delivery.

Allowed stdout:

- A compact blocker table.
- A short recommendation line.
- A deterministic fallback report when the agent CLI is unavailable or only returns chatter.
- Nothing at all for green/no-delta/all-clear.

Disallowed stdout:

- `I am going to...`, `I will...`, `Let me...`, `Now I...` progress narration.
- Local diagnostics like `[JOB] AGY exit: 0`.
- Background task scaffolding.
- Green pulses when the desired behavior is silence.
- Raw auth/OAuth URLs from failed headless CLI runs.

## Implementation sketch

Add sanitizer helpers to the cron producer rather than relying on prompts alone:

```python
AGY_SCRATCHPAD_PREFIXES = (
    "i am going to ",
    "i'm going to ",
    "i will ",
    "i'll ",
    "let me ",
    "now i ",
    "next i ",
    "i need to ",
    "i should ",
    "i want to ",
)


def sanitize_agent_output(output: str) -> str:
    cleaned = []
    in_fence = False
    for raw in output.replace("\r", "\n").splitlines():
        line = raw.strip()
        if not line:
            continue
        lowered = line.lower()
        if line.startswith("```"):
            in_fence = not in_fence
            cleaned.append(line)
            continue
        if not in_fence and lowered.startswith(AGY_SCRATCHPAD_PREFIXES):
            continue
        if not in_fence and lowered.startswith("[nightly-backlog]"):
            continue
        if not in_fence and lowered.startswith("an update was received from a background task:"):
            continue
        if not in_fence and line.startswith("[20") and "Task `" in line:
            continue
        if not in_fence and lowered in {"thinking...", "working...", "processing...", "done fetching delta issues details."}:
            continue
        cleaned.append(line)
    return "\n".join(cleaned).strip()


def has_user_facing_signal(output: str) -> bool:
    text = output.strip()
    if not text:
        return False
    try:
        data = json.loads(text.strip("`\n "))
        if isinstance(data, dict) and data.get("status") == "green":
            return True
    except Exception:
        pass
    lowered = text.lower()
    return any(marker in text for marker in ("|", "###", "GRO-")) or any(
        word in lowered for word in ("blocker", "blocked", "gap", "remediation", "recommendation")
    )
```

Green/no-delta branch should be truly silent:

```python
if not delta:
    save_snapshot(current)
    mark_completed()
    sys.exit(0)  # no stdout
```

When the CLI fails or only returns non-user-facing chatter, emit a deterministic fallback table instead of raw output:

```python
output_user = sanitize_agent_output(raw_output)
if is_green:
    pass  # no stdout
elif has_user_facing_signal(output_user):
    print(output_user)
else:
    print(render_deterministic_delta(compact_delta))
```

## Verification checklist

Create a fresh OS-safe tempfile verifier under `/tmp` using `tempfile.mkstemp(prefix="hermes-verify-", suffix=".py", dir="/tmp")` and clean it up.

The verifier should assert:

1. `python3 -m py_compile` passes for the changed script.
2. The script is executable if it is called directly by the scheduler.
3. Scratchpad fixture sanitizes to empty:
   - `[JOB] AGY exit: 0`
   - `I am going to...`
   - `I will...`
   - `Let me...`
4. Background-task fixture strips scaffolding but preserves the markdown table and recommendation.
5. Deterministic fallback includes the issue identifier and compact gap table.
6. Direct live no-delta run exits `0` with `stdout == ''` and `stderr == ''`.
7. Cron config still points at the intended script with `no_agent: true` and `last_status: ok`.
8. Latest scheduler output contains either `silent (empty output)` or the sanitized user-facing table, and does not contain scratchpad phrases.

Report as ad hoc targeted verification, not full suite green.

## Pitfall

Do not treat `last_status=ok` as enough. This failure class is about *output quality*, not process exit status. A successful run that delivers scratchpad to Telegram is still broken.
