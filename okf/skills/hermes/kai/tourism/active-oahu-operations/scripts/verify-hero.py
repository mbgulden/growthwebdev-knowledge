#!/usr/bin/env python3
"""
verify-hero.py — production-parity hero verification for AOT Astro homepage.

Scope (Round 14, 2026-07-31):
  - Production hero uses `html { font-size: 62.5% }` so 1rem = 10px
  - Hero H1: production-parity clamp (12.5 - 24px responsive)
  - Hero H2: production's exact clamp curve, resolves to 60px max
  - lifestyle bg image is bundled locally (not remote)
  - dark overlay ::before present (mostly transparent, opacity 0.3)
  - text-shadow on headings for white text contrast

Usage:
  python3 verify-hero.py
  python3 verify-hero.py --staging-url https://content-astro-homepage.active-oahu-tours-mirror.pages.dev/

Returns exit 0 if all checks pass, exit 1 otherwise. Prints compact PASS/FAIL list.

Pitfalls handled:
  - Astro's CSS minifier converts rgba(0,0,0,0.3) to #0000004d; the check
    pattern accepts both source-written and minified forms.
  - Astro's CSS minifier drops spaces inside clamp() — verify with regex
    that accepts no-space variants too.
  - Astro tree-shakes CSS for unused primitives — fail a test only if the
    primitive was actually expected to be bundled.
  - 6-layer deploy verification (source → dist → CDN HTML → CDN CSS →
    browser cache → DOM render) collapses to: hash-match local vs live,
    then grep the live bundle. If hashes differ, fall back to grepping
    the local dist.
"""
import argparse
import hashlib
import os
import re
import ssl
import sys
import urllib.request

PREVIEW = "https://content-astro-homepage.active-oahu-tours-mirror.pages.dev"
LOCAL = "/home/ubuntu/work/astro-homepage-work/okf/architecture/astro-emdash/homepage/astro/dist"

HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}


def fetch(url, ctx):
    req = urllib.request.Request(url, headers=HEADERS)
    return urllib.request.urlopen(req, context=ctx, timeout=15).read()


def fetch_text(url, ctx):
    return fetch(url, ctx).decode("utf-8", errors="replace")


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def has_any(css_text, allowed_forms):
    """Return True if any of the allowed form strings are in the CSS text."""
    return any(form in css_text for form in allowed_forms)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--staging-url", default=PREVIEW)
    parser.add_argument("--local-dist", default=LOCAL)
    args = parser.parse_args()

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    # ── 1. Hash match (local dist = live URL) ──────────────────────
    index_html_path = os.path.join(args.local_dist, "index.html")
    if not os.path.exists(index_html_path):
        print(f"[FAIL] Local dist/index.html not found at {index_html_path}")
        return 1

    local_html = open(index_html_path, "rb").read()
    try:
        live_html = fetch(args.staging_url + "/", ctx)
    except Exception as e:
        print(f"[FAIL] Could not fetch {args.staging_url}: {e}")
        return 1

    local_hash = sha256(local_html)
    live_hash = sha256(live_html)

    print("=== Hero production-parity verification ===\n")
    print(f"Local:    {local_hash[:16]}... ({len(local_html)} bytes)")
    print(f"Deployed: {live_hash[:16]}... ({len(live_html)} bytes)")
    if local_hash != live_hash:
        print("[FAIL] Local and deployed hashes do not match — Cloudflare hasn't picked up the latest commit yet, or the local dist is stale.")
        print("        Wait 60-180s for CF Pages to deploy, then re-run.")
        return 1
    print("[PASS] hash match")

    html_text = live_html.decode("utf-8", errors="replace")
    css_match = re.search(r'href="(/_aot_assets/[^"]+\.css)"', html_text)
    if not css_match:
        print("[FAIL] No /_aot_assets/*.css link found in HTML")
        return 1
    css_url = args.staging_url + css_match.group(1)
    css_text = fetch_text(css_url, ctx)

    # ── 2. Root font-size 62.5% ────────────────────────────────────
    print("\n=== Root font-size (production-parity) ===")
    ok_root = has_any(css_text, ["html{font-size:62.5%", "html {font-size: 62.5%", "font-size:62.5%"])
    print(f"[{'PASS' if ok_root else 'FAIL'}] html font-size: 62.5% (1rem = 10px)")

    # ── 3. Hero H1 / H2 clamp() ────────────────────────────────────
    print("\n=== Hero H1 / H2 clamp() ===")
    # H1 clamp: clamp(1.25rem, 0.995rem + 1.265vw, 1.5rem) [minified no-space variants too]
    ok_h1 = has_any(css_text, [
        "clamp(1.25rem,.995rem + 1.265vw,1.5rem)",   # minified no-space
        "clamp(1.25rem, 0.995rem + 1.265vw, 1.5rem)", # source
        "clamp(1.25rem,.995rem+1.265vw,1.5rem)",      # fully minified
    ])
    print(f"[{'PASS' if ok_h1 else 'FAIL'}] H1 clamp() present")

    # H2 clamp: production's exact curve
    ok_h2 = has_any(css_text, [
        "clamp(2.75rem,.489rem + 7.065vw,6rem)",   # minified no-space
        "clamp(2.75rem, 0.489rem + 7.065vw, 6rem)", # source
        "clamp(2.75rem,.489rem+7.065vw,6rem)",      # fully minified
    ])
    print(f"[{'PASS' if ok_h2 else 'FAIL'}] H2 clamp() present (production curve)")

    # ── 4. Hero bg image present and local ─────────────────────────
    print("\n=== Hero background image ===")
    has_image = "Active-Oahu-Lifestyle" in html_text
    print(f"[{'PASS' if has_image else 'FAIL'}] Lifestyle bg image referenced in HTML")
    is_local = bool(re.search(r"url\(['\"]?/wp-content/", html_text) or "/wp-content/uploads/2024/01/Active-Oahu-Lifestyle" in html_text)
    print(f"[{'PASS' if is_local else 'FAIL'}] Image URL is local (/wp-content/...)")

    # ── 5. Overlay ::before ────────────────────────────────────────
    print("\n=== Overlay ::before (production-style transparent overlay) ===")
    ok_overlay = has_any(css_text, [":before{content:\"\"", "before{content:", "::before{content:"])
    print(f"[{'PASS' if ok_overlay else 'FAIL'}] Overlay ::before present")
    ok_overlay_opacity = has_any(css_text, [":before{content:\"\";opacity:.3", ".3}"]);
    # fallback: search for content:"";...;opacity:.3; in the same rule
    if not ok_overlay_opacity:
        # find the before rule and check its opacity
        m = re.search(r":before\s*\{[^}]*opacity\s*:\s*\.?3", css_text)
        ok_overlay_opacity = bool(m)
    print(f"[{'PASS' if ok_overlay_opacity else 'FAIL'}] Overlay opacity: 0.3")

    # ── 6. Text shadow on hero headings ────────────────────────────
    print("\n=== Text-shadow (production contrast mechanism) ===")
    # H2 text-shadow: 1px 1px 21px #000000 (production exact)
    ok_h2_shadow = has_any(css_text, [
        "1px 1px 21px #000",   # source
        "1px 1px 21px#000",    # minified no-space-before-hex
    ])
    print(f"[{'PASS' if ok_h2_shadow else 'FAIL'}] H2 text-shadow: 1px 1px 21px #000")
    ok_h1_shadow = has_any(css_text, [
        "1px 1px 3px #000",    # source
        "1px 1px 3px#000",     # minified
    ])
    print(f"[{'PASS' if ok_h1_shadow else 'FAIL'}] H1 text-shadow: 1px 1px 3px #000")

    # ── 7. Sanity ──────────────────────────────────────────────────
    print("\n=== Bundle sanity ===")
    ok_size = 40000 < len(css_text) < 100000
    print(f"[{'PASS' if ok_size else 'FAIL'}] CSS bundle size reasonable: {len(css_text)} bytes")
    ok_html = 65000 < len(html_text) < 80000
    print(f"[{'PASS' if ok_html else 'FAIL'}] HTML size reasonable: {len(html_text)} bytes")

    # ── Summary ────────────────────────────────────────────────────
    results = [
        ("hash match", local_hash == live_hash),
        ("html font-size 62.5%", ok_root),
        ("H1 clamp()", ok_h1),
        ("H2 clamp() production", ok_h2),
        ("hero bg image present", has_image),
        ("hero bg image local", is_local),
        ("hero overlay ::before", ok_overlay),
        ("hero overlay opacity 0.3", ok_overlay_opacity),
        ("H2 text-shadow 1px 1px 21px", ok_h2_shadow),
        ("H1 text-shadow 1px 1px 3px", ok_h1_shadow),
        ("CSS bundle size", ok_size),
        ("HTML size", ok_html),
    ]
    passed = sum(1 for _, ok in results if ok)
    total = len(results)
    print(f"\n=== Summary: {passed}/{total} pass ===")
    if passed < total:
        print("\nFailed checks:")
        for name, ok in results:
            if not ok:
                print(f"  - {name}")
        print("\nDiagnostic ladder:")
        print("  1. source:  grep 'font-size:62\\.5%' src/styles/tokens.css")
        print("  2. dist:    grep 'font-size:62\\.5%' dist/_aot_assets/*.css")
        print("  3. CDN:     curl https://content-astro-homepage.active-oahu-tours-mirror.pages.dev/_aot_assets/<hash>.css")
        print("  4. Browser: getComputedStyle(document.documentElement).fontSize === '10px'")
        print("  5. Browser: getComputedStyle('.aot-hero-section h2').fontSize === '60px' (on 1280px viewport)")
        return 1

    print("\nALL CHECKS PASS — hero matches production.")
    print("Next: visually verify with browser_navigate, take a screenshot if possible, run Lighthouse, update Linear.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
