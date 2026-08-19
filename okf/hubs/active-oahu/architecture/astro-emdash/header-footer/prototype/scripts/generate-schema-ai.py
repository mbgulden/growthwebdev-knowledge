#!/usr/bin/env python3
"""Generate schema.org and /llms.txt navigation artifacts from AOT shell data.

This is intentionally non-public prep work for the Astro/emdash migration. It
proves search/AI outputs can derive from the same canonical nav/footer graph as
the rendered shell prototype.
"""
from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urljoin

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "src/content/nav/aot-shell-data.json"
OUT = ROOT / "generated"
SCHEMA_OUT = OUT / "schema"
LLMS_OUT = OUT / "llms"
SITE = "https://activeoahutours.com"


def load_data() -> dict:
    return json.loads(DATA_PATH.read_text())


def abs_url(href: str) -> str:
    if href.startswith("http://") or href.startswith("https://") or href.startswith("tel:") or href.startswith("mailto:"):
        return href
    return urljoin(SITE + "/", href.lstrip("/"))


def flatten_nav(items: list[dict], section: str = "primary", parent: str | None = None) -> list[dict]:
    flat: list[dict] = []
    for item in items:
        row = {
            "id": item["id"],
            "name": item["label"],
            "url": abs_url(item["href"]),
            "intent": item["intent"],
            "description": item["aiSummary"],
            "section": section,
        }
        if parent:
            row["parent"] = parent
        flat.append(row)
        flat.extend(flatten_nav(item.get("children") or [], section=section, parent=item["id"]))
    return flat


def footer_items(groups: list[dict]) -> list[dict]:
    out: list[dict] = []
    for group in groups:
        for item in group["items"]:
            out.append({
                "id": item["id"],
                "name": item["label"],
                "sourceText": item.get("sourceText", ""),
                "url": abs_url(item["href"]),
                "intent": item["intent"],
                "description": item["aiSummary"],
                "section": "footer",
                "footerGroup": group["id"],
                "footerHeading": group["heading"],
            })
    return out


def site_navigation_schema(rows: list[dict]) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "@id": SITE + "/#site-navigation",
        "name": "Active Oahu Tours site navigation",
        "description": "Canonical navigation graph generated from the Active Oahu shell data source for users, search engines, and AI assistants.",
        "itemListElement": [
            {
                "@type": "SiteNavigationElement",
                "position": i + 1,
                "name": row["name"],
                "url": row["url"],
                "description": row["description"],
                "additionalType": row["intent"],
            }
            for i, row in enumerate(rows)
            if not (row["url"].startswith("tel:") or row["url"].startswith("mailto:"))
        ],
    }


def local_business_schema(data: dict) -> dict:
    business = data["business"]
    booking = data["bookingConfig"]
    same_as = [u for u in business.get("sameAs", []) if u.startswith("http")]
    return {
        "@context": "https://schema.org",
        "@type": ["LocalBusiness", "TouristTrip"],
        "@id": SITE + "/#localbusiness",
        "name": business["name"],
        "url": business["url"],
        "telephone": business["phone"],
        "email": business["email"],
        "sameAs": same_as,
        "areaServed": ["Oahu", "Kailua", "Kaneohe Bay", "North Shore"],
        "priceRange": "$$",
        "potentialAction": {
            "@type": "ReserveAction",
            "target": {
                "@type": "EntryPoint",
                "urlTemplate": booking["href"],
                "actionPlatform": ["https://schema.org/DesktopWebPlatform", "https://schema.org/MobileWebPlatform"],
            },
            "name": booking["ctaLabel"],
        },
    }


def llms_section(data: dict, nav_rows: list[dict], footer_rows: list[dict]) -> str:
    booking = data["bookingConfig"]
    lines = [
        "# Active Oahu Tours navigation",
        "",
        "This section is generated from `prototype/src/content/nav/aot-shell-data.json`, the same canonical shell graph intended to render the Astro header/footer.",
        "",
        "## Booking",
        f"- {booking['ctaLabel']}: {booking['href']}",
        f"- FareHarbor shortname: `{booking['shortname']}`",
        f"- Fallback mode: `{booking['fallback']}`",
        "",
        "## Primary navigation",
    ]
    for row in nav_rows:
        indent = "  " if row.get("parent") else ""
        lines.append(f"{indent}- [{row['name']}]({row['url']}) — {row['intent']}: {row['description']}")
    lines.extend(["", "## Footer/contact navigation"])
    for row in footer_rows:
        lines.append(f"- [{row['name']}]({row['url']}) — {row['intent']}: {row['description']}")
    lines.extend([
        "",
        "## AI routing notes",
        "- Tours and activities live under the tour intent.",
        "- Rental pages live under the rental intent, including third-level kayak rental routes.",
        "- Place and planning content lives under the guide intent.",
        "- Booking remains a dedicated action and should not replace crawlable navigation links.",
        "- Users first, then search engines, then AI assistants, then booking conversion.",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    data = load_data()
    nav_rows = flatten_nav(data["primaryNav"], section="primary")
    utility_rows = [
        {
            "id": item["id"],
            "name": item["label"],
            "url": abs_url(item["href"]),
            "intent": item["intent"],
            "description": item["aiSummary"],
            "section": "utility",
        }
        for item in data["utilityLinks"]
    ]
    foot_rows = footer_items(data["footerGroups"])
    all_navigation_rows = utility_rows + nav_rows + foot_rows

    SCHEMA_OUT.mkdir(parents=True, exist_ok=True)
    LLMS_OUT.mkdir(parents=True, exist_ok=True)

    site_nav = site_navigation_schema(all_navigation_rows)
    local_business = local_business_schema(data)
    combined = {
        "@context": "https://schema.org",
        "@graph": [site_nav, local_business],
    }
    manifest = {
        "version": "aot-shell-schema-ai.v1",
        "source": str(DATA_PATH.relative_to(ROOT)),
        "sourceVersion": data["version"],
        "sourceCommit": data["sourceCommit"],
        "priorityOrder": data["priorityOrder"],
        "counts": {
            "utilityRows": len(utility_rows),
            "primaryNavRows": len(nav_rows),
            "footerRows": len(foot_rows),
            "schemaNavigationElements": len(site_nav["itemListElement"]),
        },
        "outputs": [
            "generated/schema/site-navigation.jsonld",
            "generated/schema/local-business.jsonld",
            "generated/schema/combined-shell-schema.jsonld",
            "generated/llms/navigation-section.txt",
        ],
    }

    (SCHEMA_OUT / "site-navigation.jsonld").write_text(json.dumps(site_nav, indent=2, ensure_ascii=False) + "\n")
    (SCHEMA_OUT / "local-business.jsonld").write_text(json.dumps(local_business, indent=2, ensure_ascii=False) + "\n")
    (SCHEMA_OUT / "combined-shell-schema.jsonld").write_text(json.dumps(combined, indent=2, ensure_ascii=False) + "\n")
    (LLMS_OUT / "navigation-section.txt").write_text(llms_section(data, nav_rows, foot_rows))
    (OUT / "schema-ai-manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
