#!/usr/bin/env python3
"""
AOT SEO Baseline Audit — June 19, 2026
Runs Phases 1, 2, 3, 6, 7 of the standard SEO sweep against
activeoahutours.com and key competitors. Saves JSON outputs to
OKF audits/baseline-2026-06-19/.
"""
import asyncio, json, os, sys
from pathlib import Path
from datetime import datetime

OUTDIR = Path("/home/ubuntu/work/aot-seo-knowledge/okf/audits/baseline-2026-06-19")
OUTDIR.mkdir(parents=True, exist_ok=True)
TS = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

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
    "kailua kayak rental",
    "oahu paddleboard rental",
    "kaneohe sandbar kayak",
    "lanikai beach kayak",
    "sharks cove snorkeling",
    "oahu e-bike rental",
    "mokulua islands kayak",
    "chinaman's hat kayak",
    "windward oahu activities",
    "kailua beach equipment rental",
    "kayaking oahu",
    "snorkeling oahu north shore",
]

TOKEN = open("/tmp/ubs_token").read().strip()
MCP_URL = "https://ubersuggest-mcp.neilpatelapi.com/mcp"
MCP_HEADERS = {"Authorization": f"Bearer {TOKEN}"}


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def save_json(name, data):
    path = OUTDIR / f"{TS}_{name}.json"
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)
    log(f"  Saved: {name}.json")
    return path


async def call_mcp(tool, args):
    from mcp import ClientSession
    from mcp.client.streamable_http import streamablehttp_client
    try:
        async with streamablehttp_client(MCP_URL, headers=MCP_HEADERS) as (read, write, _):
            async with ClientSession(read, write) as session:
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
    log("=== PHASE 1: Domain Overviews ===")
    targets = [MY_SITE] + COMPETITORS
    results = {}
    for domain in targets:
        log(f"  domain_overview({domain})")
        results[domain] = await call_mcp("domain_overview", {"domain": domain})
        await asyncio.sleep(0.5)
    save_json("phase1_domain_overviews", results)
    return results


async def phase2():
    log("=== PHASE 2: Domain Keywords (top 50 organic) ===")
    targets = [MY_SITE] + COMPETITORS
    results = {}
    for domain in targets:
        log(f"  domain_keywords({domain})")
        results[domain] = await call_mcp(
            "domain_keywords", {"domain": domain, "type": "organic", "limit": 50}
        )
        await asyncio.sleep(0.5)
    save_json("phase2_domain_keywords", results)

    # Keyword gap analysis
    my_kws = set()
    if MY_SITE in results and isinstance(results[MY_SITE], list):
        my_kws = {k.get("keyword", "").lower() for k in results[MY_SITE] if isinstance(k, dict)}

    log("=== KEYWORD GAP ANALYSIS ===")
    gaps = {}
    for domain, data in results.items():
        if domain == MY_SITE or not isinstance(data, list):
            continue
        their_kws = {k.get("keyword", "").lower() for k in data if isinstance(k, dict)}
        gap = their_kws - my_kws
        gaps[domain] = sorted(gap)
        log(f"  {domain}: {len(gap)} gap keywords")

    with open(OUTDIR / f"{TS}_keyword_gaps.json", "w") as f:
        json.dump(gaps, f, indent=2, default=str)


async def phase3():
    log("=== PHASE 3: Top Pages ===")
    targets = [MY_SITE] + COMPETITORS
    results = {}
    for domain in targets:
        log(f"  domain_top_pages({domain})")
        results[domain] = await call_mcp("domain_top_pages", {"domain": domain, "limit": 20})
        await asyncio.sleep(0.5)
    save_json("phase3_top_pages", results)


async def phase6():
    log("=== PHASE 6: SERP Analysis (priority keywords) ===")
    results = {}
    for kw in PRIORITY_KEYWORDS:
        log(f"  serp_analysis({kw})")
        results[kw] = await call_mcp("serp_analysis", {"keyword": kw, "limit": 10})
        await asyncio.sleep(0.5)
    save_json("phase6_serp_analysis", results)


async def phase7():
    log("=== PHASE 7: Competitors Tool ===")
    log(f"  competitors({MY_SITE})")
    data = await call_mcp("competitors", {"domain": MY_SITE})
    save_json("phase7_competitors", data)


async def main():
    await phase1()
    await phase2()
    await phase3()
    await phase6()
    await phase7()
    log("=== All phases complete ===")


if __name__ == "__main__":
    asyncio.run(main())
