# Fleet hardening — 2026-08-20 (tooling, canary, guard, review packet)

Session-specific detail for the HFG build-drift-elimination work (Linear parent GRO-4797, 5 epics, 13 tasks; dup GRO-4816 Canceled).

## Tooling shipped (hd-platform-staging, UNCOMMITTED — Michael's commit gate)
Branch at work time: `ned/hde-phase4-paid-bot-onboarding-quality-2026-07-15` (HEAD 4a9c73c).
- `scripts/fleet_audit.py` — matrix + `guest_fleet.json` manifest. `DECOMMISSIONED = {40, 42}` in-script (owner decision 2026-08-19 "leave as is"). Detection `fullmatch guest_(\d+)` excludes legacy scaffolds (`guest_hermes`, `guest_hermes_1`). Drift flag = live/down only. `--strict` exit 2.
- `scripts/fleet_sync.py` — live-guests-only: `.bak-<UTC>` → cp → chown 1000:1000 → md5 verify (auto-restore on mismatch) → `.build` marker → `docker restart` → `/docs` poll (90s). Idempotent "all current" no-op. Exit 0/1/2 (ok/hard/partial).
- Template gained `_log_build_identity()` (boot BUILD-IDENTITY line) + naming guard (`BLOCKED_PERSON_NAMES` / `is_blocked_person_name`) at both chart-creation entry points. Build `baf3887bf391357d61294b369b12bed7`, 2725 lines.
- `tests/test_guest_naming_guard.py` — 10 tests, run with `/usr/bin/python3 -m pytest` (platform venv has no pytest).
- Rollback vintages per live guest: `.bak-20260819T2100Z` (first 12-way sync), `.bak-20260820T0402xxZ` (canary rollout), `.bak-20260820T0451xxZ` (guard rollout).

## Proofs recorded in Linear (ad hoc, not suite green)
- SYNC end-to-end on test guest 3: drift injected (6aed97cc/2660) → detected → synced (backup, hash_ok, restart, healthy) → back to template.
- CANARY negative proof on guest 3 (04:10–04:13 UTC): appended 1 line outside sync → detector 2 `DRIFT-MARKER: guest_3 running hash 75d2003d != marker 5652256a` + DRIFT status; detector 1 latest boot log `md5=75d2003d… lines=2695 marker=5652256a… 2693` → restored via fleet_sync → 0 live-drifted.
- NAMING sweep (read-only): 10 of 12 clean; mis-files only on guests 2 & 23 (`michael gulden` / `becca gulden` in people/index.json + charts/personal/*_gulden/). Report: /tmp/hfg_naming_sweep.json (copied into the review packet evidence/). Deletion = Michael's call.

## Review-packet handoff (the reusable pattern)
Packet: `hd-platform-staging/review-packets/hfg-guest-fleet-2026-08-20/` (REVIEW_PACKET.md + evidence/).
- §1 paths, §2 verification table, §3 re-runnable recipes (mutating step #7 = drift-inject on a test guest, flagged), §5 caveats leading with the partials (uncommitted source #1), §7 sender verification log.
- Tarball `/home/ubuntu/hfg-guest-fleet-2026-08-20-for-review.tar.gz`, final SHA256 `6a17af85…cf9a32`; trigger + FINAL-STATE comment on GRO-4797 (supersede pattern — see linear-handoff-build-out gotcha #16).
- The Prismatic workspace-tree web surface 400'd (`invalid workspace identifier`) for valid workspace IDs on BOTH public and local origin — pre-existing deployed-gateway strict-registry regression (`prismatic/gateway/workspace_tree.py`), not a packet problem. Fallback = tarball + SHA in Linear. The deployed gateway source of truth is `/home/ubuntu/work/prismatic-engine` (not the *-pwp-* worktrees that look current).

## Verifier self-check lesson
First verifier run 14/16: (a) flagged the literal `guest_<$id>` placeholder from the doc table as a missing path, (b) read `docker logs` from stdout only while the boot line is on stderr. Both were verifier bugs, not packet bugs — fix the verifier, re-run, and when the fix adds a check, update the packet's §7 count (16→17) or the meta-check goes stale. Keep the count self-consistent: N checks, §7 says N/N, checker asserts the N/N string.

## OKF runbook
`okf/operations/hde-guest-fleet-ops.md` in growthwebdev-knowledge on branch `feature/fred-okf-hde-guest-fleet-ops` (pushed; main = manual-merge). HDE project-index breadcrumb staged in the same worktree. Note: the hub checkout was sitting on unpushed local branch `content/kai-okf-phase3-spokes` (ahead 2) — commit to a fresh branch from origin/main, never to whatever branch happens to be checked out.

## Open items (Michael's gates)
- Commit/PR the 5 uncommitted fleet paths (outbound gate).
- Delete or quarantine the guest 2/23 mis-filed records.
- Peer review: 12 tasks In Review + `agent:peer-review-blocked`.
- LOCK-IN: skill saved (this doc), final tree readback = the Linear readback in the FINAL-STATE comment.
