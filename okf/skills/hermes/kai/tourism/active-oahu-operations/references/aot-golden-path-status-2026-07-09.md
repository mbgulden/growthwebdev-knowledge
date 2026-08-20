# AOT golden-path status pattern — 2026-07-09

Use this when Michael asks open-ended status questions like “what else is on your plate?” or “what will help us down the golden path?”

## Live checks that produced useful signal

- Lightweight production/mirror headers:
  - `activeoahutours.com` apex returned HTTP 200.
  - `www.activeoahutours.com` returned 301 to apex, then 200.
  - `active-oahu-tours-mirror.pages.dev` returned HTTP 200.
- GitHub PR list/view across both repos:
  - `active-oahu-tours-mirror` had duplicate/successor FareHarbor `/llms.txt` PRs (#60/#61), both open/clean; #61 was the stronger/latest candidate and #60 likely superseded.
  - `active-oahu-business` had the strategy/gameplan PR and KBA counter-content PR open/clean.
- Linear open AOT queue query found a broad mixed queue: Lighthouse, interviews/content, WAF/security, diacritics/alt text, content clusters, DNS/custom domain, media/social.
- Worktree status exposed untracked audit/report/script artifacts in the main mirror worktree, making workspace hygiene a real operational item rather than an internal detail.

## Good answer shape

Start with the operational bottleneck, not a dump of every task:

1. **Current verified plate** — compact table of live site, PRs, Linear queue, workspace hygiene.
2. **Big rocks** — 3–5 grouped priorities:
   - PR / queue hygiene.
   - Strategy artifact as compass.
   - Structural site defect cleanup.
   - Lighthouse/mobile booking/conversion.
   - Content growth sequenced by evidence.
3. **Recommended next move** — short ordered list of the next paddle strokes.
4. **Bottom line** — one sentence or quote-style summary.

## Golden-path prioritization learned

- Clear duplicate/superseded PRs before taking on more work; stale open PRs distort the board.
- Merge the private business gameplan so it becomes the canonical operating map before using it to sequence new work.
- Fix structural site defects from audits before adding more content sprawl.
- Prefer conversion/mobile booking access before broad SEO expansion when the site already has active booking-flow risks.
- For KBA/Lanikai/Kailua competitor response, refresh existing high-impression pages first before creating net-new hubs.

## Pitfalls

- Do not answer this kind of question from memory alone; live state changes quickly.
- Do not bury the lead in a raw Linear list. Michael wants the exact next blank to fill.
- Include workspace hygiene when untracked artifacts affect future work, but do not overemphasize internal mess unless it blocks PR quality.
