# PWP Theme Linear bulk creation — 2026-07-09

## Context

A PWP AI-first Astro theme master plan was converted into Linear work. The target tree was 10 phased epics and 53 child issues. Michael explicitly wanted all parts input/prioritized first, then he would initiate the build process.

## What worked

- Read the master plan and convert it to an expected manifest before creation.
- Use the GrowthWebDev team, Prismatic Engine project, `Todo` state, and existing labels such as `plugin:pwp`, `prismatic-engine`, `Feature`, `epic`, and agent labels.
- Create phase parents first, then child issues with `parentId`.
- Use exact-title lookup before creating to make reruns safe.
- Final proof queried Linear and asserted:
  - `TOTAL 63`,
  - `PARENTS 10`,
  - `CHILDREN 53`,
  - every phase 0–9 present,
  - expected child count per phase.

## Problems hit

### Duplicate labels

Linear rejected child creation when the input label list included duplicate IDs:

```text
Argument Validation Error: All labelIds's elements must be unique.
```

Fix: deduplicate label IDs before every `issueCreate`.

### Rate limit hidden under HTTP 400

Linear returned rate-limit failures as HTTP 400 with body content containing `RATELIMITED` and the 2500/hour limit. The HTTP status alone was misleading.

Fix: always read and log the response body for GraphQL HTTP errors.

### Automation race

Some early phase epics were moved/labeled by automation before normalization. Because Michael had not initiated build, the final cleanup needed to remove `dispatch:ready` and reset staging state.

Fix: after bulk creation, perform a fresh readback and normalization pass.

## Final proof shape

A good final proof should be shaped like:

```text
TOTAL: 63 issues
EPICS: 10 phased epics
CHILDREN: 53 child tasks
MISSING: none
```

Then provide a table of phase epic links.

## User-facing lesson

Do not send a triumphant completion message until the tree is fully created and verified. If rate-limited, say exactly what exists, what remains, and when/how the retry will run. Dry, boring honesty beats optimistic fiction. Every time.
