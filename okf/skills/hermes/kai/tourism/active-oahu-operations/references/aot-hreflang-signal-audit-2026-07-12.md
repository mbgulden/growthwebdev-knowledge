# AOT hreflang signal audit — 2026-07-12

## When this applies

Use this pattern for AOT international SEO/hreflang work, especially after Japanese route cleanup, diacritical passes, or when Linear/GRO reports hardcoded/inconsistent `hreflang` tags.

## Core lesson

For AOT, correct hreflang does **not** mean every page must advertise `en` and `ja`. Only publish an alternate cluster when both route counterparts actually exist and are equivalent. If a page has no real translated counterpart, remove stale/fake `hreflang` tags instead of pointing search engines to `/ja/` or to a non-equivalent route.

## Workflow

1. Start from a clean `origin/main` worktree on a `content/<slug>` branch.
2. Scan all `site/**/*.html` with an HTMLParser-based scanner that records:
   - route for each file;
   - all `<link rel="alternate" hreflang="...">` tags;
   - whether tags are in `head` or `body`;
   - whether `en`/`ja` targets exist locally;
   - whether each target matches the expected current route/counterpart route;
   - duplicate/missing/unexpected hreflang values.
3. Normalize URLs with `urljoin`/`posixpath.normpath`; stale static exports can contain odd relative URLs like `../../../ja/...`.
4. Split rows into two buckets:
   - **safe existing counterpart**: both English and Japanese routes exist. Canonicalize to exactly one `en` and one `ja` absolute URL.
   - **missing counterpart**: expected translated route does not exist. Remove the invalid hreflang cluster; do **not** create fake `/ja/` fallbacks.
5. Save evidence under `okf/reports/golden-thread/<issue>-hreflang-audit-YYYYMMDD/`:
   - `hreflang-before.json`
   - `safe-pair-fix.json`
   - `invalid-cluster-removal.json`
   - `hreflang-final.json`
   - `README.md`
6. Verify final state with a fresh `/tmp/hermes-verify-*` script:
   - final scanner `issue_counts == {}`;
   - every remaining cluster has exactly `['en', 'ja']`;
   - each remaining `en` path equals current English route and `ja` path equals current Japanese counterpart;
   - invalid no-counterpart pages have no fake alternate cluster;
   - changed HTML parses with `HTMLParser`;
   - `git diff --check` passes.
7. Make helper scripts idempotent. Rerunning the fixer/remover against the final scan must report `changed_files: 0`. If the scanner row has no issues, the fixer should skip it.
8. After merge, verify:
   - `origin/main` contains the final report artifact and script fix;
   - open PR runway is clear;
   - production representative pairs have exact `en`/`ja` alternates;
   - no-counterpart representative pages have no hreflang cluster;
   - homepage smoke/site health still passes.
9. Update Linear with the PR, baseline counts, final counts, production samples, and the no-fake-alternates decision.

## Pitfalls

- Do not treat `counterpart_missing` as a reason to add a translated URL. It means the translated page does not exist.
- Do not use `/ja/` as a catch-all hreflang target for every English page; that is non-equivalent and can confuse search engines/users.
- Do not rely on a broad `git diff origin/main...HEAD` check before commit; uncommitted work requires `git status --short --untracked-files=all` scope checks.
- Post-merge production can briefly serve stale cached HTML. Compare `origin/main`, the Pages mirror, and cache-busted production before deciding whether a fix failed.
- When Hermes flags old worktree paths after a PR merged, verify both the flagged/legacy paths and canonical `main` paths. Assert the flagged helper script matches the canonical script on `main` when relevant.
- PR body temp files under `/tmp` can be part of the verification guard; include them in the exact-path verifier if Hermes lists them.

## Good acceptance wording

- “Final hreflang issue count: `{}`.”
- “218 valid en/ja clusters remain.”
- “80 invalid no-counterpart clusters were removed; no fake `/ja/` fallbacks were created.”
- “If the business wants every English page to have Japanese alternates, the next work is content/route creation, not hreflang tag editing.”
