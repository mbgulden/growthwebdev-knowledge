# AGY/Jules context-pack follow-up prompt pattern — 2026-07-19

## Session lesson

After AGY and Jules CLI context-pack PRs landed, a previously generated Kai handoff still described those PRs as open/review-needed. The correct operator behavior was to re-query live PR state, notice both PRs were merged with CI green, and pivot the Kai prompt to the next workflow gate instead of recycling stale integration instructions.

## Durable pattern

For Prismatic agent CLI/context-pack follow-ups:

1. Live-query PR state and CI immediately before packaging the prompt or report.
2. If prerequisite PRs are still open, write a review/merge/rebase prompt.
3. If prerequisite PRs are merged, write the next-slice prompt.
4. For AGY/Jules context-pack work, the next narrow slice after merge is:

```text
AGY_COMPLETED_WORK_INTEGRATION_GATE_OK
```

5. Keep the slice bounded:

```text
completed-work packet ingestion
→ packet validation/classification
→ persisted/readable state
→ dashboard/API/Linear-ready summary
→ manual merge policy preserved
```

6. Explicitly non-claim:

```text
auto-merge
production deploy
canonical full-suite green
live bulk redispatch
uncontrolled always-on workers
clean PR create/update automation
PR verification gate automation
all-agent completion
```

## Prompt artifact guard

When Michael asks for a Telegram-downloadable `.md` prompt:

- write the prompt to `/tmp/<clear-name>.md`;
- create a `/tmp/hermes-verify-*` script that checks required markers, links, headings, and secret-like patterns;
- remove the verifier after running it;
- deliver with `MEDIA:/absolute/path.md`;
- include proof as ad-hoc targeted verification, not suite green.
