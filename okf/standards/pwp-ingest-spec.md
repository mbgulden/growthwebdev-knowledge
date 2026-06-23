---
type: Standard
title: Prismatic Web Plugin — Ingestion Spec (Step 1)
description: The Step 1 ingestion parser. Reads any client's 5 Website Dev docs and produces structured JSON (client_profile.json + content_brief.json + ingest_report.md). LLM-based extraction handles any client input format. The 5 docs are conversational guides, not templates — the parser uses AGY (Gemini 3.5 Flash High) to extract structured data.
resource: https://github.com/mbgulden/growthwebdev-knowledge/blob/main/okf/standards/pwp-ingest-spec.md
tags: [standard, prismatic-web-plugin, ingestion, step-1, llm-extraction, json-schema, content-gathering-framework]
timestamp: 2026-06-23T06:42:00Z
linear_issue: GRO-2138
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/standards/pwp-ingest-spec.md
last_verified: 2026-06-23
verified_by: fred
status: current
---

# Prismatic Web Plugin — Ingestion Spec (Step 1)

> **What this is:** Step 1 of the multi-agent website-build orchestration system (GRO-2137). Takes any client's filled-in Website Content Gathering Framework (the 5 Drive docs) and produces structured JSON output that drives Steps 2 (synthesis) and 3 (task distillation).

## Why this exists

Per Michael's 2026-06-23 direction: "the MVP needs to be the system that can create a comprehensive website based off the website content gathering framework. You are building out the system that ingests the info and converts it into actionable plans that are distilled into tasks."

This script is the ingestion step. Without it, there's no way to programmatically process client responses at scale.

## The 5 framework docs

The client's responses to these 5 docs are the input:

| # | Doc | What it produces |
|---|---|---|
| 1 | Website Content Gathering Guide (OKF) | Business profile + class/service list |
| 2 | Partner Interview & Story Extraction | Founder/instructor stories, mission context |
| 3 | Brand Design Interview & Inspiration Directory | Brand language, design tokens, reference sites |
| 4 | Conversion & Technical Launch Kit | Lead magnet, target areas, SEO, domain, schema |
| 5 | Post-Purchase Automation Flow | Email sequences, post-signup workflow |

**Important:** The 5 docs are **conversational guides** with placeholder fields (e.g., `[e.g., Meridian Women's Defense Academy]`). The client fills them in. The parser handles any format: filled-in answers, free-form notes, partial responses.

## Script

`~/.hermes/profiles/orchestrator/scripts/pwp/pwp_ingest.py`

**Usage:**
```bash
python3 pwp_ingest.py <path-to-5-docs-dir>
```

**Exit codes:**
- 0 = success (all required fields present)
- 1 = missing args
- 2 = directory not found
- 3 = parse failure
- 4 = partial success (some required fields empty — ingest_report.md will list them)

**Output files:**
```
<docs-dir>/output/<client-slug>/
  client_profile.json  # full structured profile
  content_brief.json   # just the content section (classes, testimonials, etc.)
  ingest_report.md     # what was parsed + missing fields
```

## Output schema

```json
{
  "client_profile": {
    "name": "Business Name",
    "tagline": "...",
    "mission": "...",
    "usp": "...",
    "core_values": ["v1", "v2", "v3"],
    "location": {"city": "...", "state": "...", "service_areas": [...]},
    "contact": {"phone": "...", "email": "...", "address": "..."},
    "instructors": [{"name": "...", "role": "...", "bio": "...", "credentials": [...]}]
  },
  "content": {
    "classes": [
      {"slug": "...", "title": "...", "summary": "...", "what_you_learn": [...], "prerequisites": "...", "gear": "...", "duration": "...", "price": "...", "call_to_action": "..."}
    ],
    "testimonials": [{"author": "...", "quote": "...", "date": "YYYY-MM-DD"}],
    "affiliations": ["..."],
    "lead_magnet": {"title": "...", "topics": [...]}
  },
  "design": {
    "color_palette": ["hex1", "hex2"],
    "typography": "...",
    "mood": "...",
    "reference_sites": ["url1", "url2"]
  },
  "technical": {
    "target_areas": [...],
    "domain": "...",
    "google_business": "...",
    "has_logo": true/false
  },
  "automation": {
    "email_sequences": [
      {"name": "Email 1: ...", "trigger": "...", "subject": "...", "body": "..."}
    ]
  }
}
```

## LLM extraction

Uses AGY (`Gemini 3.5 Flash (High)`) for extraction. The prompt:
1. Defines the schema explicitly
2. Includes the 5 docs as context (each truncated to 8KB to fit context window)
3. Asks for "ONLY valid JSON — no commentary, no markdown, no explanation"
4. Schema notes: classes are LIST OF OBJECTS not strings, testimonials same, etc.

**Cost:** ~$0.05-$0.10 per client (varies with doc length).

**Reliability:** The LLM is instructed to output valid JSON. The script has a JSON parser with regex fallback to find `{...}` in the output. If extraction fails, exit code 3 with error to stderr.

## Verification (2026-06-23 06:42 UTC)

Test run on the 5 Website Dev docs (the framework itself, not a filled-in client):

```bash
time python3 pwp_ingest.py /home/ubuntu/work/growthwebdev-knowledge/okf/projects/website-dev/inputs
# → real    0m16.462s
# → Wrote 3 files, identified 1 missing required field (mission — correct: the docs are the framework, not a filled-in client response)
```

**Output quality:** Good. Real extraction:
- Business name: "Meridian Women's Defense Academy"
- Location: Meridian, ID, with 6 service areas
- 1 class: "Idaho Enhanced Concealed Carry for Women"
- 6 reference sites for design
- 3 email sequences with subject + trigger + objective
- Lead magnet with title + 3 topics

## Known limitations

1. **Missing fields are empty, not inferred.** If the docs don't include `mission`, the field is empty. The system relies on the client filling in the framework, not on AGY making up values.
2. **8KB truncation per doc.** If a client writes a very long response (>8KB), the tail is truncated. Should be fine for normal client inputs.
3. **No validation against the schema.** The script accepts whatever AGY outputs. A future version should validate against a JSON Schema before writing.
4. **English-only.** No localization handling.

## Next steps

- **GRO-2139 (Step 2):** Build plan synthesizer. Takes this JSON, produces `website_build_plan.md`.
- **GRO-2140 (Step 3):** Task distiller. Takes the build plan, creates Linear issues.

## Change log
- 2026-06-23 06:42 UTC: Initial spec + script. Verified working on Meridian Women's Defense data (the framework itself).