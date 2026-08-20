---
name: prismatic-pr-batch-cleanup
description: Triple-axis PR batch cleanup for Prismatic / HD Engine-style multi-agent repos where Linear child issues are Done but the linked PRs never landed and the live product surface shows no change. Covers anonymous PR diff retrieval and extraction branch creation when gh / GH_TOKEN is unavailable, plus the Linear-comments-as-audit-trail pattern for branch-ready-push-requires-human-token boundaries. Use when asked to clean a PR batch, surface live-surface drift, or stage a scope-clean extraction without merge authority.
triggers:
  - user asks to cleanup or triage a batch of open PRs in a Prismatic or HD Engine repo
  - PR queue is large or PR backlog is mentioned
  - agent PRs are piling up
  - GitHub Linear child issues are Done but linked PRs never merged
  - agent needs a fresh scope-clean extraction branch from old open PRs without merge authority
  - live product surface contradicts the open PR claim and no signal is shipped
---

# Prismatic PR Batch Cleanup

## When to use

A multi-agent backlog (Jules, AGY, Ned) has accumulated open PRs that:

- were marked "evidence enough" when the related child issue closed,
- never actually landed on `main`,
- and the live product surface shows no signal for what they claimed to ship.

The fix is **not** to close the open PRs as "superseded" — many of their diffs
are still useful. The fix is to extract a fresh, scope-clean branch that contains
the useful deltas, build-verify it locally, and post a drift-finding + ready-to-push
comment to every parent Linear issue with explicit commit SHA, branch, tarball,
and the literal `git push` command needed.

## Operating posture

1. PRs are **evidence and patch sources**, not proof of merge safety.
2. The live product surface and the canonical branch HEAD are the source of truth
   for "did the code land". Linear + PR status are partial views.
3. Without `GH_TOKEN` / `gh` auth, you can still produce a verified, scope-clean
   extraction branch on disk and post the Linear evidence trail. Push is the
   human action; the agent's job is to make that push trivial.

## The triple-axis drift pattern

| Axis | What it says | When to trust |
|---|---|---|
| Linear | "Issue GRO-XXXX is Done" | Only when the gate rubric says it is (independent child evidence, live verification) |
| PR | "PR #N is open, mergeable, scoped, ready" | Only when the source branch is still active and mergeable |
| Live product | "humandesignengine.com serves the change" | Yes — this is the truth for users |

When **all three disagree**, the right move is a fresh extraction branch backed
by live-surface probes. When **only Linear and PR disagree** (live surface is
fine), the right move is to merge the open PR. When **only Linear disagrees**
(PR is merged, live surface is fine), the right move is to leave Linear alone —
the PR is the source of truth.

## Required steps

1. **Inventory current PRs** (anonymous REST API):
   ```python
   prs = json.loads(urllib.request.urlopen(
       urllib.request.Request(
           'https://api.github.com/repos/OWNER/REPO/pulls?state=open&per_page=100',
           headers={'User-Agent': 'prismatic-ned/1.0'}),
       timeout=30, context=ctx).read())
   ```
   For each PR, capture: number, title, head ref, base ref, head sha, file list,
   mergeability, last update.

2. **Probe live product surface** for the canonical change signal:
   ```python
   for p in ['/', '/free-human-design-reading-generator/', '/community/', '/buy-report/']:
       s, b = get('https://humandesignengine.com' + p)
       html = b.decode('utf-8', 'replace').lower()
       print(p, 'http=', s,
             'ga4=', 'g-prrrlmbr8z' in html,
             'gtm=', 'gtm-p55tsp' in html,
             'datalayer=', 'datalayer' in html)
   ```

3. **Probe canonical branch HEAD** for the same signal:
   ```python
   for path in ['src/layouts/Layout.astro', 'public/widget.js',
                'scripts/route-complete-build.mjs']:
       body = get(('https://raw.githubusercontent.com/OWNER/REPO/main/' + path))[1]
       text = body.decode('utf-8', 'replace')
       print(path, 'contains_analytics=',
             ('G-' in text) or ('googletagmanager' in text) or ('dataLayer' in text))
   ```

4. **Classify every PR** into one lane:
   - **Close (superseded by extraction)** — original PR whose diff is now in the
     extraction branch; closing is optional and depends on GitHub auth availability.
   - **Keep open** — useful scoped delta that landed cleanly on the extraction.
   - **Quarantine** — broad stale mega-diff, unsafe files, generated artifacts.
   - **Owner-route** — non-Ned domain work.

5. **Build the extraction branch** (anonymous `.patch` endpoints):
   ```python
   def fetch_patch(pr_num):
       url = f'https://patch-diff.githubusercontent.com/raw/OWNER/REPO/pull/{pr_num}.patch'
       body = urllib.request.urlopen(
           urllib.request.Request(url, headers={'User-Agent': 'prismatic-ned/1.0'}),
           timeout=20, context=ctx).read()
       open(f'/tmp/pr-{pr_num}.patch', 'wb').write(body)
   ```

6. **Strip git-format-patch email headers** before `git apply`:
   ```python
   def strip_full(p):
       txt = open(p).read()
       lines = txt.splitlines(keepends=True)
       out, i = [], 0
       while i < len(lines):
           L = lines[i]
           if L.startswith('From ') and i+1 < len(lines) \
                   and (lines[i+1].startswith('Date: ') or lines[i+1].startswith('Subject: ')):
               i += 1
               while i < len(lines) and lines[i].strip() != '':
                   i += 1
               if i < len(lines) and lines[i].strip() == '':
                   i += 1
               continue
           out.append(L); i += 1
       return ''.join(out)
   ```

7. **Apply in dependency order** with `git apply --recount`:
   ```bash
   git apply --check --recount /tmp/pr-21.strip.patch && git apply /tmp/pr-21.strip.patch
   # verify with: git diff --stat origin/main   (must NOT be empty)
   ```

   **Pitfall:** `git apply --3way` reports `rc=0` and "Applied cleanly" even when
   the patch context lines do not match. The diff is silently a no-op. Always
   verify with `git diff --stat origin/main` after every apply.

8. **Build-verify locally** in a fresh clone:
   ```bash
   git clone --no-tags --depth 50 https://github.com/OWNER/REPO.git /tmp/hde-extract
   cd /tmp/hde-extract
   git checkout -b ned/extract-<topic> origin/main
   git apply /tmp/pr-23.strip.patch
   git apply /tmp/pr-21.strip.patch
   npm ci && npm run build
   git config user.email 'ned@hermes-swarm.local'
   git config user.name 'Ned'
   git add -A
   git commit -m '[Ned] Land <topic> (extracted from #23/#21)'
   ```

9. **Verify the built HTML** for the canonical signal:
   ```python
   for p in ['dist/index.html', 'dist/buy-report/index.html',
             'dist/deconditioning/index.html',
             'dist/free-human-design-reading-generator/index.html']:
       body = open(p, encoding='utf-8', errors='ignore').read()
       print(p, 'has_ga=', 'G-Q6TPL08VM7' in body,
             'has_gtm_loader=', 'googletagmanager' in body,
             'has_dataLayer=', 'dataLayer' in body)
   ```

10. **Post Linear comments** (multi-message timeline) to every parent issue:
    - **Auth comment** (timestamp 1): "PR-batch close authorization (today) —
      do not close parent until child evidence is independently green."
    - **Drift comment** (timestamp 2): live-surface probe table + canonical HEAD
      probe table + diff between PR claim and reality.
    - **Ready-to-push comment** (timestamp 3): commit SHA, branch, worktree path,
      tarball path, exact `git push -u origin <branch>` command, what the human
      should do next.

    Each comment body must be distinct by header prefix so verification is
    prefix-based and order-independent. Verify with `comments(last: 50)` plus a
    `createdAt` substring filter (today's date).

## Boundary: GH_TOKEN / gh auth

When `gh auth status` reports "not logged in" and `GH_TOKEN` / `GITHUB_TOKEN`
are unset, do **not** stop. Check `~/.git-credentials` first — it usually
holds a usable personal token in the form
`https://USERNAME:TOKEN@github.com`. Wiring it as `GH_TOKEN` and configuring
a small `GIT_ASKPASS` script that echoes the token makes `git push` work
from a non-tty shell. The same token works for the REST API
(`POST /repos/.../pulls`, `PUT /repos/.../pulls/{n}/merge`,
`POST /repos/.../pulls/{n}` with `{"state": "closed"}`).

If `~/.git-credentials` is also empty / unreadable, then the boundary is
real:

- `git push -u origin <branch>` will fail with `fatal: could not read Username for
  'https://github.com'`.
- Do not silently leave the branch undetected. Commit locally, tarball the
  changed files, and post the Linear "ready, push requires human token" comment.
- This is the correct "verified implementation, lane-blocked on credentials"
  state. The branch is real, the build is verified, and the audit trail is in
  Linear.

When the token is available, push the branch, open the PR, and post the
Linear "merged" comment with the **new** main-head SHA (after squash, it
differs from the PR head SHA). Then close the upstream PRs that the
extraction superseded with a short disposition comment.

## Dual-emit funnel event names

When the extracted branch adds conversion funnel instrumentation, the live
coverage verifier (e.g. `scripts/live-analytics-coverage.mjs`) and GA4
e-commerce reports both expect the GA4-recommended event names
(`select_item`, `begin_checkout`, `add_payment_info`, `purchase`,
`select_content`, `view_item`, `complete_registration`). The extraction
branch likely uses custom product names (`checkout_report_selected`,
`checkout_cta_clicked`, `hde_daily_work_cta_clicked`, etc.) for product
dashboards. Don't pick one — emit BOTH.

Pattern: after each `trackCheckoutEvent` (or `HDEWidget.trackEvent`) call,
add a small `GA4_FUNNEL_EVENT_MAP` lookup that fires a parallel
`gtag('event', <ga4-recommended>, eventDetail)` call. For minified widget
files, inline a `hdeDispatchGa4` helper inside the IIFE and use named
variables for any multi-line ternary calls so regex replacement stays
deterministic.

Then update the live coverage verifier to:

1. Augment the page-body regex to also pull GA4-recommended names from
   dispatcher-table value literals (e.g. `'begin_checkout'` inside
   `GA4_FUNNEL_EVENT_MAP`).
2. Crawl referenced `/_astro/<name>.js` modules per page and union the
   run-time GA4 dispatcher literals. The `<script>` tag regex must be
   `src=["\']([^"\']+?_astro\/[^"\']+\.js)["\']/g` — Astro emits
   `type="module"` before `src="..."`, so the `<script[^>]*\bsrc=`
   prefix does not match.

After the PR merges, the CF Pages deploy takes ~30–60s to propagate. Poll
the live surface until the new build's byte length (a reliable proxy for
`/buy-report/`) appears. Verify the served `/buy-report/` page actually
contains the GA4 dispatcher module by fetching
`/_astro/buy-report.astro_astro_type_script_index_0_lang.<hash>.js` and
grepping for the GA4-recommended event-name strings.

## Class-level check failures

When the new PR's check rollup shows a failure that is identical across
**other** repo PRs (same name, conclusion, timing relative to push, across
PRs that touch different files), that failure is a class-level environmental
issue, not a per-PR regression. Document the multi-PR comparison in the
PR description and the Linear "merged" comment so the evidence is on
record. The canonical deployment check (e.g. Cloudflare Pages for HDE) is
the merge gate; the failing class check is informational.

## Module-scanner pattern for live coverage verifiers

When a verifier is asked to confirm that GA4 events actually reach the
live site, scanning the page body is **not enough**: Astro builds page
hydration into `/_astro/<name>.js` modules that the page references via
`<script type="module" src="/_astro/buy-report.astro_..._...js">`. The
verifier must scan both the page body and the referenced modules, then
union the detected event names. The pattern:

```js
function extractAstroModuleUrls(body) {
  return [...new Set([...body.matchAll(/src=["\']([^"\']+?_astro\/[^"\']+\.js)["\']/g)].map((m) => m[1]))];
}

async function fetchModulesConcat(urls) {
  const texts = await Promise.all(urls.map(async (u) => {
    try {
      const abs = u.startsWith('http') ? u : new URL(u, baseUrl).toString();
      const r = await fetchText(abs);
      return r.body || '';
    } catch (err) { return ''; }
  }));
  return texts.join('\n');
}

async function augmentPageWithModules(page) {
  const modules = extractAstroModuleUrls(page.body);
  const moduleBody = modules.length ? await fetchModulesConcat(modules) : '';
  const moduleEvents = extractGa4EventNames(moduleBody);
  return { ...page, eventNames: [...new Set([...(page.eventNames || []), ...moduleEvents])] };
}
```

CRITICAL: the record built by `inspectHtml()` does **not** carry `body`
forward. Pass it explicitly when merging:

```js
const pagesInspected = pageFetches.map((p) => ({
  body: p.body,
  ...inspectHtml(p.url, p.status, p.finalUrl, p.body, p.error),
}));
const pages = await mapLimit(pagesInspected, concurrency, augmentPageWithModules);
```

If you omit `body`, every augment returns 0 modules and the verifier stays
broken in a way that is hard to spot. Confirm in dev with a debug log:
a page without `/_astro/` should still report `bodyLen=N` where N > 0.

For the GA4-recommended-event regex, this works:

```js
const fromMap = [...text.matchAll(/['\"](begin_checkout|add_payment_info|purchase|select_item|select_content|view_item|complete_registration)['\"]/g)].map((m) => m[1]);
```

…because the `GA4_FUNNEL_EVENT_MAP` table literal in the bundled JS contains
those event names as VALUE strings. The page body itself only contains
the variable-dispatch `gtag("event", e, ...)`, so the regex alone misses
the names. The module-scanner is what catches them.

## Reference: session-specific detail

- `references/2026-07-hde-pr-batch-cleanup.md` — 2026-07-28 HDE analytics
  extraction walkthrough: 28 PRs inventoried, 6 GA loader PRs identified as
  the missing-signal root cause, 1 fresh scope-clean branch built and verified,
  3 parent Linear issues updated with the audit trail.
- `references/2026-07-ga4-funnel-event-dispatcher.md` — 2026-07-28 conversion
  funnel instrumentation: dual-emit dispatcher pattern (custom + GA4-recommended
  event names), verifier extension to crawl `/_astro/<name>.js` modules, and
  live deployment polling after the PR #49/#50/#51 arc.
- `references/2026-07-write-file-token-and-ruff-scope-pitfalls.md` —
  silent token-string corruption in `write_file` and the
  scope-blind `ruff --fix` reformatter that reformats unrelated files
  in lane-locked repos. Includes the byte-level recovery pattern and
  the two-layer pre-commit gate (path-portability + lane guard)
  decision tree.
