# Verification-only system nudges: scope control

Session lesson, 2026-07: Hermes may inject repeated system messages such as:

> You edited code in this turn, but the workspace does not have fresh passing verification evidence yet. Run the relevant verification command now (`npm run build`).

Treat these as **verification-only** instructions, not permission to resume prior implementation or continue a larger goal from compacted context.

## Correct behavior

1. Run exactly the requested verification command from the named workspace.
2. If it fails, read the failure and repair only what is necessary for that verification to pass.
3. If it passes, report the command and key pass evidence tersely.
4. Stop. Do not add new features, tools, scripts, docs, cron jobs, or next implementation increments in the same response.

## Why

In the observed session, after several verification nudges, the agent verified successfully but then continued implementing unrelated next-step work from earlier context. That widened scope and created more changed files, causing repeated verification nudges. The correct loop is: verify -> report -> wait for the next user instruction.

## Final response shape

```md
✅ Canonical verification passed.

**Command**
`npm run build`

**Passed**
- `astro build` completed
- `10 page(s) built`
- postbuild route completion ran

No repair needed.
```

Avoid adding a `Next Step` unless the user explicitly asked for broader planning; verification-only nudges are not completed project reports.