# AOT project parking + cleanup pattern — 2026-07-12

## When this applies

Use when Michael asks to “park” Active Oahu Tours work, clear loose ends, or get ready to start a new project. Treat this as an operational closeout: verify live state, clean safe local clutter, route unresolved risk, and leave the next project with a clean runway.

## Parking checklist

1. **Live runway**
   - Check open PRs in both repos:
     - `mbgulden/active-oahu-tours-mirror`
     - `mbgulden/active-oahu-business`
   - Pull/fetch primary `main`; verify `HEAD == origin/main` with separate `git rev-parse --short HEAD` and `git rev-parse --short origin/main` commands.
   - Verify apex, `www` redirect, Pages mirror, and representative key routes.
   - Run a rendered homepage smoke check when the existing Playwright smoke script is available.

2. **Worktree cleanup**
   - Classify every AOT worktree before deleting anything.
   - Keep dirty worktrees and any branch with unique unmerged commits.
   - Safe-to-remove classes:
     - `ahead == 0` relative to `origin/main` (ancestor/merged).
     - `git cherry origin/main HEAD` has zero `+` entries (patch-equivalent/squash-merged).
     - missing worktree registrations after filesystem cleanup, via `git worktree prune`.
   - Remove only safe worktrees, then delete their local branches after the worktree is removed.
   - Save before/after JSON receipts under `/tmp` during the run.

3. **Silent cron parking**
   - For cron issues, do not stop at scheduler `last_status: ok`; inspect the actual cron output and data artifacts.
   - A job can be “ok” while functionally silent if the script swallows errors, writes empty output, or returns `[SILENT]` after data failure.
   - For ranking/KPI cron specifically, verify:
     - Ubersuggest token file exists but is not assumed valid.
     - Direct MCP/API probe returns usable data, not just an exit 0 wrapper.
     - `latest_keywords.json` is not overwritten with `{}` on data-source failure.
   - Harden KPI scripts so empty/error data exits non-zero, reports the actual blocker, and preserves the last non-empty baseline.
   - Harden cron prompts so they do not invent Linear IDs; they should reference the existing issue when one exists.

4. **Linear parking**
   - Security/governance tasks like WAF, CSP enforcement, and email-obfuscation rate limiting should be routed/parked with Fred or human-review if they require Cloudflare/security judgement.
   - Leave evidence comments explaining that live site health is good and the item is intentionally parked, not ignored.
   - Do not mark external-auth/token blockers Done; label/comment them as human-review or token-refresh blockers.

5. **Final verifier**
   - Create a focused `/tmp/hermes-verify-*` ad-hoc verifier.
   - Assert: PR runway clear, main clean/current, site routes healthy, smoke check passed, worktree cleanup receipt has no errors, remaining worktrees are only dirty/unique, cron failure is visible/not silent, and baseline data is preserved.
   - Remove the verifier and report it as ad-hoc verification, not canonical suite green.

## Useful worktree classification logic

For each worktree:

- `dirty = git status --porcelain --untracked-files=all` non-empty → keep.
- `ahead = git rev-list --count origin/main..HEAD`.
- `behind = git rev-list --count HEAD..origin/main`.
- If `ahead == 0` and clean → safe remove.
- If `ahead > 0`, run `git cherry origin/main HEAD`:
  - lines starting `-` are patch-equivalent to upstream (often squash-merged);
  - lines starting `+` are unique patches not in upstream.
- Clean worktree with zero `+` entries → safe remove.
- Any `+` entries → keep as unique work unless Michael explicitly authorizes archival/deletion.

## KPI cron hardening pattern

For scripts like `~/.hermes/profiles/kai/scripts/kpi_tracker.py`:

- Treat MCP/API exceptions as data-source failures, not empty successful reports.
- If keyword payloads are empty or contain `error`, exit non-zero.
- Print clear failure text such as `HTTP 401 Unauthorized`.
- Preserve `latest_keywords.json` when the run fails.
- Restore the most recent non-empty baseline if a prior bad run already wrote `{}`.
- Cron prompt should say: if script exits non-zero, returns zero usable data, reports auth errors, or says it preserved the previous snapshot, do **not** return `[SILENT]`.
- Cron prompt should also say: do not invent Linear IDs; use the existing issue unless a new issue was actually created and verified through the Linear API.

## Reporting pattern

Lead with: “Parking checklist complete — ready for a new project.”

Then include compact receipts:

- open PR counts;
- main/current commit;
- site health/smoke results;
- worktrees removed vs intentionally kept;
- cron status and any remaining external blocker;
- Linear items parked/routed;
- final ad-hoc verifier path and pass status.

Make clear that parked backlog is not the same as zero backlog. The goal is a clean runway, not pretending the roadmap is empty.
