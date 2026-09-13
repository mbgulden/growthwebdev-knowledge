# Live re-audit of handoff claims against current git state (Prismatic fleet)

**Trigger:** human asks "what do we still have to work on?" / "check in-progress projects against what's actually there" — i.e. `state/current.json` items are claims and the request is to re-derive them from durable state.

**Class:** read-only re-verification of every tracked item against CURRENT remote/checkout state, then a DELTA report (what changed vs the handoff) — never a re-presentation of the handoff itself.

## Why this class exists

Handoffs are written at turn end; origin/main, checkouts, and uncommitted files all move afterwards. A re-audit that trusts the handoff's own numbers re-derives nothing. 09-06 instance: the handoff said the PE main checkout had 2 dirty files; live `git status --porcelain` said 15. A "merged" claim is only true relative to the remote it merged into, and that remote moves. A "dead/vestigial reference" claim can only get WORSE (a vestige can be a latent bug) — and can also get BETTER (upstream may have already removed it).

## Recipe (all read-only)

1. **Fetch first, everywhere.** `git -C <repo> fetch origin --quiet` in every tracked checkout. Never compare against a stale local ref.
   - Caveat: some checkouts have no remote configured (`git remote -v` empty — the `okf` checkout on this host). `git fetch` exits 128 there. That is checkout configuration state, not a network failure; fall back to local-ref state and label it.
2. **Re-verify "merged" claims against CURRENT origin/main:**
   ```bash
   git merge-base --is-ancestor <merge-sha> origin/main && echo merged || echo NOT-ancestor
   git rev-list --count <merge-sha>..origin/main    # how far the base has moved since
   ```
   Object presence locally ≠ merged. Report the move count so the human knows the base advanced.
3. **Re-verify "dead/vestigial reference" claims — escalate before classifying:**
   ```bash
   git grep -n '<ref-symbol>' origin/main     # where is it referenced
   git grep -n 'def <fn>' origin/main         # is the target defined
   ```
   A dispatch dict mapping a key to a function defined NOWHERE on origin/main is a latent `NameError` on that dispatch path → re-label the item "fix", not "cleanup". Conversely, re-grep items the handoff calls dead — upstream may have removed them already, making the cleanup PR a no-op.
4. **Re-verify checkout state counts.** `git status --porcelain | wc -l` per tracked checkout; compare against the handoff number and report drift. Uncommitted files OLDER than the handoff (check `stat -c '%y'`) are new owner-needed items, not regressions.
5. **Report as a delta table:** per handoff item — unchanged / changed (new fact) / new item discovered / now moot. Close with the updated pending-decision list.

## Instance (2026-09-06, george)

- origin/main moved to `0a0f37c0` (+10 past AGY V0.2 squash `7de346e6`); `merge-base --is-ancestor` → still merged. ✓
- F-series: the `codex-cli` registry entry the handoff called dead was ALREADY gone from origin/main (upstream removed it) — a cleanup PR would be a no-op. But `prismatic/dispatcher.py:273` `"codex": launch_codex` with no `def launch_codex` on origin/main → latent `NameError` → item re-labeled "one-line fix", not "cleanup".
- PE main checkout: handoff claimed 2 dirty files; live porcelain = 15 (13 predate the handoff — new pending decision: owner/disposition).
- native-crons: 88 dirty (was 89 — rubric file resolved previous turn, confirmed by hash match to PE origin/main blob).
- okf: `git fetch` exit 128 → `git remote -v` empty; checkout has no remote configured. Local-ref state only.

## Tooling note: split large payloads when closing the audit out

The audit ends with a `state/current.json` update. If the model's tool input channel truncates large inline payloads (tells: your own tool-call echo comes back `…[truncated]`, or the call returns exit -1 / "1 lines output" with no real result), do NOT retry the same big payload — it truncates again. Split the work into many small calls, each well under ~1–2KB: for handoff updates, a sequence of short `execute_code` snippets that each `json.load` `current.json`, mutate exactly ONE field (one_line, then pending list, then written_at_utc), then `json.dump`; finish with one short read-back that loads the JSON and prints the mutated fields. Verified 09-06: three full-payload write attempts all truncated; three per-field mutations + one read-back all succeeded. Same discipline for big one-line terminal commands — short commands beat five chained subcommands in one oversized string.
