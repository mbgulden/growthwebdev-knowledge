#!/usr/bin/env python3
"""Ad-hoc deploy verifier: byte-compare a live Cloudflare Pages custom domain
against a reference deployment (e.g. a known-good pages.dev build),
normalizing the Cloudflare custom-domain injections that make a raw diff
lie.

Usage:
  python3 cf-pages-deploy-diff.py <PROD_BASE> <GOOD_BASE> [--api PATH ...]

Example:
  python3 cf-pages-deploy-diff.py https://humandesignengine.com \
      https://a2b0aadb.hd-platform.pages.dev --api /api/health

Exits 0 only if: homepage title check passes (see EXPECT_TITLE below),
every sitemap route is content-identical after normalization, status codes
match, and all --api routes return 200 on the prod base.

NOTE: ad-hoc verification, not a test suite. No auth required (public URLs).
"""
import re
import sys
import json
import urllib.request
import concurrent.futures as cf

EXPECT_TITLE = "Verifiable calculations"          # must be present on prod homepage
FORBID_TITLE = "Daily Practice"                    # must NOT be present (stale-copy sentinel)


def get(url, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "hermes-verify/1.0"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.status, r.read()
        except Exception as e:
            if getattr(e, "code", None) == 404:
                return 404, b""
            if i == tries - 1:
                return None, b""
    return None, b""


def norm(b: bytes) -> bytes:
    """Canonicalize Cloudflare CUSTOM-DOMAIN transformations (not build content).
    Each pattern here was traced to a real false-diff in the 2026-08-20 HDE
    prod re-point; do not delete without re-tracing."""
    b = re.sub(rb'\s*<script[^>]*cloudflareinsights[^>]*></script>', b'', b)  # web-analytics beacon
    b = re.sub(rb'<a [^>]*__cf_email__[^>]*>.*?</a>', b'[EMAIL]', b, flags=re.S)  # obfuscated email link
    b = re.sub(rb'<script[^>]*cloudflare-static/email-decode[^>]*></script>', b'', b)
    b = re.sub(rb'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', b'[EMAIL]', b)  # raw email literal
    b = re.sub(rb'href="/cdn-cgi/l/email-protection#[0-9a-f]+"', b'[EMAILHREF]', b)  # CF mailto rewrite
    b = re.sub(rb'href="mailto:[^"]*"', b'[EMAILHREF]', b)
    b = re.sub(rb'\s+', b'', b)  # CF leaves a stray newline at the beacon injection point
    return b


def main() -> int:
    args = sys.argv[1:]
    api_routes = []
    pos = []
    i = 0
    while i < len(args):
        if args[i] == "--api":
            i += 1
            api_routes.append(args[i])
        else:
            pos.append(args[i])
        i += 1
    if len(pos) != 2:
        print(__doc__)
        return 2
    prod, good = pos

    st, home = get(prod + "/")
    title = re.search(rb"<title>([^<]*)</title>", home or b"").group(1).decode() if home else ""
    home_ok = (st == 200 and EXPECT_TITLE in title and FORBID_TITLE not in title)

    _, sm = get(good + "/sitemap.xml")
    paths = sorted({re.sub(r"^https?://[^/]+", "", p.decode()) for p in re.findall(rb"<loc>([^<]+)</loc>", sm)})

    def work(p):
        ps, pb = get(prod + p)
        gs, gb = get(good + p)
        return p, ps, pb, gs, gb

    match = differ = codes = 0
    dlist = []
    with cf.ThreadPoolExecutor(10) as ex:
        for p, ps, pb, gs, gb in ex.map(work, paths):
            if ps != gs:
                codes += 1
                dlist.append((p, "status", ps, gs))
                continue
            if norm(pb) != norm(gb):
                differ += 1
                dlist.append((p, "content"))
            else:
                match += 1

    api_ok = all(get(prod + u)[0] == 200 for u in api_routes) if api_routes else True
    result = {
        "home_ok": home_ok,
        "title": title,
        "routes_identical": match,
        "routes_differs": differ,
        "routes_status_differs": codes,
        "total_routes": len(paths),
        "diff_list": dlist[:12],
        "api_routes_checked": api_routes,
        "api_functions_live": api_ok,
    }
    print(json.dumps(result, indent=1))
    return 0 if (home_ok and differ == 0 and codes == 0 and api_ok) else 1


if __name__ == "__main__":
    sys.exit(main())
