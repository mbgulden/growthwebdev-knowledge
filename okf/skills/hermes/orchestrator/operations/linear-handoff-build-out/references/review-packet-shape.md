# Review Packet Shape (sender side) — self-contained REVIEW_PACKET.md + handoff delivery

Class recipe for producing a review packet any independent reviewer can execute
cold, plus the delivery discipline (link + tarball + Linear SHAs). Distinct from
`handoff-packet-independent-review` (the receiver side) and from gotcha #16 (the
link/SHA traps — read that too; this file is the packet's *shape*).

Worked example: HFG guest-fleet packet, 2026-08-20, GRO-4797 — 23/23 ad-hoc
verifier, 4 tarball SHAs superseded down to one authoritative value.

## Section shape (in order)

1. **Header block** — author + "self-attestation", date (UTC), Linear parent +
   child IDs, one-line scope, verdict contract ("re-run §3, then post
   `VERDICT=CLEAN|NEEDS_WORK|DIRTY` as a comment on <parent>").
2. **§0 What you are reviewing** — the incident/goal, fleet/state table at packet
   time with "re-verify, don't trust" language.
3. **§1 What's inside (paths)** — artifact table: every path the reviewer will
   need (scripts, outputs, template, tests, evidence files, backups, per-guest
   dirs). Absolute paths for live-host artifacts; repo paths for git artifacts.
4. **§2 Verification table** — one row per claim: check / expected /
   author-result-at-time. This is the *attestation*; the reviewer's job is to
   re-run, not read.
5. **§3 What the reviewer needs to do (recipes)** — numbered, copy-pasteable
   commands with expected output per step. **Every step must be re-runnable
   from the live files**, with the exact interpreter/venv called out (e.g.
   "`/usr/bin/python3 -m pytest` — the platform venv lacks pytest"). Mark
   MUTATING steps explicitly ("MUTATES a test guest — ask Michael first") and
   give a default safe target.
6. **§4 Per-task evidence index** — pointer from each Linear task to its
   evidence comment (the packet consolidates; the task comments carry raw
   output).
7. **§5 Partial results & caveats** — **lead with these** (Michael's standing
   preference: partials above the headline). Uncommitted source, docs not yet on
   main, decisions still the owner's (deletions, merges), known-stale items kept
   by design. A packet without a §5 is an overclaim.
8. **§6 Out of scope** — explicitly name adjacent work the verdict does NOT
   cover (prevents scope creep in review comments).
9. **§7 Sender verification log** — ad-hoc, dated: N/N PASS via
   `/tmp/hermes-verify-<topic>.py`, the check list in one line, **explicitly
   "ad-hoc targeted verification, not a test suite"**, which steps were excluded
   by design (mutating ones) and when they were exercised live, and that the
   reviewer's §3 re-run supersedes the log.
10. **Footer** — self-attestation line + the reviewer-facing link (verified
    end-to-end) + one honest line on any prior misdiagnosis/correction, if
    applicable.

## Rules

- **Self-consistent counts.** The §7 "N/N PASS" must equal the actual check
  count in the verifier. When the verifier gains a check (new claim, new
  deep-link probe), update §7 in the SAME pass — then the packet bytes changed,
  so the SHA discipline below applies.
- **SHA supersede discipline.** Every byte change → rebuild tarball → re-run the
  verifier against the NEW sha → post a superseding Linear comment
  ("⚠️ PACKET UPDATE — supersedes the SHA above"). Once stable, post ONE
  "📌 FINAL BUNDLE STATE (supersedes all prior SHA comments — read only this
  one)" naming the single authoritative SHA and marking earlier values stale.
  Three comments are cheaper than a reviewer verifying the wrong bundle.
- **Verify the link the reviewer will fetch — with the reviewer's chain, not
  yours.** For Prismatic: `https://prismatic.growthwebdev.com/workspaces?file=
  <workspace-relative-path>` → 307 `/dashboard?file=…#workspaces` → SPA calls
  `/api/workspace-tree/resolve?file=…` (server picks the workspace — never
  hand-type `workspace_id`; `invalid workspace identifier` is almost always your
  own zero-count typo, regex `^ws-[0-9a-f]{32}$`). Verifier must check: 307
  target, resolve ok + correct relative path, preview content == disk bytes —
  on local AND public.
- **Link + tarball are complements, never alternatives.** Tarball comment:
  SHA256 + contents list + "verify SHA first, then run §3".
- **Packet lives in the repo** (e.g. `review-packets/<topic>-<date>/`) so the
  web deep-link resolves; evidence subdirectory holds machine-readable reports
  (sweep JSON etc.).
- **Re-runnable > bundled logs.** Pre-baked logs are secondary; the §3 recipes
  are the contract. Never let the packet's own logs be the only proof.
- **Ad-hoc ≠ suite green.** Every verifier summary line carries that label
  (also satisfies the system evidence-reminder contract).

## Delivery checklist (before declaring the packet "handed off")

1. `tar czf <bundle>.tar.gz` of packet dir; `sha256sum`; `tar tzf` content list.
2. Fresh extract → `diff -r` against live dir → byte-identical.
3. Verifier N/N PASS, exit 0 (artifact + integrity + link checks).
4. Linear parent comment: bundle path + SHA256 + contents + verdict contract +
   (if the web link exists) the verified link.
5. Any subsequent packet edit → repeat 1–4 with a supersede comment.
