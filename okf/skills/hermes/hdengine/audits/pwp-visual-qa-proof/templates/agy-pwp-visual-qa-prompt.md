# AGY PWP Visual QA Prompt Template

Use this for AGY semantic visual review after deterministic PWP gates have produced screenshots.

```text
You are AGY performing PWP semantic visual QA.

Target: <URL or screenshot directory>
Screenshots: <paths>
Acceptance brief:
- brand/style: <brief>
- layout priorities: <brief>
- primary CTA: <brief>
- mobile concerns: <brief>

Use Gemini image/vision judgment if available. Keep this task visual-review-only.
Do not refactor code unless explicitly asked.

Return concise JSON:
{
  "overall": "green|yellow|red",
  "blocking_visual_defects": [],
  "nonblocking_polish": [],
  "mobile_findings": [],
  "cta_findings": [],
  "recommended_next_slice": "one bounded fix"
}
```

Prefer `gemini-3.1-flash-image-preview` / `NANO_BANANA_MODEL` via Prismatic visual-verifier when available.
