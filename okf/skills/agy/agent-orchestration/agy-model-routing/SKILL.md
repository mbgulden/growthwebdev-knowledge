---
name: agy-model-routing
description: Dynamic routing and fallback of AGY tasks across Gemini and Claude engines based on complexity and context window size.
version: 2.0.0
---

# AGY Model Routing

Select and verify the correct model routing CLI parameters for AGY tasks to optimize speed, context size, and accuracy.

## Trigger Conditions

Use this skill whenever launching a task on the Antigravity CLI (`agy`) or specifying model labels in Linear issues to be picked up by the dispatcher.

## Numbered Steps with Exact Commands

1. **Verify active model configuration**:
   Read the model bindings and fallbacks:
   ```bash
   cat $HOME/.antigravity/config.json
   ```
   **SANDBOX SAFETY:** Never use `~/` — always use `$HOME/` or the absolute path `/home/ubuntu/.antigravity/config.json`. The `~` shortcut resolves to the sandbox container's home, not the host machine's home.

2. **Select model by task type**:
   - Routine/low complexity: Use `gemini-3.5-flash-medium` (`agent:agy`)
   - Moderate complexity/debugging: Use `gemini-3.5-flash-high` (`agent:agy-flash-high`)
   - Large codebase context/deep reasoning: Use `gemini-3.1-pro-high` (`agent:agy-pro`)
   - High precision coding/refactoring: Use `claude-sonnet-4.6-thinking` (`agent:agy-sonnet`)
   - Elusive bugs/deep thinking: Use `claude-opus-4.6-thinking` (`agent:agy-thinking`)

3. **Execute CLI command with explicit model flag**:
   ```bash
   # Routine task. Current AGY 1.1.4 expects display model labels, not slug strings.
   /home/ubuntu/.local/bin/agy --model "Gemini 3.5 Flash (Medium)" --print "smoke test"
   
   # Large context query
   /home/ubuntu/.local/bin/agy --model "Gemini 3.1 Pro (High)" --add-dir /home/ubuntu/work/project --print "Find all places handling OAuth"
   ```

4. **Verify routing in logs**:
   Check the dispatcher logs or active model bindings:
   ```bash
   grep -i "model" /home/ubuntu/.antigravity/config.json
   ```

## Model String Reference (Golden — from `agy models` CLI)

| Label | CLI Model String | Use Case |
|---|---|---|
| `agent:agy` | `Gemini 3.5 Flash (Medium)` | Default — fast, cheap, good |
| `agent:agy-flash-high` | `Gemini 3.5 Flash (High)` | Moderate complexity, debugging |
| `agent:agy-pro` | `Gemini 3.1 Pro (High)` | Large context, deep reasoning |
| `agent:agy-sonnet` | `Claude Sonnet 4.6 (Thinking)` | Precision coding, refactoring |
| `agent:agy-thinking` | `Claude Opus 4.6 (Thinking)` | Elusive bugs, architecture |

**NOTE:** The old string `gemini-3.5-pro` does NOT exist. It was a phantom model that silently fell back to flash. Current AGY 1.1.4 rejects slug strings such as `gemini-3.5-flash-medium`; use display labels from `agy models`.

## Pitfalls

- **Display Names vs. slug strings**: Current AGY 1.1.4 requires display names from `agy models` (e.g. `Gemini 3.5 Flash (Medium)`) in `--model`. Slug strings can be valid in dispatcher config, but not this CLI flag.
- **Sandbox `~` Trap**: Never use `~/` paths in commands. Use `$HOME/` or `/home/ubuntu/` absolute paths. The dispatcher and sub-agents run in sandboxed containers where `~` resolves to `/root` or `/sandbox`, NOT `/home/ubuntu`.
- **Missing config.json**: If `$HOME/.antigravity/config.json` is missing, the dispatcher silently falls back to default settings without routing. Verify with `cat $HOME/.antigravity/config.json`.
- **Quota Exceeded Stalls**: Premium models (thinking/pro) might hit rate limits. If a task stalls, the fallback chain (`gemini-3.5-flash-high` → `gemini-3.5-flash-medium`) activates automatically.

## Verification Steps

- Run the following smoke test to verify model routing capability:
  ```bash
  /home/ubuntu/.local/bin/agy --model "Gemini 3.5 Flash (Medium)" --print "Respond with: ROUTING_OK"
  ```
- Ensure the output contains `ROUTING_OK` and doesn't throw a parsing error.
