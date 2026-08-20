---
name: codex-argv-canonical
description: Canonical Codex CLI argv shape for Prismatic Engine lanes (codex-cli 0.132.0).
type: reference
---

# Codex CLI canonical argv (0.132.0)

The argv shape every Prismatic Engine lane that dispatches to Codex MUST build, in this exact order, unless explicitly justified otherwise.

## The argv list

```python
argv = [
    CODEX,                              # /usr/bin/codex (or shutil.which("codex"))
    "-a", "never",                      # global --ask-for-approval=never, BEFORE exec
    "exec",                             # unattended, non-TUI subcommand
    "--json",                           # stream events as JSONL for ingestion
    "--ephemeral",                      # skip ~/.codex/sessions/ persistence
    "--model", "<capability-proven>",   # slug from a live probe
    "--sandbox", "workspace-write",     # read-only | workspace-write | danger-full-access
    "--add-dir", "<explicit-path>",     # additional whitelisted writable dir, no glob
    "-C", "<exact-clean-worktree>",     # primary working directory
    "-o", "<durable-run-dir/last.md>",  # final assistant message path
    PROMPT,                             # issue body + acceptance criteria (single argv element)
]
```

## Per-arg rationale

| Arg | Why | What goes wrong if you change it |
|---|---|---|
| `CODEX` resolved via `shutil.which` | Absolute path; survives PATH changes inside PE | Using bare `codex` works if /usr/bin is on PATH; not guaranteed inside PE |
| `-a never` BEFORE `exec` | `-a/--ask-for-approval` is global; `codex exec --ask-for-approval never ...` fails argv parsing on 0.132.0 | Reviewer caught this exact bug in the first draft |
| `exec` | Unattended, non-TUI. TUI is for interactive use only | Drop into TUI; lane hangs waiting for input |
| `--json` | Streams events as JSONL for the lane to ingest | Plain output is unparseable downstream |
| `--ephemeral` | Don't fill `~/.codex/sessions/`. Host already has 252 rollouts / 7.48 MB | Without `--ephemeral`, dispatch pollutes persistence and makes evidence harder to retain |
| `--model <slug>` | Pin the model per dispatch. CLI string acceptance ≠ availability | Adopting an unprobed model risks 401 / unknown model errors at runtime |
| `--sandbox workspace-write` | Default for code generation. Restrict to `-C` + `--add-dir` | `read-only` blocks any code edits. `danger-full-access` is OUTSIDE PE |
| `--add-dir <path>` | Explicit whitelist alongside `-C`. Single path, repeated flag for multiple | Multiple paths via single comma-list is parsed differently across CLI versions |
| `-C <path>` | Primary worktree. PE should resolve, not the caller | Relative paths or unresolved symlinks break sandbox / git binding |
| `-o <path>` | Final assistant message lands at a known location for ingestion | Without this, the lane must parse the full JSONL to find the terminal message |
| `PROMPT` as one argv element | Avoids quoting hazards; preserves spaces in prompts | Passing prompt via stdin with a TTY/pipe hangs |

## Subprocess call shape

```python
import subprocess, json, pathlib

run_dir = pathlib.Path("/home/ubuntu/.prismatic/run-dispatch/<dispatch_id>")
run_dir.mkdir(parents=True, exist_ok=True)
last_message_path = run_dir / "last-message.md"

argv = [
    "/usr/bin/codex",
    "-a", "never",
    "exec",
    "--json",
    "--ephemeral",
    "--model", "gpt-5",
    "--sandbox", "workspace-write",
    "--add-dir", "/workspace/<explicit-path>",
    "-C", "/workspace/<exact-clean-worktree>",
    "-o", str(last_message_path),
    "<issue body + acceptance criteria as a single string>",
]

proc = subprocess.run(
    argv,
    cwd="/workspace/<exact-clean-worktree>",
    env={**os.environ, "HOME": "<service-home>"},   # see references/codex-service-home-auth.md
    capture_output=True,
    text=True,
    timeout=600,
)

# Parse NDJSON from stdout; persist + ingest each event
for line in proc.stdout.splitlines():
    if not line.strip():
        continue
    event = json.loads(line)
    ingest_event(event, dispatch_id=<dispatch_id>)
```

## Failure-mode table (verified 2026-07-27)

| Symptom | Likely cause | Fix |
|---|---|---|
| `error: unexpected argument found: --ask-for-approval` after `exec` | `-a` placed after `exec` | Move `-a` before `exec` |
| `error: Reconnecting... 1/5 (unexpected status 401 Unauthorized)` | Not logged in | Run `codex doctor --json`; surface to operator; do NOT attempt login from code |
| `Not inside a trusted directory and --skip-git-repo-check was not specified` | Worktree not in `~/.codex/config.toml` trust list | Add `[projects."<path>"] trust_level = "trusted"` to config.toml; do NOT default `--skip-git-repo-check` for repo tasks |
| `Reading additional input from stdin...` (hang) | Stdin is TTY/pipe; no prompt given | Always pass prompt as argv; never pipe interactive stdin in unattended lanes |
| WebSocket fails, HTTPS fallback succeeds | Network/proxy blocking WS | Tolerate; `codex doctor --json` reports `⚠ websocket`; lane must accept HTTPS-fallback path |
| `danger-full-access` blocked by approval policy | Sandbox-vs-approval mismatch | Use `--dangerously-bypass-approvals-and-sandbox` ONLY in externally-sandboxed environments. NEVER from inside PE |

## Pitfalls

- Do NOT include `codex login`, account choice, or credential provisioning in this argv. Login is a separately approved operator action.
- Do NOT mix this skill's CLI path with Hermes `codex-*` profiles. The argv talks to the standalone CLI process; the profile talks to a Hermes gateway. They are not interchangeable.
- Do NOT skip the `--ephemeral` audit when adopting `--ephemeral`. `--ephemeral` is allowed only if the caller durably retains JSONL + terminal + manifest + process identity + output digests.
- Do NOT default `--model` to anything without a live capability probe. CLI string acceptance is not availability proof.
