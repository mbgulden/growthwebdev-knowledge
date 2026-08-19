#!/usr/bin/env python3
"""
Daily rank tracker for activeoahutours.com priority keywords.
Queries Ubersuggest MCP for each keyword's current SERP position,
compares to yesterday's reading, alerts on ≥3 position drops.
"""
import asyncio, json, os, sys
from pathlib import Path
from datetime import datetime, timezone

# Token + config
TOKEN = open("/tmp/ubs_token").read().strip()
MCP_URL = "https://ubersuggest-mcp.neilpatelapi.com/mcp"
MCP_HEADERS = {"Authorization": f"Bearer {TOKEN}"}

OUT_DIR = Path("/home/ubuntu/work/aot-seo-knowledge/okf/reports")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Top 50 priority keywords (expand as we learn more)
PRIORITY_KEYWORDS = [
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
    "best beaches windward oahu",
    "things to do in kailua",
    "waimanalo beach oahu",
    "lanikai beach oahu",
    "kailua beach hawaii",
    "electric beach oahu snorkeling",
    "hawaii kayak tours",
    "oahu kayak tours",
    "oahu beach gear rental",
    "popoia island kayak",
    "kailua beach park",
    "lanikai beach parking",
    "kailua parking",
    "self-guided kayak oahu",
    "best kayaking oahu",
    "kayak rental oahu",
    "snorkeling rental oahu",
    "beach equipment rental kailua",
    "north shore oahu snorkeling",
    "oahu north shore activities",
    "haleiwa paddleboard",
    "kahana river kayak",
    "windward coast oahu",
    "kailua activities",
    "oahu adventure tours",
    "best oahu beaches",
    "kailua beach adventure",
    "lanikai paddleboard",
    "snorkel rental oahu",
    "oahu snorkeling tours",
    "things to do oahu north shore",
    "kailua bike rental",
    "haleiwa surf shop",
    "north shore surf shop",
    "oahu sunset tours",
    "family activities oahu",
    "kayak oahu",
    "oahu kayak adventure",
    "guided kayak tour oahu",
    "sharks cove oahu",
]


async def call_serp(kw):
    from mcp import ClientSession
    from mcp.client.streamable_http import streamablehttp_client
    async with streamablehttp_client(MCP_URL, headers=MCP_HEADERS) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("serp_analysis", {"keyword": kw, "limit": 20})
            text = result.content[0].text if result.content else "{}"
            return json.loads(text)


def find_aot_position(kw_data):
    """Find AOT position from SERP result."""
    entries = kw_data.get("serpEntries", [])
    for entry in entries:
        if entry.get("domain") == "activeoahutours.com":
            return entry.get("position")
    return None


async def main():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    yesterday_file = OUT_DIR / f"daily-rank-{ (datetime.now(timezone.utc).replace(day=datetime.now(timezone.utc).day) ).strftime('%Y-%m-%d') }.json"

    results = {}
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Tracking {len(PRIORITY_KEYWORDS)} keywords...", flush=True)

    for i, kw in enumerate(PRIORITY_KEYWORDS):
        try:
            data = await call_serp(kw)
            pos = find_aot_position(data)
            results[kw] = {"position": pos, "checked_at": datetime.now(timezone.utc).isoformat()}
            print(f"  [{i+1}/{len(PRIORITY_KEYWORDS)}] {kw[:40]:<40} pos={pos}")
        except Exception as e:
            results[kw] = {"error": str(e), "checked_at": datetime.now(timezone.utc).isoformat()}
            print(f"  [{i+1}/{len(PRIORITY_KEYWORDS)}] {kw[:40]:<40} ERROR: {e}")
        await asyncio.sleep(0.7)  # rate limit

    # Save JSON
    out_path = OUT_DIR / f"daily-rank-{today}.json"
    with open(out_path, "w") as f:
        json.dump({"date": today, "results": results}, f, indent=2)

    # Compare to yesterday
    alerts = []
    yesterday = (datetime.now(timezone.utc) - __import__("datetime").timedelta(days=1)).strftime("%Y-%m-%d")
    yesterday_path = OUT_DIR / f"daily-rank-{yesterday}.json"
    if yesterday_path.exists():
        with open(yesterday_path) as f:
            yest = json.load(f)
        for kw, data in results.items():
            if "error" in data or data.get("position") is None:
                continue
            yest_pos = yest.get("results", {}).get(kw, {}).get("position")
            if yest_pos is None:
                continue
            today_pos = data["position"]
            if today_pos - yest_pos >= 3:
                alerts.append({"keyword": kw, "yesterday": yest_pos, "today": today_pos, "drop": today_pos - yest_pos})

    # Generate markdown report
    md = f"""# Daily Rank Tracker — {today}

**Keywords tracked:** {len(PRIORITY_KEYWORDS)}
**AOT visible:** {sum(1 for r in results.values() if r.get('position'))}
**Errors:** {sum(1 for r in results.values() if 'error' in r)}

## ⚠️ Alerts (drops ≥3 positions)

"""
    if alerts:
        for a in alerts:
            md += f"- 🔴 **{a['keyword']}**: #{a['yesterday']} → #{a['today']} (dropped {a['drop']})\n"
    else:
        md += "✅ No significant drops\n"

    md += "\n## Top 50 keywords\n\n"
    md += "| Keyword | Position |\n|---|---|\n"
    for kw in PRIORITY_KEYWORDS:
        pos = results[kw].get("position")
        md += f"| {kw} | {('#' + str(pos)) if pos else 'NOT RANKING'} |\n"

    md_path = OUT_DIR / f"daily-rank-{today}.md"
    with open(md_path, "w") as f:
        f.write(md)

    print(f"\n✅ Saved: {out_path.name} + {md_path.name}")
    if alerts:
        print(f"⚠️  {len(alerts)} keyword drops ≥3 positions")
        # TODO: send Telegram alert

if __name__ == "__main__":
    asyncio.run(main())
