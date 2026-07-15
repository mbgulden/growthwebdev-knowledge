---
type: Report
title: Prismatic AGY audit history
description: Historical archive summary for AGY audit evidence discovered during the Prismatic OKF treasure hunt.
resource: okf/projects/prismatic-engine/archive/agy-audit-history.md
tags: [report, archive, prismatic-engine, agy, audit, okf]
timestamp: 2026-07-15T00:00:00Z
linear_issue: GRO-3721
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/projects/prismatic-engine/archive/agy-audit-history.md
last_verified: 2026-07-15
verified_by: fred
status: historical
---

# Prismatic AGY audit history

## Why this archive exists

The treasure hunt found 172 AGY audit candidates. These are useful as evidence patterns and audit history, but they are not live dashboard/control-plane proof by themselves.

## Current vs historical boundary

| Item | Treatment |
|---|---|
| AGY audit outputs | Historical evidence patterns. |
| Browser/API claims in old audits | Revalidate before citing as current. |
| Current live-proof rule | Use Batch 2 governance dashboard history and current verifiers. |
| Cleanup | Blocked. |

## Useful evidence patterns

- AGY audits help identify where UI proof, console proof, and source/API checks diverged.
- They are good prompts for future verification scripts.
- They are not replacements for fresh browser/API proof.

## Source/provenance table

| Source repo | Branch | Head | Path | Class | Recommendation | Hash |
|---|---|---|---|---|---|---|
| `prismatic-engine` | `backup/gro-3515-full-okf-blocked` | `3133a5590705` | `docs/agy-night/directory-indexes/prismatic-agents.md` | `hidden-historical` | `archive/index as historical after summary` | `1d15ae8c082d` |
| `prismatic-engine` | `backup/gro-3515-full-okf-blocked` | `3133a5590705` | `docs/agy-night/directory-indexes/prismatic-api-routers.md` | `hidden-historical` | `archive/index as historical after summary` | `4d2a718934e5` |
| `prismatic-engine` | `backup/gro-3515-full-okf-blocked` | `3133a5590705` | `docs/agy-night/directory-indexes/prismatic-core.md` | `hidden-historical` | `archive/index as historical after summary` | `81667a541963` |
| `prismatic-engine` | `backup/gro-3515-full-okf-blocked` | `3133a5590705` | `docs/agy-night/directory-indexes/prismatic-interface.md` | `hidden-historical` | `archive/index as historical after summary` | `43285bfa5f19` |
| `prismatic-engine` | `backup/gro-3515-full-okf-blocked` | `3133a5590705` | `docs/agy-night/directory-indexes/prismatic-network.md` | `hidden-historical` | `archive/index as historical after summary` | `c4475e3dd608` |
| `prismatic-engine` | `backup/gro-3515-full-okf-blocked` | `3133a5590705` | `docs/agy-night/directory-indexes/prismatic-providers-tasks.md` | `hidden-historical` | `archive/index as historical after summary` | `68606e0c5690` |
| `prismatic-engine` | `backup/gro-3515-full-okf-blocked` | `3133a5590705` | `docs/agy-night/directory-indexes/prismatic-providers.md` | `hidden-historical` | `archive/index as historical after summary` | `f47d19f5ad70` |
| `prismatic-engine` | `backup/gro-3515-full-okf-blocked` | `3133a5590705` | `docs/agy-night/module-cards/prismatic-agent-cards-py.md` | `hidden-historical` | `archive/index as historical after summary` | `e50df5aab87d` |
| `prismatic-engine` | `backup/gro-3515-full-okf-blocked` | `3133a5590705` | `docs/agy-night/module-cards/prismatic-agents-base-py.md` | `hidden-historical` | `archive/index as historical after summary` | `46de9073b81b` |
| `prismatic-engine` | `backup/gro-3515-full-okf-blocked` | `3133a5590705` | `docs/agy-night/module-cards/prismatic-agents-hermes-py.md` | `hidden-historical` | `archive/index as historical after summary` | `4ed76ccb6779` |
| `prismatic-engine` | `backup/gro-3515-full-okf-blocked` | `3133a5590705` | `docs/agy-night/module-cards/prismatic-agents-init-py.md` | `hidden-historical` | `archive/index as historical after summary` | `1e8e7cd6c2ad` |
| `prismatic-engine` | `backup/gro-3515-full-okf-blocked` | `3133a5590705` | `docs/agy-night/module-cards/prismatic-agy-live-parser-py.md` | `hidden-historical` | `archive/index as historical after summary` | `5892f2238d5e` |
| `prismatic-engine` | `backup/gro-3515-full-okf-blocked` | `3133a5590705` | `docs/agy-night/module-cards/prismatic-api-init-py.md` | `hidden-historical` | `archive/index as historical after summary` | `00d0b09b1c39` |
| `prismatic-engine` | `backup/gro-3515-full-okf-blocked` | `3133a5590705` | `docs/agy-night/module-cards/prismatic-api-main-py.md` | `hidden-historical` | `archive/index as historical after summary` | `c4b3553f2ae1` |
| `prismatic-engine` | `backup/gro-3515-full-okf-blocked` | `3133a5590705` | `docs/agy-night/module-cards/prismatic-api-routers-credits-py.md` | `hidden-historical` | `archive/index as historical after summary` | `a20a05d51d77` |
| `prismatic-engine` | `backup/gro-3515-full-okf-blocked` | `3133a5590705` | `docs/agy-night/module-cards/prismatic-api-routers-init-py.md` | `hidden-historical` | `archive/index as historical after summary` | `a440dc01c88a` |


## Duplicate/superseded handling

| Hash prefix | Duplicate count | Sample paths |
|---|---:|---|
| `1d15ae8c082d` | 3 | `{'branch': 'backup/gro-3515-full-okf-blocked', 'class': 'hidden-historical', 'path': 'docs/agy-night/directory-indexes/prismatic-agents.md', 'repo': 'prismatic-engine', 'title': 'Directory Index: `prismatic/agents`'}`, `{'branch': 'backup/gro-3522-full-okf-blocked', 'class': 'hidden-historical', 'path': 'docs/agy-night/directory-indexes/prismatic-agents.md', 'repo': 'prismatic-engine', 'title': 'Directory Index: `prismatic/agents`'}`, `{'branch': 'backup/gro-3522-inlane-disconnected', 'class': 'hidden-historical', 'path': 'docs/agy-night/directory-indexes/prismatic-agents.md', 'repo': 'prismatic-engine', 'title': 'Directory Index: `prismatic/agents`'}` |
| `4d2a718934e5` | 3 | `{'branch': 'backup/gro-3515-full-okf-blocked', 'class': 'hidden-historical', 'path': 'docs/agy-night/directory-indexes/prismatic-api-routers.md', 'repo': 'prismatic-engine', 'title': 'Directory Index: `prismatic/api/routers`'}`, `{'branch': 'backup/gro-3522-full-okf-blocked', 'class': 'hidden-historical', 'path': 'docs/agy-night/directory-indexes/prismatic-api-routers.md', 'repo': 'prismatic-engine', 'title': 'Directory Index: `prismatic/api/routers`'}`, `{'branch': 'backup/gro-3522-inlane-disconnected', 'class': 'hidden-historical', 'path': 'docs/agy-night/directory-indexes/prismatic-api-routers.md', 'repo': 'prismatic-engine', 'title': 'Directory Index: `prismatic/api/routers`'}` |
| `81667a541963` | 3 | `{'branch': 'backup/gro-3515-full-okf-blocked', 'class': 'hidden-historical', 'path': 'docs/agy-night/directory-indexes/prismatic-core.md', 'repo': 'prismatic-engine', 'title': 'Prismatic Core Directory Index'}`, `{'branch': 'backup/gro-3522-full-okf-blocked', 'class': 'hidden-historical', 'path': 'docs/agy-night/directory-indexes/prismatic-core.md', 'repo': 'prismatic-engine', 'title': 'Prismatic Core Directory Index'}`, `{'branch': 'backup/gro-3522-inlane-disconnected', 'class': 'hidden-historical', 'path': 'docs/agy-night/directory-indexes/prismatic-core.md', 'repo': 'prismatic-engine', 'title': 'Prismatic Core Directory Index'}` |
| `43285bfa5f19` | 3 | `{'branch': 'backup/gro-3515-full-okf-blocked', 'class': 'hidden-historical', 'path': 'docs/agy-night/directory-indexes/prismatic-interface.md', 'repo': 'prismatic-engine', 'title': 'Prismatic Interface Directory Index'}`, `{'branch': 'backup/gro-3522-full-okf-blocked', 'class': 'hidden-historical', 'path': 'docs/agy-night/directory-indexes/prismatic-interface.md', 'repo': 'prismatic-engine', 'title': 'Prismatic Interface Directory Index'}`, `{'branch': 'backup/gro-3522-inlane-disconnected', 'class': 'hidden-historical', 'path': 'docs/agy-night/directory-indexes/prismatic-interface.md', 'repo': 'prismatic-engine', 'title': 'Prismatic Interface Directory Index'}` |
| `c4475e3dd608` | 3 | `{'branch': 'backup/gro-3515-full-okf-blocked', 'class': 'hidden-historical', 'path': 'docs/agy-night/directory-indexes/prismatic-network.md', 'repo': 'prismatic-engine', 'title': 'Directory Index: `prismatic/network`'}`, `{'branch': 'backup/gro-3522-full-okf-blocked', 'class': 'hidden-historical', 'path': 'docs/agy-night/directory-indexes/prismatic-network.md', 'repo': 'prismatic-engine', 'title': 'Directory Index: `prismatic/network`'}`, `{'branch': 'backup/gro-3522-inlane-disconnected', 'class': 'hidden-historical', 'path': 'docs/agy-night/directory-indexes/prismatic-network.md', 'repo': 'prismatic-engine', 'title': 'Directory Index: `prismatic/network`'}` |
| `68606e0c5690` | 3 | `{'branch': 'backup/gro-3515-full-okf-blocked', 'class': 'hidden-historical', 'path': 'docs/agy-night/directory-indexes/prismatic-providers-tasks.md', 'repo': 'prismatic-engine', 'title': 'Directory Index: `prismatic/providers/tasks`'}`, `{'branch': 'backup/gro-3522-full-okf-blocked', 'class': 'hidden-historical', 'path': 'docs/agy-night/directory-indexes/prismatic-providers-tasks.md', 'repo': 'prismatic-engine', 'title': 'Directory Index: `prismatic/providers/tasks`'}`, `{'branch': 'backup/gro-3522-inlane-disconnected', 'class': 'hidden-historical', 'path': 'docs/agy-night/directory-indexes/prismatic-providers-tasks.md', 'repo': 'prismatic-engine', 'title': 'Directory Index: `prismatic/providers/tasks`'}` |
| `f47d19f5ad70` | 3 | `{'branch': 'backup/gro-3515-full-okf-blocked', 'class': 'hidden-historical', 'path': 'docs/agy-night/directory-indexes/prismatic-providers.md', 'repo': 'prismatic-engine', 'title': 'Directory Index: `prismatic/providers`'}`, `{'branch': 'backup/gro-3522-full-okf-blocked', 'class': 'hidden-historical', 'path': 'docs/agy-night/directory-indexes/prismatic-providers.md', 'repo': 'prismatic-engine', 'title': 'Directory Index: `prismatic/providers`'}`, `{'branch': 'backup/gro-3522-inlane-disconnected', 'class': 'hidden-historical', 'path': 'docs/agy-night/directory-indexes/prismatic-providers.md', 'repo': 'prismatic-engine', 'title': 'Directory Index: `prismatic/providers`'}` |
| `e50df5aab87d` | 3 | `{'branch': 'backup/gro-3515-full-okf-blocked', 'class': 'hidden-historical', 'path': 'docs/agy-night/module-cards/prismatic-agent-cards-py.md', 'repo': 'prismatic-engine', 'title': 'Module Card: `prismatic/agent_cards.py`'}`, `{'branch': 'backup/gro-3522-full-okf-blocked', 'class': 'hidden-historical', 'path': 'docs/agy-night/module-cards/prismatic-agent-cards-py.md', 'repo': 'prismatic-engine', 'title': 'Module Card: `prismatic/agent_cards.py`'}`, `{'branch': 'backup/gro-3522-inlane-disconnected', 'class': 'hidden-historical', 'path': 'docs/agy-night/module-cards/prismatic-agent-cards-py.md', 'repo': 'prismatic-engine', 'title': 'Module Card: `prismatic/agent_cards.py`'}` |
| `46de9073b81b` | 3 | `{'branch': 'backup/gro-3515-full-okf-blocked', 'class': 'hidden-historical', 'path': 'docs/agy-night/module-cards/prismatic-agents-base-py.md', 'repo': 'prismatic-engine', 'title': 'Module Card: `prismatic/agents/base.py`'}`, `{'branch': 'backup/gro-3522-full-okf-blocked', 'class': 'hidden-historical', 'path': 'docs/agy-night/module-cards/prismatic-agents-base-py.md', 'repo': 'prismatic-engine', 'title': 'Module Card: `prismatic/agents/base.py`'}`, `{'branch': 'backup/gro-3522-inlane-disconnected', 'class': 'hidden-historical', 'path': 'docs/agy-night/module-cards/prismatic-agents-base-py.md', 'repo': 'prismatic-engine', 'title': 'Module Card: `prismatic/agents/base.py`'}` |
| `4ed76ccb6779` | 3 | `{'branch': 'backup/gro-3515-full-okf-blocked', 'class': 'hidden-historical', 'path': 'docs/agy-night/module-cards/prismatic-agents-hermes-py.md', 'repo': 'prismatic-engine', 'title': 'Module Card: prismatic/agents/hermes.py'}`, `{'branch': 'backup/gro-3522-full-okf-blocked', 'class': 'hidden-historical', 'path': 'docs/agy-night/module-cards/prismatic-agents-hermes-py.md', 'repo': 'prismatic-engine', 'title': 'Module Card: prismatic/agents/hermes.py'}`, `{'branch': 'backup/gro-3522-inlane-disconnected', 'class': 'hidden-historical', 'path': 'docs/agy-night/module-cards/prismatic-agents-hermes-py.md', 'repo': 'prismatic-engine', 'title': 'Module Card: prismatic/agents/hermes.py'}` |
| `1e8e7cd6c2ad` | 3 | `{'branch': 'backup/gro-3515-full-okf-blocked', 'class': 'hidden-historical', 'path': 'docs/agy-night/module-cards/prismatic-agents-init-py.md', 'repo': 'prismatic-engine', 'title': 'Module Card: `prismatic/agents/__init__.py`'}`, `{'branch': 'backup/gro-3522-full-okf-blocked', 'class': 'hidden-historical', 'path': 'docs/agy-night/module-cards/prismatic-agents-init-py.md', 'repo': 'prismatic-engine', 'title': 'Module Card: `prismatic/agents/__init__.py`'}`, `{'branch': 'backup/gro-3522-inlane-disconnected', 'class': 'hidden-historical', 'path': 'docs/agy-night/module-cards/prismatic-agents-init-py.md', 'repo': 'prismatic-engine', 'title': 'Module Card: `prismatic/agents/__init__.py`'}` |
| `5892f2238d5e` | 3 | `{'branch': 'backup/gro-3515-full-okf-blocked', 'class': 'hidden-historical', 'path': 'docs/agy-night/module-cards/prismatic-agy-live-parser-py.md', 'repo': 'prismatic-engine', 'title': 'Module Card: `prismatic/agy_live_parser.py`'}`, `{'branch': 'backup/gro-3522-full-okf-blocked', 'class': 'hidden-historical', 'path': 'docs/agy-night/module-cards/prismatic-agy-live-parser-py.md', 'repo': 'prismatic-engine', 'title': 'Module Card: `prismatic/agy_live_parser.py`'}`, `{'branch': 'backup/gro-3522-inlane-disconnected', 'class': 'hidden-historical', 'path': 'docs/agy-night/module-cards/prismatic-agy-live-parser-py.md', 'repo': 'prismatic-engine', 'title': 'Module Card: `prismatic/agy_live_parser.py`'}` |
| `00d0b09b1c39` | 3 | `{'branch': 'backup/gro-3515-full-okf-blocked', 'class': 'hidden-historical', 'path': 'docs/agy-night/module-cards/prismatic-api-init-py.md', 'repo': 'prismatic-engine', 'title': 'Module Card: prismatic/api/__init__.py'}`, `{'branch': 'backup/gro-3522-full-okf-blocked', 'class': 'hidden-historical', 'path': 'docs/agy-night/module-cards/prismatic-api-init-py.md', 'repo': 'prismatic-engine', 'title': 'Module Card: prismatic/api/__init__.py'}`, `{'branch': 'backup/gro-3522-inlane-disconnected', 'class': 'hidden-historical', 'path': 'docs/agy-night/module-cards/prismatic-api-init-py.md', 'repo': 'prismatic-engine', 'title': 'Module Card: prismatic/api/__init__.py'}` |
| `c4b3553f2ae1` | 3 | `{'branch': 'backup/gro-3515-full-okf-blocked', 'class': 'hidden-historical', 'path': 'docs/agy-night/module-cards/prismatic-api-main-py.md', 'repo': 'prismatic-engine', 'title': 'Module Card: prismatic/api/main.py'}`, `{'branch': 'backup/gro-3522-full-okf-blocked', 'class': 'hidden-historical', 'path': 'docs/agy-night/module-cards/prismatic-api-main-py.md', 'repo': 'prismatic-engine', 'title': 'Module Card: prismatic/api/main.py'}`, `{'branch': 'backup/gro-3522-inlane-disconnected', 'class': 'hidden-historical', 'path': 'docs/agy-night/module-cards/prismatic-api-main-py.md', 'repo': 'prismatic-engine', 'title': 'Module Card: prismatic/api/main.py'}` |
| `a20a05d51d77` | 3 | `{'branch': 'backup/gro-3515-full-okf-blocked', 'class': 'hidden-historical', 'path': 'docs/agy-night/module-cards/prismatic-api-routers-credits-py.md', 'repo': 'prismatic-engine', 'title': 'Module Card: `prismatic/api/routers/credits.py`'}`, `{'branch': 'backup/gro-3522-full-okf-blocked', 'class': 'hidden-historical', 'path': 'docs/agy-night/module-cards/prismatic-api-routers-credits-py.md', 'repo': 'prismatic-engine', 'title': 'Module Card: `prismatic/api/routers/credits.py`'}`, `{'branch': 'backup/gro-3522-inlane-disconnected', 'class': 'hidden-historical', 'path': 'docs/agy-night/module-cards/prismatic-api-routers-credits-py.md', 'repo': 'prismatic-engine', 'title': 'Module Card: `prismatic/api/routers/credits.py`'}` |
| `a440dc01c88a` | 3 | `{'branch': 'backup/gro-3515-full-okf-blocked', 'class': 'hidden-historical', 'path': 'docs/agy-night/module-cards/prismatic-api-routers-init-py.md', 'repo': 'prismatic-engine', 'title': 'Module Card: prismatic/api/routers/__init__.py'}`, `{'branch': 'backup/gro-3522-full-okf-blocked', 'class': 'hidden-historical', 'path': 'docs/agy-night/module-cards/prismatic-api-routers-init-py.md', 'repo': 'prismatic-engine', 'title': 'Module Card: prismatic/api/routers/__init__.py'}`, `{'branch': 'backup/gro-3522-inlane-disconnected', 'class': 'hidden-historical', 'path': 'docs/agy-night/module-cards/prismatic-api-routers-init-py.md', 'repo': 'prismatic-engine', 'title': 'Module Card: prismatic/api/routers/__init__.py'}` |


## Cleanup status

Cleanup remains blocked. AGY audit material should remain available until final cleanup approval.

## Verification boundary

Ad hoc targeted OKF verification only — not full docs-suite green.
