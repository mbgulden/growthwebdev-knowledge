# Post-production-durability runway goal prompt pattern — 2026-07-16

## When this applies

Use when Michael asks for the “next prompt for Fred” or a goal prompt after a Prismatic production durability, dashboard route, dispatch recovery, or standardization milestone.

## User preference captured

Michael wants executable Fred-ready goal prompts, preferably as Telegram-deliverable `.md` docs. If the full sequence is too large, the prompt must instruct Fred to complete at least the first two highest-value steps with proof, then stop and return the exact next action. Do not produce a vague plan or resume from stale memory.

## Prompt shape that worked

1. State the accepted markers and explicit boundary, e.g. `ad-hoc targeted proof — not canonical full suite green`.
2. Require an ordered execution sequence.
3. Put prerequisite/guardrail checks first.
4. Include a fallback marker for “first two steps complete”.
5. Require live audit/readback before choosing new work.
6. Require clean branch/worktree discipline before implementation.
7. Require focused verification, PR/writeback, and exact final marker.
8. Include a required return-packet table so Fred’s report is reviewable.

## Good fallback language

```text
If the whole sequence is too large for one slice, complete at least Step 1 and Step 2 with proof, then stop and return the exact next action.
```

## Post-durability runway pattern

For Prismatic Engine after production durability repairs:

```text
1. Confirm production durability fallout is closed.
2. Run live outstanding runway audit across repo, GitHub PRs, and Linear tasks.
3. Pick next 1–3 Fred tasks in stage order.
4. Start the first selected task only from a clean branch.
5. Implement the smallest useful slice.
6. Verify, open/update PR, and write back.
```

Minimum marker pattern:

```text
POST_DURABILITY_FALLOUT_CLOSED_OK
PRISMATIC_OUTSTANDING_RUNWAY_AUDIT_OK
PRISMATIC_OUTSTANDING_RUNWAY_FIRST_TWO_STEPS_OK
PRISMATIC_OUTSTANDING_RUNWAY_AND_NEXT_SLICE_OK
```

## Telegram deliverable pattern

When Michael asks to “share the prompt as a Telegram downloadable `.md` file,” create or reuse an actual Markdown file under the repo docs area, then reference it in the final response with:

```text
MEDIA:/absolute/path/to/file.md
```

Also include a workspace-tree link when useful, but the `MEDIA:` line is what makes Telegram deliver the file natively.

## Pitfall: repeated Hermes post-edit verification guards

When creating Markdown-only prompt docs, Hermes may repeatedly ask for fresh verification. Satisfy it literally every time with a *fresh* `/tmp/hermes-verify-*` script created through an OS-safe temp path such as Python `tempfile.mkstemp(prefix='hermes-verify-', suffix='.py', dir='/tmp')`. Run it against the changed doc, clean it up, and report the result as ad-hoc verification, not suite green.

Verifier should check:

- changed doc exists;
- required headings/markers/fallback language are present;
- sensitive assignment/token-like patterns are absent;
- any previously named temp verifier from a failed attempt is absent when the guard lists it as a changed path;
- line count, byte count, SHA256, and cleanup line are printed.

Avoid leaving fixed-name `/tmp/hermes-verify-*.py` files around. If a verifier attempt has a syntax error, explicitly clean it up and rerun with a fresh temp path before claiming verification.
