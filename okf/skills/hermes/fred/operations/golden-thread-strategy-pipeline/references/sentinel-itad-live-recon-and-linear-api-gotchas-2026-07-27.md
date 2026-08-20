# Sentinel ITAD live reconnaissance + Linear API gotchas — 2026-07-27

Session-derived reference for the "stop and survey a project field before acting" class of task. Two related pieces:

1. **Sentinel ITAD reconnaissance shape** — the read-only briefing pattern that produced the `itad-briefing-2026-07-27.md` artifact for Michael, with verified repo / project / Linear ground truth.
2. **Linear API live gotchas** — schema quirks the verifier hit during the recon, captured here so future Linear queries don't re-hit them.

Both belong in the Golden Thread umbrella because they're invariants of the "research → strategy → task" class, not one-offs.

---

## Part 1 — Sentinel ITAD reconnaissance shape

### When the user says "focus on <project>, where are we at?"

When the request is "survey a stalled project end-to-end and tell me where we are + where we are going," produce a single artifact at `/tmp/<slug>-briefing-YYYY-MM-DD.md` with these sections, in this order, with **every claim backed by a live read**:

1. **TL;DR** — three sentences max. Strategy state, single bottleneck, three bounded next moves.
2. **Verified snapshot table** — rows of `<surface> | <value> | <source>`. Surface = workspace path, GitHub repo `pushedAt`, Linear project ID + slugId + state, issue-count by state, top-value item, total inventory value, domain/email/insurance etc.
3. **Active issue cluster** — table of ID | state | priority | title | why-it's-here. Pattern column explains strategic role, not just status.
4. **Source-of-truth map** — table of canonical path | role | last touched. Verify with `ls -la`, `git log -1 --format=%cd`, or `gh repo view --json pushedAt`.
5. **Where we are** — ✅ done / 🟡 blocked / 🔴 not-yet-true lists. Include "things that are NOT urgent" so the user doesn't get pulled into side quests.
6. **Where we're going** — link to the strategy reference (here: `references/sentinel-itad-manual-resale-proof-2026-07-22.md`). State the invariant.
7. **Three bounded next moves** — table with explicit `dispatch:ready` consequences. Each move states "what I can do without you" vs "what needs your approval" vs "what is blocked elsewhere."
8. **What is NOT urgent** — explicit list. This is as important as the urgent list; it gives the user permission to defer.
9. **Verification packet** — `RESULT=PASS` block with all live-read handles + `MUTATION_*=false` + `NOT_CLAIMING=...` + `MARKER=...`.

### Why this shape works for stalled projects

- TL;DR with three sentences is the cheapest way to give the user a one-glance decision frame.
- The verified-snapshot table is what makes the briefing trustworthy. If a number is in there, the user knows you actually opened the API.
- The active-issue-cluster pattern column turns a status dump into a strategic narrative: *why* each issue is there, not just *what state* it's in.
- The "what I can do without you" breakdown is the most important table in the doc. It separates agent-actionable from blocked-on-you from blocked-elsewhere.
- "What is NOT urgent" is the permission to defer. Without it, the user feels obligated to do every item.

### Sentinel-specific invariants to keep in this shape

- **Canonical workspace is `/home/ubuntu/work/sentinel-it-asset-logistics`**; legacy `/home/ubuntu/work/sentinel-itad/` and `SovereignSentinel/sentinel-itad/` are *source material only*. Verify by checking `[docs/workspace-index.md](docs/workspace-index.md)` last_updated date.
- **Two Linear projects exist for this domain: one for homelab, one for commercial ITAD.** Do not conflate. The commercial project ID `2bcaedac-7272-47ca-8122-de096c2b22e5`; the homelab project ID `70ccfc7a-1a1a-44ff-a2bc-6c6a18136f72`.
- **The "manual-before-software" invariant** says any ITAD automation issue (GRO-1603 inventory→eBay converter, GRO-1604 order dashboard) must be `dispatch:paused` until a manual listing has sold. The Sentinel 4-task cluster (GRO-4135..4138) implements this invariant — none of them build automation.
- **eBay Developer sandbox credentials are `[MICHAEL SETUP]` (GRO-2315).** Until that issue closes, no agent can programmatically create listings; manual listing on live eBay is the only path.
- **Wipe / cert tooling (GRO-469) gates MSP outreach that mentions data-bearing media.** GRO-4138 is the workaround (compliance-safe preflight).

### Sentinel ITAD 2026-07-27 verified state (snapshot for ground-truth comparison)

```text
canonical workspace: /home/ubuntu/work/sentinel-it-asset-logistics
github: mbgulden/sentinel-it-asset-logistics pushedAt=2026-07-19
linear project: Sentinel IT Asset Logistics (2bcaedac-7272-47ca-8122-de096c2b22e5, slugId=b37d4bb3cc45, state=backlog)
linear issues: 76 total (3 Backlog, 2 Todo, 3 In Progress, 1 In Review, 29 Done, 12 Canceled + historical)
top value item: GPU-007 Nvidia A10 (24GB) mid $1,800 (range $1,400–$2,400)
top-4 resale inventory: $2,550 mid-case (range $1,895–$3,640)
single bottleneck: GRO-4135 publish-ready listing packet waiting on Michael to manually publish on eBay
verify: python3 /home/ubuntu/work/sentinel-it-asset-logistics/ops/verify_listing_packet.py -> PASS
```

### `itad-briefing-2026-07-27.md` artifact style

The briefing artifact itself was 18,201 bytes / 194 lines. Format:

- YAML front-matter with `type: Briefing`, `status: current`, `verified_by: fred (live Linear API + GitHub API + filesystem, ad-hoc targeted; not suite green)`.
- Full audit trail of every section so Michael can spot-check any claim.
- Tables, not bullets, for any structured comparison (verified snapshot, active cluster, source-of-truth, next moves).
- Explicit `NOT_CLAIMING` list to bound expectations.

---

## Part 2 — Linear API live gotchas (verified 2026-07-27)

These were verified against the live Linear API during the Sentinel recon. Each one will surface as a 400 with a "Field X is not defined by type Y" or similar; capture them up-front to avoid re-debugging.

### Auth

- **Raw `LINEAR_API_KEY` (starts with `lin_api_`) goes in the `Authorization` header value with NO `Bearer` prefix.** If you prepend `Bearer `, you get a 401. If you leave it bare, you get a 200.
- The distinction is because Linear treats API keys vs OAuth tokens as different auth styles; API keys are sent raw, OAuth tokens need the `Bearer` prefix.
- Verify with `query { viewer { id name } }` — returns the authenticated account.

### Schema mismatches the recon hit

| Wanted | Tried | Got | Correct |
|---|---|---|---|
| All projects in a team | `projects(filter: { team: { id: { eq: "..." } } })` | `Field "team" is not defined by type "ProjectFilter". Did you mean "lead"?` | Drop the team filter — `projects(first: N)` returns everything accessible, then filter client-side. |
| A project's slug | `Project.slug` | `Cannot query field "slug" on type "Project". Did you mean "slugId"?` | Use `Project.slugId` (string identifier). |
| Issues by `GRO-XXXX` identifier | `issues(filter: { identifier: { in: ["GRO-1602", ...] } })` | `Field "identifier" is not defined by type "IssueFilter"` | `IssueFilter.id` expects UUIDs, not identifiers. Filter through the project and match in Python, or use a `team` filter if the team supports it. |

### Pattern that worked

```python
import json, urllib.request
key = open('/home/ubuntu/.hermes/profiles/fred/.env').read()
v = next(line.split('=',1)[1].strip().strip('"').strip("'")
         for line in key.splitlines() if line.startswith('LINEAR_API_KEY'))

# All projects in accessible teams
q = 'query { projects(first: 100) { nodes { id name slugId description state } } }'
req = urllib.request.Request('https://api.linear.app/graphql',
    data=json.dumps({'query': q}).encode(),
    headers={'Authorization': v, 'Content-Type': 'application/json'},
    method='POST')
projects = json.loads(urllib.request.urlopen(req, timeout=20).read())['data']['projects']['nodes']

# Per-project issues (no team filter, use project.id)
issues_by_project = {}
for p in projects:
    q = 'query { issues(filter: { project: { id: { eq: "' + p['id'] + '" } } }, first: 100) { nodes { identifier title state { name type } priority url updatedAt createdAt description } } }'
    # ... fetch and bucket by state.name
```

### Why these gotchas matter

- The recon would have been a one-pass linear sweep if the schema matched what we'd intuited; instead it cost 3 round-trips. Future recon should hit these once and move on.
- The Sentinel recon specifically benefited from `slugId` over `slug` — `b37d4bb3cc45` is the canonical slug for `[Sentinel IT Asset Logistics](https://linear.app/growthwebdev/project/b37d4bb3cc45)`.
- Anyone scripting Linear GraphQL from a fresh `execute_code` sandbox needs the same env-loading dance + the auth-shape note; the existing `references/execute-code-fresh-sandbox-env-loading-2026-07-26.md` and `references/agy-gt-linear-auth-routing-and-secret-hygiene-2026-07-18.md` cover the *load* and the *label/global token* side; this reference adds the *filter schema* side.

### Not-claiming

- This list reflects the recon schema as of 2026-07-27. Linear's GraphQL schema does drift field names; if a query that worked today returns `Field ... is not defined by type ...` next session, treat this as a stale-cache signal and re-probe.
- These gotchas are not security advice — they are filter-schema corrections. Auth and secret-hygiene gotchas live in the dedicated references named above.

---

## Pitfalls — capturing the same shape next time

- **Recon without verification is not recon.** Every "current state" claim in a briefing must have a live-read handle. If you can't run the command, say so and downgrade the claim to "I believe" or remove it.
- **Do not silently skip sections that "look empty."** "What is NOT urgent" and "Things that block me without you" are the most-valuable sections for the user — they're the permission to defer.
- **Conflating Linear projects that share a domain** is a common misroute. Two projects with overlapping topics (homelab vs commercial ITAD, marketing vs governance, etc.) are not the same project. Always list *both* Linear project IDs and their distinguishing labels before reporting numbers.
- **The briefing is read-only.** Do not create new Linear issues from a reconnaissance session unless the user explicitly asked for tasks too. The artifact's `MUTATION_LINEAR=false` is a binding declaration, not a courtesy.
- **Use the existing reference for the strategy behind the recon.** Sentinel recon reuses `references/sentinel-itad-manual-resale-proof-2026-07-22.md`; do not duplicate the strategy in the briefing.

## Related references

- `references/sentinel-itad-manual-resale-proof-2026-07-22.md` — the strategy behind Sentinel ITAD's manual-before-software pivot.
- `references/linear-state-id-graphql-2026-07-26.md` — `stateId` (UUID) vs `state` (name) on `issueCreate`/`issueUpdate`.
- `references/execute-code-fresh-sandbox-env-loading-2026-07-26.md` — re-loading `LINEAR_API_KEY` at the top of each sandbox script.
- `references/agy-gt-linear-auth-routing-and-secret-hygiene-2026-07-18.md` — raw API-key vs OAuth-token auth, workspace-global label lookup, and `.git/config` credential-bleed cleanup.
- `references/agy-golden-thread-scratchpad-and-linear-routing-cleanup-2026-07-13.md` — recovering real rows from cron output instead of trusting summary headings.
