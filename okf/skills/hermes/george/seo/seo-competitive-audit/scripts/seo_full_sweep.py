#!/usr/bin/env python3
"""
Active Oahu Tours — Full Competitive SEO Sweep
================================================
Runs autonomously. Each phase opens/closes its own MCP session to respect
the 3-4 call per session timeout limit. Saves structured JSON + summary.

Usage:
    python3 scripts/seo_full_sweep.py

Customize TARGETS and SEED_KEYWORDS below before running.
"""
import asyncio, json, os, sys
from datetime import datetime

OUTDIR = os.path.join(os.environ.get("HERMES_PROFILE", "/home/ubuntu/.hermes/profiles/kai"), "cron/output/seo-audit")
os.makedirs(OUTDIR, exist_ok=True)

# ===== CONFIGURATION — Edit these =====
MY_SITE = "activeoahutours.com"

# Direct local competitors
DIRECT = [
    "kailuabeachadventures.com",
    "kahanaadventures.com",
    "hawaiibeachtime.com",
    "hawaiianwatersports.com",
    "bluebaykayakrentals.com",
    "surfnsea.com",
]

# Core seed keywords for content expansion
SEED_KEYWORDS = [
    "kailua kayak rental",
    "oahu paddleboard rental",
    "kaneohe sandbar kayak",
    "lanikai beach kayak",
    "sharks cove snorkeling",
    "oahu e-bike rental",
    "kailua beach equipment rental",
    "mokulua islands kayak",
    "chinaman's hat kayak",
    "windward oahu activities",
]

# Priority keywords for SERP analysis (focus on positions 2-4 in striking distance)
SERP_PRIORITY = [
    "kailua beach kayak rental",
    "kailua kayak rental",
    "rent kayak kailua",
    "kaneohe sandbar kayak rentals",
    "stand up paddleboard rental",
    "kayak rental kailua beach",
    "paddle board rental oahu",
    "kaneohe bay kayak rentals",
]

# ===== HELPERS =====
TS = datetime.now().strftime("%Y%m%d_%H%M%S")
TOKEN = open('/tmp/ubs_token').read().strip()
MCP_URL = "https://ubersuggest-mcp.neilpatelapi.com/mcp"
MCP_HEADERS = {"Authorization": f"Bearer {TOKEN}"}


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def save_json(filename, data):
    path = f"{OUTDIR}/{TS}_{filename}.json"
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)
    log(f"  Saved: {filename}.json ({len(json.dumps(data, default=str))} bytes)")
    return path


def safe_parse(text):
    """Wrap json.loads in try/except for tools that return empty/non-JSON."""
    if not text or not text.strip():
        return {"error": "empty response"}
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        return {"error": f"JSONDecodeError: {e}", "raw": text[:500]}


async def call_mcp(tool, args):
    """Single MCP call in its own session (to avoid connection timeout)."""
    from mcp import ClientSession
    from mcp.client.streamable_http import streamablehttp_client
    try:
        async with streamablehttp_client(MCP_URL, headers=MCP_HEADERS) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool, args)
                text = result.content[0].text if result.content else ""
                return safe_parse(text)
    except Exception as e:
        log(f"  ERROR in {tool}({args}): {e}")
        return {"error": str(e)}


async def batch_calls(calls):
    """Run 2-4 MCP calls sequentially, each in its own session. Keep call count low."""
    results = {}
    for i, (tool, args, key) in enumerate(calls):
        log(f"  [{i+1}/{len(calls)}] {tool}({args.get('domain', args.get('keyword', ''))})")
        results[key] = await call_mcp(tool, args)
    return results


def dict_key(data, *keys):
    """Try multiple possible keys for flexibility."""
    for k in keys:
        if k in data:
            return data[k]
    return None


# ===== PHASES =====

async def phase1_domain_overviews():
    log("\n=== PHASE 1: Domain Overviews ===")
    calls = [(MY_SITE, {"domain": MY_SITE}, MY_SITE)]
    for domain in DIRECT:
        calls.append(("domain_overview", {"domain": domain}, domain))
    # Limit to 4 per session
    all_results = {}
    for i in range(0, len(calls), 4):
        batch = calls[i:i+4]
        all_results.update(await batch_calls(batch))
    save_json("phase1_domain_overviews", all_results)
    return all_results


async def phase2_competitor_keywords():
    log("\n=== PHASE 2: Competitor Keywords (gap analysis) ===")
    # Focus on the top 3-4 competitors to keep call count manageable
    top = [d for d in DIRECT if d in [
        "kailuabeachadventures.com", "surfnsea.com",
        "hawaiianwatersports.com", "hawaiibeachtime.com"
    ]]
    calls = []
    for domain in [MY_SITE] + top:
        calls.append(("domain_keywords", {"domain": domain, "type": "organic", "limit": 50}, domain))
    results = await batch_calls(calls)
    save_json("phase2_domain_keywords", results)
    return results


async def phase3_top_pages():
    log("\n=== PHASE 3: Top Pages ===")
    top = ["kailuabeachadventures.com", "surfnsea.com", "hawaiibeachtime.com"]
    calls = []
    for domain in [MY_SITE] + top:
        calls.append(("domain_top_pages", {"domain": domain, "limit": 20}, domain))
    results = await batch_calls(calls)
    save_json("phase3_top_pages", results)
    return results


async def phase4_backlink_opportunity():
    log("\n=== PHASE 4: Backlink Opportunity ===")
    # Note: This tool is known to return empty responses.
    try:
        result = await call_mcp("backlink_opportunity", {
            "positive_targets": ["kailuabeachadventures.com", "surfnsea.com"],
            "negative_targets": [MY_SITE],
            "limit": 25
        })
    except Exception:
        # Fallback: try singular param names
        try:
            result = await call_mcp("backlink_opportunity", {
                "positive_target": "kailuabeachadventures.com",
                "negative_target": MY_SITE,
                "limit": 15
            })
        except Exception as e2:
            result = {"error": str(e2), "note": "backlink_opportunity tool unavailable"}
    save_json("phase4_backlink_opportunity", result)
    return result


async def phase5_keyword_suggestions():
    log("\n=== PHASE 5: Keyword Suggestions ===")
    # Fallback to google_suggestions if keyword_suggestions fails
    results = {}
    for kw in SEED_KEYWORDS:
        log(f"  trying google_suggestions for: {kw}")
        r = await call_mcp("google_suggestions", {"keywords": [kw]})
        results[kw] = r
    save_json("phase5_keyword_suggestions", results)
    return results


async def phase6_serp_analysis():
    log("\n=== PHASE 6: SERP Analysis ===")
    # Batch in groups of 4
    all_results = {}
    calls = [("serp_analysis", {"keyword": kw, "limit": 10}, kw) for kw in SERP_PRIORITY]
    for i in range(0, len(calls), 4):
        batch = calls[i:i+4]
        all_results.update(await batch_calls(batch))
    save_json("phase6_serp_analysis", all_results)
    return all_results


async def phase7_unknown_competitors():
    log("\n=== PHASE 7: Unknown Competitors Check ===")
    unknowns = ["hawaiianwatersports.com", "bluebaykayakrentals.com", "windwardwatersports.com"]
    calls = [("domain_overview", {"domain": d}, d) for d in unknowns]
    results = await batch_calls(calls)
    save_json("phase7_unknown_competitors", results)
    return results


async def main():
    log(f"=== ACTIVE OAHU TOURS — FULL SEO SWEEP ===")
    log(f"Started: {datetime.now().isoformat()}")

    phases = [
        ("Phase 1 — Domain Overviews", phase1_domain_overviews),
        ("Phase 2 — Competitor Keywords", phase2_competitor_keywords),
        ("Phase 3 — Top Pages", phase3_top_pages),
        ("Phase 4 — Backlink Opportunity", phase4_backlink_opportunity),
        ("Phase 5 — Keyword Suggestions", phase5_keyword_suggestions),
        ("Phase 6 — SERP Analysis", phase6_serp_analysis),
        ("Phase 7 — Unknown Competitors", phase7_unknown_competitors),
    ]

    results_summary = {}
    for phase_name, phase_fn in phases:
        log(f"\n{'='*60}")
        log(f"Starting: {phase_name}")
        log(f"{'='*60}")
        try:
            data = await phase_fn()
            results_summary[phase_name] = "✓ Complete"
        except Exception as e:
            log(f"PHASE FAILED: {e}")
            results_summary[phase_name] = f"✗ FAILED: {e}"

    # Final summary
    log(f"\n{'='*60}")
    log(f"SWEEP COMPLETE")
    log(f"{'='*60}")
    for phase, status in results_summary.items():
        log(f"  {status} — {phase}")
    log(f"\nReports: {OUTDIR}/")

    save_json("_index", {
        "timestamp": TS,
        "phases": results_summary,
        "targets": [MY_SITE] + DIRECT,
        "seed_keywords": SEED_KEYWORDS,
    })


if __name__ == "__main__":
    asyncio.run(main())
