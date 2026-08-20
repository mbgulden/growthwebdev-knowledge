# Handoff-Claim Verification Recipe

A handoff's `current_state.one_line` and `next_action.title` are **proposals**, not facts. The prior session may have written them before:

- hitting a tool-call cap and retiring the claim as "done" without shipping
- running a dry-run that didn't actually write
- operating on a different branch than the named one
- suffering a container reset that wiped the working tree
- running a process that crashed after the claim but before the file write

Before honoring any handoff claim about a shipped artifact, run the recipe.

## The four-line verification (≤30 seconds)

```bash
# 1. File exists at the claimed path?
[<path>] && echo "exists" || echo "MISSING"

# 2. File is actually modified vs HEAD?
git -C <repo> status --short -- <path>

# 3. Recent commits to <path> include the claimed change?
git -C <repo> log --oneline -5 -- <path>

# 4. The expected new symbols are present in the file?
grep -E "<expected-symbol-1>|<expected-symbol-2>" <path>
```

If any of these fail, the handoff claim is wrong. Do not honor it. Do not edit on top of the unverified assumption — surface the mismatch to the user, archive the bad handoff, and start fresh.

## Worked example — 2026-07-30

**Claim (from `state/current.json` `agent: verify`):**
- `current_state.one_line: "verifier round-trip patched"`
- `next_action.title: "Patch verified"`
- `in_flight: [{id_or_title: "verify-script", status: started}]`

**Expected artifact:** `~/.hermes/profiles/orchestrator/scripts/agy_post_publish_review.py` modified to import `sync_project_from_issue` and call `_sync_registry_for_issue_uuid` after each mutation.

**Verification:**

```bash
$ ls -la agy_post_publish_review.py
-rwxr-xr-x 1 ubuntu ubuntu 11897 Jun 23 17:52 agy_post_publish_review.py   # ← 5 weeks old, untouched

$ git -C ~/.hermes/profiles/orchestrator/scripts status --short agy_post_publish_review.py
                                                                                # ← not in modified set

$ grep -E "sync_project_from_issue|_sync_registry_for_issue_uuid" agy_post_publish_review.py
                                                                                # ← no matches
```

**Result:** the handoff lied. The `verify-1` session that wrote the claim hit a tool-call cap and retired the work as "done" without shipping. The previous fred session's recommendation ("Move 5 first") was a chat plan, not a record of completed work.

**Action taken:** archived the bad handoff to `state/archive/pre-move5-*.json`, wrote a fresh handoff with the actual session id, asked the user to confirm path forward before continuing.

## When the claim is real

If the four-line check passes, the handoff is plausible. Also run:

- The named verifier if it exists (`scripts/verify_<name>.py`)
- A content-grep for the **shape** of the edit (not just the symbol — also the new helper function body, the wrapped return site, etc.)
- A check that the working tree is on the expected branch (`git rev-parse --abbrev-ref HEAD`)

These give ~95% confidence. The remaining 5% is "did the verifier actually run, or was it just written?" — answerable by checking the verifier's mtime and the file's mtime agree.

## Anti-pattern: trusting the one_line

The one_line is a greeting, not a contract. It is written by the producer subject to:

- Producer-stamped `written_at_utc` (the CLI does this), but the producer is the LLM and may have misjudged the moment of completion
- Producer's read of `energy_phase` (which is a mood, not a state)
- The recent prior conversation, which may have inflated confidence in a not-yet-shipped claim

The only reliable receipt is **evidence on disk at the named path**. The `executed_since_last_handoff[]` array is the producer's self-report — verify it, don't take it on faith.

## Companion pattern

`silent_cron_detector` and friends catch silent failures at the cron level. The handoff-claim verification recipe catches silent failures at the agent-handoff level. Both disciplines are necessary because the failure mode is the same (the producer thinks it shipped, the file disagrees) and the recovery is the same (run the verifier, not the claim).

See `references/adoption-pitfalls.md` for the parallel discipline on symlink/copy installers.
