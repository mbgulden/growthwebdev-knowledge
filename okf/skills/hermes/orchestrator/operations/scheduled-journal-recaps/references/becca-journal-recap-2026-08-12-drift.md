# Becca Journal Recap — 2026-08-12 Drift Session

Session-specific detail for the 08-12 Becca Journal Recap cron. The fifth consecutive drift event of the same shape (skip-skill + inline-verifier instead of canonical script). Two new failure modes on top of the recurring pattern. Reference index: fifth bullet in the SKILL.md Pitfalls section ("Drift reinforcement 2026-08-12").

## What happened, in order

1. **FIRST-REPLY REQUIREMENT** asked the agent to read `~/work/next-step-becca/state/current.json` to surface `current_state`, `next_action`, `in_flight`, `pending_decisions_for_human`. The `next-step-becca` repo does not have a `state/` directory — that pattern lives in Prismatic Engine, not here. The phantom-state-file trap fired.

2. The agent confirmed the state file did not exist at the canonical path (`/home/ubuntu/work/next-step-becca/state/current.json`) using `ls -la` and `read_file`. Cost: ~2 tool calls of attention that would otherwise have been the skill-first call.

3. The agent did **not** call `skill_view('scheduled-journal-recaps')` first. Read the inbox directly. Read the template. Skipped the canonical-verifier copy step.

4. Inbox at task start: 6 snapshots (00:00-05:00 UTC), 1 change event (01:00 UTC flagging `data/next_step.db`). All other snapshots: "No new files since last snapshot."

5. Wrote the recap with `seven` typo'd as `six` — recap claimed 6 snapshots and 1 change event. Compressed format retained, consistent with the 8-day continuity thread. Symlink repointed to `2026/08/12.md`.

6. **First verification nudge fired.** The agent wrote a bash heredoc verifier at `/tmp/hermes-verify-*.sh` (NOT the canonical `verify_becca_recap.py`). 20 assertions, all PASS. Mistake: the script's filename prefix is the audit hook's signal, not its assertion contents.

7. **Between the first nudge and the second verification, the snapshotter appended a 7th snapshot at 06:00:21Z flagging `journals/2026/08/12.md` as a new file.** The inbox now carried 7 snapshots and 2 change events. The recap text was factually stale.

8. **Second verification nudge fired.** The agent wrote *another* bash heredoc verifier — this time catching the 7-snapshot discrepancy. Two of the 22 assertions failed: `inbox_has_7_snapshots` and `06:00_block_flags_journal_file`. The failures were a verifier-awk syntax mistake (`awk '/p1/ && /p2/'` is not valid awk), not a recap bug.

9. The agent rewrote the recap to reflect the 7-snapshot, 2-change-event reality (classifying the second change as self-referential generated-artifact activity). Patched the awk syntax in the verifier. Re-ran: 26/26 PASS.

10. **Third verification nudge fired.** The recap content was correct, the inline verifier passed, but the audit hook still triggered because the canonical verifier had never been copied. The cycle would have continued if the agent had not stopped.

## Lessons specific to this session

### Lesson 1: read-skew is real and the canonical verifier is the only thing that catches it

When the inbox is read at task start and the recap is written with that snapshot count, but by the verification-time the snapshotter has appended another snapshot, the recap's claim is internally consistent with the recap's text. An inline verifier comparing the recap to itself will pass. The canonical `verify_becca_recap.py` re-reads the inbox at runtime and asserts `inbox_snapshot_count >= recap's claim`, which catches the skew.

Operationally: the recap went from "6 snapshots, 1 change event" at write time to "7 snapshots, 2 change events" by verification time. The recap content was factually wrong for ~3 minutes until the agent rewrote it. The fix is unconditional: copy the canonical verifier, never write an inline verifier for the snapshot-count check.

### Lesson 2: awk patterns are not booleans

`awk '/p1/ && /p2/{action}'` is a syntax error because `/regex/` is a pattern expression, not a boolean operand. The error message is unhelpful (`awk: cmd. line:1: /p1/ && /p2/{...} / syntax error` with the caret under the trailing slash). The workaround is either:

- Two patterns, no `&&`: `awk '/p1/{f=1} /p2/{f=0}'` (awk evaluates each pattern against the current line independently).
- State flag with explicit boolean: `awk 'BEGIN{f=0} /p1/{f=1; next} /p2/{f=0} f && /p3/{action}'` — here `f` is a numeric variable and `/p3/` evaluates to 1 or 0 in numeric context, so the `&&` is between two numbers.

The better answer is to use pure Python: `for line in file: if re.search(p1, line): f=1; ...` sidesteps awk entirely.

### Lesson 3: the FIRST-REPLY REQUIREMENT trap is a 5-second detour, not a deep investigation

When the FIRST-REPLY REQUIREMENT references a state file that does not exist, the fix is one fast existence check (`ls -la`, `os.path.exists`, or `read_file` with a 404-equivalent message), not a full investigation. The trap is documented in the skill itself (phantom-state-file trap), and the documented response is "proceed with the actual job using the live filesystem state rather than the FIRST-REPLY REQUIREMENT's expected shape." The trap's hidden cost is the cognitive overhead — the agent spends 2-3 tool calls confirming the file is missing, which is enough to break the skill-first precondition if the agent is not actively defending it.

### Lesson 4: the audit hook is verifier-provenance-sensitive, not assertion-content-sensitive

The hook greps changed paths for the `hermes-verify-` prefix and matches on the filename. It then runs its own check matrix against the artifact. A bash heredoc verifier with 20-30 custom assertions does not satisfy the hook because the filename prefix alone is what the hook looks for, regardless of what the script does. The canonical `verify_becca_recap.py` satisfies the hook because the script is known to the hook and its check matrix is what the hook expects.

This is the fifth day of the same drift. The previous reinforcements (08-07, 08-08, 08-09, 08-11) added bullets to the pitfalls list. That hasn't changed behavior. The next escalation is a hard numbered step in the standard workflow, not another bullet.

## What the recap looked like at each stage

### First draft (incorrect, 6 snapshots / 1 change event)

```
**Memo:** Eighth consecutive quiet day. Inbox arrived as six hourly snapshots
between 00:00 and 05:00 UTC. Five of the six reported "No new files since last
snapshot." One change event: 01:00 UTC `data/next_step.db`. Compressed format
retained per 2026-08-11's conditional.
```

### Final draft (correct, 7 snapshots / 2 change events)

```
**Memo:** Eighth consecutive quiet day. Inbox arrived as seven hourly snapshots
between 00:00 and 06:00 UTC. Six of the seven reported "No new files since last
snapshot." Two change events: 01:00 UTC `data/next_step.db` (classified as
routine internal state) and 06:00 UTC `journals/2026/08/12.md` (classified as
self-referential, the snapshot clock catching its own tail). Compressed format
retained.
```

The difference: one snapshot, one change event, one bullet distinction (internal vs self-referential) — three lines. The verifier caught the discrepancy; the recap was rewritten to match the actual inbox.

## File refs

- Canonical verifier: `~/.hermes/profiles/orchestrator/skills/operations/scheduled-journal-recaps/scripts/verify_becca_recap.py`
- Becca recap root: `/home/ubuntu/work/next-step-becca/journals/`
- Inbox for 2026-08-12: `/home/ubuntu/work/next-step-becca/journals/inbox/2026-08-12.md`
- Final recap: `/home/ubuntu/work/next-step-becca/journals/2026/08/12.md`
- Continuity thread: `journals/2026/08/05.md` through `2026/08/12.md` — eight quiet days.
