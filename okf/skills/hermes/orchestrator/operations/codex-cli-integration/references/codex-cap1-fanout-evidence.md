---
name: codex-cap1-fanout-evidence
description: Evidence required to bump Codex CLI parallelism from cap-1 to cap-N in a Prismatic Engine lane.
type: reference
---

# Cap-1 → cap-N evidence checklist for Codex CLI lanes

Prismatic Engine lanes default to **one parallel Codex CLI invocation** (cap-1). Bumping to cap-N is a deliberate decision that requires independent evidence across four axes. This file is the checklist; the lane should refuse fan-out until every item is signed off.

## Why cap-1 is the default

Each `codex exec` is a separate OS process with:

- Its own sandbox (bubblewrap by default on Linux).
- Its own session file (unless `--ephemeral`).
- Its own rate-limit bucket against `api.openai.com`.

The lane does not yet know how many concurrent Codex CLI processes the openai-codex OAuth bucket tolerates before rate-limiting. Sandboxes may also collide if multiple dispatches touch overlapping worktrees. Defaulting to cap-1 keeps the failure modes observable per dispatch.

## What cap-1 does NOT preclude

- Multiple **sequential** dispatches per process (each completes before the next starts).
- A single `codex exec` delegating to internal sub-agents via the `--enable multi_agent` feature flag (when enabled; current status `stable` but NOT in PE lane scope yet).

## The four axes

To move from cap-1 to cap-N, gather evidence in each:

### 1. Rate-limit evidence

- Sustained N dispatches per minute against the same auth file for ≥ 10 minutes.
- 0 × `429 Too Many Requests` from `api.openai.com` (across WebSocket + HTTPS fallback).
- `x-ratelimit-requests-remaining` headers stay above the configured floor (`min_remaining`) throughout.
- Observed token-bucket refill rate published by OpenAI captured.

### 2. Sandbox-collision evidence

- N dispatches, each with a distinct `-C <worktree>` (no overlap).
- N dispatches, each with a distinct `--add-dir <path>` (no overlap).
- A negative test: N dispatches sharing a single `-C` produces the expected contention (one succeeds, others surface clear `busy` / `lock-held` errors, no silent corruption).
- Sandbox-bind errors (AppArmor, bubblewrap profile) do not crash the dispatch service.

### 3. Exact-run evidence

- Each of N dispatches returns a stable `turn.completed` event with a non-empty terminal message at `-o <path>`.
- Each of N dispatch IDs is distinct and traceable in `~/.prismatic/run-dispatch/<dispatch_id>/`.
- `codex exec` exit codes are 0 across all N; no `Reconnecting... 5/5` tail-errors.
- JSONL stream per dispatch is parseable downstream, with `thread.started`, `turn.started`, `item.completed`, `turn.completed` events in order.

### 4. Recovery evidence

- One in-flight dispatch is killed (SIGTERM). Other N-1 dispatches complete normally.
- One in-flight dispatch receives 401 mid-stream. Other N-1 dispatches continue; failed one is recovered per `references/codex-service-home-auth.md` (operator re-auth, redispatch).
- Restart of the dispatch service does not leave orphan processes (no surviving `codex` PIDs after service stop).

## Capture template

When you have the evidence, capture it in a single ad-hoc verifier:

```bash
PROBE=/tmp/hermes-verify-codex-cap-<N>-<ts>.sh
cat > "$PROBE" <<'EOF'
#!/bin/bash
set -euo pipefail
N=2   # target cap
PROMPT="Reply with exactly: CAP_OK"
LOG=/tmp/fred-codex-cap-<N>.log
: > "$LOG"

for i in $(seq 1 $N); do
  (
    DIR=/tmp/codex-fanout-<ts>/$i
    mkdir -p "$DIR"
    /usr/bin/codex -a never exec --json --ephemeral \
      --model gpt-5 --sandbox workspace-write \
      -C "$DIR" -o "$DIR/last.md" \
      "$PROMPT" < /dev/null
  ) >> "$LOG" 2>&1 &
done
wait
grep -c '"type":"turn.completed"' "$LOG"   # expect: N
grep -c '"type":"turn.failed"' "$LOG"      # expect: 0
grep -c '429' "$LOG"                       # expect: 0
EOF
chmod +x "$PROBE"
bash "$PROBE"
```

Report as **ad-hoc targeted verification, not suite green** unless a canonical test suite covers this exact fan-out shape.

## What bumps cap-N is NOT

- "It worked once with 3 simultaneous." Cap-N requires sustained evidence, not a one-shot.
- "Nobody complained about 429s." Absence of complaint is not rate-limit evidence.
- "The OpenAI rate-limit doc says X per minute." OpenAI's published limits are dynamic and per-account. The lane MUST measure against the actual auth file in use.

## Pitfalls

- Bumping cap-N without sandbox-collision evidence. Two dispatches sharing a worktree can corrupt each other's `-C` directory before sandbox refuses the write.
- Bumping cap-N without recovery evidence. A single stuck dispatch can starve the entire lane queue.
- Skipping the negative test (overlapping worktrees). Negative tests are how you discover contention early.
- Using `--dangerously-bypass-approvals-and-sandbox` to bypass sandbox-collision evidence. That's a different bug.
- Treating a parallel dispatch as "fan-out" without verifying JSONL streams are temporally separated. Two `turn.completed` events at the same millisecond across dispatches require robust downstream correlation by `dispatch_id`, not just by timestamp.
