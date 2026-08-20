# Project-portfolio gap analysis — 2026-07-27

Session-derived reference for the class of "what gaps need filling across the whole portfolio?" question Michael asks. Distinct from per-project reconnaissance (which is one-project-at-a-time); this is portfolio-wide and produces a ranked gap list with priority order.

## When the user says "what gaps need filling?"

Use this shape. Produces a single artifact (chat or `/tmp/<filename>.md`) with:

1. **TL;DR** — one sentence: the single highest-priority gap and why.
2. **Ranked gap table** — rows of `<area> | <gap> | <why it matters> | <P0/P1/P2>`. P0 = revenue-closest or actively-blocking, P1 = operational debt, P2 = strategic.
3. **Priority order block** — a one-line list of the top three with their rationale ("revenue first because…").
4. **The one next action** — explicitly: what the agent can do without Michael, what needs Michael, what's blocked elsewhere.

## Why this shape works for portfolio questions

- Portfolio-level questions need a **ranked** answer, not a flat list. Without ranking, Michael has to do the prioritization himself — which is exactly the work he wants off his plate.
- P0/P1/P2 lets Michael scan in 5 seconds and pick the "I'm doing that one today" item without reading the whole table.
- "The one next action" forces a single bounded slice. If the gap analysis produces 7 next actions, the analysis is wrong; it should produce one that resolves the P0.
- Portfolio gap analyses are **not** research dumps. The user already knows what's in the portfolio; they want a strategic ranking.

## Worked example: 2026-07-27 portfolio gaps

Michael asked "what gaps need filling?" — the response was a 7-area ranked gap list with revenue-priority ordering. The shape:

| # | Gap | Priority | Why |
|---|---|---|---|
| 1 | Active Oahu: turn the live site into booked revenue | P0 | Closest to money |
| 2 | Michael's manual sales actions | P0 | Human-only bottleneck |
| 3 | Active Oahu operating handoff | P1 | Reduces Michael dependency |
| 4 | Prismatic/Agentic Swarm: durable proof | P1 | Proves the machine works |
| 5 | Linear backlog hygiene | P1 | Prevents churn |
| 6 | HD Engine: close path from localhost to product | P2 | Long-term platform |
| 7 | AI Consulting: prove a channel | P2 | High-ticket validation |

The "one next action" was: **run a narrow Active Oahu booking-CTA reconciliation and mobile smoke test**, then convert findings into smallest revenue-impacting fix list. No new infrastructure until proven.

## Distinction from `references/sentinel-itad-live-recon-and-linear-api-gotchas-2026-07-27.md`

| Aspect | Recon (per-project) | Gap analysis (portfolio) |
|---|---|---|
| Scope | One project | Whole portfolio |
| Output size | 1 briefing artifact | Chat reply + maybe one table |
| Sections | 9 (TL;DR, snapshot, cluster, source-of-truth, where-are-we, where-going, three moves, NOT-urgent, verification) | 4 (TL;DR, ranked table, priority block, one next action) |
| Live-read depth | Deep (one project's full surface) | Shallow (one signal per area) |
| Time cost | ~10–20 min | ~3–5 min |
| Trigger | "focus on X" | "what gaps need filling" |

Use recon when the question scopes to one project. Use gap analysis when the question is portfolio-wide.

## Pitfalls

- **Do not produce 10+ gaps.** A portfolio gap analysis with 10 items fails the "one next action" promise. If you have 10 gaps, the analysis is wrong; re-rank ruthlessly.
- **Do not put equal priority on everything.** If everything is P0, nothing is P0. Reserve P0 for revenue-closest and human-blockers; everything else is P1 or P2.
- **Do not mix classes of work.** A gap about "Active Oahu CTA broken" is operational. A gap about "AI Consulting channel not validated" is strategic. Mixing them in one table makes both look like low-priority tickets. Cluster similar gaps in adjacent rows so the user can scan a band at a time.
- **Do not include gaps that are not gaps.** "We need more Linear issues" is not a gap. "Active Oahu has 3 broken booking CTAs" is a gap. State the gap as a concrete missing thing, not as a generic aspiration.
- **Do not skip the "why" column.** A ranked table without a why column is just a list. The why is what turns a list into a strategy.

## Output format constraints

- **Telegram-friendly width.** Lead with the link, then the substance. Don't exceed ~70 chars per visual line. Use real Markdown tables because they degrade gracefully in plain text.
- **Tables for structured data, bullets only for genuinely free-form items.** "What is NOT urgent" can be a bullet list; the ranked gaps themselves must be a table.
- **One action item at the bottom, not a numbered list of five.** The point of the gap analysis is to commit to ONE bounded next step.

## Related references

- `SKILL.md` §6 "Create Linear tasks with rubrics and exit criteria" — when a gap is concrete enough to become a Linear epic.
- `references/sentinel-itad-live-recon-and-linear-api-gotchas-2026-07-27.md` — per-project recon shape (deeper than portfolio gap analysis).
- `references/active-oahu-cro-cta-reconciliation-2026-07-20.md` — example of a gap-to-task pipeline for one specific domain.