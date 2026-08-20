#!/usr/bin/env python3
"""
Active Oahu Tours SEO Baseline Audit Template
============================================

Reusable sweep template for activeoahutours.com (or any single-domain SEO
baseline audit). Runs 5 phases of the Ubersuggest MCP, saves JSON per phase
plus a markdown summary.

Usage:
    python3 aot_seo_baseline_audit.py

Customize:
    - MY_SITE: the target domain
    - COMPETITORS: list of competitor domains
    - PRIORITY_KEYWORDS: keywords you care about for SERP analysis
    - OUTDIR: where to save outputs (default: ./audits/baseline-YYYY-MM-DD/)

This is a TEMPLATE — copy and modify for each audit. The original
AOT June 19 2026 audit at /home/ubuntu/work/aot-seo-knowledge/okf/audits/baseline-2026-06-19/
is the reference implementation.

Prerequisites:
    pip install --break-system-packages mcp
    /tmp/ubs_token must contain a valid Ubersuggest MCP token (see
    seo-competitive-audit's references/ubs-token-refresh-pkce.md)
"""
import asyncio, json, os, sys
from pathlib import Path
from datetime import datetime

# === TARGETS — EDIT THESE ===
MY_SITE = "activeoahutours.com"
COMPETITORS = [
    "kailuabeachadventures.com",
    "hawaiibeachtime.com",
    "hawaiianwatersports.com",
    "bluebaykayakrentals.com",
    "kahanaadventures.com",
    "surfnsea.com",
]
PRIORITY_KEYWORDS = [
    # Edit for your initiative
    "kailua kayak rental",
    "oahu paddleboard rental",
    "sharks cove snorkeling",
    "kaneohe sandbar kayak",
    "lanikai beach kayak",
    "oahu e-bike rental",
    "mokulua islands kayak",
    "chinaman's hat kayak",
    "windward oahu activities",
    "snorkeling oahu north shore",
]

# === TOKEN + ENDPOINT ===
TOKEN = open("/tmp/ubs_token").read().strip()
MCP_URL = "https://ubersuggest-mcp.neilpatelapi.com/mcp"
MCP_HEADERS = {"Authorization": f"Bearer {TOKEN}"}

# === OUTPUT ===
TS = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
DATE = datetime.utcnow().strftime("%Y-%m-%d")
OUTDIR = Path(f"./audits/baseline-{DATE}")
OUTDIR.mkdir(parents=True, exist_ok=True)


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def save_json(name, data):
    path = OUTDIR / f"{TS}_{name}.json"
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)
    log(f"  Saved: {name}.json")
    return path


async def call_mcp(tool, args):
    """Single MCP call in its own session (avoid timeouts)."""
    from mcp import ClientSession
    from mcp.client.streamable_http import streamablehttp_client
    try:
        async with streamablehttp_client(MCP_URL, headers=MCP_HEADERS) as (r, w, _):
            async with ClientSession(r, w) as session:
                await session.initialize()
                result = await session.call_tool(tool, args)
                text = result.content[0].text if result.content else "{}"
                try:
                    return json.loads(text)
                except Exception:
                    return {"raw_response": text[:500]}
    except Exception as e:
        log(f"  ERROR in {tool}({args}): {e}")
        return {"error": str(e)}


async def phase1():
    """Domain overviews for our site + competitors."""
    log("=== PHASE 1: Domain Overviews ===")
    results = {}
    for domain in [MY_SITE] + COMPETITORS:
        log(f"  domain_overview({domain})")
        results[domain] = await call_mcp("domain_overview", {"domain": domain})
        await asyncio.sleep(0.5)
    save_json("phase1_domain_overviews", results)
    return results


async def phase2():
    """Top 50 organic keywords per domain + gap analysis."""
    log("=== PHASE 2: Domain Keywords ===")
    targets = [MY_SITE] + COMPETITORS
    results = {}
    for domain in targets:
        log(f"  domain_keywords({domain})")
        results[domain] = await call_mcp(
            "domain_keywords", {"domain": domain, "type": "organic", "limit": 50}
        )
        await asyncio.sleep(0.5)
    save_json("phase2_domain_keywords", results)

    # Compute gap: what competitors rank for that we don't
    my_kws = set()
    if MY_SITE in results and isinstance(results[MY_SITE], list):
        my_kws = {k.get("keyword", "").lower() for k in results[MY_SITE] if isinstance(k, dict)}

    gaps = {}
    for domain, data in results.items():
        if domain == MY_SITE or not isinstance(data, list):
            continue
        their_kws = {k.get("keyword", "").lower() for k in data if isinstance(k, dict)}
        gaps[domain] = sorted(their_kws - my_kws)
        log(f"  Gap for {domain}: {len(gaps[domain])} keywords")

    save_json("keyword_gaps", gaps)


async def phase3():
    """Top 20 pages per domain."""
    log("=== PHASE 3: Top Pages ===")
    targets = [MY_SITE] + COMPETITORS
    results = {}
    for domain in targets:
        log(f"  domain_top_pages({domain})")
        results[domain] = await call_mcp("domain_top_pages", {"domain": domain, "limit": 20})
        await asyncio.sleep(0.5)
    save_json("phase3_top_pages", results)


async def phase6():
    """SERP analysis for priority keywords."""
    log("=== PHASE 6: SERP Analysis ===")
    results = {}
    for kw in PRIORITY_KEYWORDS:
        log(f"  serp_analysis({kw})")
        results[kw] = await call_mcp("serp_analysis", {"keyword": kw, "limit": 10})
        await asyncio.sleep(0.5)
    save_json("phase6_serp_analysis", results)


async def phase7():
    """Direct competitors (by keyword overlap)."""
    log("=== PHASE 7: Competitors Tool ===")
    data = await call_mcp("competitors", {"domain": MY_SITE})
    save_json("phase7_competitors", data)


async def main():
    log(f"=== AOT SEO Baseline Audit — {DATE} ===")
    log(f"Target: {MY_SITE}")
    log(f"Competitors: {len(COMPETITORS)}")
    log(f"Priority keywords: {len(PRIORITY_KEYWORDS)}")
    log(f"Output dir: {OUTDIR}")
    log("")

    await phase1()
    await phase2()
    await phase3()
    await phase6()
    await phase7()

    log("")
    log("=== All phases complete ===")
    log(f"Outputs in: {OUTDIR}")
    log("Next: synthesize state-of-<site>-baseline.md from these JSONs")


if __name__ == "__main__":
    asyncio.run(main())