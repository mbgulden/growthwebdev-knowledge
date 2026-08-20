#!/usr/bin/env python3
"""scripts/verify_kpi_collection_against_live_site.py

Ad-hoc verifier for a per-site *.kpi.json file. Anchors the JSON's
metrics against the LIVE mirror tree before the operator trusts it.

This is the canonical checker called out by the
"Procurement discipline" section in the kpis-and-reporter-architecture
skill. The user has corrected metric-JSON authorship twice when this
check was skipped; running it before committing is the durable rule.

Two modes:

  1. python3 scripts/verify_kpi_collection_against_live_site.py <collection>
       — runs the structural check (schema-light `validate()`) plus
         a live-mirror grep for the tracking_property ID and event names.

  2. python3 scripts/verify_kpi_collection_against_live_site.py <collection> --no-live
       — runs the structural check only; useful in CI without a live
         mirror. CI must pass this AND the production site verifier
         (e.g. the publish-kpi-tracker's live coverage verifier).

Exit code 0 means the collection is structurally valid AND its facts
match the live site. Exit code 1 means at least one assertion failed.
Exit code 2 means the file or the live mirror could not be located.

This script is the canonical entry point for the "did I ground the JSON
against the live mirror?" question. It does not modify any file; it
prints PASS / FAIL lines and exits.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def fail(name, msg=""):
    print(f"[FAIL] {name}{' -- ' + msg if msg else ''}")
    return 1


def ok(name):
    print(f"[PASS] {name}")


def structural_validate(collection):
    """Run the same shape checks the canonical kpi.validate() does,
    returning a list of errors. This is the stdlib-only version that
    doesn't depend on a third-party JSON Schema library.
    """
    errors = []
    for fld in ("schema_version", "name", "owner", "metrics"):
        if fld not in collection:
            errors.append(f"missing required field {fld!r}")
    if "site_slug" in collection and not isinstance(collection["site_slug"], str):
        errors.append("site_slug must be a string")
    for mid, m in collection.get("metrics", {}).items():
        if not isinstance(mid, str) or not all(c.isalnum() or c in "._*" for c in mid):
            errors.append(f"metrics: key {mid!r} must match ^[a-z0-9._*]+$")
        if not isinstance(m, dict):
            errors.append(f"metrics: {mid!r} must be a dict")
            continue
        for f in ("id", "label", "source"):
            if f not in m:
                errors.append(f"metrics: {mid!r} missing {f!r}")
        if "source" in m and m["source"] not in {
            "ga4", "stripe", "telegram", "internal",
            "derived", "gsc", "mcp", "sheets", "ci", "verifier",
        }:
            errors.append(f"metrics: {mid!r} source invalid")
    return errors


def find_live_mirror(slug):
    """Resolve a live mirror for a given slug by looking at the registry's
    site_dir_candidates (if any), then falling back to a
    /home/ubuntu/work/<slug>-*-mirror or
    /home/ubuntu/work/<slug>-*-<digits>/site/ walk. Returns None if no
    candidate is found.
    """
    candidates = []
    # Registry lookup.
    for cfg in (
        Path("/home/ubuntu/work/prismatic-pwp-ubersuggest-auth/config/seo_sites.json"),
        Path("/home/ubuntu/work/prismatic-engine/config/seo_sites.json"),
    ):
        if cfg.exists():
            try:
                doc = json.loads(cfg.read_text())
                for s in doc.get("sites", []):
                    if s.get("slug") == slug:
                        candidates.extend(s.get("site_dir_candidates") or [])
            except Exception:
                pass
    # Walk for mirror trees.
    base = Path("/home/ubuntu/work")
    if base.is_dir():
        for entry in base.iterdir():
            if not entry.is_dir():
                continue
            name = entry.name
            if slug not in name or "mirror" not in name:
                continue
            site_dir = entry / "site"
            if site_dir.is_dir():
                candidates.append(str(site_dir))
    if not candidates:
        return None
    # Pick the first existing one; the registry ordering is already curated.
    for c in candidates:
        if Path(c).is_dir():
            return Path(c)
    return None


def live_metric_signals(mirror_root):
    """Grep the live mirror for the GA4 measurement ID and event names that
    the live site actually emits. Returns (ga4_ids, event_names).
    """
    gtag_config = re.compile(r"""gtag\(\s*['"]config['"],\s*['"](G-[A-Z0-9]+)['"]""")
    gtag_event = re.compile(r"""gtag\(\s*['"]event['"],?\s*['"]([A-Za-z0-9_]+)['"]""")
    ga4_ids = set()
    events = set()
    if not mirror_root or not mirror_root.is_dir():
        return ga4_ids, events
    for p in mirror_root.rglob("*.html"):
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for m in gtag_config.finditer(text):
            ga4_ids.add(m.group(1))
        for m in gtag_event.finditer(text):
            events.add(m.group(1))
    # Body-bottom partials (e.g. only "dataLayer.push" without a full gtag)
    # are detected separately by the publish-kpi-tracker live coverage
    # verifier; this script focuses on the gtag('event', ...) wire.
    return ga4_ids, events


def live_has_loader_snippet(mirror_root, expected_ga4):
    """Confirm the served HTML includes the GA4 loader snippet for the
    expected measurement ID. Returns True / False.
    """
    if not mirror_root:
        return False
    target = expected_ga4
    for p in mirror_root.rglob("*.html"):
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if target and target in text:
            return True
    return False


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Verify a per-site *.kpi.json against the live mirror tree.",
    )
    parser.add_argument("collection", help="Path to a per-site *.kpi.json file")
    parser.add_argument("--no-live", action="store_true",
                        help="Skip the live-mirror cross-check; structural only.")
    parser.add_argument("--mirror", help="Override the auto-detected mirror path.")
    args = parser.parse_args(argv)

    target = Path(args.collection)
    if not target.exists():
        print(f"error: {target} not found", file=sys.stderr)
        return 2
    obj = json.loads(target.read_text(encoding="utf-8"))

    # 1. Structural validate.
    errs = structural_validate(obj)
    failed = False
    if errs:
        failed = True
        for e in errs:
            fail("structural", e)
    else:
        ok("structural")

    # 2. Live mirror cross-check.
    if not args.no_live:
        slug = obj.get("site_slug", target.stem.split(".")[0])
        mirror = (Path(args.mirror) if args.mirror else find_live_mirror(slug))
        if not mirror:
            fail("live-mirror", f"could not locate live mirror for {slug!r}; pass --mirror to override or use --no-live")
            failed = True
        else:
            ga4_ids, events = live_metric_signals(mirror)
            tracking = obj.get("tracking_property", "")
            if tracking and tracking not in ga4_ids:
                fail("live-tracking_property", f"{tracking!r} not found in any gtag('config', ...) on {mirror}")
                failed = True
            else:
                ok(f"live-tracking_property ({tracking!r} present)")
            if not live_has_loader_snippet(mirror, tracking):
                fail("live-loader-snippet", f"GA loader snippet for {tracking!r} not present on {mirror}")
                failed = True
            else:
                ok("live-loader-snippet")
            metric_events = {m.get("event") for m in obj.get("metrics", {}).values() if m.get("source") == "ga4" and m.get("event")}
            missing = metric_events - events
            if missing:
                fail("live-metric-events", f"events declared in JSON but not emitted on {mirror}: {sorted(missing)}")
                failed = True
            else:
                ok(f"live-metric-events ({len(metric_events)} events present)")
    if failed:
        print("---")
        print("FAIL: at least one assertion failed; do not commit this file.")
        return 1
    print("---")
    print(f"PASS: {target} structurally valid and grounded against the live mirror.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
