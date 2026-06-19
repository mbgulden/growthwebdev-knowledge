---
type: Reference
title: Jules CLI Capability Report
description: Capability assessment of the Jules CLI — what it does well, failure modes, integration patterns.
resource: /home/ubuntu/work/agentic-swarm-ops/JULES-CAPABILITY-REPORT-2026-06-08.md
tags: [reference, jules, cli, capability]
timestamp: 2026-06-19T10:52:02Z
linear_issue: null
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/integrations/jules-cli-capability-report.md
last_verified: 2026-06-19
verified_by: kai
status: current
migrated_from: /home/ubuntu/work/agentic-swarm-ops/JULES-CAPABILITY-REPORT-2026-06-08.md
---

# Jules CLI Capability Report (2026-06-08)

**Target Audience:** Fred (Orchestrator), Michael, and the Agentic Swarm
**Status:** AUTHORITATIVE REFERENCE
**Version:** Jules v0.1.42
**Date:** June 8, 2026

---

## 1. EXECUTIVE SUMMARY
Jules is the swarm's specialized **Asynchronous GitHub PR Worker**. I excel at independent, repository-focused coding tasks that result in high-quality Pull Requests, documentation updates, and schema refactors. I operate in isolated remote VMs, allowing me to scale to hundreds of concurrent sessions without polluting the local orchestrator's environment. Fred should route any task to me that is well-defined, repo-centric, and does not require immediate interactive feedback or local filesystem access.

## 2. CLI SURFACE (Verified v0.1.42)
The following commands are available and verified in my current build:

| Command | Usage | Purpose |
|:---|:---|:---|
| `login` | `jules login` | Authenticates via Google OAuth (PKCE flow). |
| `logout` | `jules logout` | Revokes active OAuth credentials. |
| `new` | `jules new [flags] "<prompt>"` | Launches a new async coding session for the current repo. |
| `remote` | `jules remote [subcommand]` | Management of remote sessions and repositories. |
| `teleport` | `jules teleport <session_id>` | Clones a session's repo and applies changes locally. |
| `version` | `jules version` | Displays binary version, commit hash, and build date. |

### Key Flags:
- `--repo <owner/repo>`: Specify the target repository (used with `remote new`).
- `--parallel <1-5>`: Launch multiple concurrent sessions for the same prompt to compare implementations.
- `--session "<prompt>"`: Used with `remote new` to specify the instruction.
- `--apply`: Used with `remote pull` to apply a session's patch to the local workspace.

## 3. TUI COMMANDS
Unlike Hermes, I am primarily an **asynchronous CLI**. However, I have a minimal interactive TUI for session management:
- **Slash Commands:** Currently unsupported in the CLI binary itself; interaction is handled via the web UI or by spawning new sessions with `--continue` logic (passed via the prompt).
- **Session Actions:** Within the web interface, users can "Approve," "Retry," or "Cancel" sessions.

## 4. AUTH & LOGIN
- **Flow:** Google OAuth 2.0 with PKCE (Proof Key for Code Exchange).
- **Persistence:** Tokens are cached in `~/.jules/cache/`.
- **Auto-Refresh:** The CLI automatically refreshes tokens during background operations. If a refresh fails (e.g., re-auth required), I return a specific exit code for the orchestrator to trap.

## 5. SESSION MODEL
- **Infrastructure:** Every session spawns a temporary, isolated Google-managed VM.
- **Git Context:** I clone the target repository at the start of every session. I do NOT see local uncommitted changes unless they are explicitly passed in the prompt or pushed to the remote.
- **Parallelism:** Hard cap of **300 sessions per day**. Up to 5-way parallelism per individual task via `--parallel`.
- **Lifecycle:** `Init -> Clone -> Planning -> Executing -> PR Created -> Awaiting Review`.

## 6. CAPABILITY MATRIX

| Capability | Rating | Note |
|:---|:---|:---|
| **Code Implementation** | 🟢 Excellent | My core strength. Multi-file refactors, features, bug fixes. |
| **Pull Request Creation** | 🟢 Excellent | Native integration with GitHub. |
| **Documentation** | 🟢 Excellent | Producing and updating Markdown/SOPs in-repo. |
| **Test Generation** | 🟢 Excellent | I can run tests in my remote VM and iterate on failures. |
| **Vision (Single Image)** | 🟡 Adequate | I can describe screenshots but prefer AGY for pixel-perfect QA. |
| **Complex Refactors** | 🟢 Excellent | High success rate on tasks taking <30 mins of compute. |
| **Large Context (>200k)** | 🔴 Poor | Use AGY for 1M+ token research tasks. |
| **Local File Access** | 🔴 None | I cannot read your `/home/ubuntu` directory. |
| **Infra/Cloud Config** | 🔴 Forbidden | I am restricted from modifying K8s, billing, or networking. |

## 7. INTEGRATIONS
- **GitHub:** REAL. Native support for PRs, commits, and branch management.
- **Linear:** REAL (indirect). Integrated via the Hermes Dispatcher (`agent:jules` label).
- **Google Drive:** ASPIRATIONAL. No native access; use AGY for Drive tasks.
- **Slack/Jira:** ASPIRATIONAL. Currently no direct CLI connectors.

## 8. LIMITS & FAILURE MODES
- **Context Window:** ~200,000 tokens (Gemini 2.5 Pro).
- **Timeouts:** Remote VM sessions have a 60-minute hard timeout.
- **Failures:** Common patterns include:
  - **Rebase Hell:** If the base branch moves significantly during a long task.
  - **Outside-Git writes:** Files written to `/tmp/` in the VM are lost; they MUST be in the repo path.
  - **Model Stall:** Occasionally gets stuck in "Planning" if the prompt is contradictory.

## 9. BEST PRACTICES
- **Atomic Prompts:** One task per session. "Update the login logic" is better than "Refactor the whole app."
- **Self-Contained Context:** Include all necessary file paths and business logic in the prompt.
- **Risk Labeling:** Always flag PRs with `requires:human-approval` if they touch critical paths.
- **CI First:** Ensure the repo has passing CI so I can verify my own work.

## 10. ROUTING GUIDE (FOR FRED)
- **Send to JULES if:** The task is "Build X and open a PR," "Fix bug Y," or "Update documentation."
- **Send to AGY if:** The task is "Research competitors," "Analyze this 500-page PDF," or "Visual QA of the site."
- **Send to CODEX if:** The task is "Fix these merge conflicts locally," "Debug this interactive shell issue," or "Review this PR in VS Code."
- **Send to HUMAN if:** The task involves secrets, billing, or high-risk infrastructure changes.

## 11. UNDOCUMENTED / INTERNAL FEATURES
- **`jules remote pull --apply`**: This is an "engineer's secret" for rapidly pulling my remote work into a local environment for testing without waiting for a PR merge.
- **Session History:** `~/.jules/transactions.log` (if enabled) contains a local record of all dispatched tasks, useful for debugging orchestrator desync.
- **Hidden Env Var:** `JULES_DEBUG=1` enables verbose logging of the remote VM handshaking process.

## 12. HONEST SELF-ASSESSMENT
**Strengths:** I am the most reliable agent for "getting the code into the repo." I am faster than Codex for independent tasks because I don't contend for local terminal resources.
**Weaknesses:** I am "blind" to the local state. If Michael is editing a file locally, I won't know unless he pushes it. I can also be over-eager to fix things outside the original scope if the prompt is too broad.
**Needs Improvement:** My "Awaiting User Feedback" state can be a black hole for the orchestrator if not monitored closely.

---
*Generated by Jules v0.1.42 for the Swarm Operations Team.*
