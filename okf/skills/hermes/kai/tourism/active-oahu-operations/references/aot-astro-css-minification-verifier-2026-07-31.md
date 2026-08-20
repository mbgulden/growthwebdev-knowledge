# Astro CSS Minification Pitfalls — Round 10 (2026-07-31)

**Class:** AOT homepage production-parity verification pitfall.
**Scope:** When writing verification scripts that assert specific CSS values in built bundles.

## Problem

Astro's CSS minifier (esbuild) shortens hex codes and pseudo-element syntax. Naive
verification scripts that grep for the production-source values fail with "NOT FOUND"
even when the rule is in the bundle. Two minification forms bit me in Round 10:

| Source (in `*.astro` file)   | Minified (in `_aot_assets/*.css`) | Same color? |
|------------------------------|-----------------------------------|-------------|
| `rgba(0, 0, 0, 0.3)`         | `#0000004d`                       | yes (30% black) |
| `#003366`                    | `#036`                            | yes (navy) |
| `::before`                   | `:before`                         | yes (same selector) |
| `#ff7f00`                    | `#ff7f00` (kept — not compressible to 3-digit) | yes |
| `rgb(155, 69, 0)`            | `#9b4500`                         | yes |
| `#ffffff`                    | `#fff` or `#ffffff` (both seen)   | yes |

The Round 10 hero verifier initially reported "FAIL: Overlay color rgba(0,0,0,0.3)
or similar" even though the rule was present. The script grepped for the source-
written form, not the minified form.

## Detection recipe

When a verifier fails on a CSS rule you just wrote, **before assuming the rule is
missing, check the actual minified bundle**:

```bash
# 1. Find which CSS bundle the HTML points to
grep -oE '/_aot_assets/[\w.]+\.css' dist/index.html

# 2. Look at the actual minified rule
grep -oE 'selector-that-might-exist[^{]*\{[^}]+\}' \
  dist/_aot_assets/index.<hash>.css
```

For the hero overlay specifically:

```bash
grep -oE 'hero-left-col[^{]*:before\{[^}]+\}' dist/_aot_assets/*.css
# → hero-left-col[data-astro-cid-2filmj7h]:before{content:"";position:absolute;inset:0;background-color:#0000004d;z-index:-1;transition:all .3s ease-in-out}
```

## Verification script fix pattern

**Wrong:** Single-form grep.

```python
check("Overlay color rgba(0,0,0,0.3)", "rgba(0,0,0,0.3)" in css, "30% black")
```

**Right:** Accept both source and minified forms.

```python
check("Overlay color rgba(0,0,0,0.3) or similar",
      "rgba(0,0,0,0.3)" in css.replace(" ", "")
      or "#0000004d" in css
      or "#0000004c" in css,  # 29% black — close enough
      "30% black (or minified)")
```

For 6-digit hex → 3-digit hex compression:

```python
# Source: #003366 → Minified: #036
check("Color #003366 or #036",
      "#003366" in css.replace(" ", "")
      or ":#036;" in css
      or ":#036}" in css,
      "navy")
```

For `::before` → `:before`:

```python
check("Has ::before (or :before)",
      "::before" in css or ":before" in css,
      "pseudo-element present")
```

## Minimum-viable rule-of-thumb for CSS verifiers

When you don't know what the minifier will do, **build a quick lookup table** for
the specific colors/selectors you'll assert. Add both the source form and the
minified form, then OR them together:

```python
ALLOWED_FORMS = {
    "overlay_30_black": ["rgba(0,0,0,0.3)", "rgba(0,0,0,.3)", "#0000004d", "#0000004c"],
    "navy_036": ["#003366", "#036"],
    "orange_ff7f00": ["#ff7f00", "#FF7F00"],  # not compressible
    "before_pseudo": ["::before", ":before"],
}

def has_any(css: str, key: str) -> bool:
    return any(form in css for form in ALLOWED_FORMS[key])

check("Overlay 30% black", has_any(css, "overlay_30_black"), "30% black")
check("Pseudo before", has_any(css, "before_pseudo"), "::before/:before")
```

## Why this matters in the AOT loop

Every production-parity round (Rounds 4, 5, 6, 9, 9b, 10) involves a fresh build
and a verification script that asserts specific CSS values. If the script can't
handle minified forms, **every round ships with a "verification failed" warning
that masks actual green**. That's how Round 10's first verification run reported
"30/30 FAIL" even though the underlying rules were correct.

## Pitfalls

1. **Don't assume minified CSS uses 8-digit hex for non-`rgba` colors.** Astro's
   minifier converts `#003366` → `#036` (3-digit) but leaves `#ff7f00` as-is (not
   compressible). The 8-digit hex trick (`#0000004d`) is specifically for `rgba()`
   with alpha < 1, which can't be expressed as 3-digit or 6-digit hex.

2. **The `::before` → `:before` conversion is one-way.** `::before` (double colon)
   is the CSS3 pseudo-element syntax; `:before` (single colon) is the CSS2 syntax.
   Browsers accept both. Astro's minifier always uses single colon.

3. **Whitespace removal inside `rgba()`**: `rgba(0,0,0,0.3)` minifies to
   `rgba(0,0,0,.3)` (leading 0 dropped) — and also `#0000004d`. Both are present
   in the same bundle sometimes (one rule for the explicit form, one for the
   calculated).

4. **Color names are not minified.** `transparent`, `white`, `black` stay as-is.
   The minifier only shortens hex codes and `rgba()`.

## Related references

- `references/aot-cloudflare-spa-fallback-asset-404-2026-07-30.md` — bundling
  images locally before deploying (the Round 10 trigger that exposed this).
- `references/aot-production-parity-implementation-playbook-2026-07-30.md` —
  end-to-end production-parity workflow that uses these verifier patterns.
- `references/aot-header-refinement-round-9-2026-07-31.md` — earlier round
  where minified form comparison also bit (Round 9 hero button had
  `box-shadow:#0000000f 0 2px 4px` instead of `rgba(0,0,0,0.06) 0 2px 4px 0`).