# CDN-Served Stale JS After Deploy (2026-07-31)

> **Session source:** Active Oahu lightbox work. After pushing a fix that updates `gallery-lightbox.js` (and verifying `dist/index.html` hash matches), `curl https://...active-oahu-tours-mirror.pages.dev/js/gallery-lightbox.js` returned the **previous version** of the file — same old logic, no new URL derivation. The deploy had only partially propagated.
>
> **Use this when:** a user reports a fix didn't work, or your browser-based verification shows the same broken behavior after a fresh deploy + hash match.

## The Trap

```bash
# Hash matches → looks safe
LOCAL=$(sha256sum dist/index.html | awk '{print $1}')    # 675434ed...
DEPLOYED=$(curl -s "$URL" | sha256sum | awk '{print $1}') # 675434ed...
[ "$LOCAL" = "$DEPLOYED" ] && echo "MATCH"
```

But the JS file is a separate asset:

```bash
# The HTML points to /js/gallery-lightbox.js — this is fetched independently
curl -s "$URL/js/gallery-lightbox.js" | grep "data-full"
# Empty — old version still served
```

CF Pages serves `index.html` and its sub-assets from different cache layers. The HTML can be hot while the JS is cold (or vice versa).

## Why This Happens

CF Pages uses Cloudflare's CDN to cache static assets. Hash-named CSS bundles are content-addressable — when the file content changes, the hash changes, the URL changes, and the CDN serves the new URL fresh. **Same-content URLs do not get this automatic cache busting.**

For unhashed assets (especially files in `public/js/` or `public/wp-content/`), the URL stays the same across deploys. The CDN's `must-revalidate` cache directive helps, but there's a window where:

- The deploy was acknowledged.
- The HTML edge cache was invalidated and refreshed.
- The HTML now references `/js/gallery-lightbox.js` (unchanged URL).
- The CDN edge for `/js/gallery-lightbox.js` may still be serving the previous version because Cloudflare's per-asset invalidation hasn't fired yet (or the edge wasn't in the cache and revalidated from origin while the deploy was mid-flight, locking in the old version).

Real timing: 1–15 minutes for the asset cache to fully refresh, even when the HTML refresh is immediate.

## Detection Recipe

When the user says "the feature I just shipped doesn't work":

```bash
# 1. Confirm the local file has the new content
grep -c "expected_new_symbol" "$WORK/public/js/script.js"
# Expected: 1 (or higher if it's already there)

# 2. Confirm the dist file has the new content
grep -c "expected_new_symbol" "$WORK/dist/js/script.js"
# Expected: 1

# 3. Check what the deployed URL is serving
DEPLOYED=$(curl -s "$URL/js/script.js")
echo "$DEPLOYED" | grep -c "expected_new_symbol"
# Expected: 1, BUT IF 0 → CDN is serving the old version

# 4. If 0, add a cache-buster and re-check
curl -s "$URL/js/script.js?nocache=$(date +%s)" | grep -c "expected_new_symbol"
# Likely 1 — the cache-buster forces edge revalidation

# 5. If the cache-buster works but the original URL doesn't, this ISN'T a deploy failure,
#    it's CDN cache lag. Wait 5–15 minutes and re-test the original URL.
```

If step 1 and 2 are both 0, the source wasn't actually edited (the `aot-hallucinated-commit-verification-2026-07-31.md` failure mode). Fix the source first.

If step 3 is 0 but step 4 is 1, it's CDN lag — be patient, don't re-deploy.

## Multiple Cache Layers Can Desync

CF Pages sits behind Cloudflare's global CDN. There are typically 3 cache layers:
1. **Browser cache** — per-user, controlled by `cache-control` headers from CF Pages.
2. **Cloudflare edge cache** — regional POPs.
3. **Origin (CF Pages KV)** — the source of truth.

A `must-revalidate` header means "stale-while-revalidate" is OK — the browser may show a cached old version for one fetch while fetching the new version in parallel. After that one fetch, the browser has the new version.

For unhashed assets at scale, the safest pattern is to **add a version query parameter** at deploy time:
```
/js/gallery-lightbox.js?v=20260731-1234
```

CF Pages deploy hooks can inject this via a build plugin or by template-substituting in BaseLayout. For AOT, a simpler approach is to **rename the file** when its contents change:

```bash
mv public/js/gallery-lightbox.js public/js/gallery-lightbox.20260731.js
# Update BaseLayout:
# <script src="/js/gallery-lightbox.20260731.js" defer></script>
```

This sidesteps the cache problem entirely.

## The Lesson for the Agent

The classic verification "did it deploy?" check is:

```bash
sha256sum dist/index.html  # local
curl -s "$URL" | sha256sum  # deployed
[ "$1" = "$2" ] && echo "DEPLOYED"
```

This proves **the HTML on the edge matches the HTML on disk**. It does NOT prove:

- That the HTML is what the agent intended (see hallucinated-commit failure mode).
- That all sub-resources (JS, CSS, images) are also fresh.
- That the CDN hasn't cached the wrong version of any asset.

A complete verification requires per-asset checks:

```bash
for path in /js/gallery-lightbox.js /_aot_assets/index.HASH.css /wp-content/uploads/_lightbox/IMG.jpg; do
  echo "=== $path ==="
  remote_hash=$(curl -s "$URL$path" | sha256sum | awk '{print $1}')
  local_hash=$(find "$WORK/dist$path" -exec sha256sum {} \; 2>/dev/null | awk '{print $1}')
  [ "$remote_hash" = "$local_hash" ] && echo "MATCH" || echo "MISMATCH ($remote_hash vs $local_hash)"
done
```

This is verbose for routine work; use it when a user reports "it's still broken" — that's the trigger.

## What to Tell the User

When the user reports a deploy didn't work, the agent's first move should be:

1. **Confirm with tool output that the deployed asset is old**, not the local one.
2. **Don't re-deploy** until you understand whether (a) the deploy didn't happen, (b) the deploy happened but the cache is stale, or (c) the deploy was correct but the source code never had the fix.

```bash
echo "=== Local source ==="
grep "expected_symbol" "$WORK/public/js/script.js"
echo "=== Built dist ==="
grep "expected_symbol" "$WORK/dist/js/script.js"
echo "=== Deployed URL (with cache-buster) ==="
curl -s "$URL/js/script.js?cb=$(date +%s)" | grep "expected_symbol"
echo "=== Deployed URL (no cache-buster) ==="
curl -s "$URL/js/script.js" | grep "expected_symbol"
```

If all four show the symbol → the fix is live, the user's browser cached an old version → ask them to hard-refresh.

If 1+2 show but 3+4 don't → CDN lag → wait 5 minutes and tell the user to try again.

If 1+2+3 show but 4 doesn't → edge is mid-deploy, just-pushed asset is being propagated.

If 1 doesn't show → source was never edited. That's the hallucinated-commit failure.

## Related Skills

- `aot-hallucinated-commit-verification-2026-07-31.md` — the parent failure mode (source never edited).
- `aot-cloudflare-spa-fallback-asset-404-2026-07-30.md` — different failure mode (asset returns HTML instead of binary).
- `references/aot-astro-template-jsx-pitfalls-2026-07-29.md` — §"Cloudflare Pages deploy lag" — the earlier, less severe version of this issue.
