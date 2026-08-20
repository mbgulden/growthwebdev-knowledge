# AOT PR Merge + Production Verification Notes — 2026-07-08

Use this as a pattern for AOT PRs that change production behavior.

## Sequence that worked

1. Review PR live with GitHub state/checks:
   - `gh pr view <n> --repo mbgulden/active-oahu-tours-mirror --json state,isDraft,mergeable,mergeStateStatus,statusCheckRollup,files,url`
   - Confirm all checks are `SUCCESS`, PR is not draft, and `mergeable=MERGEABLE` / `mergeStateStatus=CLEAN` before merging.
2. Merge low-risk governance/audit PRs before site-behavior PRs.
3. Merge site-behavior PRs, then run production verification against `activeoahutours.com`, `www.activeoahutours.com`, and the Pages mirror.
4. If production verification finds a regression, do **not** close Linear yet. Open a hotfix branch/PR, verify locally/preview, merge, purge cache where needed, then re-run production verification.
5. Only close Linear when final production verification passes. Leave items in review if an acceptance criterion needs external/human-only access, e.g. Google Search Console sitemap submission.

## Cloudflare cache / deployment verification pattern

When merged content does not appear consistently:

- Check both Pages mirror and production apex with cache-busting query params.
- Purge exact URLs through Cloudflare when needed, including both apex and `www` forms.
- Re-fetch after purge with `Cache-Control: no-cache` and a distinct User-Agent.

Example Python Cloudflare purge shape:

```python
payload = {"files": [
  "https://activeoahutours.com/path/",
  "https://www.activeoahutours.com/path/",
]}
POST /client/v4/zones/{zone}/purge_cache
headers: X-Auth-Email, X-Auth-Key, Content-Type: application/json
```

## Mobile/browser behavior verification pattern

Static HTML checks are not enough for mobile UI changes. For mobile CTA work, verify both markup and rendered behavior:

- Static fetch: marker/component/events present in production HTML.
- Mobile browser/CDP: at ~390px width, scroll down, assert CTA exists, expected button label is visible, `display != none`, opacity is nonzero, and desktop width hides it.

Useful fields to inspect in page JS:

```js
(() => {
  const bar = document.querySelector('[data-aot-mobile-cta]');
  const btn = document.querySelector('[data-aot-mobile-cta-button]');
  if (!bar || !btn) return { exists: false };
  const cs = getComputedStyle(bar);
  return {
    exists: true,
    hidden: bar.hidden,
    classes: bar.className,
    display: cs.display,
    opacity: cs.opacity,
    button: btn.textContent.trim(),
    bodyPadding: getComputedStyle(document.body).paddingBottom,
    width: innerWidth,
    scrollY: scrollY
  };
})()
```

## Pitfall encountered

A broad selector in the CTA suppression logic treated normal page markup as an active FareHarbor overlay:

```js
[class*="fareharbor"]
```

That caused the CTA to be hidden on some production pages even though static checks passed. Fix pattern:

- Do not suppress on broad `fareharbor` class presence alone.
- Check specific visible overlay candidates only: FareHarbor iframe, `.fh-modal`, `.fareharbor-iframe`, `[data-fh-modal]`, lightframe classes/IDs.
- Add a visible-overlay helper that checks computed style and bounding box before suppressing.

## Linear closure discipline

- Close issues only after merged PRs and production verification are complete.
- If an acceptance criterion cannot be verified with available access, post evidence and leave the issue in review. Example: `sitemap.xml` was live and `200`, but Google Search Console submission was not verified because no GSC session/API access was available.
