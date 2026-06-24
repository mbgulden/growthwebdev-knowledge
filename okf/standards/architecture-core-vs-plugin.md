---
title: Prismatic Engine Architecture — Core vs Plugin
description: The rule for what lives in Prismatic Engine Core vs what lives in a plugin (like PWP). Per Michael (2026-06-23): "PWP is just a plugin. If it has features/capabilities that prismatic engine or any other plugin needs to function, then the feature/capability should live in Prismatic Engine Core."
type: Standard
resource: https://github.com/mbgulden/growthwebdev-knowledge/blob/main/okf/standards/architecture-core-vs-plugin.md
tags: [standard, architecture, prismatic-engine, plugins, core, pwp, michael-spec]
timestamp: 2026-06-23T23:55:00Z
---

# Prismatic Engine Architecture — Core vs Plugin

## The Rule

**Per Michael (2026-06-23):**
> "PWP is just a plugin. If it has features/capabilities that prismatic engine
> or any other plugin needs to function, then the feature/capability should
> live in 'Prismatic Engine Core'."

**Test for "is this Core?":**
> "Would a different plugin (not PWP) need this to function?"
>
> - **Yes** → Core
> - **No, only PWP needs it** → Plugin
> - **Yes, but the plugin is the primary user** → Core, plugin consumes via API

## Repository Structure (correct layout)

```
$PRISMATIC_HOME/                          # e.g., ~/work
├── prismatic-engine/                     # The Core engine repo
│   ├── prismatic/
│   │   ├── core/                         # Core services
│   │   │   ├── dispatcher.py            # Task dispatcher
│   │   │   ├── registry.py              # Plugin loader
│   │   │   ├── router.py                # Best-fit routing
│   │   │   ├── contracts.py             # Plugin contracts
│   │   │   ├── locking.py               # Swarm locking
│   │   │   ├── hardware_profiles.py     # Hardware-aware scheduling
│   │   │   ├── scheduler.py             # Scheduled tasks  ← needed
│   │   │   └── webhook.py               # Webhook receiver  ← needed
│   │   ├── capabilities/                 # Reusable capabilities
│   │   │   ├── provider_dispatch.py     # Codex/MiniMax/Hermes routing  ← needed
│   │   │   ├── agent_discovery.py       # Find what agents exist  ← needed
│   │   │   ├── adapters/                 # External service adapters  ← needed
│   │   │   │   ├── linear.py
│   │   │   │   ├── cloudflare.py
│   │   │   │   ├── github.py
│   │   │   │   ├── drive.py
│   │   │   │   └── local.py
│   │   │   └── version_control.py       # Snapshots + rollback infrastructure  ← needed
│   │   └── interface/                    # Plugin ABC
│   │       └── plugin.py                # PrismaticPlugin base class
│   └── plugins/                          # All plugins live here
│       ├── pwp/                         # The Prismatic Web Plugin
│       │   ├── plugin-manifest.yaml     # Plugin metadata
│       │   ├── pwp/                     # Plugin code
│       │   │   ├── __init__.py          # Plugin class
│       │   │   ├── site_builder.py      # PWP-specific: builds sites
│       │   │   ├── templates/           # PWP-specific: web templates
│       │   │   ├── static/              # PWP-specific: CSS, JS
│       │   │   └── cli.py               # PWP-specific: web CLIs
│       │   └── tests/
│       ├── hermes-plugin-orchestrator-command-deck/   # existing
│       ├── hermes-plugin-swarm-manager/                # existing
│       └── ... (9 existing example plugins)
└── (legacy: ~/.hermes/profiles/orchestrator/scripts/ — to be migrated)
```

## Classification of Current PWP Files

Per R1 of GRO-2350:

| File | Classification | Where it goes | Justification |
|---|---|---|---|
| `provider_dispatch.py` | **Core** | `prismatic/capabilities/` | Every plugin needs to discover/dispatch providers |
| `agent_discovery.py` | **Core** | `prismatic/capabilities/` | Every plugin needs to know what agents exist |
| `pwp_scheduler.py` | **Core** | `prismatic/core/` | Every plugin needs scheduling (or PWP can use core's) |
| `pwp_webhook.py` | **Core** | `prismatic/core/` | Every plugin needs webhook receiving |
| `pwp_adapters.py` | **Core** | `prismatic/capabilities/adapters/` | Linear/CF/GitHub adapters are general infrastructure |
| `pwp_version_control.py` | **Core** | `prismatic/capabilities/` | Snapshots + rollback are reusable |
| `site_builder.py` | **PWP** | `plugins/pwp/pwp/` | Only PWP builds sites |
| `templates/*` | **PWP** | `plugins/pwp/pwp/templates/` | Web-specific HTML |
| `static/style.css` | **PWP** | `plugins/pwp/pwp/static/` | Web-specific CSS |
| `deploy_cf_pages.py` | **PWP** (uses Core) | `plugins/pwp/pwp/cli/` | PWP-specific deploy command |
| `pwp_build.py` | **PWP** (uses Core) | `plugins/pwp/pwp/cli/` | PWP-specific build command |
| `pwp_vc_cli.py` | **PWP** (uses Core VC) | `plugins/pwp/pwp/cli/` | PWP version control CLI |
| `drive_ingest.py` | **Both** | `prismatic/capabilities/adapters/drive.py` + thin PWP wrapper | Other plugins might also ingest Drive |
| `generate_placeholder_images.py` | **PWP** | `plugins/pwp/pwp/` | PWP-specific image gen |
| `pwp_site.py` | **PWP** | `plugins/pwp/pwp/state.py` | PWP's per-site state model |
| `test_pwp.py` | **PWP** | `plugins/pwp/tests/` | PWP-specific tests |

## What Prismatic Engine Core Already Provides (R2)

From inspection of `/home/ubuntu/work/prismatic-engine/prismatic/`:

| Already exists | Location | Replaces my duplicate in scripts/ |
|---|---|---|
| Event-driven dispatcher | `core/dispatcher.py` | (none — I didn't duplicate this) |
| Plugin loader | `core/registry.py` | (none — I used sys.path hacks instead) |
| Plugin ABC | `interface/plugin.py` | (none — PWP has no plugin class) |
| Hardware profiles | `core/hardware_profiles.py` | (partial — my GPU monitor duplicates some of this) |
| Best-fit routing | `core/router.py` | `agent_rubric_bridge.py` (partial duplicate) |
| Path contracts | `core/contracts.py` | (none) |
| Swarm locking | `core/locking.py` | (none — should use for PWP deploys) |

**Conclusion:** I built PWP features in `scripts/` instead of:
- Moving them to `prismatic/core/` or `prismatic/capabilities/`
- Using the existing `prismatic/core/dispatcher.py` instead of my own dispatcher

## Migration Roadmap (from GRO-2350)

| Phase | What | When |
|---|---|---|
| 1 | R1: Classify every file (this doc) | DONE |
| 2 | R2: Audit existing Core (this doc) | DONE |
| 3 | R3: Design plugin structure | R3 task filed |
| 4 | R4: Define Core API surface | R4 task filed |
| 5 | R5: Execute migration | R5 task filed (script + run) |

## Linear Tracking

- **Epic:** GRO-2350 — `[ARCH] Refactor: PWP becomes a plugin, capabilities move to Prismatic Engine Core`
- **Children:** GRO-2351..GRO-2355 (5 children, all P1, all `provider:any` + `agent:agy`)

## Why This Matters

1. **Single source of truth** — capabilities aren't duplicated across plugins
2. **Reusability** — other plugins (e.g., knowledge base plugin, agent monitoring plugin) get provider_dispatch + scheduler + webhook for free
3. **Maintainability** — fixing a bug in the scheduler fixes it for all plugins
4. **Discoverability** — anyone building a new plugin knows exactly what's available
5. **Compliance with Michael's spec** — explicit architectural rule

## What I'll Do Next

1. Wait for Michael's sign-off on the classification
2. Execute R5 (migration script) once R1-R4 are done
3. After migration: all PWP features still work, but the code lives in the right place
4. AGY's audit (GRO-2344) will catch any additional issues with the new structure

## Related Docs

- `okf/standards/fred-self-audit-2026-06-23.md` — Fred's audit (predecessor)
- `okf/standards/agent-auto-discovery.md` — currently in scripts/, should move to Core
- `okf/standards/provider-agnostic-dispatch.md` — currently in scripts/, should move to Core
- `okf/standards/post-publish-review-architecture.md` — already uses Core concepts
- PWP repo: `/home/ubuntu/.hermes/profiles/orchestrator/scripts/pwp/`
- Prismatic Engine repo: `/home/ubuntu/work/prismatic-engine/`
</content>
