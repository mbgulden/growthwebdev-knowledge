# Structured Report Catalogue — Multi-Report Series Pattern

## When to Use

When creating 3+ related SEO/strategy reports for a single site that:
- Have cross-dependencies (report B references report A)
- Share common data sources (Ubersuggest, GA4, GSC)
- Should be referenceable by future agents
- Need consistent deliverable organization

## Directory Structure Template

```
<project-site>/_seo/
├── _index.md                         ← Catalogue root (THIS FILE)
├── consolidated-baseline.md           ← Technical baseline (if exists)
├── <latest-sweep>-YYYY-MM-DD.md       ← Latest Ubersuggest/audit data
│
├── reports/                           ← Strategy reports (one per initiative)
│   ├── NN-initiative-name/            ← NN = sequence number
│   │   ├── plan-YYYY-MM-DD.md         ← Implementation plan
│   │   ├── <report-name>-YYYY-MM-DD.md← Main deliverable(s)
│   │   ├── summary-YYYY-MM-DD.md      ← Executive summary (1 page)
│   │   ├── walkthrough-YYYY-MM-DD.md  ← Execution log
│   │   └── ...                        ← Additional topic-specific files
│   └── NN-other-initiative/
│
├── data/                              ← Raw data by source
│   ├── ubersuggest/
│   ├── google-analytics/
│   └── search-console/
│
├── reference/                         ← Methodology docs, templates
├── images/                            ← Report visuals
├── scripts/                           ← Reusable analysis scripts
└── raw/                               ← Unprocessed tool outputs
```

## Report Naming Convention

| File Type | Pattern | Example |
|-----------|---------|---------|
| Full report | `<topic>-YYYY-MM-DD.md` | `topical-authority-2026-06-11.md` |
| Plan | `plan-YYYY-MM-DD.md` | `plan-2026-06-11.md` |
| Summary | `summary-YYYY-MM-DD.md` | `summary-2026-06-11.md` |
| Walkthrough | `walkthrough-YYYY-MM-DD.md` | `walkthrough-2026-06-11.md` |
| Data pull | `<source>_<domain>_<date>_<type>.json` | `ubersuggest_activeoahutours_20260611_domain_keywords.json` |

## Index File Requirements

Every `_seo/` directory root MUST have an `_index.md` containing:

1. **Purpose** — Why this directory exists
2. **Directory structure** — A tree diagram
3. **Naming conventions** — How files are named
4. **Dependency chain** — Which reports build on which
5. **Status table** — Current state of each initiative (Queued/In Progress/Done)
6. **Required context note** — What future agents should check before starting new work

## Linear Issue Structure (For Multi-Issue Series)

Each issue in a series must follow the same template:

```
## Goal
Single clear objective.

## Research Context
What to read first (other reports in _seo/), what fresh data to pull (Ubersuggest, GA4, GSC), cross-references to prior issues.

## Deliverables
Each deliverable as a bullet with path relative to _seo/reports/NN-initiative/:
1. plan-YYYY-MM-DD.md — methodology and approach
2. <topic-specific>-YYYY-MM-DD.md — main analysis
3. [additional topic files as needed]
4. summary-YYYY-MM-DD.md
5. walkthrough-YYYY-MM-DD.md

## Critical Rules
Any constraints, non-negotiable requirements, or pitfalls.
```

## The "Questions Audit" Meta-Pattern

A special type of SEO report that surfaces QUESTIONS rather than answers. Use when:

- The site has accumulated enough reports that you need a strategic review
- You need to identify what the business owner SHOULD be asking but hasn't
- You want to generate backlog items for future work

### Structure

1. **Ranking Questions** — Technical SEO, content gaps, authority gaps, competitive gaps
2. **Cashflow Questions** — Conversion, pricing, upsell, retention
3. **Guest Value Questions** — Information availability, trust signals, logistics, post-booking
4. **Authority & Authenticity Questions** — Local expertise, cultural respect, voice consistency
5. **Data Gap Questions** — What we don't know but should
6. **Master Question List** — Single consolidated priority-ordered list

### Rules
- DO NOT answer the questions — identify them
- Each question must be specific and actionable
- Each question must trace to one of the 4 outcomes: ranking, cashflow, guest value, or authenticity
- Questions should be organized so they can be turned into future Linear tasks
