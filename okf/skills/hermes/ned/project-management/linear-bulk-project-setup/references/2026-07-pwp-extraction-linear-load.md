# PWP extraction prompt → Linear execution tree (2026-07-23)

## When this reference applies
Use when Michael forwards a Markdown implementation/extraction prompt and wants it loaded into Linear as a full epic/task tree for Ned to execute systematically.

## What mattered
- The source prompt was a forwarded `.md` document, not just chat prose.
- The issue tree needed to preserve hard boundaries from the prompt itself:
  - fixed source repo and source SHA
  - target repo name
  - explicit non-goals / safety constraints
- Michael wanted the tasks tagged for Ned specifically so the tree could be worked in sequence later.

## Proven pattern
1. Read the forwarded document and extract a phase/task manifest first.
2. Create one umbrella epic, then per-phase epics, then child tasks.
3. Put the forwarded document name/path and fixed source SHA into every issue body.
4. Label every issue `agent:ned` plus domain/project labels (here: `plugin:pwp`, `prismatic-engine`).
5. Leave issues in `Todo` unless Michael explicitly says to begin execution now.
6. Do not bulk-apply `dispatch:ready` just because the tree is comprehensive.
7. Verify by reading the created issues back from Linear and checking:
   - counts
   - parent-child structure
   - labels
   - project assignment
   - state
   - presence of forwarded-doc context in descriptions

## Concrete result shape used
- 1 umbrella epic
- 5 phase epics
- 31 child tasks
- 37 total issues

## Useful implementation notes
- Exact-title dedupe is safer than relying on deprecated Linear search surfaces.
- A paginated `issues(first:, after:)` readback works for idempotent verification when title search is unreliable or deprecated.
- Duplicate project names may exist in Linear; verify the actual project ID/URL you attach work to, then read it back.

## Non-goal reminder
Creating the Linear tree is not proof the extraction work is done. It only stages the execution queue.