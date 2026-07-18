---
type: Standard
title: Swarm Coordination Protocol
description: Protocol for multi-agent coordination, active-work claims, checkpointing, and URL verification. Repaired from old-format PR #12 standard.
resource: okf/standards/swarm-coordination-protocol.md
tags: [standard, swarm, coordination, agents, governance]
timestamp: 2026-07-18T00:00:00Z
linear_issue: null
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/standards/swarm-coordination-protocol.md
last_verified: 2026-07-18
verified_by: fred
status: current
---

# Swarm Coordination Protocol

**Status:** Canonical, v1 (2026-06-29)
**Audience:** All agents (Fred, AGY, Ned, Jules, Kai, Hermes)
**Source of truth:** This document. When in doubt, read this.

---

## Purpose

This document defines **how multiple agents coordinate when working in the
same repositories**. It exists because:

1. Agents have lost work to silently-failing tooling (Gap 10, ~50KB uncommitted)
2. Agents have shipped "fake success" URLs that 404'd on push (OKF bug)
3. Agents have stepped on each other's edits (no coordination mechanism)

The three problems share one root cause: **no shared protocol for "I am
about to do X" + "X is done" + "did X actually succeed"**.

This protocol defines that protocol.

---

## The Three Layers

| Layer | Purpose | Tool | When to use |
|---|---|---|---|
| **1. Active-work registry** | "I'm working on these files; don't touch them" | `claim-work` | Before starting any work that touches files |
| **2. Commit checkpointing** | "Don't lose my work even if I crash" | `subagent_checkpoint_monitor.py` | While running subagents |
| **3. URL verification** | "Did my push actually land?" | `verify-push` + `safe-pr-create` | After every push |

Each layer is independent. You can use one without the others. But the three
together prevent the three classes of bugs above.

---

## Layer 1 — Active-Work Registry (`claim-work`)

### What it does

A shared JSON file at `~/.antigravity/active_work.json` tracks which agent
is working on which files in which repos. Other agents (or pre-commit hooks)
check the registry before touching those files.

### When to register a claim

**Register BEFORE you start editing files.** Don't edit first and then claim
— by then another agent might already have edited.

```bash
# Example: Fred is going to edit prismatic/journal.py
claim-work register \
  --repo prismatic-engine \
  --agent fred \
  --branch feature/journal-fix \
  --files prismatic/journal.py \
  --description "Fix _last_sync schema-drift crash"
```

### Heartbeat

Claims expire after 30 minutes by default. If your work is still in progress,
refresh every 5 minutes:

```bash
claim-work heartbeat \
  --repo prismatic-engine --agent fred --branch feature/journal-fix
```

If your agent goes silent for >30 min, your claim auto-expires. Another
agent can then take over the file.

### Release when done

```bash
claim-work release \
  --repo prismatic-engine --agent fred --branch feature/journal-fix
```

### Check before editing

Before you edit any file, check if someone else has claimed it:

```bash
claim-work check --repo prismatic-engine --file prismatic/journal.py --agent fred
# Exit 0 = available
# Exit 1 = claimed by another agent; shows who
```

### Pre-commit hook (recommended)

Install the pre-commit hook so the registry check is automatic:

```bash
bash /home/ubuntu/bin/install-claim-check-hook.sh /home/ubuntu/work/prismatic-engine fred
```

After install, every `git commit` will refuse to commit if any staged file
is claimed by another agent.

### Inspect the registry

```bash
claim-work list                    # All claims
claim-work list --repo prismatic-engine --active-only
```

---

## Layer 2 — Subagent Commit Checkpointing

### What it does

When launching a long-running subagent (AGY, Claude Code, etc.), a daemon
monitors the workdir. If the subagent accumulates >5 modified files OR uses
>75% of its tool budget without committing, the daemon auto-commits a WIP
snapshot. If the subagent crashes/exits, a final checkpoint runs.

### How to use

The launcher (`launch_agy_with_artifact.py`) starts the checkpoint daemon
automatically. You don't need to do anything special — just launch agents
the usual way.

To disable for a single run:

```bash
python3 launch_agy_with_artifact.py --no-checkpoint \
  --dispatch-file /tmp/x.md --identifier GRO-1234 --workdir /path
```

### What you see when it fires

- `🟡 [checkpoint] N files modified — committing WIP`
- `[WIP-auto-checkpoint] <some files>` commit appears in the workdir

The WIP commits are intentionally dirty — you should clean them up
(rebase / drop) before merging.

---

## Layer 3 — URL Verification (`verify-push`)

### What it does

After `git push`, the actual file URLs at `raw.githubusercontent.com/...`
are curled. If any return 404, the script reports it. This catches the
"fake push succeeded" bug where git says OK but GitHub hasn't propagated.

### Standalone use

```bash
verify-push https://raw.githubusercontent.com/me/repo/main/file.md
# Exit 0 = live
# Exit 1 = 404 or other error
```

### Wrap every PR

Use `safe-pr-create` instead of `gh pr create` directly:

```bash
safe-pr-create \
  --head feature/foo \
  --title "Add foo" \
  --body "..." \
  --verify-paths foo.md docs/bar.md
# Creates PR, verifies file URLs, reports PASS/FAIL
```

### After OKF doc updates

When you push to `growthwebdev-knowledge`, verify the raw URLs before
telling anyone the doc is "live":

```bash
verify-push \
  https://raw.githubusercontent.com/mbgulden/growthwebdev-knowledge/main/okf/path/to/doc.md
```

---

## Decision Tree: When to Use What

```
I'm about to edit files in a repo
  └─ Q: Will this take >2 minutes? Will another agent touch the same files?
       ├─ YES → Register claim with `claim-work register`
       │         Install pre-commit hook if you haven't
       └─ NO  → Skip claim (single-file quick edits are usually safe)

I'm launching a long-running subagent
  └─ Use launch_agy_with_artifact.py (auto-enables checkpoint daemon)
     └─ Optional: --no-checkpoint if workdir isn't a git repo

I'm about to push code or docs
  └─ Use safe-pr-create (wraps `gh pr create` + verify-push)
     └─ OR: git push + verify-push manually on raw URLs

I'm about to claim "X is live / shipped / done"
  └─ verify-push the actual URL first. NEVER claim a URL is live
     based on git push exit code alone.
```

---

## Anti-Patterns (Things To Stop Doing)

| Anti-pattern | Why it's bad | Do this instead |
|---|---|---|
| Edit first, claim later | Another agent might already be editing | `claim-work register` BEFORE editing |
| Skip heartbeat during long work | Claim expires; another agent steals your files | `claim-work heartbeat` every 5 min |
| `git push` → claim "live" without verifying | "Fake success" on broken links (OKF bug) | `verify-push` the raw URL |
| `gh pr create` directly | No URL verification built in | `safe-pr-create` |
| Push directly to `deploy-fresh` from feature branch | Bypasses peer review + lane governance | Open PR, wait for review, merge |
| Re-pitch a rejected idea | User already said no (spleen) | Move on; don't re-ask |
| Promise file is live because git push returned 0 | Git push ≠ URL is live | `verify-push` first |

---

## Tool Reference

| Tool | Path | Purpose |
|---|---|---|
| `claim-work` | `~/bin/claim-work` | Active-work registry CLI |
| `claim-work check` | (subcommand) | Check if file is claimed |
| `claim-work register` | (subcommand) | Register a new claim |
| `claim-work heartbeat` | (subcommand) | Refresh TTL |
| `claim-work release` | (subcommand) | Release a claim |
| `claim-work list` | (subcommand) | View all claims |
| `claim-work prune` | (subcommand) | Remove expired claims |
| `subagent_checkpoint_monitor.py` | `~/.hermes/profiles/orchestrator/scripts/` | Auto-commit WIP for subagents |
| `launch_agy_with_artifact.py` | `~/.hermes/profiles/orchestrator/scripts/` | AGY launcher with auto-checkpoint |
| `verify-push` | `~/bin/verify-push` | URL verification post-push |
| `safe-pr-create` | `~/bin/safe-pr-create` | `gh pr create` + URL verification |
| `install-claim-check-hook.sh` | `~/bin/install-claim-check-hook.sh` | Install pre-commit hook in a repo |

---

## Specs and Design Docs

Each tool has a deeper spec in the OKF standards directory:

- `okf/standards/subagent-checkpoint-monitor-spec.md`
- `okf/standards/url-verification-spec.md`
- `okf/standards/claim-work-spec.md`
- `okf/standards/swarm-coordination-protocol.md` (this file)

When in doubt, the spec doc is the source of truth for implementation details.
This protocol doc is the source of truth for **when and why** to use them.

---

## Maintenance

This protocol is owned by **Fred (the orchestrator)**. Changes should:

1. Update the spec docs in OKF first
2. Update this protocol doc second
3. Commit to `growthwebdev-knowledge` (OKF repo)
4. Reference the change in the next status update

If a tool breaks or a new tool is added, update the relevant spec doc
and add a row to the Tool Reference table above.

---

**Last updated:** 2026-06-29
**Author:** Fred
**Version:** 1.0
