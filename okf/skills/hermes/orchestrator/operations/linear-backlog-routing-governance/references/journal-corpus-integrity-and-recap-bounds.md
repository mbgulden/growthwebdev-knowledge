# Journal corpus integrity & bounded recap audit

Use this after implementing incremental journal collection or evidence-cited recaps.

## Audit sequence

1. **Separate code proof from corpus proof.** Passing cursor/dedupe tests only prove newly collected data. Inspect each live `events-YYYY-MM-DD.json` for total rows, non-empty stable-id coverage, duplicate-key rate, and event-type/source distribution.
2. **Treat legacy rows without stable IDs as unverified.** Preserve index/recap/quarantine artifacts in a dated repair backup before any rebuild. Do not silently call historical rows canonical or deduplicated.
3. **Bound every output surface.** Cap rendered claims *and* CLI/API result payloads. Return compact counts plus a manifest path, not an unbounded list of evidence hashes.
4. **Smoke from a neutral working directory.** Verify the installed runtime, not a nearby feature worktree. Assert daily/weekly artifact byte size, rendered claim count, citation coverage, and compact CLI output.
5. **Audit quarantine quality.** Require an operational failure signal plus malformed timestamp; exclude banners/decorative output. Aggregate repeated lines and cap per-source output.
6. **Align code with policy.** Compare retention settings in collector code against approved governance policy before declaring a canonical store ready.

## Minimal proof packet

```text
EVENT_ROWS=<n>
STABLE_ID_COVERAGE=<n>/<n>
DUPLICATE_KEY_RATE=<n>/<n>
RECAP_CLAIMS=<n>
RECAP_BYTES=<n>
CLI_COMPACT_OUTPUT=PASS
QUARANTINE_SIGNAL_RATIO=<n>/<n>
RUNTIME_IMPORT=<installed module path>
```

## Release rule

Do not release dashboard/API work that labels data "current" or "canonical" until stable-ID coverage and legacy separation are explicitly evidenced.