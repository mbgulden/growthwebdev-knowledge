# PWP Refactor — Prepared (Awaiting AGY Audit + Approval)

**Status:** Ready for audit, NOT executed
**Linear:** Epic `GRO-2350` (refactor) + `GRO-2356` (audit before execution)
**Owner:** Fred (preparation) + AGY (audit) + Michael (approval)

## Context

Per Michael (2026-06-23):
> "PWP is just a plugin. If it has features/capabilities that prismatic
> engine or any other plugin needs to function, then the feature/capability
> should live in 'Prismatic Engine Core'."

> "Be sure to have AGY audit your script before you run it and do the
> full switchover. Or just have AGY audit afterwards."

This document captures the preparation phase. Nothing has been moved yet.

## What Was Prepared (in this turn)

### 1. Destination structure (ready, mostly empty)

```
/home/ubuntu/work/prismatic-engine/
├── prismatic/
│   ├── core/
│   │   ├── scheduler.py         ← NEW (ready for migration)
│   │   ├── webhook.py           ← NEW (ready for migration)
│   │   └── (existing: dispatcher, registry, router, contracts, locking, hardware_profiles)
│   └── capabilities/
│       ├── __init__.py          ← NEW
│       ├── provider_dispatch.py ← NEW (ready for migration)
│       ├── agent_discovery.py   ← NEW (ready for migration)
│       ├── version_control.py   ← NEW (ready for migration)
│       └── adapters/
│           ├── __init__.py      ← NEW
│           ├── linear.py        ← NEW (split from pwp_adapters.py)
│           ├── cloudflare.py    ← NEW (split from pwp_adapters.py)
│           ├── github.py        ← NEW (split from pwp_adapters.py)
│           ├── drive.py         ← NEW (split from pwp_adapters.py)
│           └── local.py         ← NEW (split from pwp_adapters.py)
└── plugins/
    └── pwp/
        ├── __init__.py          ← NEW
        ├── plugin-manifest.yaml ← NEW (validates against example_plugin pattern)
        ├── pwp/
        │   ├── __init__.py      ← NEW
        │   ├── plugin.py        ← NEW (extends PrismaticPlugin)
        │   ├── site_builder.py  ← (will be migrated from scripts/pwp/pwp/)
        │   ├── state.py         ← (will be migrated from scripts/pwp/pwp/pwp_site.py)
        │   ├── images.py        ← (will be migrated from scripts/pwp/generate_placeholder_images.py)
        │   ├── cli/
        │   │   ├── __init__.py  ← NEW
        │   │   ├── build.py     ← (will be migrated from scripts/pwp/pwp_build.py)
        │   │   ├── deploy.py    ← (will be migrated from scripts/pwp/deploy_cf_pages.py)
        │   │   ├── vc.py        ← (will be migrated from scripts/pwp/pwp_vc_cli.py)
        │   │   └── ingest.py    ← (will be migrated from scripts/pwp/drive_ingest.py)
        │   ├── templates/       ← (will be migrated from scripts/pwp/pwp/templates/)
        │   └── static/          ← (will be migrated from scripts/pwp/pwp/static/)
        └── tests/
            ├── __init__.py      ← NEW
            └── test_pwp.py      ← (will be migrated from scripts/pwp/test_pwp.py)
```

### 2. Plugin manifest + entrypoint

**`/home/ubuntu/work/prismatic-engine/plugins/pwp/plugin-manifest.yaml`**
- schema_version: 1.0.0
- name: prismatic-web-plugin
- version: 0.1.0
- entry_point: pwp.plugin:PwpPlugin
- core_version_constraint: ">=1.0.0, <2.0.0"
- Lists capabilities_provided + capabilities_consumed

**`/home/ubuntu/work/prismatic-engine/plugins/pwp/pwp/plugin.py`**
- Class `PwpPlugin(PrismaticPlugin)`
- Implements: `on_init`, `register_tools`, `health_check`
- Hook subscribers: `on_provider_dispatch`, `on_site_build`, `on_version_rollback`, `on_sync`
- 5 tools registered: `pwp_build_site`, `pwp_deploy`, `pwp_rollback`, `pwp_sync`, `pwp_list_sites`

### 3. Migration script (READY, tested with --dry-run)

**`/home/ubuntu/.hermes/profiles/orchestrator/scripts/pwp_refactor_migrate.py`**

Capabilities:
- `--dry-run` — Show what would happen, no changes
- `--migrate` — Execute the migration (backs up first)
- `--rollback` — Restore from most recent backup
- `--verify` — Show current state (Core exists? Plugin exists?)

Output of dry-run (just executed):
```
=== PWP Refactor — DRY RUN ===

--- Step 1: Copy files ---
Would copy: provider_dispatch.py → prismatic/capabilities/provider_dispatch.py
Would copy: agent_discovery.py → prismatic/capabilities/agent_discovery.py
Would copy: pwp_scheduler.py → prismatic/core/scheduler.py
Would copy: pwp_webhook.py → prismatic/core/webhook.py
Would copy: pwp_adapters.py → prismatic/capabilities/adapters/_legacy_combined.py
Would copy: pwp/pwp/site_builder.py → plugins/pwp/pwp/site_builder.py
Would copy: pwp/pwp/pwp_site.py → plugins/pwp/pwp/state.py
Would copy: pwp/pwp/pwp_version_control.py → prismatic/capabilities/version_control.py
Would copy: pwp/deploy_cf_pages.py → plugins/pwp/pwp/cli/deploy.py
Would copy: pwp/pwp_build.py → plugins/pwp/pwp/cli/build.py
Would copy: pwp/pwp_vc_cli.py → plugins/pwp/pwp/cli/vc.py
Would copy: pwp/drive_ingest.py → plugins/pwp/pwp/cli/ingest.py
Would copy: pwp/generate_placeholder_images.py → plugins/pwp/pwp/images.py
Would copy: pwp/test_pwp.py → plugins/pwp/tests/test_pwp.py

--- Step 2: Copy static files ---
Would copy dir: pwp/pwp/static/ → plugins/pwp/pwp/static/

--- Step 3: Update imports in existing files ---
Files updated: 5

--- Step 4: Verify ---
  ✅ Pwp source exists: True
  ❌ Core capabilities exist: False  (will become True after migrate)
  ❌ Core services exist: False      (will become True after migrate)

=== DRY RUN complete ===
```

### 4. Linear tracking (audit before execution)

**Epic `GRO-2356`** + **5 children** for AGY's audit:

| ID | What |
|---|---|
| GRO-2357 | AM1: Audit migration script for correctness + safety |
| GRO-2358 | AM2: Audit file classification (Core vs PWP) |
| GRO-2359 | AM3: Audit import update logic |
| GRO-2360 | AM4: Audit plugin loading |
| GRO-2361 | AM5: Audit state preservation |

All children labeled `provider:any` + `agent:agy` so any worker can pick up.

## What's NOT done (waiting for AGY audit + Michael approval)

- ❌ Migration script not executed (dry-run only)
- ❌ Source files not moved
- ❌ Imports not updated
- ❌ Tests not run in new location

## Decision Required: Before vs After Audit

Michael's exact words: "AGY audit your script before you run it and do the
full switchover. Or just have AGY audit afterwards."

**My recommendation: BEFORE.**
- AGY catches issues in the script (file classification, import mapping, safety)
- I fix issues, THEN run
- Avoids needing to do a migration twice

But it's your call. If you want to skip the audit and just run, say "go".

## How to run (after approval)

```bash
# 1. AGY audits (already filed as GRO-2356..2361)
# 2. Review AGY's findings, fix any issues
# 3. Once clear:
cd /home/ubuntu/.hermes/profiles/orchestrator/scripts

# 3a. Dry-run (confirm plan)
python3 pwp_refactor_migrate.py --dry-run

# 3b. Execute migration (backs up automatically)
python3 pwp_refactor_migrate.py --migrate

# 3c. Verify
python3 pwp_refactor_migrate.py --verify

# 3d. If anything broke, rollback
python3 pwp_refactor_migrate.py --rollback
```

## What This Refactor Accomplishes

1. **Architectural rule compliance** — capabilities that other plugins need live in Core
2. **Reusability** — provider_dispatch, scheduler, webhook, adapters available to any plugin
3. **Single source of truth** — no duplicate capability code across plugins
4. **Plugin discoverability** — PluginLoader finds PWP via manifest
5. **Clean separation** — Core (runtime) vs Capabilities (reusable) vs Plugin (domain-specific)

## Risk Mitigation

- **Backup before any change** — `--migrate` auto-creates `~/.pwp-backups/pwp-pre-refactor-{timestamp}/`
- **Rollback available** — `--rollback` restores from latest backup
- **Verification step** — `--verify` shows current state before doing anything
- **Dry-run mode** — `--dry-run` shows the plan without executing
- **Source files preserved** — migration COPIES files (doesn't delete originals); can re-run if needed

## Related Docs

- `okf/standards/architecture-core-vs-plugin.md` — the architectural rule
- `okf/standards/fred-self-audit-2026-06-23.md` — Fred's pre-preparation audit
- `okf/standards/agy-pwp-audit-2026-06-23.md` — AGY's pending audit (GRO-2344)
- `okf/standards/pwp-refactor-prepared.md` — THIS document
- `okf/standards/pwp-refactor-migration-summary.md` — will be written AFTER execution
</content>
