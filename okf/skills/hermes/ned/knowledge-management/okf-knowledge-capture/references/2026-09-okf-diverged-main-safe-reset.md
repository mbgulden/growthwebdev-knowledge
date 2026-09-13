# OKF diverged local main — safe reset with content rescue (2026-09-05)

Context: the OKF checkout's (`/home/ubuntu/work/growthwebdev-knowledge`) local `main`
was 8 commits ahead of `origin/main` (and 1 behind). The 8 local commits were 6
auto-regen skill mirrors + 2 hand-authored coach-portal doc commits. The reset was
approved on a recommendation that "all 8 are noise" — that was wrong; 2 carried
unique content origin lacked.

## What went wrong with the initial read

A blob-level comparison (`git diff origin/main <local-tip> -- okf/skills/`) flagged
~1500 files as "differing". That is meaningless for auto-regen files: the regen cron
rewrites mirrors on every run, so blobs differ by design. The only real question is:
**which local-only files are hand-authored, and does their content exist in origin
(or the live skill)?**

## Correct procedure (verified — nothing lost)

1. `git log origin/main..main --oneline` — enumerate the local-only commits (8).
2. Per commit, `git show --format= --name-only <sha>` — group files by commit;
   classify: `okf/skills/**` files under `auto-regen`-subjected commits = reproducible;
   anything else = suspect.
3. For each suspect file: `git diff origin/main <local-sha> -- <file>`.
   The coach-portal doc showed origin (5745B) **lacked** two sections the local
   commit added (6156B): "Production promotion (2026-08-25)" (18 lines) and
   "2026-08-25 Update — mobile-first rebuild + population/platform visibility"
   (8 lines).
4. **Rescue BEFORE reset:** append both unique sections to the live skill
   `~/.hermes/profiles/ned/skills/devops/telegram-bot-onboarding-operations/references/
   hde-coach-portal-cloudflare-access-2026-07-16.md` (4454B → 7447B; pre-merge backup
   saved to /tmp first). The live skill is the auto-regen source of truth, so the
   content propagates into the OKF mirror on the next regen — no hand-edit of
   `okf/skills/` needed (which would be out-of-lane + clobbered anyway).
5. `git reset --hard origin/main`. Dropped commits remain recoverable via reflog.
6. Verify: `git rev-list --left-right --count origin/main..main` = `0  0`;
   `git status --short` clean; `grep -c "mobile-first\|population" <live skill>` = 3.

## Rules extracted

- Never trust "all local commits are auto-regen" from a subject-line skim; verify per-commit file lists.
- Classification is per-file (path + authorship), not per-repo: auto-regen mirrors are reproducible from live skills; hand-authored docs are not.
- Rescue target = the live skill, not the OKF mirror (mirror is a derived artifact; hand-edits are out-of-lane and get clobbered).
- Reset is low-risk (reflog), but the rescue must precede it, never follow it.
- The MCP okf hub's `status` HEAD reflects the *local* checkout, not origin — expect it to show the local tip until the PR merges; after a reset it tracks origin.
