# Multi-User / Multi-Business Setup — Research Series

**Status:** Research pending (filed 2026-06-23)
**Linear:** Epic `GRO-2326` + 9 children (`GRO-2327`..`GRO-2335`)
**Owner:** AGY (research) + Fred (implementation)

## Context

Per Michael (2026-06-23):
> "The 'main' user of the prismatic engine should be able to set permissions.
> Maybe that's also in the user UI? So permissions are just set per user.
>
> I haven't really thought too deep about multi user setups…
> Can you input a task for AGY for a report series on multi user/business setups
> using AI, how we should arrange it, permissions, managing resources,
> roles and responsibilities. All the things!"

## What the engine looks like today (no formal permissions)

| "User" | Type | Current access |
|---|---|---|
| Michael | Human, owner | All tokens, all deploys, all config |
| Fred | AI orchestrator | Runs all workflows, full env |
| AGY | AI worker (Google CLI) | Code generation |
| Jules | AI worker (Google CLI) | Code review |
| Kai | AI worker (Google CLI) | Content + CSS |
| Ned | AI worker (Google CLI) | Infra |
| Hermes | Platform runtime | The whole orchestration substrate |

No RBAC, no audit trail, no quotas, no multi-tenancy. Adding more users
or businesses today means duplicating the setup.

## The 9 research topics

| ID | Topic | Priority |
|---|---|---|
| GRO-2327 | R1: Permission models for AI dev tools (2026 landscape) | P1 |
| GRO-2328 | R2: Resource management + quotas for AI agent fleets | P1 |
| GRO-2329 | R3: RBAC + multi-tenancy implementation plan | P1 |
| GRO-2330 | R4: UI for permissions + roles | P2 |
| GRO-2331 | R5: Audit trails + action history | P2 |
| GRO-2332 | R6: Agent identity in AI dev tools | P1 |
| GRO-2333 | R7: Multi-business tenancy: data isolation | P2 |
| GRO-2334 | R8: Onboarding + offboarding process | P3 |
| GRO-2335 | R9: Cost allocation + billing per user/business | P3 |

Each report: 1500+ words, concrete recommendations, output to
`okf/reports/multi-user-research-{topic}-{date}.md`.

## Recommended execution order

1. **First (parallel):** R1 (R3) — landscape + RBAC implementation
2. **Then:** R6 (agent identity) — decision drives everything else
3. **Then (parallel):** R2 (resources), R5 (audit), R7 (tenancy)
4. **Then:** R4 (UI) — depends on the above
5. **Finally (parallel):** R8 (onboarding), R9 (cost)

## Connection to the PWP work

The Prismatic Web Plugin already supports multiple sites per engine (we
shipped `~/.pwp/sites/{slug}.json` state tracking). The multi-user
research feeds directly into:

- **Valkyrie Arms Training** (`valkyriearmstraining.com`) — first "client"
- **Future clients** — each is a tenant
- **CF Pages projects** — already isolated, just need to surface in UI
- **Approval workflows** — already exist for prod, need multi-user approval chains
- **Billing** — needed once we have multiple paying clients

## What happens after AGY ships the research

Once all 9 reports land (estimate: 1-3 days for AGY to complete a
focused research sprint):

1. **Synthesis report** (Fred): cross-reference the 9 reports, identify
   the top 3 decisions that need to be made
2. **Architecture proposal** (AGY): concrete schema + tooling
   recommendations based on the research
3. **Implementation backlog** (linear issues filed for each component)
4. **UI/UX update** (extend `okf/standards/ui-ux-plan.md` with permissions section)

## How the user (Michael) participates

The research will produce recommendations, not final decisions. Before
any code ships, Michael reviews:
- Permission tiers: which roles should exist?
- Multi-tenancy: one DB per business vs shared?
- Cost model: charge clients or just track usage?

These are decisions, not research outputs.

## Related docs

- `okf/standards/ui-ux-plan.md` — existing UI/UX plan (will be extended)
- `okf/standards/agent-best-fit-rubric.md` — agent assignment (may need user dimension)
- `okf/standards/agent-auto-discovery.md` — auto-discovery (already supports users)
- `okf/standards/post-publish-review-architecture.md` — review chain (may extend to user approval)
- `pwp/pwp_site.py` — site state (will become tenant state)