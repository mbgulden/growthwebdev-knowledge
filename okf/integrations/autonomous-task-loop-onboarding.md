---
type: Reference
title: Autonomous Task Loop — Onboarding Protocol for Agents (2026-06-23)
description: How Prismatic Engine cron agents must onboard before executing Linear tasks. The 9-step commit-early pattern, OKF consultation rules, and reporting format. Born from GRO-310 lazy-lookup failure and GRO-2226 budget exhaustion post-mortems.
resource: okf/integrations/autonomous-task-loop-onboarding.md
tags: [reference, agent, autonomous, onboarding, commit-early, okf-consultation, prismatic-engine]
timestamp: 2026-06-23T19:00:00Z
linear_issue: null
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/integrations/autonomous-task-loop-onboarding.md
last_verified: 2026-06-23
verified_by: ned
status: current
---

# Autonomous Task Loop — Onboarding Protocol

**Audience:** Any agent whose cron loop picks up Linear tasks autonomously (ned, kai, fred, agy, codex-5-5, etc.).

**Why this exists:** Two incidents on 2026-06-23 showed that the autonomous loop was structurally broken:

1. **GRO-310 (DNS Switch to Cloudflare):** Ned picked up the task, concluded "blocked" because "we don't have CF API access for this account," and reported failure. **The OKF `cloudflare-account-activeoahu.md` doc had the answer**, and the API key was already in the orchestrator's `.env`. Failure mode: **lazy lookup**.

2. **GRO-2226 (PWP tests):** Ned spent 90/90 tool calls exploring → reading → writing → testing → running pytest, then ran out of budget before committing, unlocking, or transitioning the Linear state. The work was 95% complete but lost. Failure mode: **no commit checkpoint**.

This doc is the corrective protocol. Adopt it across all lane agents.

---

## The Three Mandatory Pre-Task Steps

Before doing ANY work on a task, in this exact order:

### 1. Read the task carefully

- Title + description + acceptance criteria
- Parent issue for context
- Comments for prior attempts

Don't pattern-match on keywords. Don't skim.

### 2. Search the OKF for relevant docs

**The OKF is your first stop, not your last.** Located at `/home/ubuntu/work/growthwebdev-knowledge/okf/`.

Per-agent "always-read" doc list:

| Agent | Always-read docs (before claiming blocked) |
|---|---|
| **ned** | `okf/integrations/api-key-locations.md`, `okf/integrations/cloudflare-account-activeoahu.md`, `okf/integrations/prismatic-webhook-chain-recovery-2026-06-23.md`, `okf/integrations/autonomous-task-loop-onboarding.md` (this doc) |
| **kai** | `okf/integrations/cloudflare-account-activeoahu.md`, OKF project spokes for active-oahu.com repos |
| **fred** | `okf/integrations/api-key-locations.md`, `okf/integrations/agent-profile-inventory.md`, `okf/integrations/autonomous-task-loop-onboarding.md` (this doc) |
| **agy** | `okf/integrations/api-key-locations.md`, OKF project spokes for assigned work |

Search command:
```bash
grep -ril "<keyword>" /home/ubuntu/work/growthwebdev-knowledge/okf/ | head -10
```

### 3. Load the relevant skill

Use `skill_view(name)` to load. The skill will inject known-good patterns and recovery procedures into your context. **If you're about to claim "we don't have X" — load the relevant skill FIRST.**

Per-lane canonical skills:

| Domain | Skill |
|---|---|
| Cloudflare tunnel/DNS/ingress | `cf-tunnel-api-config` |
| Cloudflare Pages / Workers dashboard work | `cloudflare-deployment` |
| GPU/Ollama/local models | `kubernetes-gpu-llm-serving` |
| Image analysis | `agy-vision-pipeline` |
| Hardware/asset tracking | `homelab-inventory-management` |
| System health audit | `infrastructure-health-sweep` |
| Memory hygiene | `memory-hygiene-automation` |
| **Agent autonomy patterns (META — always load this)** | `autonomous-execution-discipline` |

---

## The 9-Step Commit-Early Pattern

**Non-negotiable.** Every state mutation creates a recoverable checkpoint.

```
Step 1 — Lock the files (1 tool call)
Step 2 — Create branch (1 tool call)
Step 3 — Heartbeat lock (1 call, repeat every 4 min during long ops)
Step 4-N — Write code, COMMIT after each logical chunk
         (NOT after all tests pass — commits go BEFORE long operations)
Verify (1-2 calls — pytest, build, etc.)
FINALIZE — single execute_code call containing:
  - final commit (with --allow-empty)
  - swarm unlock
  - Linear state → In Review
  - report
Clean up (push, optional)
```

### Why "commit before tests, not after"

If the budget runs out mid-task, the work-in-progress commit is your rollback point. The pre-test commit IS the deliverable; the test run is validation. If validation blows up the budget, you still have code on a branch.

### Why "finalize as ONE execute_code call"

`execute_code` iterations are **refunded** from the budget (per `run_agent.py::IterationBudget.refund()`). One execute_code call can run commit + unlock + Linear state-transition + report — 4 critical operations in 1 tool call instead of 4. They run atomically: either all complete or none do.

The finalize script template:

```python
import subprocess, os
def run(c): return subprocess.run(c, shell=True, capture_output=True, text=True).stdout

# 1. Final commit (--allow-empty handles partial work)
run("git add -A && git commit -m '[<agent>] <ISSUE>: finalize' --allow-empty")

# 2. Unlock
run("node /home/ubuntu/.antigravity/swarm.js unlock <paths> <agent>")

# 3. Linear state → In Review
key = os.environ.get('LINEAR_API_KEY', '')
subprocess.run(['curl', '-s', 'https://api.linear.app/graphql',
    '-H', f'Authorization: {key}', '-H', 'Content-Type: application/json',
    '-d', '{"query":"mutation { issueUpdate(id:\\"<ISSUE>\\", input:{stateId:\\"<in-review-id>\\"}) { success } }"}'])

# 4. Report
print(f"Task <ISSUE>: branch=<branch>, finalized at <timestamp>")
```

---

## "Don't Trust, Verify" Rules

Per the `autonomous-execution-discipline` skill (load it for the full ruleset):

1. **Never conclude "we don't have X" without:**
   - Searching the OKF (`grep -ril`)
   - Searching session transcripts (`session_search`)
   - Grepping relevant `.env` files
   - Trying the obvious API call with existing credentials

   One source of evidence is not enough.

2. **Never conclude "blocked" without trying the workaround.** The CF API key recovery (GRO-2050 area) is the canonical example: what looked "blocked" was a missing `.env` entry. The OKF had the recovery procedure.

3. **Never conclude "needs manual intervention" without naming:**
   - The specific manual step
   - The tool/script that would automate it
   - The OKF doc (if any) that describes the workflow

4. **Test your work before committing.** Run pytest, run the script, curl the API endpoint. Don't trust your own implementation claim. The `verify_syntax.py` script exists for a reason — use it.

---

## Reporting Format

Complete or blocker reports MUST follow this structure:

```
✅ TASK <id> — <title>
What I did: <1-3 bullets, specific files/repos changed>
Branch: <branch-name>
Commits: <commit hashes>
Tests: <results>
OKF docs consulted: <list>
Skills loaded: <list>
Linear state: <new state>
Next: <what should happen next, or "awaiting review">

OR for blockers:

🔴 TASK <id> — BLOCKED
What I tried: <bullets>
What I found in OKF: <any docs that touched on this>
What I think the real blocker is: <diagnosis>
What would unblock it: <concrete ask>
```

Be specific. Generic reports are useless. "Couldn't access CF API" is useless. "Curl with the `CLOUDFLARE_AOT_*` vars from orchestrator `.env` returns HTTP 200 with the activeoahutours zone; tunnel route exists but ingress rule missing — see §3 of `cf-tunnel-api-config` skill" is useful.

---

## Per-Agent Onboarding File Locations

Each agent profile has its own onboarding file at `~/.hermes/profiles/<agent>/AGENT-ONBOARDING.md`. This doc is the **canonical reference**; per-agent files are **profile-specific excerpts** pointing here.

| Agent | Onboarding file |
|---|---|
| ned | `~/.hermes/profiles/ned/AGENT-ONBOARDING.md` ✅ exists |
| kai | `~/.hermes/profiles/kai/AGENT-ONBOARDING.md` ❌ TODO |
| fred | `~/.hermes/profiles/fred/AGENT-ONBOARDING.md` ❌ TODO |
| agy | `~/.hermes/profiles/agy/AGENT-ONBOARDING.md` ❌ TODO |
| codex-5-5 | `~/.hermes/profiles/codex-5-5/AGENT-ONBOARDING.md` ❌ TODO |

**Adoption task (GRO-2228 candidate):** generate the per-agent onboarding files. Each one is short — just references this canonical doc + lists the lane-specific skills/docs.

---

## Implementation History

- **2026-06-23:** Protocol adopted after GRO-310 (lazy lookup) and GRO-2226 (budget exhaustion) post-mortems. Ned's onboarding file + cron prompt updated. Other agents' onboarding files pending.

---

## References

- `~/.hermes/profiles/ned/AGENT-ONBOARDING.md` — Ned's profile-specific onboarding
- `~/.hermes/profiles/ned/cron/jobs.json` (job `a9374c15f022`) — Cron prompt with onboarding link
- `okf/integrations/cloudflare-account-activeoahu.md` — Canonical CF account ref
- `okf/integrations/api-key-locations.md` — Where every API key lives
- `okf/integrations/prismatic-webhook-chain-recovery-2026-06-23.md` — Webhook chain diagnostics
- Skill: `autonomous-execution-discipline` — Core meta-skill (always load)
- Skill: `cf-tunnel-api-config` — Cloudflare tunnel/API recovery
- Skill: `infrastructure-health-sweep` — System health audits
- `prismatic-engine-operations` skill — Engine architecture and patterns
