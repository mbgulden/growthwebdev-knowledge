---
name: client-discovery-intelligence-repos
description: Turn client discovery recordings/transcripts into separated proprietary source vaults and derived intelligence/report repos, with evidence-backed nugget extraction and ad-hoc verification.
---

# Client Discovery Intelligence Repos

Use this when Michael asks to “listen to” client meeting recordings/transcripts, extract nuggets/pain points/opportunities, and organize the output into repos or durable artifacts. This class covers client discovery intelligence, proprietary-source separation, and report packaging — not app/tool implementation.

## Core principle

Keep **client proprietary source material** separate from **derived strategy/report artifacts** and separate again from any **generic reusable app/tool code**.

Default split:

1. **Source vault repo** — raw audio, raw transcript, exported docs, transcript chunks, source metadata.
2. **Reports/intelligence repo** — synthesized reports, pain-point inventory, opportunity map, specs, next actions.
3. **App/tool repo** — future reusable implementation only; use synthetic fixtures, never raw client source.

## Workflow

1. **Acquire source material**
   - Prefer authenticated Drive/MCP when working.
   - If Drive auth is unavailable but the user provided a share link, use the browser/public shared path and direct export/download URLs when accessible.
   - For Google Docs, direct text export often works with:
     `https://docs.google.com/document/d/<DOC_ID>/export?format=txt`
   - For Drive files, direct download often works with:
     `https://drive.google.com/uc?export=download&id=<FILE_ID>`

2. **Verify source metadata before synthesis**
   - Confirm files downloaded and identify their types.
   - For audio, capture duration/size when possible with `ffprobe` or equivalent.
   - For transcripts, capture character/word counts.
   - If the transcript exists, use it as the primary source and treat audio as raw evidence unless actual transcription/audio analysis is required.

3. **Create repo boundary first**
   - Put raw materials only in the source vault.
   - Put derived reports only in the reports repo.
   - Do not leave an intermediate mixed repo behind.
   - Add READMEs that explicitly state the boundary and where related repos live.

4. **Extract “nuggets” from pain points**
   - Look for the client’s own language, metaphors, numbers, and constraints.
   - Convert pain into product/strategy implications.
   - Preserve evidence-backed specificity without dumping raw transcript.
   - Separate acute operational pain from long-term platform opportunity.

5. **Recommended report set**
   - `01-executive-nuggets.md` — highest-value insights and thesis.
   - `02-pain-point-inventory.md` — evidence-backed pains, why they matter, opportunities.
   - `03-funnel-or-process-diagnosis.md` — current vs desired operating flow.
   - `04-output-spec.md` — concrete artifact spec, e.g. candidate card/report/dashboard.
   - `05-priority-map.md` — location/team/workstream priority map when applicable.
   - `06-implementation-model.md` — phased rollout and operating model.
   - `07-data-security-boundary.md` — repo/data/access separation and guardrails.
   - `08-next-actions.md` — one clean next slice with finish line.

6. **Commit and publish when safe**
   - Create private repos by default for client proprietary work.
   - Commit source vault and reports separately.
   - Push only after confirming no raw source is in the reports/app repo.

7. **Ad-hoc verification is mandatory when no canonical suite exists**
   - Create a focused temporary verifier under `/tmp` using a `hermes-verify-` filename prefix.
   - Check repo existence, expected files, clean git status, remote privacy/configuration when applicable, and source/report separation.
   - Run it, remove it when possible, and label the result as **ad-hoc verification**, not suite green.

## Report style for Michael

- Lead with status and clickable artifacts.
- Include a compact table of repos/files when useful.
- State verification evidence explicitly.
- Use one “Next step” tied to the golden path; do not dump a large menu.

## Pitfalls

- Do not mix raw client recordings/transcripts into a generic app repo.
- Do not claim you “listened” to audio if you only used the transcript; say transcript was used as primary source and audio was archived/verified.
- Do not treat a Drive auth failure as a durable tool rule. If a shared link is accessible, use direct export/download as a workaround and report the auth blocker plainly.
- Do not overbuild the app during intelligence extraction. Package the insight first, then propose the smallest prototype slice.
- Do not call a Markdown/report repo “suite green”; use ad-hoc verification language.

## References

- `references/north-care-memory-care-discovery.md` — example of applying this pattern to a memory-care operator discovery call.