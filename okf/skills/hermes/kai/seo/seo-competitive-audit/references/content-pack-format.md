# Content Pack Format — Writer Handoff Document

After audit data + site scaffolding are ready, compile a self-contained
document the writer (e.g., Ella) can work from without needing to cross-reference
multiple files. One document per batch of tasks.

## Template Structure

---

# 🎯 [Project Name] — Content Pack: [Batch Name]
**From Kai** | [Date]
**For tasks:** [List of task IDs]

---

## Section 1: Current Priority Tasks (Numbered)

For each task:

### Task 1: [Action Verb] [Page Name]
**Target keyword:** `[keyword]` ([volume] vol, #[position])

**Current state:** [What exists already, if anything]
- [URL on site]
- [Current ranking, traffic]
- [What it does well / what's missing]

**What to write/add:**
- [Specific section or content to add]
- [Another specific change]
- [Another change]

**Who to outrank:**
- #1: [competitor] (DA XX) — [what they do that works]
- #2: [competitor] (DA XX) — [why they're beatable]

**Expected impact:** +[N] clicks/month from moving #[X] → #[Y]

---

## Section 2: SERP Data Per Target Keyword

For each keyword targeted in this batch:

### "keyword" (volume vol) — We're #X

| Pos | Site | DA | Clicks | Notes |
|:---:|------|:--:|:------:|-------|
| 1 | domain.com | XX | X,XXX | |
| **X** | **us** ✅ | **XX** | **X** | Current |
| 5 | domain.com | XX | X | Beatable — lower DA |

**SERP Features:** [list any: AI Overview, Local Pack, PAA, etc.]
**Squeeze:** [Specific action to move up]

---

## Section 3: Pre-Written AEO Snippet Blocks

These target Google's featured snippet (Position 0). Drop them into the
page as the first content block after the H1.

### For [Page/Topic]:
> **[Question or short header]**
>
> [50-80 word answer that directly addresses the searcher's intent.
> Include a specific data point or insider tip. End with a clear,
> definitive statement.]

---

## Section 4: FAQ Schema JSON-LD Blocks

Copy-paste ready. Inject before `</head>`.

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "...?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "..."
      }
    }
  ]
}
```

---

## Section 5: Quick Win Checklist

| Page | One Change | Effort | Expected Impact |
|------|-----------|:------:|:--------------:|
| /page-url/ | Add FAQ section | 15 min | +10% traffic |
| /other-page/ | Fix 404 link | 5 min | +N clicks recovered |

---

## Section 6: Site Architecture Reference

| # | Page Name | URL | Status | Keyword | Vol |
|:-:|-----------|:---:|:------:|:-------:|:---:|
| A1 | Tour name | /activities/.../ | ✅ Exists | kw | vol |
| A2 | Guide name | /guides/.../ | 🆕 New | kw | vol |

---

## Key Principles

- **Self-contained:** The writer should need exactly one document.
  Don't make them ping you for context.
- **Copy-paste ready:** AEO blocks and FAQ schema should be usable
  as-is. No missing brackets or placeholder content.
- **SERP data is the competitive brief.** Every keyword entry should
  answer "who beats us and why."
- **Expected impact is directional.** Use the `clicks` field from
  SERP entries above and below your position. Be conservative
  (clicks are model estimates).
- **Blocker flagging:** If a task requires Michael's interview
  recording, flag it clearly. Don't let placeholder content get
  mistaken for final.
