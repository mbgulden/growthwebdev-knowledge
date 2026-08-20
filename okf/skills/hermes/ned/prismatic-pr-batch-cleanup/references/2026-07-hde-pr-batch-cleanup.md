# Session reference: 2026-07-28 HDE PR batch cleanup

## Context

Ned was asked to "continue down the golden path" on PR-batch cleanup for
HDE's three parent epics:

- GRO-4004 — Security, performance, operational reliability
- GRO-4010 — North Star daily work product progression
- GRO-3992 — Site-wide analytics and conversion instrumentation

All three had been reopened from Done to Todo on 2026-07-28 02:08 because their
child issues still lacked independent evidence. The session had no `GH_TOKEN`
and no `gh` auth. The user authorized a single Linear comment confirming the
PR-batch close authorization and directed continued execution.

## What the session did

1. **Inventoried 28 open HDE PRs** via anonymous REST API.

2. **Probed live product surface** (humandesignengine.com, https):
   | Path | HTTP | Body | GA4/GTM/dataLayer |
   |---|---|---|---|
   | `/` | 200 | 17115 bytes | none |
   | `/free-human-design-reading-generator/` | 200 | 8191 bytes | none |
   | `/community/` | 200 | 17115 bytes | none |
   | `/buy-report/` | 200 | 17076 bytes | none |

3. **Probed canonical branch HEAD** (raw.githubusercontent.com):
   - `src/layouts/Layout.astro` (2573 bytes): no `G-PRRRLMBR8Z`, no `GTM-P55TSP`, no `dataLayer`.
   - `public/widget.js` (21281 bytes): no analytics at all.
   - Last `Layout.astro` commit on main: `916af80aa8 2026-07-17`.

4. **Identified the gap**: PRs #21 and #23 had the necessary code but were never
   merged. The parent GRO-3992's "site-wide analytics instrumentation" claim was
   disproven by direct evidence.

5. **Anonymous `.patch` retrieval** for PRs #21 and #23, then **stripped
   git-format-patch email headers** and applied via `git apply --recount` on a
   fresh `ned/extract-analytics-loader` branch from `origin/main`.

6. **Build verification** in `/tmp/hde-analytics-extraction`:
   - `npm ci` rc=0
   - `npm run build` rc=0 — 10 Astro pages, postbuild normalized 93 built HTML files
   - `dist/index.html`, `/buy-report/`, `/deconditioning/`,
     `/free-human-design-reading-generator/`, `/checkout/pay/` all carry the
     canonical GA4 loader (`G-Q6TPL08VM7`, `googletagmanager` script, `dataLayer` init)

7. **Local commit** `cb07217 [Ned] Land HDE analytics loader + widget event helpers
   (extracted from #23/#21)` on `ned/extract-analytics-loader`.

8. **Tarball** at `/tmp/hde-analytics-extraction.tgz` (17,812 bytes).

9. **Multi-message Linear timeline** on each parent:
   - 02:08 — Reopen from Done to Todo (pre-existing, by prior dispatch)
   - 05:38 — PR-batch close authorization (parent stays Todo)
   - 05:47 — Live-surface drift finding (table + canonical HEAD probe)
   - 05:50 — Extraction branch ready, push requires human token

10. **No GH_TOKEN** — push required human action. Posted commit SHA +
    branch + worktree + tarball path + literal `git push` command.

## Drift findings

- The shipped GA4 ID is `G-Q6TPL08VM7`, not the `G-PRRRLMBR8Z` / `GTM-P55STP`
  in `config/seo_sites.json`. Treat config as outdated relative to the shipped
  loader and align in a follow-up.

## Lessons encoded

- `git apply --3way` is silently a no-op when patch context doesn't match. Always
  verify with `git diff --stat origin/main` after applying.
- The `git apply --recount` option restores proper hunk counting after a
  git-format-patch header is stripped.
- Linear `IssueFilter` does NOT accept `identifier`. Use `id` per issue.
- Linear `WorkflowState` does NOT have `title`. Use `name` / `type`.
- `comments(last: N)` drops older comments. Use `comments(last: 50)` plus a
  date-substring or body-prefix filter for verifier-style checks.
- `commentCreate` returns `success: true` but the comment may not be queryable
  on the same connection for a few hundred ms. Always re-fetch.

## Files produced

- `/tmp/hde-analytics-extraction/` — fresh clone with the extraction branch
- `/tmp/hde-analytics-extraction.tgz` — tarball of the 7 changed files
- Linear comments on GRO-4004, GRO-4010, GRO-3992 (timestamped 2026-07-28)
