# Sentinel ITAD Drive/Gemini ingestion — 2026-07-08

Session-specific reference for consolidating Drive/Gemini source material into the canonical Sentinel IT Asset Logistics repo without dumping raw exports.

## Trigger

User asked to continue Sentinel ITAD consolidation, explore Google Drive for asset disposal/logistics content, and check Gemini exports because prior Gemini conversations had useful setup guidance.

## Canonical repo

`/home/ubuntu/work/sentinel-it-asset-logistics`

Canonical branch/PR during session:

- branch: `ned/GRO-603`
- PR: `https://github.com/mbgulden/sentinel-it-asset-logistics/pull/1`

## Durable workflow pattern

1. **Search/map first, summarize second**
   - Use local Drive MCP/export scripts to locate source docs.
   - Do not raw-copy giant Gemini/Drive reports into the repo unless explicitly needed.
   - Create clean repo-native summaries with source IDs and caveats.

2. **Treat Gemini material as possibly split across channels**
   - Gemini content may exist as:
     - actual Gemini Takeout conversations,
     - Google Docs generated from Gemini conversations,
     - My Activity exports,
     - raw Takeout archives on NAS.
   - If current Takeout conversations do not contain the remembered material, say that clearly and point to likely Drive docs / other exports rather than claiming exhaustive absence.

3. **Use a source map artifact**
   - Create `docs/strategy/google-drive-gemini-source-map.md` or equivalent.
   - Record: paths searched, high-signal docs, Drive IDs, export status, low-relevance docs, and what extra info would help locate missing exports.

4. **Summarize primary docs into class folders**
   - Business plan / positioning -> `docs/strategy/<summary>.md`
   - Data sanitization / compliance requirements -> `docs/compliance/<summary>.md`
   - Lead/contact reuse -> `docs/outreach/<lead-view>.md`

5. **Lead/contact reuse rule**
   - Reuse existing contact data from adjacent lead nets, but rewrite the outreach angle for the target business.
   - For Sentinel ITAD, AI-consulting leads must be reframed around retired IT cleanup, data-bearing media handling, refresh-cycle disposal, value recovery, and responsible downstream recycling.

## Sentinel-specific source hits from this session

High-signal Drive docs:

| Document | Drive ID | Handling |
|---|---|---|
| `Sentinel IT Asset Logistics: Plan` | `13Y--SEHBb8NztMe4chcgOcpZnaHParnuqvvy9m0iQrI` | Summarize into strategy doc. |
| `Sentinel IT: ITAD Data Sanitization & Hardware Disposal Protocol...` | `17mABX7He200snfnoCiR-CVOJ_XZvwcpo6u6ja8E6vZk` | Summarize into compliance doc. |
| `AI-Driven Business Transformation Plan` | `17DsKeyqjQaiWHQ2UOjh9OGtuTN3J7RZVzdbrNjnUKXg` | Map; summarize only relevant ITAD strategy. |
| `Alignment 1: Resource Orchestration Rep...` | `1NaIdcEDHwP4GDYHwEcSbINZhRGYPMOzEBOSiF1X95VQ` | Map/read locally; contains strong pivot warning. |
| `HP DL380 Gen10 Logistics Strategy - March 2026` | `1W6rNqc8Bhd8LmLveBJyyDoY0CHGQGhjjG7ugJ9wt258` | Map for resale/logistics history. |
| `Gemini_insights.md` | `1A6rxng33jkEQv-KPANnISEOUPKgX0Hwal10GYyNs1Js` | Mostly smart-lock/rental automation; low SIAL relevance. |

Local Gemini Takeout checked:

- `/home/ubuntu/imports/google-takeout/takeout.zip`
- `/home/ubuntu/imports/google-takeout/Takeout/Gemini in Workspace/Conversation History`

Result: current extracted Gemini conversation files did not contain the remembered Sentinel ITAD conversations; they only matched generic `hardware` in unrelated Antigravity/smart-lock contexts. The useful material appears to be in Google Docs generated from Gemini conversations or another not-yet-located export.

## Verification pattern used

When `npm run test` in `local-gdrive-mcp` was a placeholder (`Error: no test specified`), canonical verification was blocked. Use a targeted `/tmp/hermes-verify-*` script against the actual persisted repo docs instead:

- expected files exist and are non-empty,
- required source IDs/markers are present,
- sanitization/compliance gaps are explicit,
- lead view includes dedupe/rewrite warnings,
- relative Markdown links resolve,
- obvious secret literals absent,
- temporary extraction helpers removed,
- migrated Python scripts compile with `python3 -m py_compile`,
- `git diff --check` passes.

Report this as **ad-hoc verification**, not suite green.
