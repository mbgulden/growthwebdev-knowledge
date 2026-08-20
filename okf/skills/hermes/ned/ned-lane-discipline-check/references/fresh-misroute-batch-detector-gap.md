# Fresh-misroute-batch detector gap (GRO-594..2976, 2026-06-29 ~21:07Z)

**This is the canonical disposition for a recurring-misroute batch whose IDs are NOT in the detector's `RECURRING_BATCH_SIGNATURES` table.** Codified from Pass-N+18 (2026-06-29 ~21:07Z), the first pass on the GRO-594..2976 batch. Future fresh misroute batches that don't match `gro-484-502` or `gro-504-512-537` should follow this playbook until the signature is registered in `suppress_class_detect.py` (see "Recipe for adding a signature" below).

## When this playbook applies

The scanner feed contains 10 `agent:ned`-labeled issues whose **IDs do not appear in `RECURRING_BATCH_SIGNATURES`**, and `suppress_class_detect.py` returns `verdict: FULL_REPORT` with `issue_ids_match_recurring_batch.pass: false`. The detector's other probes will also typically fail:

- `triage_doc_fresh.pass: false` — no prior Ned-style audit doc on disk for these IDs
- `prior_cron_output_fresh.pass: false` — newest is the current pass (age 0h), or too old to count
- `linear_state_audit.dequeue_count: 0` — these issues have "Dispatcher: routed to <lane>" comments, NOT the specific dequeue phrases (`out of lane`, `dequeued`, `wrong agent`, `not Ned's lane`, `relabel`, `lane violation`, `misroute`) the detector pattern-matches. The detector returns `dequeue_count: 0` despite the batch being clearly misrouted.
- `linear_state_audit.dispatch_ready_count: 2` — GRO-2533 and GRO-2436 carry `dispatch:ready` in this batch. **This is misleading**: the label was applied by the backlog surgeon (GRO-2861) without content filtering, and the actual partition rules (see `references/mixed-batch-triage-recipe.md`) override it because the titles target cross-profile territory (orchestrator memory) or human-required work (Google Workspace setup).
- `linear_state_audit.drift_count: 2` — GRO-2436 is `In Progress`, GRO-2434 is `Done` (already handled by AGY sandbox this minute). The detector treats drift as in-lane evidence; it's actually "out-of-scope, do not execute" evidence.

**Do NOT trust the FULL_REPORT verdict as a license to execute.** The verdict is a function of the detector's hardcoded vocabulary, not of the actual disposition. The right action is to walk the partition rules manually and confirm SUPPRESS eligibility — then follow the 5a.3 fresh-batch-anchor-comment path, not the "execute" path.

## Disposition (validated Pass-N+18)

For the GRO-594..2976 batch, manual partition walk returned:

| ID | Title | Correct lane | Ned-lane? |
|----|-------|--------------|-----------|
| GRO-594 | GPU temp trending dashboard | `agent:fred` | ❌ |
| GRO-597 | Commit homelab-hardware-inventory.md | `agent:fred` (×2 Dispatcher "routed to Fred") | ❌ |
| GRO-616 | Generate homelab-hardware-inventory.md | `agent:fred` (chain) | ❌ |
| GRO-617 | Weekly hardware inventory refresh cron | `agent:fred` (×3 Dispatcher) | ❌ |
| GRO-701 | Prometheus Exporter for inventory.json | `agent:fred` (chain) | ❌ |
| GRO-702 | Configure weekly cron for inventory refresh + auto-commit | `agent:fred` (×3 Dispatcher) | ❌ |
| GRO-2434 | Integrate Gumroad for Course Sales | `agent:kai-content` (already Done by AGY sandbox 21:04:54Z) | ❌ |
| GRO-2436 | Memory Grooming weekly cron silent-failing | `agent:orchestrator` (cross-profile write territory) | ❌ |
| GRO-2533 | `[MANUAL]` Michael: Google Workspace | `agent:human` (explicit MANUAL tag) | ❌ |
| GRO-2976 | Memory Capacity Auto-Trim Insufficient | `agent:orchestrator` (cross-profile write territory) | ❌ |

**Outcome: 0/10 in Ned's lane. SUPPRESS-eligible regardless of detector verdict.**

## 5-step disposal recipe (validated Pass-N+18)

1. **Manual partition walk** using `references/mixed-batch-triage-recipe.md` rules 1–5. Do NOT trust `dispatch:ready` as a positive in-lane signal — apply rules 3 (different lane in triage comment) and 5 (marketing-keyword / cross-profile-keyword in title) first.
2. **Write audit doc** at `prismatic-engine/scripts/ops/gro-<lowest-batch-id>-<highest>-batch-routing-1st-pass-infra-findings.md` (anchor-by-lowest convention).
3. **Commit on `ned/gro-485-triage-pass-1`** with `[Ned] Add Nth-pass audit doc for fresh GRO-<low>..<high> misroute batch (...)` subject. Re-using the GRO-485 branch (single-day log) is consistent with all 17 prior passes today and keeps the evidence chain contiguous. Do NOT create a new branch per fresh batch.
4. **Post ONE consolidated anchor comment** to the **lowest-GRO-ID** in the batch (anchor fallback for fresh batches — no prior Ned-triage thread exists). Use the file-based `write_file` JSON payload + `curl -d @file.json` pattern (see `references/linear-dequeue-graphql-recipe.md` and the inline-escaping pitfall captured in `references/ned-r154-batch-b-sustained-suppress-manual-curl-20260629.md`).
5. **Final response: `[SILENT]`**. No Telegram delivery. Per the SKILL.md "Final-response format" section, the audit doc + commit + anchor comment is the durable evidence; the final response is the suppression signal.

## Detector vocabulary gaps (recipe for patch)

The detector's pattern-matching vocabulary is too narrow. Two specific gaps:

1. **`"routed to <lane>"` is NOT a dequeue phrase.** The detector only matches the explicit dequeue keywords (`out of lane`, `dequeued`, etc.). Michael's Dispatcher routes ("📡 Dispatcher: task `GRO-XXX` routed to Fred") carry the same intent — explicit hand-off to another agent — but the detector misses them. Suggested patch to `scripts/suppress_class_detect.py`: extend the `dequeue_patterns` list with `routed to\s+(?:fred|kai|agy|designer|orchestrator)` (regex). This would have flipped the GRO-594..2976 batch's `min_dequeue_count` from 0 to 6 in this pass, giving the detector the same FULL_REPORT-but-manual-suppress signal it would have given on Batch B's first sighting.

2. **`dispatch:ready` is too aggressive a positive in-lane signal.** The detector treats `dispatch:ready_count == 0` as a SUPPRESS-eligibility prerequisite, but also treats `dispatch:ready_count > 0` as a positive in-lane indicator (encouraging execute). The GRO-594..2976 batch shows the failure mode: `dispatch_ready_count: 2` for GRO-2533 and GRO-2436, both of which are out-of-lane per the partition rules. Suggested patch: cross-reference `dispatch:ready` issues with their titles against the partition-rule classifiers (cross-profile keyterms: `orchestrator`, `beyondsaas`, `google workspace`; MANUAL tag; etc.) before counting them as in-lane positive.

These two gaps are the single most important reason this pass required ~30 tool calls of manual GraphQL fetches when it could have been ~6 with a smarter detector. Patching them would let future fresh-misroute batches (e.g., a GRO-2598..2699 batch emerging next week) be classified automatically, with a SINGLE detector call + manual edge-case walk for the 2-3 issues that the heuristics can't classify.

## Recipe for adding a signature to the detector

Once a fresh misroute batch has been dispositioned via this playbook and the per-issue correct-lane mapping is settled, register the new signature in `scripts/suppress_class_detect.py`:

1. Sort the batch IDs in ascending order.
2. Build the signature string as `gro-<low>-<high>` (e.g. `gro-594-2976` for the batch above).
3. Append to `RECURRING_BATCH_SIGNATURES` (a constant list inside the script — read with `search_files pattern="RECURRING_BATCH_SIGNATURES",path="/home/ubuntu/.hermes/profiles/ned/skills/ned-lane-discipline-check/scripts/"` to find current contents).
4. Test: `python3 suppress_class_detect.py --issues <comma-sep batch> --repo /home/ubuntu/work/prismatic-engine --cron-output-dir /home/ubuntu/.hermes/profiles/ned/cron/output --include-linear` and verify `issue_ids_match_recurring_batch.matched_signature == "gro-594-2976"` on the next cron pass.

Pitfall: the signature string IDs MUST be lowercase and the range is `low-high` with a hyphen, not "to" or commas. The current signatures `gro-484-502` and `gro-504-512-537` both follow this format. Match it.

## Pass-log entry (add to `references/pass-log-2026-06.md`)

Append-only, no rewrites. New entry to add:

```
- **Pass-N+18 (2026-06-29 ~21:07Z)** — Detector verdict: `FULL_REPORT`
  (5a.7a-bis check failed — no registered signature). Manual partition walk
  per `references/mixed-batch-triage-recipe.md` returned 0/10 in Ned's lane.
  Disposition: SUPPRESS via 5a.3 fresh-batch path (anchor comment on
  GRO-594 lowest-ID). Audit doc:
  `scripts/ops/gro-594-2976-batch-routing-1st-pass-infra-findings.md`.
  Commit `4d7b4c10` on `ned/gro-485-triage-pass-1`. Anchor comment ID
  `f3350c65-868c-4066-86a8-8b2a519c97e5` on GRO-594 at 21:08:38Z.
  Detector gaps identified: (a) `routed to <lane>` not in dequeue
  vocabulary; (b) `dispatch:ready` too aggressive positive in-lane signal.
  See `references/fresh-misroute-batch-detector-gap.md`. Final response: `[SILENT]`.
```

## Latent misroute pool — scanner rotates within a ~13-ID universe (codified 2026-06-29 ~21:18Z, Pass-N+19)

Pass-N+19 observed that the scanner is NOT feeding 10 random `agent:ned` issues — it's feeding **10 out of a stable ~13-ID latent misroute pool**. The pool membership (as of 2026-06-29 21:18Z):

- 7 inventory-pipeline IDs: `GRO-593`, `GRO-594`, `GRO-597`, `GRO-616`, `GRO-617`, `GRO-701`, `GRO-702` (Fred resale/inventory pipeline)
- 2 orchestrator-memory IDs: `GRO-2436`, `GRO-2976`
- 1 MANUAL Michael ID: `GRO-2533`
- 1 Done Gumroad ID: `GRO-2434` (Done — won't re-appear in the rotation once consumed)
- 1 eBay resale ID: `GRO-1662` (Fred resale partition, unblocked by GRO-654)
- 1 Phase 1 consulting ID: `GRO-502` (Fred live coaching; overlaps Batch B's GRO-484..502 universe)

Observed rotations:
- **Pass-N+18 (21:08:38Z)** picked: `{2434, 2436, 2533, 594, 597, 616, 617, 701, 702, 2976}` — anchor on GRO-594
- **Pass-N+19 (21:18Z)** picked: `{1662, 502, 593, 594, 597, 616, 617, 701, 702, 2976}` — anchor on GRO-1662

**Implications:**

1. **The detector signature should cover the WHOLE POOL, not just the rotated windows.** A signature like `gro-1662-2976` (which includes Pass-N+19's lowest ID and Pass-N+18's highest ID) is more durable than `gro-594-2976` (which only covers Pass-N+18's range). When the pool membership changes (a new ID gets misrouted in), extend the signature; when an ID is consumed (Done, etc.), the signature naturally narrows. Range-bounding by observed rotation is robust against future scanner variations.

2. **Future passes will pick other 10-subsets of this 13-ID pool.** Any subsequent pass that picks 7+ of these IDs and 0-3 new ones from the same partition SHOULD be classified the same way (suppress via the rotation-equivalence ratchet when prior anchor is <6h and criterion (c) holds).

3. **When a NEW ID appears outside the pool (e.g. GRO-2598 next week), the partition walk must include it explicitly before the ratchet applies.** The default is to re-run the disposal recipe with a fresh audit doc + new anchor comment covering the expanded ID set.

**Suggested detector patch:** add a `LATENT_MISROUTE_POOL` constant to `scripts/suppress_class_detect.py` listing the 13 known pool IDs. The detector's `issue_ids_match_recurring_batch` check should return `pass: true` when the scanner feed is a 10-subset of this pool (overlap ≥7). This replaces the brittle signature-string match with a set-membership check, which is robust against pool expansion and rotation.

## Pass-N+19 actual-execution recipe (codified 2026-06-29 ~21:18Z)

When the 5-step disposal recipe re-runs on a **rotated** feed (criterion (c) failed because prior anchor's per-issue triage table does not name all 10 IDs in the current feed), the recipe differs from the original 5-step:

1. **Manual partition walk** using `references/mixed-batch-triage-recipe.md` rules 1–5 — same as before.
2. **Audit doc filename** MUST use the current pass's lowest-GRO-ID, not the prior pass's. Pass-N+18 used `gro-594-2976-batch-routing-1st-pass-infra-findings.md`; Pass-N+19 used `gro-1662-2976-batch-routing-19th-pass-infra-findings.md`. Do NOT reuse the prior pass's filename — the new filename IS the durable record of the rotation, and a future reconstructor reading `ls scripts/ops/` should be able to see the ID-shift in the filename itself.
3. **Commit on `ned/gro-485-triage-pass-1`** with `[Ned]` prefix. Same single-day log branch as all prior passes today. The commit message should explicitly name the rotation delta (which IDs swapped in, which swapped out, which partitions are unchanged) — Pass-N+19's commit message is the canonical template:
   `[Ned] Add 19th-pass audit doc for fresh GRO-<lowest-current-pass>..<highest-current-pass> misroute batch (cron <timestamp>, rotation delta vs Pass-N+18 — <new-IDs> swapped in for <dropped-IDs>, 0/10 in Ned's lane, anchor comment going to <lowest-GRO-ID>, partial-coverage fail on rotation-equivalence criterion (c) requires recipe re-run, probe-skip per Pass-12 protocol, no in-lane work to execute)`
4. **Anchor comment target IS THE LOWEST-GRO-ID IN THE CURRENT PASS'S FEED, NOT THE PRIOR PASS'S.** Pass-N+18 anchored to GRO-594; Pass-N+19 anchored to GRO-1662 (the new lowest). Michael scans lowest-first when triaging; anchoring to a non-lowest ID hides the comment from his view. Use the file-based `write_file` JSON payload + `curl --data-binary @file.json` pattern — Pass-N+19 confirmed this works for multi-line markdown bodies with no inline-escaping issues.
5. **Final response: `[SILENT]`.** Same as the original 5-step recipe.

**Anti-pattern:** posting the Pass-N+19 anchor to GRO-594 (the prior pass's anchor ID) because "the rotation is small and GRO-594 is still in the feed." This is wrong: GRO-594 is in the feed but is no longer the lowest; the comment will be buried under future scanner churn. Always anchor to the current lowest.

## Latent pool expansion log (append-only)

- 2026-06-29 ~21:08Z — Pool established with 13 IDs from Pass-N+18 observation.
- 2026-06-29 ~21:18Z — Pass-N+19 confirms 3-ID rotation within pool; pool membership unchanged.
- 2026-06-29 ~22:44Z — Pass-N+21 confirms 3-ID rotation within pool; pool membership unchanged. Rotation delta vs Pass-N+20: GRO-2976 + GRO-593 + GRO-502 swapped in for GRO-2978 + GRO-2979 + GRO-2980 (all 3 rotated-out IDs were telemetry-investigation-family subsumed by GRO-2981 root-cause per Pass-N+20 analysis; the rotated-in set is the original Pass-N+19 trio returning to the feed).
- 2026-06-30 ~01:26Z — **Pass-N+29: pool GREW to ~16 IDs.** 3 new IDs rotated IN (GRO-490, GRO-492, GRO-499) — all Phase 1 consulting/curriculum + personal-brand content. These three were not in any prior anchor or audit doc; the scanner rotated them in from a growing backlog of Phase 1 issues aging into the dispatcher trap. 3 rotated OUT vs Pass-N+28 (GRO-701, GRO-702, GRO-1662 — the eBay resale / Prometheus Exporter chain that finally cleared the inventory-pipeline partition). Net pool membership change: +3. **Pool is NOT bounded — it grows as Phase 1 / personal-brand backlog ages into the dispatcher misroute.** Implication for the suggested `LATENT_MISROUTE_POOL` set-membership check in `suppress_class_detect.py`: the pool signature must be updated each time genuinely-new IDs appear, not treated as a fixed constant.

Future pool expansions (new misroute IDs observed) append here with timestamp + new IDs + reason.

## Pass-N+29 genuinely-new-IDs scenario (codified 2026-06-30 ~01:26Z)

Pass-N+29 (this pass) was the **first pass where the rotated-in IDs were NEVER named in any prior anchor.** Previous rotation-equivalence FAILs (Pass-N+19, Pass-N+26) were partial — the prior anchor named some but not all 10 of the current scanner-feed IDs, and the missing IDs were rotation-delta-narrative mentions at minimum. Pass-N+29's 3 rotated-in IDs (GRO-490/492/499) had **zero prior mention** anywhere in the audit-doc chain on `ned/gro-485-triage-pass-1` (verified via `grep -oE "GRO-[0-9]+"` on all 28 prior audit docs — none contain GRO-490, GRO-492, or GRO-499).

This is the **strongest possible FAIL** of criterion (c) — not a partial-coverage ambiguity like Pass-N+21's interpretation question, but a clean miss. The Pass-N+19 actual-execution recipe applies cleanly with no judgment calls.

**Pass-N+29 application of the Pass-N+19 recipe:**

| Step | Pass-N+19 (precedent) | Pass-N+29 (this pass) |
|------|-----------------------|----------------------|
| Lowest GRO-ID in feed | GRO-1662 (shifted from GRO-594) | GRO-490 (shifted from GRO-500) |
| Audit doc filename | `gro-1662-2976-batch-routing-19th-pass-infra-findings.md` | `gro-490-617-batch-routing-29th-pass-infra-findings.md` |
| Anchor comment target | GRO-1662 (new lowest) | GRO-490 (new lowest) |
| Anchor comment id | (Pass-N+18's anchor on GRO-594 retained as durable prior evidence) | `77497546-775b-486a-86fd-c98fa130e2ff` on GRO-490 at 01:27:XXZ |
| Rotation delta vs prior pass | GRO-1662 + GRO-502 + GRO-593 swapped in for GRO-2434 + GRO-2436 + GRO-2533 | GRO-490 + GRO-492 + GRO-499 swapped in for GRO-701 + GRO-702 + GRO-1662 |
| Pool membership change | 0 (same 13 IDs, just rotated) | +3 (16 IDs total) |
| Pass-N+21 filename rule application | N/A (Pass-N+19 preceded the rule) | Lowest shifted AND high shifted → both segments shift: `gro-<new-low>-<new-high>-batch-routing-Nth-pass-infra-findings.md` |

**Pitfall — when pool growth changes the filename range, BOTH segments may shift.** Pass-N+19 only shifted the lowest (high end stable: GRO-2976). Pass-N+29 shifted BOTH (lowest GRO-490 from prior GRO-500, high GRO-617 from prior GRO-1662). The Pass-N+21 filename rule's table covers the both-shift case implicitly ("When both shift, shift both"), but this is the first operational evidence of that sub-case in the wild.

**Pitfall — never reuse a prior pass's anchor comment id.** Each genuinely-new-ID scenario gets a fresh anchor id (`77497546-...` for Pass-N+29, distinct from GRO-500's Pass-N+23 anchor `2bc...` and GRO-594's Pass-N+18 anchor `f3350c65-...`). The fresh id is itself the durable evidence that the freshness gate was reset; if a future pass sees the SAME anchor id, criterion (c) holds via the existing gate; if it sees a NEW anchor id at the lowest-GRO-ID, the gate was reset and the new anchor's per-issue triage table is authoritative.

**Pitfall — pool-growth observation:** when a pass adds IDs to the pool, the future detector patch must extend `LATENT_MISROUTE_POOL` (or whatever the pool-tracking constant ends up being in `suppress_class_detect.py`). A detector signature that covers only the original 13 IDs will miss the 3 new ones, which means the next pass that picks all 13-original + 1-new will fail the set-membership check (10-vs-13 set, overlap = 9 < threshold 10) and fall through to the manual-recipe path. Tracking pool size over time is necessary for setting the right set-membership threshold.

**Decision tree for criterion-(c) FAIL sub-cases** (codified Pass-N+29 — previously scattered across pass-log entries):

| Sub-case | Example pass | Detection | Action |
|----------|--------------|-----------|--------|
| Partial coverage with narrative mention | Pass-N+21 | Anchor body mentions IDs in rotation-delta narrative but NOT in per-issue table | Run `grep -oE "GRO-[0-9]+"` on anchor body; if all 10 IDs present in regex output, criterion (c) HOLDs under interpretation #2, [SILENT] |
| Genuinely-new IDs (zero prior mention) | Pass-N+29 | `grep` finds IDs absent from anchor body entirely | Clean FAIL — recipe re-runs with fresh anchor on new lowest, no judgment call |
| Anchor aged past 6h | Pass-N+18 threshold-edge | Anchor on thread but `createdAt` > 6h old | See `references/anchor-threshold-crossing-transition.md` for the 3-step threshold-crossing transition protocol |

This decision tree should be the canonical entry-point for any future Ned pass that runs the rotation-equivalence ratchet and gets a FAIL on criterion (c).

## Pass-N+21 criterion-(c) coverage interpretation (codified 2026-06-29 ~22:44Z)

Pass-N+21 surfaced a judgment-call pitfall in criterion (c) of the Pass-N+19 rotation-equivalence ratchet. The ratchet's criterion (c) reads:

> (c) the lowest-GRO-ID anchor from the prior disposal is still on the active comment thread with age <6h AND its per-issue triage table covers ALL 10 IDs in the current scanner feed (not just 7/10)

The Pass-N+20 anchor comment body on GRO-1662 (id `566903ae-2f32-40e7-890b-7f88029edb4d` at 22:03:00Z, age 0.69h at this pass) had a 10-row per-issue triage **table** listing only the IDs in the Pass-N+20 scanner feed (GRO-1662/702/701/617/616/597/594/2978/2979/2980) — but the body text also **named** the rotated-out IDs (GRO-593, GRO-502, GRO-2976) in the rotation-delta narrative describing the prior pass. The current scanner feed (Pass-N+21) had GRO-2976 + GRO-593 + GRO-502 as rotated-in IDs.

**Two reasonable interpretations of "per-issue triage table covers ALL 10 IDs":**

1. **Strict table-row coverage** — only IDs appearing as rows in the per-issue triage table count toward coverage. Under this interpretation, the Pass-N+20 anchor covers 8/10 of Pass-N+21's feed (GRO-2976 is in the table as row 7, but GRO-593 and GRO-502 are NOT in the table). Coverage FAILS; recipe must re-run with fresh anchor.

2. **Any name-mention coverage** — IDs mentioned anywhere in the anchor body (table, narrative, rotation-delta, prior-pass reference) count. Under this interpretation, the Pass-N+20 anchor covers 10/10 of Pass-N+21's feed (GRO-2976 in table, GRO-593 + GRO-502 in rotation-delta narrative). Coverage HOLDS; SILENT verdict.

**Codification — Pass-N+21 chose interpretation #2 (any name-mention) for these reasons:**

- The rotation-delta narrative is **explicit, intentional, and serves the same purpose as the table**: it documents the disposition of the named IDs (correct lane + Ned-lane flag). A future reconstructor reading the body gets the same disposition information whether they read the table or the narrative.
- The Pass-N+19 codification's "(not just 7/10)" was contrasting against a Pass-N+18 anchor that did NOT mention the rotated-in IDs at all (GRO-1662/593/502 were silently absent from the body). The contrast is between "anchor mentions them" vs "anchor is silent on them" — not between "table row" vs "narrative mention."
- Requiring strict table-row coverage would force a recipe re-run on every pass where the rotation moved IDs between table and narrative, generating fan-noise with no information gain.
- The verification recipe in the "Pass-N+19 SILENT-after-anchor ratchet" section (4 checks: author + body length + createdAt + contains all 10 batch IDs OR explicit "10/10 out of Ned's lane" / "0/10 in-lane" line) already implements interpretation #2 — it accepts body-text mentions, not just table-row matches.

**Pitfall (do this BEFORE deciding SILENT vs recipe re-run):** when the rotated-in IDs are only in the anchor's narrative and not in its table, do a `grep -oE "GRO-[0-9]+"` on the full anchor body. If all 10 scanner-feed IDs appear in the regex output, criterion (c) holds under interpretation #2 — [SILENT]. If any are missing entirely (not in table AND not in narrative), criterion (c) fails — run the 5-step disposal recipe.

**Future refactor candidate:** update the criterion-(c) wording in the SKILL.md to remove the ambiguity. Suggested replacement:

> (c) the lowest-GRO-ID anchor from the prior disposal is still on the active comment thread with age <6h AND every ID in the current scanner feed is named anywhere in the anchor body (table row OR narrative mention OR rotation-delta reference) — byte-equivalence of the 10-ID list is NOT required

This codification should be applied to the SKILL.md in a future patch; this reference doc captures the operational precedent.

## Pass-N+21 stable-lowest-ID filename rule (codified 2026-06-29 ~22:44Z)

The Pass-N+19 codification step (1) says: "shift the audit-doc filename's lowest-GRO-ID segment to the current pass's lowest ID." This rule was written when the rotation shifted the lowest GRO-ID (Pass-N+18's lowest was GRO-594; Pass-N+19's lowest was GRO-1662 — a shift). Pass-N+21 had no shift (GRO-1662 was still the lowest in the scanner feed).

**Codification — what to do when the lowest GRO-ID is stable across passes:**

| Highest GRO-ID in scanner feed | Filename | Reason |
|-------------------------------|----------|--------|
| Same as prior pass | `gro-<lowest>-<highest>-batch-routing-Nth-pass-infra-findings.md` | Stable filename signals "same rotation, just a new pass" — the Nth-pass counter IS the rotation signal |
| Different from prior pass (high end moved) | `gro-<lowest>-<new-highest>-batch-routing-Nth-pass-infra-findings.md` | Filename tracks the current pass's range; rotation visible in filename itself |
| Different from prior pass (low end moved) | Same as prior pass (`gro-<prior-lowest>-<new-highest>-...`) | Lowest is the anchor convention; do NOT shift filename when lowest is stable even if the high end moved |

**Pass-N+21 application:** prior pass (Pass-N+20) used `gro-1662-2978-batch-routing-20th-pass-infra-findings.md`. Current pass's scanner feed high-end = GRO-2976 (which is LOWER than Pass-N+20's GRO-2978). Lowest GRO-ID = GRO-1662 (stable). Filename = `gro-1662-2976-batch-routing-21st-pass-infra-findings.md` (changed high-end from 2978 to 2976 to reflect the current pass's range).

**Pitfall:** do NOT keep `gro-1662-2978-batch-routing-21st-pass-infra-findings.md` even though GRO-2978 is no longer in the feed. The filename's high-end should reflect the **current scanner feed's** high-end, not the prior pass's. A future reconstructor doing `grep -l "GRO-2978" scripts/ops/gro-1662-2978-*.md` should find the audit doc that was active when GRO-2978 was in the rotation — that's Pass-N+20's doc, not Pass-N+21's.

## Pass-N+21 stale-lock observation (out-of-scope, codification 2026-06-29 ~22:44Z)

At Pass-N+21 (~22:44Z), the lock registry showed 1 stale lock: `path: prismatic/` `agent: ned` `heartbeat: 21.5m old` (TTL is 5 min). Pass-N+20 had noted "Lock registry confirmed clean per 17th-pass audit (no active locks)." The stale lock appeared between Pass-N+20 (22:00Z) and Pass-N+21 (22:44Z).

**Codification — do NOT clean stale locks from a SILENT pass.** The skeleton hard-rule says "Never reboot or make infrastructure changes without explicit approval." A stale-lock cleanup is a write operation against `/home/ubuntu/.antigravity/swarm_locks.json` — even though the lock is held by `ned` (the agent identity writing the audit doc), the cleanup is not the SILENT-pass's responsibility. The next non-SILENT Ned pass (or the next time the lock owner writes to the path and notices its own stale lock) will clean it up as a side effect.

**Document the stale lock in the audit doc's "Probe-skip" section** so a future reconstructor sees the observation. Pass-N+21's audit doc cites this codification explicitly.

## See also

- `references/recurring-misroute-batch-playbook.md` — sub-case A (recurring) and sub-case B (first-sighting zero-comments). This doc handles the **third sub-case** the playbook didn't explicitly cover: fresh batch with comments present and strong misroute evidence but unregistered signature.
- `references/mixed-batch-triage-recipe.md` — partition rule set used for the manual walk.
- `references/recurring-batch-suppress-2026-06-29.md` §"Workaround for unregistered batches" — the original workaround (which this playbook extends).
- `references/linear-dequeue-graphql-recipe.md` — anchor-comment GraphQL recipe.
- `references/ned-r154-batch-b-sustained-suppress-manual-curl-20260629.md` — file-based payload pitfall.

## Pass-N+19 SILENT-after-anchor ratchet (2026-06-29 ~21:17Z)

The pass that followed Pass-N+18 (~10 min later) validated that this disposal recipe produces a stable ratchet: subsequent passes on the same fresh-misroute batch can [SILENT] without re-running the 5-step disposal. Pass-N+19 evidence:

- **Scanner feed:** identical 10 IDs to Pass-N+18 (GRO-594/597/616/617/701/702/2434/2436/2533/2976). Strict-identical.
- **Anchor comment age:** 10 min (well under 6h freshness gate from r149).
- **Action:** [SILENT]. No new audit doc. No new commit. No new Linear comment. No `finalize_task.sh` call.
- **Probe results:** r119+r132 lane classifier returned 0/10 in Ned-lane (1 hit on GRO-594 overridden by per-issue triage table in the anchor comment — same override Pass-N+18 recorded).

**Why SILENT is correct here:** the Pass-N+18 anchor comment at 21:08:38Z IS the comprehensive 10/10 disposition for this batch. The next-pass probe confirms the same disposition. Re-running the 5-step disposal would (a) trigger a fresh `finalize_task.sh` call that falsely promotes Backlog→In Review on 9/10 issues (the r91 anti-pattern — the script's STEP 3 out-of-lane guard blocks state transition, but the boilerplate post-finalize-evidence comment still lands on the anchor), (b) generate duplicate audit docs (Pass-N+18 already wrote `scripts/ops/gro-594-2976-batch-routing-1st-pass-infra-findings.md` with full disposition), and (c) churn an anchor that already carries the per-issue triage table covering all 10 IDs.

**Codification — the Pass-N+18 → Pass-N+19 transition pattern:**

| Prior-pass state | This-pass action |
|---|---|
| Disposal recipe just ran (anchor comment <6h old) | **SILENT** — the anchor comment IS the durable evidence; re-running disposal would be duplicative + r91 fan-noise |
| Anchor comment 6h–24h old | r151 stale-comment refresh: post ONE short comment acknowledging the anchor is still current; do NOT re-run the full disposal |
| Anchor comment >24h old OR batch composition drifted | Re-run the 5-step disposal; anchor to whichever ID has the most recent Michael-as-Ned triage |

**Anti-pattern (proven Pass-N+19):** re-running the disposal recipe on a fresh batch <6h after the prior pass's anchor comment. The 5-step recipe is for FIRST-SIGHTING batches, not for the steady-state that follows. A future agent that runs `bash finalize_task.sh` on the anchor because "the 6h gate hasn't elapsed yet" reproduces the r91 mistake.

**Detection recipe (1 tool call, free):** before any action on a fresh-misroute batch, query the anchor (lowest GRO-ID) for `comments(last: 1)` and check:
1. Author email is `mbgulden@gmail.com` AND body opens with `## Ned` or contains `ned-lane-discipline-check` — yes = anchor is the Pass-N+18 Ned-as-Michael comment shape
2. Body length > 800 chars — yes = comprehensive per-issue triage table is present
3. `createdAt` within 6h — yes = freshness gate satisfied
4. Body contains all 10 batch IDs OR an explicit "10/10 out of Ned's lane" / "0/10 in-lane" line — yes = coverage gate satisfied

If all 4 are YES, [SILENT]. If any is NO, apply the appropriate remediation (re-anchor, post short refresh, or re-run disposal).

**Cost saved:** Pass-N+19 ran ~6 tool calls (skeleton read + 2 fresh GraphQL probes for batch composition + classifier + final response). A redundant-disposal pass would have been ~30 tool calls (the full Pass-N+18 recipe: 10 per-issue GraphQL fetches + manual partition walk + write_file JSON payload + curl Linear commentCreate + git add + git commit + branch check). The ratchet pattern preserves ~24 tool calls per subsequent pass until the anchor ages past the relevant threshold.
