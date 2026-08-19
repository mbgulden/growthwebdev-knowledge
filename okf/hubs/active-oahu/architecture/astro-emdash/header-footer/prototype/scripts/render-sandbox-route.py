#!/usr/bin/env python3
"""Render a non-public Astro sandbox shell proof from canonical AOT shell artifacts.

This script intentionally writes only architecture/prototype artifacts under
okf/architecture/astro-emdash/header-footer/prototype/. It does not touch the
production static `site/` output.
"""
from __future__ import annotations

import hashlib
import html
import json
from pathlib import Path
from urllib.parse import urljoin

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "src/content/nav/aot-shell-data.json"
SITE_NAV_SCHEMA = ROOT / "generated/schema/site-navigation.jsonld"
LOCAL_BUSINESS_SCHEMA = ROOT / "generated/schema/local-business.jsonld"
COMBINED_SCHEMA = ROOT / "generated/schema/combined-shell-schema.jsonld"
LLMS_NAV = ROOT / "generated/llms/navigation-section.txt"
ROUTE_OUT = ROOT / "rendered/sandbox-shell-route.html"
PAGE_OUT = ROOT / "src/pages/_sandbox/aot-shell.astro"
SITE = "https://activeoahutours.com"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def abs_url(href: str) -> str:
    if href.startswith(("http://", "https://", "tel:", "mailto:")):
        return href
    return urljoin(SITE + "/", href.lstrip("/"))


def nav_html(items: list[dict], level: int = 1) -> str:
    cls = "primary-nav" if level == 1 else "sub-menu"
    lines = [f'<ul class="{cls}" data-depth="{level}">']
    for item in items:
        children = item.get("children") or []
        child_marker = f' data-has-children="true"' if children else ""
        lines.append(f'<li data-intent="{html.escape(item["intent"])}"{child_marker}>')
        lines.append(
            f'<a href="{html.escape(abs_url(item["href"]))}" data-ai-summary="{html.escape(item["aiSummary"])}">{html.escape(item["label"])}</a>'
        )
        if children:
            lines.append(nav_html(children, level + 1))
        lines.append("</li>")
    lines.append("</ul>")
    return "\n".join(lines)


def footer_html(groups: list[dict]) -> str:
    lines = []
    for group in groups:
        lines.append(f'<section class="footer-group priority-{html.escape(group["priority"])}" aria-labelledby="footer-{html.escape(group["id"])}">')
        lines.append(f'<h2 id="footer-{html.escape(group["id"])}">{html.escape(group["heading"])}</h2>')
        lines.append("<ul>")
        for item in group["items"]:
            lines.append(
                f'<li data-intent="{html.escape(item["intent"])}"><a href="{html.escape(abs_url(item["href"]))}">{html.escape(item["label"])}</a></li>'
            )
        lines.append("</ul>")
        lines.append("</section>")
    return "\n".join(lines)


def main() -> None:
    shell = load_json(DATA)
    site_nav_schema = load_json(SITE_NAV_SCHEMA)
    local_business_schema = load_json(LOCAL_BUSINESS_SCHEMA)
    combined_schema = load_json(COMBINED_SCHEMA)
    llms_text = LLMS_NAV.read_text()
    llms_digest = hashlib.sha256(llms_text.encode()).hexdigest()[:16]

    booking = shell["bookingConfig"]
    business = shell["business"]
    language_links = [x for x in shell["utilityLinks"] if x["intent"] == "language"]

    ROUTE_OUT.parent.mkdir(parents=True, exist_ok=True)
    PAGE_OUT.parent.mkdir(parents=True, exist_ok=True)

    site_nav_json = json.dumps(site_nav_schema, ensure_ascii=False).replace("</", "<\\/")
    local_business_json = json.dumps(local_business_schema, ensure_ascii=False).replace("</", "<\\/")
    combined_schema_json = json.dumps(combined_schema, ensure_ascii=False).replace("</", "<\\/")

    route_html = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="robots" content="noindex,nofollow">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Active Oahu Tours Astro shell sandbox</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Open+Sans+Condensed:wght@700&display=swap" rel="stylesheet">
  <style>
    :root {{ --aot-blue: #004466; --aot-orange: #f57c00; --font-headings: "Open Sans Condensed", "Arial Narrow", Arial, sans-serif; }}
    body {{ margin: 0; font-family: Arial, sans-serif; color: #123; }}
    h1, h2, h3, h4, h5, h6 {{ font-family: var(--font-headings) !important; font-weight: 700 !important; font-style: normal !important; }}
    .skip-link {{ position: absolute; left: 0; top: 0; background: #fff; color: #004466; padding: .5rem; transform: translateY(-120%); }}
    .skip-link:focus {{ transform: translateY(0); }}
    header, footer {{ padding: 1rem; background: #f5fbfd; }}
    nav ul {{ list-style: none; padding-left: 0; }}
    nav .sub-menu {{ padding-left: 1.25rem; }}
    a {{ color: #004466; }}
    .book-now {{ display: inline-block; background: var(--aot-orange); color: #111; padding: .6rem .9rem; font-weight: 700; }}
    main {{ padding: 1rem; }}
    pre {{ white-space: pre-wrap; background: #f6f6f6; padding: 1rem; overflow-x: auto; }}
  </style>
  <script type="application/ld+json" id="aot-site-navigation-schema">{site_nav_json}</script>
  <script type="application/ld+json" id="aot-local-business-schema">{local_business_json}</script>
  <script type="application/ld+json" id="aot-combined-shell-schema">{combined_schema_json}</script>
</head>
<body data-shell-source="aot-shell-data.v1" data-llms-digest="{llms_digest}" data-booking-shortname="{html.escape(booking['shortname'])}">
  <a class="skip-link" href="#main">Skip to content</a>
  <header role="banner" aria-label="Active Oahu Tours sandbox header">
    <section id="branding" aria-label="Brand and booking">
      <a class="aot-logo" href="{SITE}/" aria-label="Active Oahu Tours home">Active Oahu Tours</a>
      <p><a href="{html.escape(business['telephoneHref'])}">{html.escape(business['phone'])}</a></p>
      <a class="book-now" href="{html.escape(booking['href'])}" data-booking-shortname="{html.escape(booking['shortname'])}" data-booking-event="{html.escape(booking['analyticsEvent'])}">{html.escape(booking['ctaLabel'])}</a>
      <p class="language-links">{' '.join(f'<a href="{html.escape(abs_url(link["href"]))}">{html.escape(link["label"])}</a>' for link in language_links)}</p>
    </section>
    <nav aria-label="Primary" data-source="aot-shell-data.json">
      {nav_html(shell['primaryNav'])}
    </nav>
  </header>
  <main id="main" tabindex="-1">
    <h1>Active Oahu Tours Astro shell sandbox</h1>
    <p>This non-public route proves the Astro shell can render from canonical shell data while embedding the generated search and AI artifacts.</p>
    <section aria-labelledby="schema-proof">
      <h2 id="schema-proof">Schema and AI proof</h2>
      <ul>
        <li>SiteNavigationElement rows: {len(site_nav_schema['itemListElement'])}</li>
        <li>Footer groups: {len(shell['footerGroups'])}</li>
        <li>LLMS navigation digest: {llms_digest}</li>
        <li>Priority order: {' → '.join(shell['priorityOrder'])}</li>
      </ul>
      <h3>LLMS navigation excerpt</h3>
      <pre>{html.escape('\n'.join(llms_text.splitlines()[:14]))}</pre>
    </section>
  </main>
  <footer role="contentinfo" aria-label="Active Oahu Tours sandbox footer">
    <section aria-label="Business contact">
      <h2>{html.escape(business['name'])}</h2>
      <p><a href="{html.escape(business['telephoneHref'])}">{html.escape(business['phone'])}</a> · <a href="mailto:{html.escape(business['email'])}">{html.escape(business['email'])}</a></p>
    </section>
    <nav aria-label="Footer" data-source="aot-shell-data.json">
      {footer_html(shell['footerGroups'])}
    </nav>
  </footer>
</body>
</html>
'''
    ROUTE_OUT.write_text(route_html)

    page_stub = '''---
import SiteShell from "../../components/shell/SiteShell.astro";
import shellData from "../../content/nav/aot-shell-data.json";
import siteNavigationSchema from "../../generated/schema/site-navigation.jsonld";
import localBusinessSchema from "../../generated/schema/local-business.jsonld";
import llmsNavigation from "../../generated/llms/navigation-section.txt?raw";
---
<!--
  Non-public Astro sandbox route stub.
  It documents the intended integration point; the deterministic rendered proof
  lives at prototype/rendered/sandbox-shell-route.html until an Astro build
  harness is introduced.
-->
<SiteShell title="Active Oahu Tours Astro shell sandbox">
  <script type="application/ld+json" set:html={JSON.stringify(siteNavigationSchema)} />
  <script type="application/ld+json" set:html={JSON.stringify(localBusinessSchema)} />
  <h1>Active Oahu Tours Astro shell sandbox</h1>
  <p data-booking-shortname={shellData.bookingConfig.shortname}>Canonical shell data, schema, and AI navigation output load together here.</p>
  <pre>{llmsNavigation.split("\\n").slice(0, 14).join("\\n")}</pre>
</SiteShell>
'''
    PAGE_OUT.write_text(page_stub)

    print(json.dumps({
        "rendered": str(ROUTE_OUT.relative_to(ROOT)),
        "pageStub": str(PAGE_OUT.relative_to(ROOT)),
        "siteNavigationElements": len(site_nav_schema["itemListElement"]),
        "footerGroups": len(shell["footerGroups"]),
        "llmsDigest": llms_digest,
        "bookingShortname": booking["shortname"],
    }, indent=2))


if __name__ == "__main__":
    main()
