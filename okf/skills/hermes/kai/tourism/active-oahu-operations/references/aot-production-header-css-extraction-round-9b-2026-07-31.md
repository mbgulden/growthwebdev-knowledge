# Header Production CSS Extraction: Reading nav-fix.css for Ground Truth (Round 9b — 2026-07-31)

> **Session source:** Active Oahu Round 9b. After Round 9 audit fixes, two follow-up bugs surfaced: (a) the audit subagent's claimed `phone color #006699 blue` was wrong — production is `#ff7f00` orange per `nav-fix.css`, (b) the audit's claimed `::before pseudo missing` was also wrong — production uses a `::before` with `content: "Call or Text"`. The fix was to bypass the subagent's audit and read production's actual CSS file (`nav-fix.css?v=16`) directly.
>
> **Use this when:** an external audit (subagent or browser_console-derived) contradicts what you can read directly in production's own CSS files. The lesson: ground-truth CSS lives at `https://activeoahutours.com/wp-content/themes/activeoahu/css/nav-fix.css` (18KB), not in browser-computed-style abstractions.

## Pitfall 1: Audit Subagent Reports Wrong Values

The Round 9 audit reported several values that were wrong when checked against production:

| Claimed by audit | Actual in production | Source of truth |
|---|---|---|
| Phone color = `#006699` blue | `#ff7f00` orange | `.social-header .feature { color: #ff7f00 !important }` in nav-fix.css |
| "Call or Text" missing | Present as `::before { content: "Call or Text" }` 9px gray | `.social-header-h3::before` rule in nav-fix.css |
| Lang switcher missing | Present in HTML | `<span class="lang-switcher">English</span>` |
| Breadcrumb hidden on homepage | Visible | Direct grep in production HTML |
| Body font is Lato | Open Sans (Kadence default) | Computed body style |

**Detection recipe:** when a subagent audit contradicts what you can verify in seconds, verify directly. Don't iterate on a subagent's claims.

## Pitfall 2: Reading Production's nav-fix.css Directly

```bash
# The ground-truth CSS for header/branding/nav:
curl -s -A "Mozilla/5.0" \
  "https://activeoahutours.com/wp-content/themes/activeoahu/css/nav-fix.css?v=16" \
  > /tmp/nav-fix.css

# Look for production-exact values:
grep -B 1 -A 8 '\.social-header-h3' /tmp/nav-fix.css
grep -B 1 -A 6 '\.social-header .feature' /tmp/nav-fix.css
grep -B 1 -A 6 '\.main-navigation' /tmp/nav-fix.css
grep -B 1 -A 8 '\.navbar\b' /tmp/nav-fix.css
grep -B 1 -A 8 '\.breadcrumb-container' /tmp/nav-fix.css
```

**Why this file matters:** production's nav-fix.css is the AUTHORITATIVE source for all header/nav styling. Every other CSS file (style.css, kadence-*.css) is overwritten by nav-fix.css's `!important` rules. When in doubt, read this file first.

## Pitfall 3: minified CSS Escapes Detection

Astro's CSS minifier rewrites `::before` to `:before` (single colon, the legacy syntax that's still equivalent). Search for both forms:

```bash
grep -oE ':before\{[^}]+\}|::before\{[^}]+\}' dist/_aot_assets/*.css
# Find: .social-header-h3:before{content:"Call or Text";font-size:9px;...}
```

**Also:** `rgba(0,0,0,0.06)` becomes `#0000000f` (the 8-digit hex shorthand). Both are the same color, but a verification script searching for `rgba(0,0,0,0.06)` will miss the minified version.

**Detection recipe for verification scripts:**
```python
check("box-shadow present",
  "rgba(0,0,0,0.06)" in css.replace(" ", "") or
  "rgba(0,0,0,.06)" in css.replace(" ", "") or
  "#0000000f" in css
)
```

## Pitfall 4: Production Header HTML Has Pseudo-Elements That Aren't in the Source HTML

Production's `<h3 class="social-header-h3">` contains ONLY the phone number. The "Call or Text" label appears ABOVE the phone via `::before { content: "Call or Text" }`. Audit by reading HTML alone misses the pseudo-element. Audit by reading nav-fix.css catches it.

Same applies to glyphicon icons in production's `<span class="glyphicon glyphicon-calendar">` — production uses an empty `<span>` element + `::before` content via Bootstrap's glyphicon font. Staging has been using Unicode emoji `📅` as a substitute (works for visual parity, but it's a different DOM).

## Production Header HTML Pattern (Reference)

```html
<h3 class="social-header-h3">
  <span class="feature">(808)498-1894</span>
</h3>
<!-- CSS adds: .social-header-h3::before { content: "Call or Text" } -->
```

## Production Header Spec (Verified 2026-07-31 from nav-fix.css)

```css
.social-header-h3 { font-size: 18px !important; line-height: 1.2; }
.social-header-h3::before {
  content: "Call or Text" !important;
  font-size: 9px !important;
  display: block !important;
  text-align: right !important;
  color: #888 !important;
  font-weight: normal !important;
}
.social-header .feature,
.social-header-h3 .feature { color: #ff7f00 !important; }

.main-navigation {
  background-color: #006699 !important;
  min-height: 42px !important;
}
.main-navigation .menu > li > a {
  padding: 10px 16px !important;
  color: #fdf5e3 !important;
  line-height: 22px !important;
  font-size: 15px !important;
  font-family: "Open Sans Condensed", sans-serif !important;
  font-weight: 400 !important;
}
.main-navigation .menu > li > a:hover,
.main-navigation .menu > li > a:focus {
  background-color: #005580 !important;
  color: #fff !important;
}
.main-navigation .current_page_item > a {
  background-color: #0085b0 !important;
  color: #fff !important;
}
.main-navigation .sub-menu {
  background-color: #004f75 !important;
}
.main-navigation .sub-menu a {
  color: #ffffff !important;
  background-color: #004f75 !important;
  padding: 8px 16px !important;
  font-size: 14px !important;
  font-family: "Open Sans Condensed", sans-serif !important;
  font-weight: 600 !important;
}

#branding .aot-logo img {
  max-height: 52px !important;
  width: auto !important;
  max-width: none !important;
}
```

## The `execute_code` Python Edit Pattern (Bulk Edits)

When `patch` keeps failing (the `path required` error trap), use `execute_code` with a Python script that does the multi-line edit:

```python
import subprocess
script = '''
with open("src/components/shell/PrimaryNav.astro") as f:
    content = f.read()
old = """  .nav-link {
    display: flex;
    align-items: center;
    padding: 1rem 1.125rem;"""
new = """  .nav-link {
    display: flex;
    align-items: center;
    padding: 10px 16px;
    color: #fdf5e3;"""
content = content.replace(old, new)
with open("src/components/shell/PrimaryNav.astro", "w") as f:
    f.write(content)
'''
result = subprocess.run(["python3", "-c", script], capture_output=True, text=True)
```

**This is the reliable fallback when `patch mode='replace'` keeps failing with "path required".** See `tool-parameter-required-fields-checklist` for the underlying trap.

## Related

- `aot-header-refinement-round-9-2026-07-31.md` — the prior round's nav flex / banner duplication fixes.
- `aot-cdn-stale-js-after-deploy-2026-07-31.md` — also: after pushing 48/48 verified clean, a verification script gave 1 transient FAIL because Cloudflare had not yet propagated the new CSS bundle (the old `index.jqNyCV6z.css` was being served). Always re-check after 30-60s if a "fresh deploy" verification fails unexpectedly.
- `aot-browser-tool-cache-vs-cdn-cache-2026-07-31.md` — the related browser-side cache layer.
- `tool-parameter-required-fields-checklist` — the `patch` `path required` failure pattern.
- `aot-staging-vs-prod-structural-diff-2026-07-30.md` — the broader structural diff recipe.

## When Round 9b Verification Hit 1 False FAIL on First Run

The verification script reported 2 FAILs (`::before pseudo` + `box-shadow rgba(0,0,0,0.06)`), but curl-based verification later proved both WERE present in the deployed CSS bundle:
- `::before` was minified to `:before` (single colon, legacy equivalent)
- `rgba(0,0,0,0.06)` was minified to `#0000000f` (8-digit hex)

After fixing the verification regex, the script passed 48/48. Same class as the `aot-hallucinated-commit-verification` reference: don't trust a verification FAIL when you have reason to suspect the verifier, not the artifact.
