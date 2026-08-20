# AOT Strategic Gameplan Consolidation

Use this when Michael asks whether ActiveOahuTours.com has a gameplan, asks for the strategy, or asks for a comprehensive plan based on repo reports plus Search Console/Ubersuggest/analytics.

## Source hierarchy

1. **Live site/repo state** — production apex, `www`, mirror, open PRs, branch/worktree status.
2. **GSC for AOT truth** — use `sc-domain:activeoahutours.com`; pull recent final data by `query,page`; aggregate by query and page.
3. **Ubersuggest for competitor intel** — domain overviews/top pages/keywords for AOT and competitors; do not treat Ubersuggest AOT traffic as truth.
4. **Private business reports** — competitive strategy, vendor/analytics notes, media index, operations/governance decisions.
5. **Public mirror audits** — site inventory, orphan pages, schema, broken links, CTA/CRO audits, Lighthouse/a11y reports.
6. **GA4/analytics** — include only when access is actually verified. If ADC lacks Analytics scopes, report the concrete blocker and continue with GSC + Ubersuggest + repo audits instead of inventing conversion data.

## Recommended output artifacts

Save strategy work in the private business repo, not the public mirror:

```text
okf/reports/strategy/YYYY-MM-DD-active-oahu-tours-gameplan.md
okf/reports/strategy/data/YYYY-MM-DD-aot-gameplan-data.json
```

Open a PR from a clean worktree/branch such as:

```text
strategy/aot-gameplan-YYYY-MM-DD
```

## Plan structure

A strong gameplan should include:

- Direct answer: whether a single plan existed, and what was consolidated.
- North star: one concise statement of what the site is trying to become.
- Current verified state: live site, repo/PR state, GSC metrics, competitor snapshot, site audit/CRO/media facts.
- Strategy lanes: measurement, mobile conversion, internal architecture, evidence-backed content clusters, trust/media.
- 30/60/90 roadmap.
- Priority backlog grouped as P0/P1/P2.
- KPI framework and cluster scorecard.
- Immediate next 10 tasks.
- Explicit caveats/blockers, especially GA4 access if unavailable.

## Data extraction pattern

For GSC, pull approximately 90 days of final rows with dimensions `query,page`, then aggregate:

- totals: clicks, impressions
- top queries: clicks, impressions, CTR, impression-weighted position, top pages
- top pages: clicks, impressions, CTR, impression-weighted position, top queries
- opportunities: high impressions + low CTR + position in striking distance

For Ubersuggest, collect at minimum:

- `domain_overview` for AOT and major competitors
- `domain_top_pages` for AOT and the most direct competitor
- `domain_keywords` for AOT and the most direct competitor
- `competitors` for AOT if the tool returns usable data

## Verification

Because strategy/report work often has no canonical test suite, create a focused `/tmp/hermes-verify-*` script that checks:

- Markdown plan exists and is substantial.
- Raw JSON parses.
- GSC totals in the plan match the JSON/live pull.
- Required sections exist.
- Key evidence strings exist.
- PR body contains summary, verification, and caveat language.

Report this as **focused ad-hoc verification**, not a canonical suite green.

## Pitfalls

- Do not answer a strategic state question from memory alone; inspect live repo/site state and current data where accessible.
- Do not claim GA4 conversion evidence unless Analytics access is verified or the user supplied an export.
- Do not create a strategy in the public deployable mirror; competitive/GSC/vendor strategy belongs in `active-oahu-business`.
- Do not treat “more content” as the plan. AOT’s durable sequence is measurement → mobile conversion → internal links → evidence-backed content clusters → trust/media.
- Do not bury the immediate next actions; Michael wants the exact next blank to fill after a big synthesis.