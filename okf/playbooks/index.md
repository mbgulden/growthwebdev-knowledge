---
type: Index
title: Playbooks
description: Operational playbooks — step-by-step procedures for recurring tasks (incident response, deployment, recovery).
resource: okf/playbooks/index.md
tags: [index, playbooks]
timestamp: 2026-06-19T11:30:00Z
linear_issue: GRO-2039
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/playbooks/index.md
last_verified: 2026-06-25
verified_by: kai
status: current
---

# Playbooks

Step-by-step procedures for recurring operational tasks. A playbook is
distinguished from a **standard** by being a procedure (do these steps
in this order) rather than an invariant (follow these rules).

## Current playbooks

| Playbook | Description |
|---|---|
| [`prismatic-engine-tasks.md`](./prismatic-engine-tasks.md) | Where everything is, how to do common tasks (deploy, debug, rotate secrets, re-enable AGY) |

## Candidates (when promoted)

- Ubersuggest MCP token-refresh procedure (currently inline in
  [`okf/integrations/ubersuggest-mcp.md`](../integrations/ubersuggest-mcp.md))
- Re-auth flow for any OAuth-based integration
- LinearGraphQL rate-limit recovery
- Cloudflare Pages rollback
