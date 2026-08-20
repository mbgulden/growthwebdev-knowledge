# AOT Lanikai + Snorkel Path Content Refresh — 2026-07-09

## When this reference applies

Use this when executing Golden Thread SEO/content children that refresh place guides and support booking paths, especially Lanikai, Kailua, Sharks Cove, snorkel gear, beach gear, or other culture/safety-sensitive Oʻahu pages.

## Durable workflow lessons

1. **Clear the runway before content expansion.** Before starting the next Golden Thread content child, check open PRs. Close stale duplicate PRs when a newer verified PR already merged, and merge clean low-risk content/research PRs after focused verification.
2. **Close parent epics only after child verification.** For a Golden Path parent, query children live and close the parent only after every child is completed and an evidence comment is posted.
3. **Use conservative place/safety language.** For Lanikai-style pages, avoid overselling: describe neighborhood access, limited legal parking, changing restrictions, reef-safe behavior, condition matching, and respectful local etiquette.
4. **Correct conversion-path truth, not just keywords.** The Sharks Cove page incorrectly implied gear was delivered to the cove; the verified business flow is Kailua-shop pickup. Fix claims like this while strengthening SEO/internal links.
5. **Support snorkel paths with connected links.** Build a clear path from guide → rental product → destination guide, e.g. Lanikai guide → `/rentals/snorkel-gear-rentals/` → `/sharks-cove-snorkeling/`.
6. **Fix stale internal routes while refreshing copy.** Replace dead/stale paths such as `/activities/sharks-cove-self-guided-snorkel/` with the canonical live page `/sharks-cove-snorkeling/`.
7. **Verify both structure and production.** Use one `/tmp/hermes-verify-*` script before PR for HTML parse, copy markers, internal targets, and `git diff --check`; after merge/deploy/cache purge, use a second fresh `/tmp/hermes-verify-*` script against production URLs.
8. **Do not close on first stale production miss.** If Cloudflare deploy is successful but a marker is missing once, purge exact URLs and rerun a cache-busted fetch/verifier before declaring a production failure.

## Example pre-PR verifier assertions

- Changed HTML files parse with Python `html.parser`.
- Lanikai title/meta include parking/snorkeling/respectful-visit framing.
- Quick-answer block exists.
- Residential/parking respect copy exists.
- Honu/reef safety copy exists.
- Sharks Cove copy says Kailua-shop pickup, not gear delivery to the cove.
- Pūpūkea Marine Life Conservation District respect language exists.
- Stale guide path is absent.
- Canonical internal targets exist for `/rentals/snorkel-gear-rentals/`, `/beach-gear-rentals/`, and `/sharks-cove-snorkeling/`.
- `git diff --check` passes.

## Example production verifier assertions

- Lanikai page contains updated title, quick-answer block, and honu safety copy.
- Sharks Cove page contains Kailua pickup copy and Pūpūkea MLCD respect copy.
- Snorkel gear page links to `/sharks-cove-snorkeling/`, includes the North Shore surf condition qualifier, and no longer contains `sharks-cove-self-guided-snorkel`.

## Reporting pattern

When reporting to Michael, separate:

- PRs merged/closed.
- Exact main deploy commit.
- Cloudflare Pages deploy status by commit.
- Cache purge result.
- Focused ad-hoc verification output, clearly labeled as not canonical suite green.
- Remaining Golden Thread children and the exact next paddle stroke.