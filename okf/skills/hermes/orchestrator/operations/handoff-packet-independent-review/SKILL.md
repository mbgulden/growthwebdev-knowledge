---
name: handoff-packet-independent-review
description: Independently review an inbound handoff packet (tarball + review checklist) from a peer agent (e.g. George, Ned) or contractor before posting a verdict to Linear. Archive packets re-run proofs from a fresh extraction; live-tree packets (uncommitted working-tree code, e.g. fleet on live mounted files) re-run against the live disk with provenance + branch-ahead-count as first-class checks. Never trust pre-baked logs. Lead with a verification table; surface procedural bugs separately from substantive findings; never post a CLEAN verdict resting on packet-supplied evidence alone. Reviewer-side complement to linear-handoff-build-out and plan-reconciliation-after-peer-review.
---

# Independent Review of an Inbound Handoff Packet

A peer agent or contractor just handed you a tarball with a `REVIEW_PACKET.md` claiming it's ready for sign-off. The packet contains a self-attestation (`author_of_self_attestation=<peer>`), a list of pre-baked logs, a contract reference, and a checklist of things for *you* to verify. Your job is to be the second pair of eyes: re-run every proof from a fresh extraction of the bundle, do not trust the bundled logs as primary evidence, and surface both substantive findings and procedural bugs before posting a verdict.

This is the **reviewer-side** class. The sender-side is `linear-handoff-build-out`. The plan-correction class (reviewer to planner) is `plan-reconciliation-after-peer-review`. They overlap in spirit (independent verification, leading with recipes) but differ in direction and shape.

## When to use

- A peer agent says "please do this review" or "verify the bundle" and attaches a tarball path and SHA256.
- The packet is a **live-tree packet** — the code under review is uncommitted working-tree state and the packet says "no git archive to extract; re-run against the §1 paths" (see "Two packet classes" below).
- A `REVIEW_PACKET.md` (or equivalent) names a HEAD commit, a contract version, a Linear ticket, and a checklist of proofs to re-run.
- A self-attestation says "prepared by <peer> (self-attestation)" — the packet-author vouched for themselves; you are the independent witness.
- The packet contains pre-baked logs (`focused-pytest.log`, `r1_reproducer.log`, etc.) that the author claims prove the gate. You need to re-run them, not read them.
- A Linear comment from the prior review says `VERDICT=CLEAN` with caveats that may or may not be closed by the new HEAD.

## When NOT to use

- The peer is asking you to *send* a handoff, not *review* one. That's `linear-handoff-build-out`.
- The peer is asking you to reconcile a draft plan against a list of corrections. That's `plan-reconciliation-after-peer-review`.
- No packet exists yet — you're being asked to produce one, not review one.
- The packet is for a *user-facing* artifact (a UI change, marketing copy, a public doc) where the verification surface is different. This skill is for technical/engineering packets (gate proofs, test logs, contract enumerations, source archives).

## Two packet classes — archive vs live-tree

Step 2's "extract to a fresh tempdir, never the live tree" applies to **archive packets**: the bundle contains the code under review (a git archive, an `exact.tar.gz`, etc.), and you re-run proofs against the extraction.

**Live-tree packets** exist when the code under review is uncommitted working-tree state — e.g. a fleet of live-mounted files where the disk *is* the running build and there is nothing to extract. These packets say so explicitly ("no git archive to extract; re-run against the §1 paths"). For them:

1. The tarball contains only the packet + evidence JSONs, not the code. The bundle-identity check (step 1) and extract-vs-disk byte-identity still apply to the packet files.
2. The re-run surface is the **live tree at the §1 paths**. Provenance becomes part of the re-run: capture `git branch --show-current && git rev-parse --short HEAD` plus `git status --short -- <§1 paths>` and compare against the packet's provenance claim (branch, HEAD, "N paths uncommitted"). If the live tree has advanced since the packet was written (newer build hash / line count), re-anchor every baseline claim to the CURRENT build identity and note the advance — do not fail the review over it.
3. **The uncommitted state is itself a first-class caveat to verify:** is it really uncommitted, and — critically — how far ahead of the integration branch is the working branch (`git rev-list --count origin/main..HEAD`)? A "commit + PR the 5 paths" closure can silently drag dozens of unrelated commits into main if the branch is entangled. Surface the count; it changes the closure options (direct PR vs clean branch from main).

## Workflow

1. **Verify the bundle identity BEFORE extracting anything.**
   - `sha256sum <bundle.tar.gz>` and confirm it matches the SHA256 the peer quoted in the cover note. If it does not, stop — the bundle is corrupted in transit, the peer has stale evidence, or the cover note was wrong. Do not proceed with the review.
   - `tar -tzf <bundle.tar.gz>` and confirm the file count and top-level layout match the cover note's "what's inside" list. **Pre-baked packet text is itself an unverified claim; the tar listing is the ground truth.** Drift between the two is a procedural bug, not necessarily a blocker, but it goes in the report.
2. **Extract to a fresh tempdir, never the live tree.** (Archive packets only — see "Two packet classes".)
   - `tar xzf <bundle.tar.gz -C <fresh_tmpdir>` — never `--strip-components` or any transform, since you want the exact shape the peer shipped.
   - The fresh extraction is your test surface. Treat the live repo as suspect — the peer may have uncommitted local edits, the wrong branch checked out, or a dirty working tree.
3. **Read the REVIEW_PACKET.md and inventory the verification checklist.**
   - Most packets have a §3 "what the reviewer needs to do" with N numbered steps.
   - Build a working table mapping each step to the exact command you'll run against the extracted tree.
4. **Re-run every proof from a fresh extraction, not the live tree.** (Live-tree packets: against the live disk at the §1 paths, per "Two packet classes".)
   - Pytest: `cd <extract>/; python -m pytest <paths> --tb=short -q` — confirm pass count matches the bundled log line for line.
   - Gate reproducers: invoke each reproducer script against the extracted tree, capture the `RESULT=R*_GATE_PASS` line.
   - Regression scripts: `python3 <extract>/run-regression.py` from the extract dir.
   - Identity checks: re-hash the inner `exact.tar.gz` if one is present, confirm it matches the `archive_sha256` in `logs/identity.log`.
   - Do NOT skip a step because the bundled log looks plausible. The point is independent verification, and the cheapest way to lose reviewer credibility is to post a CLEAN verdict that turns out to rest on bundled evidence.
5. **Cross-check the contract / allowlist claims against the source.**
   - If the packet claims a contract enumerates certain paths, open the contract file and grep for each named path. Missing enumeration = caveat, not necessarily a blocker, but it goes in the report.
   - If the packet claims a bug was fixed (e.g. "BacklogImporter._process_manifest now computes the real digest"), grep the source for the fix pattern and confirm the old anti-pattern is absent. The two checks together (new pattern present and old pattern absent) are the only way to be sure the fix is real, not just claimed.
6. **Surface procedural bugs separately from substantive findings.**
   - Procedural bugs = packet metadata drift (file counts, paths, version numbers, contract paths). These make the packet harder to follow and may confuse future readers, but they do not invalidate the underlying technical work.
   - Substantive findings = the underlying proofs don't pass, the fix isn't really there, the contract doesn't actually enumerate what it claims, the HEAD under review doesn't match the identity log.
   - In the verdict report, **lead with substantive findings** (they gate the verdict) and put procedural bugs in a "non-blocking" section. A procedural bug should never block a CLEAN verdict unless it makes the substantive verification unreproducible.
7. **Lead with a verification table.**
   - One row per check from the §3 checklist. Columns: §-number, check, expected outcome, actual outcome, pass/fail. The peer can scan it in 10 seconds and see what you actually verified vs. what you skipped.
   - Tables beat prose for any structured data; reserve prose for the procedural-bug section and the open-questions section.
8. **Post the verdict to Linear with explicit scope.**
   - `VERDICT=CLEAN` — all substantive checks pass; procedural bugs (if any) are non-blocking. The peer may proceed to the next gate.
   - `VERDICT=NEEDS_WORK` — specific gate(s) failed; the peer should back up to the named gate and re-emit. Cite the failing row of your table.
   - `VERDICT=DIRTY` — fundamental issue (e.g. the fix contradicts the contract, the bundled logs are fabricated, the HEAD is wrong); back to base, re-plan.
   - Always reference the HEAD SHA you verified, not the HEAD the peer *said* they shipped. If the two differ, the packet is the wrong one.
9. **Do not trust pre-baked logs as primary evidence.**
   - Pre-baked logs in the packet are useful as a *secondary* cross-check (your re-run output should match them line-for-line modulo timestamps and fresh-DB job ids), not as the primary evidence for your verdict. If the re-run output matches the pre-baked log, that's a strong signal the peer is being honest. If it doesn't, the pre-baked log is wrong, and the verdict is whatever the re-run output says.
10. **Verify the reviewer's caveats as claims.** A caveat ("uncommitted source", "LOCK-IN incomplete: GRO-4814/4815 still Todo", "branch HEAD 4a9c73c") is a re-checkable assertion, not a disclaimer. Verify each against live state (Linear read, `git status`, branch ahead-count, file existence) before agreeing to it. Caveats gate **closure**, not the verdict; a wrong or stale caveat mis-schedules closure, and rubber-stamping an unverified caveat is exactly the packet-text-as-truth failure this skill exists to prevent.

## Pitfalls

- **Don't re-run destructive §3 steps without explicit owner permission.** A step marked mutating (touches a live guest, a test env, prod-adjacent state) is not re-run by the reviewer unilaterally — even on "test" guests, the owner may want them untouched for hours. The author's timestamped log + specific claim ("I ran this at 04:13 UTC on guest 3") is the secondary evidence: record the table row as `not independently re-run (mutating; author log cited)`. Silent-skip and re-run-then-apologize are both wrong; the explicit table row is what makes the review's scope visible.
- **Don't read the pre-baked logs and call it verified.** That's the easiest way to ship a CLEAN verdict on a broken packet. The pre-baked logs are what the peer *claims* — your job is to independently produce equivalent output from the same source. If you wouldn't accept a CLEAN verdict from a peer who only read their own logs and trusted them, you shouldn't ship one of your own based on the same.
- **Don't conflate "the packet says X" with "X is true."** Packet text is an assertion. Tar listings, source file contents, and reproducible command output are the ground truth. When they disagree, ground truth wins and the packet is wrong.
- **Don't block on procedural bugs unless the substantive verification is impossible.** A stale file count in the cover note is annoying; a wrong `cd <extract>/src` instruction is annoying-but-fixable; an entire step that can't be reproduced is blocking. Sort accordingly.
- **Don't trust the file count from the packet.** Always `tar -tzf | wc -l` (or count entries in `tar -tzf` output) yourself. The cover note's "2521 files" is the peer's claim; the actual count is the disk's claim. Drift is a procedural bug, not a verdict-changer.
- **Byte-identity loops (extract vs disk): build both paths from the same relative layout, and canary one file first.** A one-level path-prefix mismatch (e.g. `extract/<top>/<f>` vs disk `<base>/<top>/<f>`) produces a false DIFF on *every* file — and a false "drift" report is worse than a missed one, because it sends the owner chasing a problem that doesn't exist. Before the loop: `ls` both sides (or hash one known-stable file) and confirm the layouts align. (Observed 2026-08-20: HFG packet extract-vs-disk check reported DIFF on both files on pass 1; root cause was a doubled path prefix in the loop, not real drift — pass 2 with corrected layout: MATCH ×2.)
- **Don't assume the extraction layout matches the instructions.** The packet may say "cd <extract>/src" but the actual git archive extracts to a flat repo root (no `src/`). Run `ls` on the extraction before running the §3 commands, and adapt the commands to the actual layout. Note the drift in the procedural-bugs section.
- **Don't post a CLEAN verdict that rests on packet-supplied evidence alone.** If a step of the §3 checklist can't be reproduced (e.g. a reproducer script that lives outside the bundle and the peer didn't ship it), the verdict is `NEEDS_WORK` with "step N not reproducible from packet" as the reason, not `CLEAN`.
- **Don't let a clean CLEAN verdict table bury real caveats.** If 5 of 6 proofs pass and the 6th has caveats, the headline is "5/6 clean, 1 caveat" — not "CLEAN." Future readers (and the peer) trust the headline; if the headline hides a real partial, the next session ships on top of the partial and you both end up debugging it twice.
- **Don't skip the contract/allowlist cross-check.** It's tempting to treat the contract as "documentation" and skip the grep. But the contract is the enforcement layer for the next change; if it claims to enumerate a file and doesn't, the next reviewer will hit the same gap.
- **Don't accept "DB is fresh each time" as an excuse for non-deterministic reproducer output.** It's fine for the reproducer to produce different job ids across runs (the DB row is new each time) — that's expected behavior. What is NOT fine is for the reproducer to produce different gate verdicts (PASS vs FAIL) across runs. If it does, it's flaky and the verdict is `NEEDS_WORK` with "reproducer is non-deterministic" as the reason.
- **The manifest is not the universe.** When fingerprinting a fleet/system for a review, glob the WHOLE directory family, not just the manifest's IDs (observed 2026-08-20 HFG review: the 12-guest manifest missed `guest_hermes` + `guest_hermes_1` directories; a whole-family md5 `uniq -c` surfaced a third, off-manifest build hash). Surface off-manifest findings as caveats — never silently drop them, and never "fix" them within the review's scope.

## Companion skills

- `linear-handoff-build-out` — the sender-side. When *you* are producing a handoff packet, this is the class-level discipline for the build-out, including the seven-field description and the REVIEW_PACKET.md template. Read this skill if the peer is asking *you* to send, not review.
- `plan-reconciliation-after-peer-review` — for the different case of "I have a draft plan, a peer reviewed it, fold in the corrections." Both classes are about independent verification, but the direction is reversed and the artifact shape is different (a plan vs. a packet).
- `verification-recipe-vs-assertion` — the principle this skill enacts: lead with the verification recipe (the command the next agent can re-run), not the assertion of the correct value. When sending a reviewer to agent handoff (or vice versa), the recipe is the unit of truth.
- `branch-deletion-approval` — applies if the handoff packet proposes a destructive cleanup (rm worktree, delete branch, archive release). All such proposals need explicit Michael approval even when the packet claims they're safe.
- `prismatic-evidence-handling` — for the evidence-handling discipline when the packet's proof is structured around `/tmp/hermes-verify-*` markers and contract pause-marker files.

## Worked example (2026-08-06, RF-V1 R4 V3 review)

- **Packet:** `/home/ubuntu/rf-review-packets/rf-v1-r4-v3-for-fred.tar.gz`, SHA256 `e826797f...`, sent by George after `VERDICT=CLEAN` on prior HEAD `5e334c1`. New HEAD `6d4b3fb` closes two caveats from the prior review.
- **Re-run from fresh extract (`/tmp/rf-extract-rla9tses`):** focused pytest 86 passed, R1/R2/R3 reproducers all `*_GATE_PASS`, run-regression.py `ALL CHECKS PASS`, conftest files confirmed docstring-only, V3 contract enumerates all 4 required paths, BacklogImporter fix present and old `'a' * 64` pattern absent.
- **Substantive findings:** zero. CLEAN.
- **Procedural bugs (non-blocking):** REVIEW_PACKET §3 step 2/3 say `cd <extracted archive>/src` but the inner git archive extracts to a flat repo root with no `src/` — instructions don't work as written. Packet claims "2521 files" but `tar -tzf` shows 2950. Both are 30-second edits to REVIEW_PACKET.md.
- **Verdict:** `VERDICT=CLEAN` to Linear GRO-4477, with procedural bugs flagged in the same comment so George can fix the packet before Fred opens it.
- **Lesson:** the verification table and the procedural-bug split turned a "looks fine" pass into a structured CLEAN-with-known-nits — Fred can scan the table in 10 seconds and fix the nits in 5 minutes. That's the value this skill provides over "post CLEAN if the proofs look plausible."

## Worked example (2026-08-20, HFG guest-fleet live-tree packet, GRO-4797)

- **Packet:** `hd-platform-staging/review-packets/hfg-guest-fleet-2026-08-20/REVIEW_PACKET.md` + tarball SHA `432fcb76…` (posted as 📌 FINAL). **Live-tree shape:** the fleet runs mounted working-tree files; 5 paths uncommitted on branch `ned/hde-phase4-…` (HEAD `4a9c73c`).
- **Re-run against live disk (all non-mutating §3 steps):** audit 12 guests / 10 live / 0 drift; sync idempotence ("all current — nothing to do"); template py_compile; guard tests 10/10; guard live count 3; boot-log canary md5==marker on all 10 live guests (`baf3887b`/2725); naming-sweep evidence hits only guests 2+23; backups 10/10; tarball sha256 + extract==disk byte-identical; deep-link chain 200 + resolve `ok:true`; Linear tree state matched the caveats (GRO-4814/4815 Todo, GRO-4816 Canceled dupe).
- **Mutating step 7 (desync a test guest + restore):** not independently re-run — author's timestamped log cited (2026-08-20 04:10–04:13 UTC, guest 3); table row marked accordingly.
- **Findings BEYOND the reviewer's own:** (a) the working branch is **35 commits ahead of `origin/main`** — a direct PR would carry unrelated GRO-4011 work; closure options narrowed to "clean branch from main" vs "direct PR"; (b) GRO-4814's skill already existed (`hde-guest-fleet-ops`) — a "pending" caveat that was actually "done, needs the Linear mark."
- **Verdict:** CLEAN confirmed independently; closure gates surfaced to the owner as one decision. The live-tree variant + caveat-verification step did the work: the archive-packet workflow ("extract, never live tree") would have been unusable as written for this packet.
