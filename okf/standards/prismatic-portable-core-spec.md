---
type: Standard
title: Prismatic Portable Core Spec
description: Architectural invariants that make Prismatic Engine runnable anywhere — Linux, Windows, or macOS — with or without Linear and with or without any agent harness. The seam between "must work standalone" and "must integrate cleanly" lives here.
resource: okf/standards/prismatic-portable-core-spec.md
tags: [standard, portability, prismatic, architecture, decoupling]
timestamp: 2026-06-27T06:50:00Z
linear_issue: pending
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/standards/prismatic-portable-core-spec.md
last_verified: 2026-06-27
verified_by: michael
status: current — D1–D6 signed off 2026-06-27
---

# Prismatic Portable Core Spec

## 0. Why this document exists

Prismatic Engine was built on VM 800 (`/home/ubuntu`, Linear, Synology NAS, Hermes harness, AGY as worker).
That host was the original test bed, not the destination. The portable-core invariants below make the
engine runnable anywhere a developer wants it: a fresh `git clone` on Linux, a Windows machine, a Mac,
inside Docker, on a cloud VM, or in CI — without a hidden dependency on the original host's shape.

This is the standard that every "PORTABILITY" Linear issue and every AGY audit points at. It is the
single source of truth for "is this portable?" and "is this decoupled enough?"

## 1. Locked decisions (D1–D6)

### D1 — Platform priority
**Support order: Windows first, Linux (current host) first-class, macOS first-class.**

Rationale: Michael develops on Windows. The engine must run where the developer works.
Linux stays first-class because VM 800 is the operational host. macOS is in scope for testing
(Michael has access to a Mac) but is not the build host.

### D2 — Distribution shape
**Ship as both: an installable Python package AND a container image. Both must work.**

Rationale: developers want `pip install prismatic-engine` (Windows-friendly); operators want a
container image (Linux-friendly, deployable). Neither excludes the other. The two distributions share
the same source code and the same configuration contract; they differ only in packaging.

### D3 — No personal info, no real secrets in the repo
**The repo must work without any personal info, real API keys, or live Linear/Hermes endpoints.**

Concrete consequences:

- `.env.template` ships placeholder values only (`your_linear_api_key_here`, etc.)
- No real tokens, no Tailscale IPs, no live webhook URLs, no real email addresses
- No "Michael-only" assumptions (paths, usernames, hostnames)
- All secrets read from environment variables or operator-provided `.env` files
- CI never has access to live credentials

### D4 — Prismatic Engine works standalone, no harness required
**The engine must boot, run, and serve its public surface with no agent harness present.**

Concretely:

- The `PrismaticPlugin` ABC is the extension seam, not a dependency
- Any plugin (Hermes, AGY worker, custom) is optional
- The engine exposes a CLI that runs without IPC bridge, without AGY supervisor, without orchestrator
- The engine's own gateway/server, REST API, and state DB run on their own

### D5 — Prismatic Engine works without Linear (Linear is one task provider among many)
**Task providers are a swappable interface. Linear is the first-class example; it is not the requirement.**

Concretely:

- `prismatic/providers/tasks/base.py` already defines `TaskProvider` ABC + `Issue` dataclass. This is the seam.
- `prismatic/providers/tasks/linear.py` is one implementation. Add at least one more reference
  implementation (a JSON-file task provider, suitable for offline/development use).
- Engine startup never requires Linear credentials.
- Any reference to `Linear`, `LINEAR_API_KEY`, or `linear.py` outside of `prismatic/providers/tasks/`
  is a portability bug.

### D6 — Harness integration is a documented API, not discovery
**The engine ↔ harness boundary is a stable interface, not a private hand-shake.**

Concretely:

- Plugins consume the engine via the public API: `prismatic.api`, `prismatic.dispatch`, `prismatic.gateway`
- The engine never imports from a specific harness (no `from hermes_agents import ...`)
- A new harness can be written without modifying engine source
- The "harness is optional" mode (D4) is the same code path as "harness is present"

## 2. Architectural invariants (the non-negotiables)

### I1 — Path resolution
Every path must resolve via one of:

| Source | Use case |
|---|---|
| `os.environ.get("X")` with portable default | Operator-configurable location |
| `Path.home() / "..."` | Per-user dotfiles |
| `Path.cwd() / "..."` | Project-relative |
| A documented config file (`.env`, YAML, JSON) | Complex settings |

Forbidden: hardcoded `/home/ubuntu`, `/Users/michael`, `C:\Users\michael`, hardcoded `/tmp`,
hardcoded `/var/log`, hardcoded `~/mounts/synology-*`.

### I2 — Configuration precedence
Resolution order (highest priority first):

1. Explicit CLI args
2. Environment variables (`PRISMATIC_HOME`, `PRISMATIC_STATE_DIR`, `ANTIGRAVITY_LOCK_FILE`, etc.)
3. `.env` file in CWD
4. `~/.prismatic/config.yaml`
5. Hardcoded portable default

This is a single standard. Different modules must not invent their own precedence rules.

### I3 — Distribution contract
Both distribution shapes must pass the same smoke test:

- Boot the engine
- Run `prismatic --version` → returns version string
- Run `prismatic status` → returns engine status without external dependencies
- Read a fixture file from the package
- Write to the configured state directory

### I4 — Task provider interface stability
The `TaskProvider` ABC must not break. Adding methods is allowed with a default implementation;
removing or renaming methods is a breaking change.

### I5 — Harness interface stability
The `PrismaticPlugin` ABC must not break. Plugins registered via the existing manifest loader
must continue to work.

### I6 — Test fixture portability
Every test must be runnable:

- On Linux
- On Windows
- On macOS
- Inside a container
- Without any external service (Linear, Telegram, Slack, Stripe, etc.) reachable

The test suite must self-fail loudly if it touches a network mount, a non-cross-platform path,
or a hardcoded username.

### I7 — Logging portability
Logs go to:
- stdout (always)
- A configured file (when configured)
- The configured state directory's `logs/` subfolder (default)

Never to `/var/log/prismatic/*`, never to `~/Library/Logs/*`, never to a hardcoded Windows path.

### I8 — Process and signal portability
No POSIX-only signal assumptions. The engine must run on Windows where signals behave differently.
`os.kill`, `signal.SIGTERM`, `kill -9` assumptions → break the contract.

### I9 — Filesystem permission portability
Code that assumes POSIX `0o755` / `0o600` permission semantics must wrap them in a portability
helper. Windows handles permissions differently; the helper decides what to do.

### I10 — Network bind portability
Default bind addresses use `127.0.0.1` (loopback). Operators override via `PRISMATIC_BIND_HOST`.
Never hardcoded `0.0.0.0` (security) and never hardcoded external IPs.

## 3. The seam: Prismatic Engine ↔ harness ↔ task provider

```
   ┌──────────────────────────────────┐
   │  Operator / user                 │
   └──────────────┬───────────────────┘
                  │  prismatic CLI, REST API
                  ▼
   ┌──────────────────────────────────┐
   │  Prismatic Engine core           │   ← D4: runs standalone
   │  - prismatic.api (REST)          │
   │  - prismatic.gateway (WS, IPC)   │
   │  - prismatic.core (registry,     │
   │    locking, hardware profiles)   │
   │  - prismatic.billing             │
   │  - prismatic.credit_*            │
   │  - prismatic.providers           │   ← D5: swappable
   │    ├── tasks.base (ABC)          │
   │    ├── tasks.linear (impl)       │
   │    ├── tasks.jsonfile (impl)     │   ← new, required for offline mode
   │    └── signals.{base,file,http,  │
   │              redis,nudge_…}      │
   └──────────────┬───────────────────┘
                  │  PrismaticPlugin ABC + manifest
                  ▼
   ┌──────────────────────────────────┐
   │  Plugin / harness (optional)     │   ← D4, D6
   │  - hermes-plugin-*               │
   │  - pwp-plugin                    │
   │  - third-party plugin            │
   └──────────────────────────────────┘
```

The engine knows about plugins via the ABC. It does not know about specific harness implementations.
A harness is a plugin that happens to manage agents. The engine does not depend on any harness.

## 4. The minimum portable subset

The engine's "minimum portable subset" — the surface that is always supported regardless of
platform, task provider, or harness — is:

| Surface | Always supported | Notes |
|---|---|---|
| Python 3.11+ on Linux | ✅ | Current host |
| Python 3.11+ on Windows | ✅ | Windows-first per D1 |
| Python 3.11+ on macOS | ✅ | Mac is a verification target |
| Container (linux/amd64, linux/arm64) | ✅ | Both shapes per D2 |
| `pip install` from PyPI | ✅ | Both shapes per D2 |
| `prismatic` CLI | ✅ | One binary entrypoint |
| REST API on `127.0.0.1:<port>` | ✅ | Port is configurable |
| State persisted to local filesystem | ✅ | SQLite + JSON |
| Linear as task provider | Optional | First-class but not required |
| JSON-file task provider | ✅ | New, required for offline mode |
| Hermes plugin | Optional | Engine must run without it |
| AGY plugin | Optional | Engine must run without it |
| Stripe billing | Optional | Skipped when no Stripe creds |
| Webhooks to Linear | Optional | Skipped when no Linear creds |
| Custom signal provider via plugin | Optional | Documented extension point |

## 5. What changes for a developer who clones the repo

```bash
git clone https://github.com/mbgulden/prismatic-engine
cd prismatic-engine
cp .env.template .env       # safe — only placeholders in template
# edit .env if you want Linear; otherwise leave empty
pip install -e .            # dev install
prismatic --version         # should print 0.x.y
prismatic status            # should print engine status
```

That's the entire first-run experience. No host-specific setup, no NAS mounts, no `/home/ubuntu`
magic. If any step fails on Windows or macOS, that is a portability bug.

## 6. Outstanding items (mapped 1:1 to Linear issues, tracked in queue)

| ID | Stream | Title |
|---|---|---|
| O1 | Stream 1 | Decoupling audit — every Linear reference outside `prismatic/providers/tasks/` |
| O2 | Stream 1 | Decoupling audit — every `LINEAR_API_KEY` reference outside the Linear provider |
| O3 | Stream 1 | JSON-file task provider implementation plan |
| O4 | Stream 1 | "No-Linear demo mode" runbook |
| O5 | Stream 1 | "No-Hermes demo mode" runbook |
| O6 | Stream 1 | "No-agent-harness demo mode" runbook |
| O7 | Stream 2 | Hardcoded `/home/ubuntu` → `Path.home()` refactor readiness map |
| O8 | Stream 2 | POSIX-vs-Windows socket/pid file audit |
| O9 | Stream 2 | Path separator audit (forward slash vs `os.path.join`) |
| O10 | Stream 2 | Windows-native smoke test plan |
| O11 | Stream 2 | macOS smoke test plan |
| O12 | Stream 2 | Shell-assumption audit (`&`, `find`, `xargs`, `ps`) |
| O13 | Stream 3 | `pyproject.toml` portability audit |
| O14 | Stream 3 | Native-extension dependency audit (which deps are Linux-only) |
| O15 | Stream 3 | Container base image recommendation doc |
| O16 | Stream 3 | Windows distribution story (wheel / exe / chocolatey) |
| O17 | Stream 3 | "Works without secrets in the repo" verification checklist |
| O18 | Stream 3 | Smoke-test CI matrix proposal |
| O19 | Stream 4 | Harness-decoupling interface proposal (Streams 4+5 require Michael sign-off on this spec) |
| Stream 5 | Operator workflow codification (plan → tasks → AGY queue → session → push) |

O1–O18 queued as AGY-safe read-only audit tasks (GRO-2786..GRO-2803). O19
and O20 were queued after Michael signed off on D1–D6 (GRO-2811..GRO-2818).
All five streams now dispatch-ready; AGY is draining them at the proven
max-concurrent=2 envelope.

## 7. Verification commands (the smoke test)

After the portability epic lands, every distribution shape (pip wheel, container, source) must
pass this from a clean checkout on a fresh machine:

```bash
# 1. Clean clone (no .env, no state, nothing)
git clone https://github.com/mbgulden/prismatic-engine /tmp/prismatic-test
cd /tmp/prismatic-test

# 2. Install (whichever shape is being tested)
pip install -e .                      # OR: docker build -t prismatic:test .

# 3. No secrets anywhere
grep -rE 'sk_(live|test)_|mk_live_|sk-' . --include='*.py' --include='*.yaml' --include='*.json' --include='*.md' --include='*.yml' 2>/dev/null
# Must return empty

# 4. No hardcoded /home/ubuntu outside .env.template
grep -rE '/home/ubuntu' prismatic/ --include='*.py' 2>/dev/null
# Must return empty

# 5. Engine boots with no env
unset LINEAR_API_KEY PRISMATIC_HOME
prismatic --version
prismatic status
# Both must succeed

# 6. JSON-file task provider works (offline mode)
prismatic task-providers
# Must list at least linear + jsonfile

# 7. No external network calls on boot
strace -e network -f prismatic status 2>&1 | grep -E 'connect|sendto' | head
# (POSIX) or
procmon /filter prismatic.exe  # (Windows)
# Must show only localhost or unix-socket activity, no public IPs
```

If any of these checks fails on a fresh Linux/Windows/macOS machine, that's a portability bug
that blocks the spec from being declared "shippable."

## 8. Risk register

| Risk | Severity | Mitigation |
|---|---|---|
| Native Python deps that don't build on Windows (e.g., `uvloop`) | High | Audit O14, swap or platform-conditional |
| Hardcoded `/home/ubuntu` paths in third-party deps | Medium | Pin to deps that respect `Path.home()` |
| POSIX-only signal handling in `gateway/server.py` | High | Wrap in `prismatic/platform_compat/` helper |
| Linear webhook secret format drift | Low | Track in O17 verification checklist |
| Stripe webhook secret leakage (if anyone copies a real secret) | Critical | D3 + automated `gitleaks` in pre-push |
| Container image bloat from layered installs | Medium | Use multi-stage Docker build (see O15) |
| macOS Gatekeeper blocking unsigned binary distribution | Medium | Document signing requirement (O16) |

## 9. Cross-references

- **North Star** (parent document — read this first): [`../vision/prismatic-north-star.md`](../vision/prismatic-north-star.md)
- Existing epic docs (Phase 1–5): [`./agy-portability-epic-2026-06-27.md`](../operations/agy-portability-epic-2026-06-27.md)
- Deep-dive: [`./agy-portability-deep-dive-2026-06-27.md`](../operations/agy-portability-deep-dive-2026-06-27.md)
- OS-level sandboxing: [`./agy-os-level-sandboxing-2026-06-27.md`](../operations/agy-os-level-sandboxing-2026-06-27.md)
- Harness coupling taxonomy: [`./prismatic-harness-coupling-taxonomy.md`](./prismatic-harness-coupling-taxonomy.md)
- AGY architecture recipe: [`./agy-architecture-recipe.md`](./agy-architecture-recipe.md)
- Agent dispatch architecture: [`./agent-dispatch-architecture.md`](./agent-dispatch-architecture.md)

## 10. Sign-off

This spec is in `status: current`. Michael signed off on D1–D6 on 2026-06-27.
All five streams (O1–O20) are queued as AGY-safe read-only audit tasks:

| Stream | Range | Items |
|---|---|---|
| Stream 1 (decoupling) | GRO-2786..2791 | O1–O6 |
| Stream 2 (platform portability) | GRO-2792..2797 | O7–O12 |
| Stream 3 (distribution) | GRO-2798..2803 | O13–O18 |
| Stream 4 (harness decoupling) | GRO-2811..2814 | O19 |
| Stream 5 (operator workflow) | GRO-2815..2818 | O20 |

When the audit artifacts land, the next phase is implementation readiness:
a small number of human-decision items (pricing, public-API stability
contract, container base image, CI matrix), each one in its own Linear
issue, gated by Michael sign-off on the artifacts AGY produces.