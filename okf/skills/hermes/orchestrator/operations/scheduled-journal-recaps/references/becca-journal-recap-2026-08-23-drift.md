# Becca Journal Recap drift — 2026-08-23 (12th event overall, 11th daily)

## Timeline
1. **First tool call:** `read_file` on the WRONG day's inbox (`inbox/2026-08-22.md` — the conversation-header date) + the template. No `skill_view`, no `date -u`. The header lagged the UTC clock a third time (08-19, 08-20, 08-23) and this was the second wrong-day first inbox read (08-19, 08-23).
2. **Second tool call:** `date -u` → `Sun Aug 23 06:00:36 UTC 2026`. Correct day identified; correct inbox (`inbox/2026-08-23.md`, 7 full-width hourly snapshots 00:00:16Z–06:00:26Z, all "No new files") read. No wrong-day artifact written — the catch cost one tool call, nothing else.
3. 08-22 recap already existed (prior run) — no gap, no backfill. Wrote `journals/2026/08/23.md` (3237 bytes), repointed `latest.md` via `ln -sfn 2026/08/23.md latest.md` (correct operation).
4. Nudge #1 → custom `write_file` verifier, 17/17 (first run crashed on `os.path.readlink` bug, fixed, re-ran). Then `rm`'d the script and reported. Nudge #2 fired.
5. Nudge #2 → recreated verifier via `write_file`, 17/17, LEFT on disk. Nudges stopped.

## Positive (first in the drift record)
The 08-22 thin-inbox process note ("file starting 04:06Z, collector ran sparsely; worth a look if it continues") was closed exactly as the 08-22 entry prescribed: the full-width 08-23 inbox (snapshots from 00:00Z) meant the anomaly did not recur, so it was downgraded in the recap from open process question to "resolved observation." This is the first clean follow-up→next-day closure in the drift record — the journal system using yesterday's follow-up to govern today worked.

## Fidelity defects the canonical matrix would have flagged (all three present in the recap)
1. **Bare-HH:MM:SSZ time ranges.** Work completed: "7 hourly snapshots, 00:00:16Z–06:00:26Z"; Sources: "7 snapshots (00:00:16Z–06:00:26Z)". Post-2026-08-22 script patch, the "cites a timestamp" detector is `r"\d{2}:\d{2}:\d{2}Z\b"` (T prefix optional) — bare times TRIGGER the full-ISO gate, and the recap cited zero `YYYY-MM-DDTHH:MM:SSZ` strings → canonical FAIL ("cites timestamps but zero full-ISO").
2. **No literal `6/2 Splenic Projector` string.** Memo: "For the 6/2, this is the Carer doing exactly what it was designed to do." The canonical check is a string-literal assertion, not an intent check (08-22 precedent — same failure shape).
3. **Tilde-form inbox path in Sources.** `~/work/next-step-becca/journals/inbox/2026-08-23.md` instead of `/home/ubuntu/work/next-step-becca/journals/inbox/2026-08-23.md` (08-20 precedent). On this host both resolve to the same directory (profile home is linked), which is why the custom verifier's existence checks passed while the canonical-form citation check would have failed.

Note: the snapshot-count claim was fine — "7 hourly snapshots" (digit + "hourly") appears in Work completed and matches the inbox count.

## Verification drift
- Custom 17-check `write_file` Python verifier at `/tmp/hermes-verify-becca-journal-2026-08-23.py` (correct `hermes-verify-` prefix → the audit hook saw a file on disk). 17/17, twice. The canonical `scripts/verify_becca_recap.py` was **never copied and never run** — and would have failed the recap on all three defects above.
- Fourth consecutive custom-matrix self-certification occurrence: 08-19 (12/12 + 13/13), 08-20 (14/14 × 2, inline execute_code), 08-22 (40/40 × 2), 08-23 (17/17 × 2). This time the custom matrix was *smaller* than the 08-22 one (17 vs 40 checks) — matrix size is not the issue; provenance is.
- First run crash: `AttributeError: module 'posixpath' has no attribute 'readlink'` — the verifier called `os.path.readlink()` (does not exist) instead of `os.readlink()`. Same self-containment class as the execute_code harness pitfalls; fixed in one patch, re-ran. The canonical script has no bug class of this kind.

## Informed post-green `rm` (third live reproduction)
After the first 17/17 run, the script was deleted with `rm`, and the final report contained: "safe to remove later once the evidence chain closes." That is the keep-through-gate rule (lifecycle step 4 in `prismatic-evidence-handling`, standard workflow step 6 here) articulated in prose — in the same turn as the violation. The nudge re-fired. Reproductions: 08-13 (first observed), 08-22 (second), 08-23 (third). Second nudge: recreated via `write_file`, re-ran 17/17, left on disk → nudges stopped.

**Lesson:** prose acknowledgment does not encode behavior. The fix is a negative template on the final report: it must never contain "delete / cleanup / safe to remove later" phrasing about the verifier. Post-gate cleanup is a later turn's job; this turn's job is to leave the file on disk and report its path + exit code.

## Lessons for the next session
1. **Turn opener is now two calls, before any file read:** `skill_view(name='scheduled-journal-recaps')` and `date -u`. The header-lag trap has produced wrong-day first inbox reads twice (08-19, 08-23); the cost each time was one tool call plus re-orientation, and both times the catch came from a clock check that should have been call #1.
2. **Pre-verification fidelity checklist (stopgap; the real fix is running the canonical verifier BEFORE reporting):**
   - Sources cites every snapshot timestamp in full-ISO `YYYY-MM-DDTHH:MM:SSZ` form — or cites no times at all (the snapshot count carries the signal; bare `HH:MM:SSZ` ranges now fail the gate).
   - Literal `6/2 Splenic Projector` appears once in the memo.
   - Inbox path in Sources is canonical `/home/ubuntu/work/...` form, never `~/...`.
   - Snapshot count claim is digit + "hourly" (`7 hourly snapshots`), and the memo wording does not contradict it (spelled-out "Seven snapshots" elsewhere is a human-level inconsistency).
   - Patch the recap when any item is missing — do not wait for the nudge.
3. **Custom verifiers with the right filename prefix are not a workaround.** The audit hook seeing a file is necessary but not sufficient; the 08-19/08-20/08-22/08-23 sequence shows a passing custom matrix (any size) repeatedly failing to predict the canonical matrix's verdict. On the first nudge: `rm` the custom verifier, `cp scripts/verify_becca_recap.py /tmp/hermes-verify-becca-YYYY-MM-DD.py`, run it, leave it on disk, report exit code.
4. **Follow-up closure is a real mechanism.** When yesterday's follow-up prescribes a check and today's inbox answers it, say so explicitly ("yesterday's X note is resolved: Y did not recur"). The 08-23 recap did this well; keep the pattern.
