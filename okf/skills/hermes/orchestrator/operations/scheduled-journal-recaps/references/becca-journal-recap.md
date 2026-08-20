# Becca Journal Recap Notes

## Job shape
- Inbox: `~/work/next-step-becca/journals/inbox/YYYY-MM-DD.md`
- Template: `~/work/next-step-becca/journals/template.md`
- Output: `~/work/next-step-becca/journals/YYYY/MM/DD.md`
- Latest symlink: `~/work/next-step-becca/journals/latest.md` pointing to the new recap, preferably as a relative path like `YYYY/MM/DD.md`.

## Voice and lens
Becca is a 6/2 Splenic Projector. Keep the Human Design framing light and useful:
- identify the signal in the noise,
- avoid forcing action when the inbox is quiet,
- name integration/rest when that is the honest read,
- do not add invented transit or chart mechanics unless computed elsewhere.

## Recap synthesis from sparse snapshots
For hourly snapshot inboxes:
- Treat repeated “No new files since last snapshot” entries as system stability, not work completed.
- Treat changed paths as the meaningful signals.
- If a database file changed but details are not visible from the inbox, cite the path and make review a follow-up rather than inventing the contents.
- Include captured snapshot timestamps under Sources and links when they are the main available evidence.

## Self-referential snapshot: the recap writes itself into the inbox
The snapshot cron (this job, running from the `fred` Hermes profile) runs hourly on the inbox directory. Because the recap is written into the same directory tree the snapshotter watches, the next hourly snapshot WILL detect the recap file itself as a “change.” Concretely, the inbox snapshot entry will read:

```
## Snapshot YYYY-MM-DDTHH:00:00Z
### Changes detected
- `/home/ubuntu/.hermes/profiles/fred/home/work/next-step-becca/journals/YYYY/MM/DD.md`
```

Recipe for handling this:

1. **Don't ignore it.** The snapshotter is doing its job — the recap truly was a new file in the watched tree. If you write the recap and then verify before the next snapshot fires, you'll see the inbox end before the self-detection; if you verify after, you'll see it. Both are valid observation windows.
2. **Don't claim a clean inbox.** Once the self-detection lands, the inbox is no longer “no changes today.” Reframe the recap honestly: “the only change observed was the recap itself” or equivalent.
3. **Patch the recap.** Update the memo, Work completed, and Sources/links to explicitly note:
   - the inbox window extended one more hour (e.g. `00:00 → 06:00 UTC` not `00:00 → 05:00 UTC`),
   - the snapshot timestamp that detected the self-change (e.g. `YYYY-MM-DDTHH:00:00Z`),
   - the observed artifact path (which will be the `fred`-profile-home expanded path, not the canonical `/home/ubuntu/work/...` path — they're the same file via the profile-home symlink).
4. **Re-run the verifier.** A verifier that counts snapshots or asserts an exact inbox window will fail. Update its assertions (e.g. `>= 6` snapshots rather than `== 6`) and re-run.
5. **Frame for Becca.** This is a 6/2 Projector moment worth naming plainly: the day's only observed change is the journal writing about the day. The 6-line role observes before acting; here the observation is its own action. Honor the quiet, log the change, do not invent more.

## Cross-profile path note
The recap cron runs from the `fred` Hermes profile, so the snapshotter sees the recap under `/home/ubuntu/.hermes/profiles/fred/home/work/next-step-becca/journals/YYYY/MM/DD.md`. The canonical path that other profiles (and humans) use is `/home/ubuntu/work/next-step-becca/journals/YYYY/MM/DD.md`. They resolve to the same file via the profile-home symlink. When the recap cites the detected artifact path in Sources and links, prefer the canonical path (`/home/ubuntu/work/...`) for consistency with the rest of the recap, and add a brief note that the snapshotter observed it via the `fred` profile-home expanded form.

## Session drift — 2026-08-07 Becca Journal Recap (skip-skill pattern)

Concrete drift on 2026-08-07, captured here so the next session doesn't repeat it:

- The cron prompt for Becca Journal Recap fired at 06:00 UTC. The session opened with the FIRST-REPLY REQUIREMENT state dump (one-line + next-action + in-flight + pending-decisions), proceeded to `date -u`, read the inbox, read the template, wrote the recap, updated the symlink — and **never called `skill_view('scheduled-journal-recaps')`**. The skill ships a canonical `scripts/verify_becca_recap.py` that was one `cp` away and was never consulted.
- Verification was rolled inline: two `/tmp/hermes-verify-becca-journal-2026-08-07*.py` scripts were written with `write_file`, run with `terminal`, then `rm`'d in a second `terminal` call. Both ran 6 inline checks (file exists, UTF-8 valid, title + 5 template sections, symlink target, byte-equal content, continuity reference to yesterday's journal). Both passed.
- The workspace then **fired the verification nudge twice** — once after the recap edit (legit), once after the first verifier script was `rm`'d (false positive, but the workspace lists the deleted-by-current-turn file as a changed path). The second nudge was answered by writing a fresh re-run script.
- The recap text missed checks the canonical verifier performs and the inline script never did:
  - **Full-ISO per-timestamp fidelity** for all 6 inbox snapshots. The recap quoted `00:00..05:00 UTC` in ranges instead of each `YYYY-MM-DDTHH:MM:SSZ` individually, and was not checked against the canonical verifier's per-timestamp assertion.
  - **Inbox path string** cited in the recap (`journals/inbox/2026-08-07.md`) was not asserted by the inline script.
  - The recap also failed the **self-referential snapshot** recipe in this file (above): the snapshot cron detects the recap as a change at the 06:00 boundary, but the recap's "Sources and links" did not include that 06:00 detection because the session wrote and verified before the 06:00 inbox snapshot landed. Tomorrow's recap (08-08) will see the self-detection in `journals/inbox/2026-08-07.md` and should honor the recipe above (reframe the inbox as "the only change observed was the recap itself," cite the 06:00 self-detection, name this as a 6/2 Projector observation moment).
- Concrete corrections for the next session that opens a Becca Journal Recap cron prompt:
  1. **First tool call**: `skill_view(name='scheduled-journal-recaps')`. Not optional. Not conditional. The skill name is the loader hook; if it loads, follow it.
  2. **Last tool call before final response**: copy `scripts/verify_becca_recap.py` to `/tmp/hermes-verify-becca-YYYY-MM-DD.py`, run it, delete it inside the same Python script's `finally` (see the canonical recipe in this file's "Focused ad-hoc verifier example" section, below). Never `write_file` an inline heredoc verifier when the canonical script exists.
  3. **If you already wrote a heredoc verifier this turn and this skill is now loaded**: delete the heredoc, run the canonical recipe once, report the canonical recipe's exit code in the final response. Two verifiers in one turn is the audit red flag.
  4. **Self-referential snapshot**: re-read the inbox before the final response, not just at the start. If `06:00` (or later) has landed and detected the recap as a change, the recap text needs the reframing and the Sources-and-links update before the final verifier runs.

## Focused ad-hoc verifier example
Use a temporary `/tmp/hermes-verify-*.py` script created via `tempfile`, then delete it in `finally`. The verifier should assert:

- For repeated workspace “unverified” nudges after a local-only or `[SILENT]` cron result, run a **fresh** verifier after the nudge and report the new evidence instead of returning `[SILENT]` or referring back to prior verification.
- The final response to a verification nudge should include: verifier path, exit code, cleanup result, changed recap path, latest symlink target, and a concise list of checked behaviors. Label it **ad-hoc verification**, never “suite green,” unless a canonical suite actually ran.
- **First choice:** copy `scripts/verify_becca_recap.py` (from this skill) to `/tmp/hermes-verify-becca-YYYY-MM-DD.py` and run that. Do not type a fresh heredoc verifier when the canonical one is one `cp` away — see the “Ad-hoc verification pattern” section in SKILL.md.

```python
# Preferred recipe — delegate to the skill's canonical verifier.
import shutil, subprocess, pathlib
src = pathlib.Path("~/.hermes/profiles/orchestrator/skills/operations/scheduled-journal-recaps/scripts/verify_becca_recap.py").expanduser()
dst = pathlib.Path("/tmp/hermes-verify-becca-YYYY-MM-DD.py")  # filename hooks the audit system
shutil.copyfile(src, dst)
try:
    r = subprocess.run(["python3", str(dst)], capture_output=True, text=True)
    print("exit:", r.returncode); print(r.stdout)
finally:
    dst.unlink(missing_ok=True)
```

```python
# Inline fallback only when you truly need a custom one-off verifier.
# Hardcode canonical paths — do NOT use ~/ or Path.home() (see HOME trap below).
from pathlib import Path

journal = Path('/home/ubuntu/work/next-step-becca/journals/YYYY/MM/DD.md')
latest = Path('/home/ubuntu/work/next-step-becca/journals/latest.md')
inbox = Path('/home/ubuntu/work/next-step-becca/journals/inbox/YYYY-MM-DD.md')
required = [
    '# Daily Journal — YYYY-MM-DD',
    '**Memo:**',
    '## Work completed',
    '## Decisions made',
    '## Sources and links',
    '## Blockers',
    '## Follow-ups',
]
text = journal.read_text(encoding='utf-8')
missing = [item for item in required if item not in text]
assert not missing, missing
assert str(inbox) in text
assert latest.is_symlink()
# Name check, not .resolve() string check — see Symlink .resolve() pitfall in SKILL.md.
assert pathlib.Path(os.readlink(latest)).name == journal.name
```
(Plus the additional imports `os` and `pathlib` at the top of the file.)

**Why these paths are hardcoded (not `~/...` or `Path.home() / ...`):** when this cron runs from the `fred` Hermes profile, `HOME` inside any `execute_code`-spawned Python is `/home/ubuntu/.hermes/profiles/fred/home`. `os.path.expanduser("~")` and `Path.home()` resolve to that profile-home. The recap file, however, lives at the canonical `/home/ubuntu/work/next-step-becca/...` path. A verifier that builds paths via `Path.home() / "work" / "next-step-becca" / ...` will silently point at a directory that does not exist, and checks against `str(inbox)` (where the inbox path is the canonical form printed in the recap) will FAIL even when the file is there. If you prefer a relative build, resolve once with the shell: `canonical = subprocess.check_output(['readlink', '-f', os.path.expanduser('~/work/next-step-becca/journals')]).decode().strip()` and use that as the verifier's root.

**Why the symlink check uses `os.readlink(...).name`, not `latest.resolve() == journal.resolve()`:** on this filesystem the recap file is reachable at both `/home/ubuntu/.hermes/profiles/fred/home/work/next-step-becca/journals/YYYY/MM/DD.md` (profile-home expanded) and `/home/ubuntu/work/next-step-becca/journals/YYYY/MM/DD.md` (canonical) — same inode, two path strings. `Path.resolve()` returns whichever path the symlink chain traversed and may not equal `journal.resolve()` even when both point to the same file. Compare by basename + parent: `pathlib.Path(os.readlink(latest)).name == journal.name`, or by relative target: `os.readlink(latest) == "YYYY/MM/DD.md"`.

Report this as “ad-hoc verification passed,” not “tests passed,” unless a canonical suite also ran.
