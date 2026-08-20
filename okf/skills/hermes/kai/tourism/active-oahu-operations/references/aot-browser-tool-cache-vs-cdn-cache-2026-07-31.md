# Browser-Tool Cache vs. CDN Cache — Two Layers, Same Symptom (2026-07-31)

> **Session source:** Round 9 header refinement. After `git push` + `sha256sum` confirmation that local `dist/index.html` matches live URL (`526681aa48a0dbf1...`), `browser_navigate` to the live URL still showed the **old DOM**: the duplicate `#deal-banner` was still at y=0 even though `curl` confirmed it was gone. `browser_navigate("?v=refine2")` (different query string) — same old behavior. Even `location.reload(true)` did not purge the browser's disk cache.
>
> **Companion to:** `aot-cdn-stale-js-after-deploy-2026-07-31.md` (CDN stale assets behind a fresh HTML). This reference is about a **different** cache layer — the **browser's** cache.

## The Two Layers

When the user (or an agent) reports "the fix didn't take effect after deploy", there are now TWO plausible causes:

### Layer A — CDN stale (already documented)

The Cloudflare edge cache serves an old version of an unhashed asset (`/js/gallery-lightbox.js`) even though the HTML was just refreshed. Documented in `aot-cdn-stale-js-after-deploy-2026-07-31.md`. Resolved by waiting 5-15 minutes or by renaming the file.

### Layer B — Browser-tool / user-browser cache

The `browser_navigate` tool (or a user's browser) keeps serving a cached version of the page because:

1. The page's response includes `cache-control: public, max-age=N` (CF Pages uses `max-age=0, must-revalidate` by default, but `must-revalidate` allows stale-while-revalidate).
2. `browser_navigate` does NOT issue a hard refresh (no `Cache-Control: no-cache` header in the request, no bypass query param).
3. The browser's disk cache may serve the prior version until explicitly invalidated.

The same visible symptom ("old DOM, new deploy"), different layer, different resolution.

## The Diagnostic Ladder

Run these **in order**. Each step isolates a specific layer.

```bash
WORK=/home/ubuntu/work/astro-homepage-work/okf/architecture/astro-emdash/homepage/astro
URL="https://content-astro-homepage.active-oahu-tours-mirror.pages.dev/"

# === Layer 1: Source files (definitely local) ===
# Does the source have the change?
grep -c "expected_symbol" "$WORK/src/path/to/file.astro"
# 0 → "hallucinated commit" failure mode. Fix source first.
# ≥1 → proceed to Layer 2.

# === Layer 2: Built dist (definitely local) ===
grep -c "expected_symbol" "$WORK/dist/index.html"
# 0 → build never ran, or build ran against old source. Re-build: npm run build.
# ≥1 → proceed to Layer 3.

# === Layer 3: Live URL HTML (CDN edge cache) ===
curl -s -A "Mozilla/5.0" "$URL" | grep -c "expected_symbol"
# 0 → CDN edge caching old HTML. Force fresh: curl with cache-buster, or wait.
DEPLOYED_CB=$(curl -s -A "Mozilla/5.0" "$URL?cb=$(date +%s)" | grep -c "expected_symbol")
# If 0 here → CDN is genuinely stuck → wait, or PATCH deploy.
# If 1 here but 0 in Layer 3 → CDN stale asset. Different layer.

# === Layer 4: Live URL sub-assets (separate cache) ===
curl -s -A "Mozilla/5.0" "$URL/js/gallery-lightbox.js" | grep -c "expected_symbol"
# 0 → CDN JS stale (the documented 2026-07-31 case).
# 1 → the asset is fine, the issue is in the browser, not the CDN.

# === Layer 5: Browser tool session cache ===
# Even with all layers 1-4 ✅, browser_navigate to "$URL" still shows old DOM.
# The browser's disk cache survives browser_navigate calls within a session.

# Fix: pass a unique cache-buster query param to browser_navigate.
# browser_navigate(url="https://...?cb=N", where N is a fresh number)

# Even that can fail if the browser's cache key is the URL minus query.
# Definitive fix: clear disk cache from browser-side
# (not exposed by Hermes browser tool — work around by re-checking via
#  browser_console.fetch with cache: "no-store")

# === Layer 6: User's actual browser ===
# If the agent's browser is fresh but the user's browser is stale, tell the user
# to hard-refresh: Ctrl+Shift+R (Win/Linux) / Cmd+Shift+R (Mac).
```

## The Browser-Tool Trick That Actually Worked

```python
# In browser_console, force a fresh fetch (bypasses disk cache):
await fetch(window.location.href, { cache: "no-store" }).then(r => r.text())
# Then evaluate the response, not document.body which is still the cached DOM.
```

OR — use `browser_navigate` to a URL with a **path-changing** cache-buster:

```
browser_navigate("https://...?cb=1")     # might miss
browser_navigate("https://.../?nocache")  # different query key
browser_navigate("https://...?v=999")    # different query key
```

The Hermes browser tool may or may not honor query-string cache busting. If
`browser_snapshot` after the new URL still shows old DOM, the browser tool
itself is the cache layer — not the network.

## The Hard Lesson

**`curl` confirming a fresh deploy only proves the CDN is serving the new asset.** It does NOT prove the **browser inside the testing tool** is rendering the new asset. Two distinct caches; treat both.

When the verification chain runs:

```
source → dist → CDN edge → browser cache → DOM render
   [✓]      [✓]      [✓]              ❌ ← this can still be old
```

any layer failing breaks the chain. A 5-layer diagnostic ladder (above) catches
which layer is stale. Without it, the agent retries the wrong fix.

## Practical Workflow

After every Astro homepage deploy, the minimum verification set is:

```bash
# 1. Local dist hash matches deployed HTML hash
[ "$(sha256sum dist/index.html | cut -c1-16)" = \
  "$(curl -s -A 'Mozilla/5.0' "$URL" | sha256sum | cut -c1-16)" ] \
  || echo "HTML hash mismatch — investigate"

# 2. Browser tool sees new content (cache-busting required)
#    In browser_console:
#      return await fetch("$URL?cb=$(date +%s)", {cache: "no-store"}).then(r => r.text().then(t => t.includes("expected_symbol")))
```

If the fetch-based check returns `true` but `browser_snapshot` shows the old DOM, the browser tool has its own cache that survived even the cache-busting query param. Restart the browser session via `browser_navigate` to a completely different URL first, then back.

## Related

- `aot-cdn-stale-js-after-deploy-2026-07-31.md` — parent reference for CDN edge cache.
- `aot-hallucinated-commit-verification-2026-07-31.md` — for Layer 0 (source file) verification.
- `aot-2026-07-31-lightbox-url-derivation-bug.md` — when the URL is right but the image is wrong.
