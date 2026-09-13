---
name: outbound-deep-links
description: "Before writing GRO-XXXX or file links, verify they resolve."
---

# outbound-deep-links

## The rule

A link is a promise about where the recipient lands. **Verify the destination, not the status code.** SPAs with catch-all routes return 200 for *every* path — including dead ones. `curl -I` returning 200 is not evidence a deep link works.

Applies whenever a reply, report, handoff, or cron message contains a Linear issue ID, a workspace file path, or a dashboard URL — and whenever a documented link format looks stale.

## Canonical formats (verified live 2026-08-28)

| Thing | Format | Notes |
|---|---|---|
| Linear issue | `https://linear.app/growthwebdev/issue/<IDENTIFIER>` | Slug optional. Confirm existence via Linear API `searchIssues(term: …)` (recipe below). Linear is the source of truth for tasks. |
| Workspace file (prismatic) | `https://prismatic.growthwebdev.com/workspaces?file=<PATH>` | 307 → `/dashboard?file=…#workspaces`. PATH is relative to the OWNING workspace root (e.g. `prismatic/gateway/server.py` under the "Prismatic Engine" ws; `prismatic-engine/…` or `hd-platform-staging/…` under "Work Repositories"). The server picks the workspace via `/api/workspace-tree/resolve?file=…`. **Never hand-type a `workspace_id`.** |
| Dashboard tab | `https://prismatic.growthwebdev.com/<tab>` or `/dashboard?tab=<id>` | 14-tab set (dashboard, telemetry, merge, review-factory, workspaces, skills, signals, swarmproof, pwp, plugins, crons, quota, foundation, settings). **No `tasks` tab.** |

**Dead format — never emit:** `https://prismatic.growthwebdev.com/tab/tasks?issue=<ID>`. The 14-tab dashboard rebuild (2026-08-26, commit `050e50fe`) retired the tasks surface; the route still serves a catch-all 200, but the SPA only reads the params `tab`, `file`, `workspace_id`, `path`, `theme` — `?issue=` is ignored, so the link silently lands on the home tab. (Known follow-up: PE-repo link generators — `prismatic/agent_status.py`, `prismatic/agent_governance_status.py`, `prismatic/gateway/routes/pwp.py` — still emit this format; that fix belongs in the PE repo lane.)

## Verification recipes (run these, don't guess)

1. **Workspace file deep link (end-to-end):**
   ```bash
   curl -s -o /dev/null -w "%{http_code} | %{url_effective}\n" -L "https://prismatic.growthwebdev.com/workspaces?file=<PATH>"
   # expect: 200 | .../dashboard?file=…#workspaces
   curl -s "https://prismatic.growthwebdev.com/api/workspace-tree/resolve?file=<PATH>"
   # expect: {"ok":true,"workspace_id":"ws-…","relative_path":"<PATH>"}
   ```
2. **Linear issue (existence + canonical URL):**
   ```bash
   curl -s -X POST https://api.linear.app/graphql -H "Authorization: $LINEAR_API_KEY" -H "Content-Type: application/json" \
     -d '{"query":"{ searchIssues(term: \"GRO-XXXX\") { nodes { identifier url title state { name } } } }"}'
   ```
   A node with the matching `identifier` proves the issue exists; its `url` field is the canonical link. (API drift: `issue(identifier:)`, `issues(filter: {identifier})`, and `issueSearch` are all rejected/deprecated as of 2026-08 — use `searchIssues(term:)`. Details in `references/linear-graphql-lookup-2026-08.md`.)
3. **SPA param consumption (when in doubt whether a route honors a param):** fetch the deployed HTML (e.g. `curl -sL https://prismatic.growthwebdev.com/dashboard`), extract every `params.get("…")` / `URLSearchParams` usage, and confirm the param name is actually read. A param nobody reads is a dead deep link regardless of status code:
   ```python
   import re
   params = sorted(set(re.findall(r'\.get\("([a-z_]+)"\)', html)))
   ```

## Stale-format detection (when a documented link format stops working)

1. **Grep the deployed SPA** for emitted link templates (`/tab/`, `?issue=`, …) — tells you what the platform still emits (may itself be stale).
2. **Grep the owning repo** for link-builder code (`grep -rn "growthwebdev.com" --include="*.py" prismatic/`) — code-level canonical formats.
3. **Check the platform's git log** for route/UI rebuilds (`git log --oneline -- '*dashboard*' | grep -i tab`) — pin down WHEN the format changed and why.
4. **Verify the new format end-to-end** (recipes above), then update every doc that encodes the format (SOUL.md §VII for the next-step profile, OKF references elsewhere) in the SAME pass, marking the old format "dead, never emit" so the next session can't resurrect it.

## Anti-patterns

- Trusting HTTP 200 as proof a deep link works (SPA catch-alls make 200 universal).
- Reusing a documented link format without re-checking after a UI/route rebuild.
- Hand-typing a `workspace_id` into a URL (use `?file=` and let the resolve API pick the workspace).
- Linking a dashboard route for a Linear issue when the issue has a first-class `linear.app` URL.
- Updating the spec doc only after the user notices broken links — discover drift, verify, and patch the spec in one pass.
