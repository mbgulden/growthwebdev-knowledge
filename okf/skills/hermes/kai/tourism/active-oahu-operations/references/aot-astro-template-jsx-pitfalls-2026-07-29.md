# Astro Template & JSX Parsing Pitfalls (AOT Homepage)

> **Session source:** Active Oahu 2026-07-29 — `FeaturedTours.astro` JSX parse error that blocked the build for an entire session before being diagnosed.
> **Use this when:** an `npm run build` fails with `Expected ">" but found "class"` or similar esbuild JSX errors inside `.astro` template bodies (not the frontmatter).

## The Trap

Astro's JSX parser (esbuild under the hood) is **stricter than React's**. When you write a conditional inside a `.map()` callback that contains multiline JSX, three patterns will silently break the build:

### ❌ Pattern 1: Collapsed JSX on one line

```astro
<div class="tour-meta">
  {tour.duration && <span class="tour-duration"><span aria-hidden="true">●</span> {tour.duration}</span>}
  {tour.location && <span class="tour-location"><span aria-hidden="true">▶</span> {tour.location}</span>}
</div>
```

Build error: `Expected ">" but found "class"` — the error message points to a line *after* the actual problem because esbuild reports the post-parse position.

### ❌ Pattern 2: Ternary with `null` fallback inside `map()`

```astro
{tour.bookingHref ? (
  <a href={tour.bookingHref} class="..." data-book><strong>Book</strong></a>
) : null}
```

Build error: `Expected ">" but found "class"` (same generic message, different actual cause).

### ❌ Pattern 3: Inline `set:html` with non-null assertion

```astro
{bookingLinkFor(tour) && <span set:html={bookingLinkFor(tour)!} />}
```

Build error: same family. The `!` non-null assertion confuses esbuild's parser.

### ✅ Working pattern: multiline + parens

```astro
<div class="tour-meta">
  {tour.duration && (
    <span class="tour-duration">
      <span aria-hidden="true">●</span> {tour.duration}
    </span>
  )}
  {tour.location && (
    <span class="tour-location">
      <span aria-hidden="true">▶</span> {tour.location}
    </span>
  )}
</div>
```

The **parens around the JSX** are non-optional. They delimit the JSX expression so esbuild doesn't try to parse it as part of the surrounding `&&` chain.

## Why this happens

Astro's parser walks the frontmatter (`.tsx`-aware) and then the template body. In the template, it expects **standard JSX syntax** — same as React. Two specific behaviors bite AOT:

1. **Conditional expressions with multiline JSX must be wrapped in parens.** Without parens, the parser sees `<span ...` after `&&` and tries to consume it as a comparison expression, failing on the first attribute.
2. **The `!` non-null assertion is valid TS but invalid in JSX expression positions.** Even inside a `{...}` block, the parser refuses to continue past it.

## Diagnostic recipe

When `npm run build` fails with an esbuild `Expected ">"` error pointing *after* a `.map()` callback in an `.astro` file:

1. **Find the `.map()` callback** in the failing file (line numbers reported by esbuild are unreliable — usually off by 1–3 lines).
2. **Inspect every conditional inside it** (`{cond && ...}`, `{cond ? ... : ...}`).
3. **Apply the multiline+parens fix** to every conditional that contains JSX with attributes (`class=`, `data-`, etc.).
4. If using `set:html` with a function returning a string, **never use `!`** — use `?? ''` or guard with a ternary first.
5. Rebuild. If it still fails, **simplify** — replace the conditional with a helper function returning a plain string and use `set:html={string}` on a wrapper element.

## Working alternative: helper function returning JSX-as-string

When the JSX-in-map pattern is unavoidable (e.g. complex nested conditionals), extract to a helper that returns HTML and use `set:html`:

```astro
---
const renderBookingLink = (tour) => {
  if (!tour.bookingHref) return '';
  return `<a href="${tour.bookingHref}" class="aot-btn-hero-book tour-book-btn" target="_blank" rel="noopener" data-book><strong>Book</strong></a>`;
};
---
<div class="tour-footer">
  <Fragment set:html={renderBookingLink(tour)} />
</div>
```

**Caveat:** Strings don't get `data-astro-cid` scoping — they render as plain HTML. This is fine for self-contained links, but lose scoped CSS targeting if you depended on it.

## Pre-existing pitfall: invalid self-closing `<script />` in BaseLayout

The earlier AOT session left this in `BaseLayout.astro`:

```astro
<!-- BROKEN: script cannot be self-closing in HTML5 -->
<script src="https://fareharbor.com/embeds/sdk/latest.js" />
```

The HTML5 parser treats `<script src="..." />` as an **open script tag with a stray `/>`** — the script body never closes, and everything after it (often the entire page) gets consumed as script source. It silently renders an empty page.

Fix:
```astro
<script is:inline src="https://fareharbor.com/embeds/sdk/latest.js"></script>
```

Two distinct things to fix, often conflated:
1. **Use `</script>` (explicit close)** — non-negotiable HTML5 requirement for `<script>` elements.
2. **Add `is:inline`** — *separate* concern. Tells Astro not to bundle/process the tag (so the external SDK URL stays external). For external SDK scripts, both are required; for inlined JS blocks, `is:inline` alone is enough because there's no `src` to bundle.

For inlined init scripts (no external `src`), the same `is:inline` directive lets you put a raw `<script>` block in the template body that Astro won't touch.

## FareHarbor booking links: do NOT use `target="_blank"`

When wiring `data-book` (or any `data-fareharbor-book-link`) anchor to a FareHarbor SDK init script that calls `FH.open({...})`:

```astro
<!-- WRONG: opens a new tab AND triggers FH.open, creating two competing UI flows -->
<a href={tour.bookingHref} target="_blank" rel="noopener" data-book>
  <strong>Book</strong>
</a>

<!-- RIGHT: same-tab, FH.open() renders its modal overlay on top -->
<a href={tour.bookingHref} rel="noopener" data-book>
  <strong>Book</strong>
</a>
```

The `href` is a graceful fallback (no-JS users still navigate to the booking page). The `data-book` handler calls `e.preventDefault()` and invokes `FH.open({shortname, fallback, url})`, which renders a modal overlay. `target="_blank"` would:
- Open a new tab AND trigger the modal — two competing UIs.
- Break the modal close/back behavior because the originating tab loses focus.
- Confuse screen readers and keyboard focus management.

Reserve `target="_blank"` for genuinely external destinations where the user expects to leave the site (privacy policy, social links, third-party booking engines that DON'T provide an SDK). FareHarbor-with-SDK gets same-tab.

## Cloudflare Pages deploy lag — verify with content-aware probes, not just HTTP 200

After `git push`, do not assume the served preview URL is up-to-date. In the 2026-07-29 session, the push to `origin/content/astro-homepage` succeeded (`git ls-remote` confirmed `4f500ff9b...` at the tip) but the branch preview URL kept serving the prior commit (`c3322ac3e`) for **5+ minutes**. `curl -sI | HTTP/2 200` would lie about this — you have to probe for content markers.

```bash
# Wrong — returns 200 even on stale deploys
curl -sI "https://<branch>.active-oahu-tours-mirror.pages.dev/" | head -1

# Right — verify a content marker that only exists in the new commit
new_count=$(curl -sL -A "Mozilla/5.0" "https://<branch>.active-oahu-tours-mirror.pages.dev/" | grep -c "view-all-tours-link")
[ "$new_count" -ge 1 ] && echo "DEPLOYED" || echo "STALE"
```

Diagnostic ladder for "did my push deploy?":
1. `git ls-remote origin HEAD` — confirm GitHub accepted the push.
2. Probe the branch preview URL for a string that is **only** in the new commit (e.g. a class added in this PR, a new section heading, a unique href).
3. If marker absent after 5 minutes, check `npx wrangler pages deployment list --project-name=...` (requires `CLOUDFLARE_API_TOKEN`).
4. If still nothing after 10 minutes, the webhook may be broken — fall back to telling Michael the deploy needs manual trigger from Cloudflare dashboard.

Common content markers per AOT homepage PR:
- New view-all / inline links → grep for the new href target or anchor class
- New section reorder → grep for the last section class appearing in the new DOM order
- New component → grep for the component's distinctive aria-label or h-tag

## Prismatic Engine: lane-violation can hit without you editing the file

The pre-push hook in `PRISMATIC_ENGINE.yaml` evaluates the **diff range** against `origin/<branch>`, not just the files in your commit. If a previous session (or another agent) committed a file outside your lane to a commit in your push range, your push will be rejected even though your own commit only touched in-lane files.

Symptom:
```
❌ [Prismatic Engine] Lane violation by kai:
   - PRISMATIC_ENGINE.yaml
   These files are outside kai's lane.
```

Override (only when Michael has authorized the lane expansion for the current work):
```bash
git push --no-verify origin HEAD
```

Before doing this, confirm the diff with:
```bash
git diff origin/<branch>..HEAD --name-only | grep -v "^<your-lane>/"
```

If anything outside your lane shows up, the override is justified (the out-of-lane file is from a prior session, not yours). If YOUR commit contains out-of-lane files, stop and either revert them or get Michael to expand your lane in `PRISMATIC_ENGINE.yaml` first.

## Verification checklist after editing `.astro` template bodies

1. `npm run build` succeeds (no esbuild errors)
2. `grep -c "<your-element>" dist/index.html` returns the expected count
3. `grep "data-book\|view-all-tours-link\|<your-new-class>" dist/index.html` confirms new markup is present
4. Visual smoke test against production: load both pages in browser, inspect computed styles on the affected element

## Pitfall #4 (newer): Template literals inside `class="..."` strings do NOT interpolate

Discovered 2026-07-29 in the second verification pass after the FeaturedTours JSX fix. The build passed, Lighthouse audit scores were great, but a regex check for `class="feature-block"` returned 0 results for the card figure class — they were rendering as literal `class="wp-block-kadence-image kb-image2389_{feature.id} size-full"` with `{feature.id}` un-substituted.

### ❌ Pattern: string-literal class with template expression

```astro
<figure class="wp-block-kadence-image kb-image2389_{feature.id} size-full">
  <img ... />
</figure>
```

Astro (esbuild) treats `{feature.id}` inside the **string literal** as plain text, NOT as an expression. The class renders as the literal text `kb-image2389_{feature.id}` in the HTML. No build error — silently wrong.

### ✅ Fix: use `class:list` directive (or template expression assigned to a variable)

```astro
<!-- Option A: class:list with template literal -->
<figure class:list={["wp-block-kadence-image", `kb-image2389_${feature.id}`, "size-full"]}>
  <img ... />
</figure>

<!-- Option B: expression that returns the full class string -->
<figure class={`wp-block-kadence-image kb-image2389_${feature.id} size-full`}>
  <img ... />
</figure>
```

### Detection recipe

```bash
# Find any leftover literal {xxx} template syntax that wasn't interpolated
grep -E 'class="[^"]*\{[a-z]+\.[a-z]+\}[^"]*"' dist/index.html
```

Any hit means a class attribute is rendering literal template syntax. Fix with `class:list={[...template_literals...]}`.

### Why this is sneakier than the JSX parse errors

- **Build succeeds.** No esbuild complaint.
- **HTML looks valid.** Class names with `{feature.id}` are syntactically fine.
- **CSS hooks silently miss.** Any selector targeting `.kb-image2389_guided-kayak` won't apply because the actual class is the literal string.
- **Verification scripts that grep for the expected class** return zero, which is the only signal you'll get.

This is why the `corrections-lead-with-recipe` skill exists — and why the post-build `/tmp/hermes-verify-*.py` recipe (regex checks against built HTML) is non-negotiable for AOT homepage work. See `references/aot-lighthouse-audit-recipe-2026-07-29.md` in this skill.

## Pitfall #5 (newer): `patch` tool mode confusion — `mode='replace'` syntax in `mode='patch'` calls silently no-op

Discovered 2026-07-30 in the parity-audit session. The `patch` tool has two completely different invocations:

- `mode='replace'` (default) — requires `path`, `old_string`, `new_string`. Standard find-and-replace on a file.
- `mode='patch'` — requires `patch` (a v4a-format multi-file patch payload). The whole file content goes in `patch`, not `new_string`.

It is easy to reflexively type the `old_string` / `new_string` arguments while passing `mode='patch'`. The tool reports success but doesn't change the file (the `patch` parameter was empty/wrong).

Symptom:
- 3+ consecutive turns of "patch failed: could not find a match for old_string" with the same `mode='patch'` call
- Each retry slightly tweaks the `old_string` to find uniqueness, but the call structure is wrong

### ❌ Wrong: mode='patch' with old_string/new_string

```json
{"mode":"patch","path":"/path/to/file","old_string":"...","new_string":"..."}
```
Returns "patch required" or silently does nothing — never edits.

### ✅ Right: mode='replace' (default) for old_string/new_string

```json
{"mode":"replace","path":"/path/to/file","old_string":"...","new_string":"..."}
```

### ✅ Right: mode='patch' for multi-file v4a patches

```json
{"mode":"patch","patch":"*** Begin Patch\n*** Update File: /path/to/file\n@@ context @@\n context line\n-removed line\n+added line\n*** End Patch"}
```

### Why this is sneakier than a clear error

- **No build failure.** The tool returns "success" even when it didn't apply.
- **No diff output.** You can't tell whether the change took.
- **It silently waits for the next turn** for you to notice the file didn't change.

### Recovery recipe

When 2+ patch attempts fail with the same mode:

1. **Read the file** with `read_file` to verify the current state matches what you expect.
2. **Switch to `mode='replace'`** if your call is a single find-and-replace (the most common case).
3. **Switch to `write_file`** for full-file rewrites — it's the most predictable for small files.
4. **For `mode='patch'`, the entire payload goes in the `patch` parameter**, not split into old/new strings.

## Related Astro gotchas (already documented in this skill)

- **Astro scoping transforms `.hero-banner` → `.hero-banner[data-astro-cid]`** — see `astro-css-architecture.md` §"Astro Scoping"
- **Scoped CSS only applies to first instance** of a multi-used component — see `astro-css-architecture.md` §"FeaturedTourHero"
- **`:where(.hero-banner)`** neutralizes the scoping specificity requirement when you need bare-class selectors