---
type: Index
title: Integrations
description: Index of external tool integrations (MCP servers, SaaS APIs, OAuth setups) used across growthwebdev projects.
resource: okf/integrations/index.md
tags: [index, integrations, mcp, saas]
timestamp: 2026-06-19T11:15:00Z
linear_issue: GRO-2039
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/integrations/index.md
last_verified: 2026-06-19
verified_by: kai
status: current
---

# Integrations

External tool integrations that span multiple growthwebdev projects. Each
integration is owned by one agent (typically Kai) and documented with its
auth flow, token storage, and known failure modes.

## What counts as an "integration"

A documented integration is any external system accessed programmatically
across more than one project, where future agents will need to re-auth,
debug, or extend. Examples:

- MCP servers (Ubersuggest, future SEO/marketing tools)
- SaaS APIs used by multiple sites (Cloudflare, Stripe, Google APIs)
- Shared OAuth clients with project-scoped token files

A integration doc is *not* a project-specific configuration (those live in
project spokes). It's the canonical reference that any agent picks up
when first encountering the integration.

## Current integrations

| Integration | OKF location | Owner | Status |
|---|---|---|---|
| Linear webhook handler | [`./webhook-handler-test-pattern.md`](./webhook-handler-test-pattern.md) | fred | ✅ Active |
| Ubersuggest MCP | [`./ubersuggest-mcp.md`](./ubersuggest-mcp.md) | kai | ✅ Active |
| Linear webhook events | [`./linear-webhook-events.md`](./linear-webhook-events.md) | What events to subscribe to when configuring Linear webhooks (GRO-2084) |
| Cloudflare Tunnel webhooks | [`./cloudflare-tunnel-webhooks.md`](./cloudflare-tunnel-webhooks.md) | How webhooks.growthwebdev.com routes to port 9000 via Tunnel (GRO-2084) |
| Jules CLI | [`./jules-cli-capability-report.md`](./jules-cli-capability-report.md) | kai | ✅ Active |
| API keys & tokens registry | [`./api-key-locations.md`](./api-key-locations.md) | fred | ✅ Active |
| Cloudflare AOT account (activeoahutours.com) | [`./cloudflare-account-activeoahu.md`](./cloudflare-account-activeoahu.md) | ned | ✅ Active |

## Format

Each integration doc uses frontmatter `type: Integration` plus:

- `auth_method` — OAuth-PKCE, OAuth-OOB, API key, service account, etc.
- `token_storage` — where the credentials live on disk
- `oauth_client_id` — for Google/MCP-style flows
- `scope` — required OAuth scope(s)
- `tier` — what subscription tier unlocks the tools we use
- `last_verified` — when the connection was last confirmed working

Body sections:

1. **TL;DR** — one-paragraph summary of status
2. **Connection** — endpoint URL, auth flow, token storage
3. **Tool inventory** — what tools are available and their tier requirements
4. **Known failure modes** — what breaks and how to recover
5. **Re-auth procedure** — copy-paste-ready commands

Cross-references: each integration links to the Linear issue that tracks
it (when applicable) and to any project spokes that use it.
