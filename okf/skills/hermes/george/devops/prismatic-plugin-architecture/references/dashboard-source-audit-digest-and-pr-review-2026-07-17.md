# Dashboard source-audit digest + PR review pattern (2026-07-17)

## Context

Michael asked for a branch/repo/worktree audit of stray Prismatic Engine dashboard/governance/work sources for Fred. A comprehensive 5k+ line source audit was useful as an appendix, but Michael correctly flagged that it was a huge blob and hard for Fred to execute from.

## Durable lesson

For dashboard reconnect/source-map work, produce two artifacts:

1. **Full audit appendix** — comprehensive ranked source inventory with branch/worktree/file details.
2. **Execution digest / cheat sheet** — short Fred-facing packet that collapses the blob into A/B/C/D buckets, a do-first sequence, exact commands, and red flags.

The digest should be the primary handoff. The full audit should be referenced only as the appendix.

## Recommended digest shape

```markdown
# Fred Dashboard Reconnect Cheat Sheet — Source Audit Digest

## Purpose
Small operator packet; full audit is appendix only.

## Fred’s do-first sequence
1. Do not merge/reset anything.
2. Use runtime/main and active branch as anchors.
3. Inspect dashboard sources first.
4. Mine governance/workflow sources second.
5. Ignore archives unless a named missing tab/adapter points there.

## Tiny rubric
| Label | Meaning | Fred action |
|---|---|---|
| A | likely dashboard preservation/integration source | inspect immediately |
| B | governance/workflow source | inspect after dashboard shell map |
| C | runtime/canonical anchor | diff against, do not overwrite |
| D | archive/cleanup source | fallback only |

## Bucketed sources

## Exact commands Fred can run

## Red flags

## Full audit pointer
```

## PR source-map review pattern

When Fred returns a doc-only source-map PR:

1. Verify PR metadata with `gh pr view <n> --json number,title,headRefName,baseRefName,state,isDraft,mergeable,url,statusCheckRollup,files,commits`.
2. Fetch the PR ref locally without checking it out.
3. Confirm changed files are doc-only if claimed.
4. Extract the source-map document to `/tmp` and inspect required sections/markers.
5. Independently verify the concrete claims that matter:
   - runtime/main dashboard/server anchor equality;
   - active unrelated branch left untouched;
   - named next source path exists;
   - named candidate files exist;
   - source worktree dirty/clean status matches the doc;
   - stale `/tmp/hermes-verify-*` paths are not embedded in committed docs.
6. Run a fresh tempfile-created `/tmp/hermes-verify-*` script and remove it afterward.
7. Report as ad-hoc targeted review, not canonical suite green.

## Language to preserve

- “High score means inspect first, not merge.”
- “Full audit is appendix; digest is execution packet.”
- “Do not replace the shell; mine named missing adapters/panels one at a time.”

## Pitfall

A huge comprehensive report can be technically correct but operationally weak. For Fred/Ned/AGY handoffs, legibility and next-action compression are part of the deliverable, not polish after the fact.
