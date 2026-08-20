# Ground KPI metric JSON against the live site **before** writing

A category "writes a fresh `kpi-collections.json` and gets the names wrong" failure pattern. The structural validator (`validate()`) catches: bad source, missing required field, inner-id mismatch, dotted-key pattern. It does **not** catch: a metric event that the live site never emits, a `tracking_property` that doesn't match the GA4 ID actually configured, or a `source_urls[0]` that doesn't reference a real page.

The user's correction that prompted this reference:

> "Your verifier is fine for structure — it just can't catch factually-wrong values. Next time, ground your JSON against the live site before writing, not after."

This is procurement discipline, not validation. Do it **before** the file is written so a wrong file is never produced.

## Authoring workflow (required from this point forward)

1. **Pick the mirror / live site.** Don't guess paths from memory. Confirm:
   - The repo root is `~/work/<repo>/` with `site/<slug>/index.html` style structure.
   - For multi-mirror repos (e.g. `active-oahu-tours-mirror`, `active-oahu-tours-mirror-2529`), the canonical one is identified by `config/seo_sites.json` `site_dir_candidates[0]` or by the most recently dated `prismic_published` log. If unclear, ask before writing.
2. **Pull the live GA4 ID.** From the live mirror, locate every `gtag('config', 'G-XXX')` invocation:
   ```bash
   grep -rhE "gtag\\(\\s*['\"]config['\"]" <REPO>/site/ | head -5
   ```
   The first unique `G-XXX` is your `tracking_property`. Quote it verbatim in the JSON.
3. **Pull the live event names.** From the live mirror, enumerate every `gtag('event', '<name>')` invocation:
   ```bash
   grep -rhE "gtag\\(\\s*['\"]event['\"]" <REPO>/site/ | grep -oE "'[A-Za-z0-9_]+'" | sort -u
   ```
   **There is no second source of truth.** If the user tells you "the site emits X, Y, Z", that's a passing ground for saying so, but the emitting code is the actual source. The grep output is canonical.
4. **Verify a source_url is real.** Hit `https://<domain>/` over HTTPS. Confirm the response body includes the GA4 loader snippet (`googletagmanager` or `gtag/js`).
5. **Write the JSON.** The metric `event` field must be a subset of the live event names. The `expected_data_layer_events` array must equal the live event names exactly.
6. **Save and verify.** Run the live-mirror-anchored verifier (`scripts/verify-aot-kpi-collections-2529.py` or equivalent — see Appendix A below). All assertions must pass.

## What this prevents

Five concrete failure modes that this catches before the file is written:

| Failure mode | What catches it |
|---|---|
| `tracking_property: G-FAKE00000` | grep against the live mirror pulls the real ID |
| `event: booking_start` listed but not actually emitted anywhere | grep for `gtag('event', 'booking_start')` returns nothing |
| `expected_data_layer_events` includes 4 events but the site only emits 2 | live-event-name set `= {booking_click, booking_complete}` ≠ JSON set |
| `source_urls[0]` points at a domain that doesn't ship the GA4 loader | HTTPS probe + body sniff for `googletagmanager` |
| `id: booking_click_total` but the live page emits `gtag('event', 'booking-evnt-click')` (typo) | grep against the live mirror returns the literal string and the assertion fails |

## Cross-domain booking flows: does this still apply?

Yes, but with this nuance: the `tracking_property` and the GA4 event names are still ground-truthed against the live mirror. The `source: "stripe"` part of the sourcing rule is **not** relaxed — Stripe is the source of truth for revenue when the booking flow is direct. When the booking flow is on a third-party provider (FareHarbor, Peek, etc.), Stripe is not the source — the provider's CSV export is. The two GA4 events (`booking_click`, `booking_complete`) are captured by the embed wrapper script and forwarded to GA4; surface those in the JSON, do not invent a `*revenue_usd` metric.

## Appendix A: live-mirror-anchored verifier template

The verifier pattern below cross-checks the JSON against the live mirror tree at the OS level. It catches every class of structurally-valid-but-factually-wrong output.

```python
#!/usr/bin/env python3
"""Ad-hoc verifier for a per-site kpi-collections.json file.

Two kinds of checks:
  (A) Schema correctness vs the kpis-and-reporter-architecture skill.
  (B) Factual correctness vs the live mirror tree at <REPO>/site/.
"""

import json
import os
import re
import subprocess
import sys
import ssl
import urllib.error
import urllib.request
from pathlib import Path

ALLOWED_SOURCES = {"ga4", "stripe", "telegram", "internal", "derived"}
SAFE_FORMULA = re.compile(r"^[\d\s+\-*/().]+$")

TARGET = Path("<REPO>/scripts/kpis/kpi-collections.json")  # absolute path
LIVE_ROOT = Path("<REPO>/site")

failures = []
def assert_true(name, cond, detail=""):
    tag = "PASS" if cond else "FAIL"
    print("[{0}] {1}{2}".format(tag, name, (" -- " + detail) if detail else ""))
    if not cond:
        failures.append(name + (": " + detail if detail else ""))
def assert_eq(name, got, want):
    assert_true(name, got == want, "got {0!r}, want {1!r}".format(got, want))

# (A) schema
assert_true("file exists", TARGET.exists(), str(TARGET))
data = json.loads(TARGET.read_text(encoding="utf-8"))
assert_eq("schema_version", data.get("schema_version"), "1.0")
# ... (full schema checks per the SKILL.md "Multi-site standardization" section)

# (B) live-mirror factual cross-check
assert_true("live mirror site/ exists", LIVE_ROOT.is_dir(), str(LIVE_ROOT))

# tracking_property: pull the GA4 ID directly from the live gtag('config', ...) calls
configs = subprocess.run(
    ["grep", "-rhE", r"gtag\(\s*['\"]config['\"]", str(LIVE_ROOT)],
    capture_output=True, text=True, timeout=20,
)
live_ga4_ids_with_quotes = re.findall(r"['\"]G-[A-Z0-9]+['\"]", configs.stdout)
# Strip surrounding quotes from each captured GA4 ID; the regex captures
# the argument list verbatim and includes the surrounding '"' or "'".
live_ga4_ids = sorted(set(s.strip("'\"") for s in live_ga4_ids_with_quotes))
assert_true("live GA4 IDs found in mirror", len(live_ga4_ids) > 0, "")
assert_eq(
    "tracking_property matches live GA4 ID(s)",
    data["globally_required"]["tracking_property"],
    live_ga4_ids[0] if len(live_ga4_ids) == 1 else "one of {0}".format(live_ga4_ids),
)

# Emitted event names: every gtag('event', '<name>') on the live site
events_proc = subprocess.run(
    ["grep", "-rhE", r"gtag\(\s*['\"]event['\"],?\s*['\"]([A-Za-z0-9_]+)['\"]", str(LIVE_ROOT)],
    capture_output=True, text=True, timeout=20,
)
live_event_names = sorted(set(re.findall(
    r"gtag\(\s*['\"]event['\"],?\s*['\"]([A-Za-z0-9_]+)['\"]", events_proc.stdout)))
metric_events = sorted(
    m["event"] for m in data["collections"][0]["metrics"]
    if m.get("source") == "ga4" and m.get("event")
)
assert_eq(
    "metric events == live gtag('event', ...) calls",
    metric_events,
    live_event_names,
)

# source_urls[0] actively ships the GA4 loader
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
target_url = data["collections"][0]["source_urls"][0].rstrip("/")
req = urllib.request.Request(target_url, headers={"User-Agent": "hermes-verify/1.0"})
try:
    with urllib.request.urlopen(req, timeout=10, context=ctx) as r:
        body_text = r.read().decode("utf-8", "replace").lower()
    assert_true(
        "live URL {0} ships GA4 loader".format(target_url),
        "googletagmanager" in body_text or "_gtag" in body_text,
        "no gtm snippet on the page",
    )
except urllib.error.HTTPError as e:
    assert_true("live URL {0} responded".format(target_url), False,
                "status={0}".format(e.code))

print()
print("=" * 72)
print("TOTAL FAILURES:", len(failures))
for f in failures:
    print("  - " + f)
print("=" * 72)
sys.exit(0 if not failures else 1)
```

## Important string-vs-byte regex trap

When extracting GA4 IDs from the live mirror, the regex `r"['\"]G-[A-Z0-9]+['\"]"` captures the surrounding quotes because `grep` output includes the literal argument list. The `strip("'\"")` step is what makes the equality check work. Forgetting it produces a spurious failure like `got 'G-PRRRLMBR8Z', want '"G-PRRRLMBR8Z"'`. Always strip quotes before comparing on the JSON side.

The same trap applies to `event` names if the regex captures the second argument's quotes; the canonical event name (e.g. `booking_click`) lives between the open and close quote, so the regex must use a capture group `(...)` and not the surrounding quotes.

## Catalogue of grep invocations

| What you need | Grep |
|---|---|
| GA4 measurement ID | `grep -rhE "gtag\(\s*['\"]config['\"]" <REPO>/site/` |
| GA4 event names | `grep -rhE "gtag\(\s*['\"]event['\"],?\s*['\"]([A-Za-z0-9_]+)['\"]" <REPO>/site/` |
| Strip surrounding quotes | `s.strip("'\"")` in Python |
| Count occurrences per event | `grep -rhEo '...' <REPO>/site/ \| sort \| uniq -c` |
| Source URLs actually used by rendered pages | `grep -rhE 'src="https?://[^"]+' <REPO>/site/ \| sort -u` |

## Why this is a procurement rule, not a validation rule

The mirror's `grep` output is the **procurement contract**. Running it **before** writing the JSON means a wrong file is never produced; running it **after** (as a verifier) means a wrong file gets written, then the verifier catches it, then the file is rewritten, then the verifier re-runs. The latter is what happened in the session that produced this reference. The first turn wrote a `kpi-collections.json` with four invented event names (`booking_start`, `begin_checkout`, `purchase`, `generate_lead`) that were never emitted anywhere on the live site — the structural schema passed, but the live URL would be empty if anyone ran a dashboard against it.

The lesson is structural: separate the procurement step from the structural-validation step, and run the procurement step **first**. By the time the file is written, every field whose value can be returned by a `grep` over the live mirror has been confirmed against the live mirror. The structural validator is then a sanity check, not the discovery tool.
