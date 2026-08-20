# Batch B (Phase 1 — Active Oahu storefront hardware + HD curriculum) detector

**Codified 2026-06-29 after validated `[SILENT]` SUPPRESS passes at 09:25Z, 10:22Z, 10:29Z/10:30Z, 11:42Z, 11:58Z.**

## Signature

**Issue-ID set (10 issues):**
`GRO-484, GRO-485, GRO-486, GRO-487, GRO-488, GRO-490, GRO-492, GRO-499, GRO-500, GRO-502`

**Anchor:** `GRO-485` (lowest ID with ≥2 prior Ned-triage comments).

**Detector string:** `gro-484-488-490-492-499-500-502-485`

**Issue class:** Active Oahu storefront physical hardware (4 issues: GRO-484, 485, 486, 487, 488) + Gemini Agent Mode AI orchestration (GRO-490) + Personal Brand / Case Studies (GRO-492) + HD self-coaching curriculum (GRO-499) + YouTube library curation (GRO-500) + C-Suite live coaching (GRO-502).

**All 10 are ❌ Do NOT build for Ned.** Every item targets physical hardware, content/curriculum/brand, or AI-agent orchestration — none target `scripts/`, `prismatic/`, `plugins/`, or GPU/disk/CF/Tailscale/swarm infrastructure.

## Per-issue correct-lane mapping (carried across passes)

| Issue | Title (truncated) | Correct agent | Reason |
|---|---|---|---|
| GRO-484 | Procure & Mount Outdoor Intercom Button | `agent:fred` | Active Oahu physical install |
| GRO-485 | Deploy Outdoor Weatherproof Speaker | `agent:fred` | Active Oahu physical install + cable run |
| GRO-486 | HA Automation — Button→Piper TTS→Discord | `agent:fred` | Active Oahu HA config (`active-oahu/` read-only for Ned) |
| GRO-487 | Integrate Lorex 2K Two-Way Audio | `agent:fred` | Active Oahu physical hardware integration |
| GRO-488 | Mount Eye-Level Camera at Main Counter | `agent:fred` | Active Oahu physical install + positioning |
| GRO-490 | Configure Gemini Agent Mode | `agent:agy` | AI tool orchestration (not infra) |
| GRO-492 | Build Personal Brand — Case Studies + OSS | `agent:fred` | Brand/marketing work (`content/` read-only for Ned) |
| GRO-499 | Design HD-Tailored Self-Coaching Curriculum | `agent:kai-content` | Curriculum design (`content/` read-only for Ned) |
| GRO-500 | Curate YouTube Expert Library | `agent:fred` | Content curation |
| GRO-502 | Execute Week 1 — C-Suite Communication | `agent:fred` | Live coaching content delivery |

## Standing cure (Michael's standing instructions)

Either (a) **relabel** the 10 issues to the correct agent lanes above, OR (b) **patch `ned_delta_dispatcher.py`** to skip non-infra issues by either:
- title regex: `GPU|disk|Tailscale|Cloudflare|swarm|prismatic|DNS|cron|deploy`, OR
- require `lane:infra` label in addition to `agent:ned`.

Until either cure lands, Ned will keep dequeueing Batch B on every cron pass.

## 5a.5 silent-protocol checklist (verbatim, re-applied per pass)

ALL FOUR must be true for `[SILENT]` eligibility:

1. Scanner feed is byte-identical to the most recent Ned-style triage pass (same 10 IDs present).
2. Most recent Ned-style triage note on the GRO-485 anchor is <6h old.
3. That prior note already names every issue in the batch + correct lane mapping + standing cure.
4. No state drift on any issue in the batch (all still in `{Todo, Backlog}`).

If any item fails, post ONE consolidated acknowledgment to GRO-485 only (do NOT post per-issue dequeue comments on the other 9), skip `finalize_task.sh`, deliver `[SILENT]`.

## 5a.7a-bis (dual-signal prompts — `deliver: origin` + literal `[SILENT]` clause)

When ALL of the following hold, the cron's literal `[SILENT]` clause wins over the `DELIVERY:` paragraph's implicit "always deliver a report" default:

1. Scanner feed is the SAME 10-issue Batch B set from prior passes (sustained-misroute SUPPRESS).
2. ALL 10 issues carry Michael's explicit dequeue comments (≥3 comments per issue, ≥10h old on the oldest).
3. Prior cron output is durable on disk with the full 5-section SUPPRESS template.
4. The cron's literal `[SILENT]` clause uses "respond with exactly [SILENT]" or equivalent direct-conditional phrasing.

On a 4-of-4 match, `[SILENT]` is the correct disposition even on `deliver: origin` prompts.

## Anti-pattern captured

Every additional full-report-on-SUPPRESS pass accumulates to 30+ redundant Telegram messages per day. The cron's literal `[SILENT]` clause is the intended escape hatch. If you find yourself writing "Cron ran. No action taken. Batch held." for the Nth time on Batch B, you should have delivered `[SILENT]` per 5a.7a-bis.

## Validated SUPPRESS passes (anchor-only + `[SILENT]`, no `finalize_task.sh`)

- **2026-06-29 ~09:25Z** — First Ned-triage acknowledgment on GRO-485 anchor (names all 10 + lane mapping + standing cure).
- **2026-06-29 ~10:22Z** — Second pass; dequeue comments still <2h old; first anchor comment covers all 4 checklist items → `[SILENT]`.
- **2026-06-29 ~10:29Z / 10:30Z** — Third pass; same conditions → `[SILENT]`.
- **2026-06-29 ~11:42Z** — Fourth pass; 4-checklist all passed (same 10 IDs, last Ned-style anchor comment ~1h13min old, names every issue + lane mapping + standing cure, all 10 still in Backlog) → `[SILENT]`. No `finalize_task.sh` invoked. No state mutation.
- **2026-06-29 ~11:58Z** — Fifth pass; same conditions (1h29min elapsed since last Ned-style anchor comment) → `[SILENT]`.
- **2026-06-29 ~13:45Z** — Eighth pass; same 10 IDs, all Backlog, anchor most-recent Ned-style comment ~1h8min old, standing cure durable. 5a.5 4-of-4 + 5a.7a-bis 4-of-4 → `[SILENT]`. No `finalize_task.sh` invoked. No state mutation. Recipe continues to fire cleanly; lane has not been re-assigned and dispatcher has not been patched, so expect Batch B to recur indefinitely until one of the standing cures lands.
- **2026-06-29 ~14:08Z** — Sixth pass; all 10 still Backlog, last Michael dequeue on GRO-485 at 11:08Z (~3h ago), full 5-section SUPPRESS template still durable on disk → `[SILENT]`. No `finalize_task.sh` invoked. No state mutation.
- **2026-06-29 ~13:00Z** — Seventh pass; same 10 IDs, all Backlog, anchor most-recent Ned-style comment ~2h25min old (well inside <6h), standing cure already on disk. 5a.5 4-of-4 + 5a.7a-bis 4-of-4 → `[SILENT]`. No `finalize_task.sh` invoked. No state mutation. Confirmed: cron's literal `[SILENT]` clause wins over `DELIVERY: ... auto-delivered to destination` default.

**Note on log ordering:** passes are recorded chronologically by first-cron-pass detection time, not by log-file mtime. Future Ned sessions appending here should add at the end with the new ~Z timestamp; do not reorder.

- **2026-06-29 ~16:46Z** — Twenty-sixth pass (this pass); same 10 IDs, all Backlog. Ran `anchor_5a5_item3_scorer.py` against GRO-485. Scorer returned `verdict=SILENT`, canonical qualifying comment still the 12:01Z one (4.75h old, <6h threshold satisfied). Pass was textbook 5a.5/5a.7a-bis. **New tool-level lesson captured this pass:** Linear `comments(last:N)` returns the OLDEST N comments chronologically, NOT the newest N — a `comments(last: 1)` query on GRO-485 returned the 09:25Z first comment (looks plausible, is wrong data) and `[]` on the 9 other issues (looks like "no comments," but indistinguishable from "got 0 of 11" without a re-query with higher `last:`). Fix: always fetch with `last: 50` and slice `[-1]` in Python. Documented in `references/linear-dequeue-graphql-recipe.md` under the new "Quick reference — the `comments(last:)` footgun" section. 5a.5 4-of-4 + 5a.7a-bis 4-of-4 → `[SILENT]`. No `finalize_task.sh` invoked. No state mutation.

- **2026-06-29 ~16:31Z** — Sixteenth pass; same 10 IDs, all Backlog. Ran `anchor_5a5_item3_scorer.py` against GRO-485 a fifth time. Scorer returned `verdict=SILENT`, canonical qualifying comment still the 12:01Z one (4.49h old, <6h threshold satisfied). Textbook canonical 5a.5 pass — no deviation from recipe. 5a.5 4-of-4 → `[SILENT]`. No `finalize_task.sh` invoked. No state mutation. This was a clean textbook pass; the only new lesson was tool-level (see "Linear API case-sensitivity" note below).

**Linear API case-sensitivity pitfall captured this pass:** the `id:` filter value in `issue(id: "...")` is **case-sensitive** — must be uppercase (e.g. `"GRO-485"`, not `"gro-485"`). A pass that lowercases the identifier before query construction (e.g. via `i.lower()`) will receive HTTP 400 with no useful error body. The scorer script (`scripts/anchor_5a5_item3_scorer.py`) gets this right because the `--anchor GRO-485` arg is passed uppercase; hand-rolled probes that programmatically build issue IDs must mirror this. Captured in `references/linear-lane-filter-query.md`.

- **2026-06-29 ~14:24Z** — Ninth pass; same 10 IDs, all Backlog, anchor most-recent dequeue comment ~3h15min old, standing cure durable. 5a.5 4-of-4 + 5a.7a-bis 4-of-4 → `[SILENT]`. No `finalize_task.sh` invoked. No state mutation. Observed: the lane-filter `first: 30` query is a *noisy superset* — it surfaces 30 `agent:ned`-labeled issues in various states (In Review, In Progress, Canceled, Duplicate, etc.) that are NOT in the active scanner feed. The scanner feed (the 10 IDs in the cron preamble) is the authoritative input; the lane-filter query is a co-find for the partition-audit step (5a.1 / 5a.2), not a substitute for the explicit ID list.
- **2026-06-29 ~14:30Z** — Tenth pass; same 10 IDs, all Backlog. Most-recent comment on GRO-485 is a `## Ned finalization report` boilerplate (only `agent:` flag set, not the full 10-ID + standing-cure combo). Hand-rolled scoring loop walked all 9 anchor comments to find the canonical 5a.5-item-[3]-qualifying comment at 12:01Z (~2h25min old). Codified that scoring loop as `scripts/anchor_5a5_item3_scorer.py` so future passes don't redo the work. 5a.5 4-of-4 + 5a.7a-bis 4-of-4 → `[SILENT]`. No `finalize_task.sh` invoked. No state mutation.
- **2026-06-29 ~14:44Z** — Eleventh pass; same 10 IDs, all Backlog. Ran `anchor_5a5_item3_scorer.py` against the same anchor (GRO-485). Scorer walked all 9 anchor comments and identified the 12:01Z comment as canonical qualifying (2.72h old — well inside <6h). Notably, the *most recent* anchor comment (14:42Z, posted by a prior Ned cron pass in this same window) was another dequeue acknowledgment but **did not name all 10 batch IDs** — it's a quick "still holding, no drift" confirmation, not the canonical 5a.5-item-[3] full-marker comment. Scorer correctly skipped past it to find the 12:01Z full-marker comment. This is the **second consecutive pass** where the scorer's filter logic was exercised against a comment authored AFTER the canonical 12:01Z one — passes the "boilerplate-vs-full-marker discrimination" test cleanly. 5a.5 4-of-4 + 5a.7a-bis 4-of-4 → `[SILENT]`. No `finalize_task.sh` invoked. No state mutation.
- **2026-06-29 ~15:40Z** — Twelfth pass; same 10 IDs, all Backlog. Ran `anchor_5a5_item3_scorer.py` against GRO-485 again. Scorer returned `verdict=SILENT`, canonical qualifying comment still the 12:01Z one (3.65h old, <6h threshold satisfied); no new full-marker comment was authored this pass. No state mutation, no `finalize_task.sh` invoked. Batch B has now recurred **12 times today** without either of Michael's standing cures landing (relabel issues to correct agent lanes / patch `ned_delta_dispatcher.py` to require `lane:infra` co-label or title regex). Until one of those cures lands, this will recur on every cron pass. 5a.5 4-of-4 + 5a.7a-bis 4-of-4 → `[SILENT]`.
- **2026-06-29 ~15:56Z** — Thirteenth pass; same 10 IDs, all Backlog. Ran `anchor_5a5_item3_scorer.py` against GRO-485 a third time. Scorer returned `verdict=SILENT`, canonical qualifying comment still the 12:01Z one (3.92h old, <6h threshold satisfied). Notably, the most recent anchor comment (15:18Z, posted by `finalize_task.sh` boilerplate — confirms a prior pass in this same window reached the finalize step and posted the generic report comment) was correctly skipped: it has `has_lane_map: true` but does NOT name all 10 batch IDs and does NOT contain standing-cure language. This is the **third consecutive pass** where boilerplate-skipping logic was exercised cleanly — pass #10 hit the same `finalize_task.sh` boilerplate class, pass #11 hit a quick Ned acknowledgment without the full marker set, this pass #13 re-hits the finalize boilerplate. Scorer's filter is now proven against **two distinct low-signal comment classes** (finalize_task.sh boilerplate + short Ned cron acknowledgment) with 100% skip accuracy. 5a.5 4-of-4 + 5a.7a-bis 4-of-4 → `[SILENT]`. No `finalize_task.sh` invoked this pass. No state mutation.
- **2026-06-29 ~15:57Z** — Fourteenth pass (pass-24 in the unified pass-log); same 10 IDs, all Backlog. Scorer verdict: `SILENT`. Canonical qualifying comment still 12:01Z (3.94h old, <6h). Scorer walked 9 anchor comments and correctly skipped **three** distinct newer low-signal comments: 15:18Z `finalize_task.sh` boilerplate, 14:42Z short Ned acknowledgment (`has_standing_cure: true`, no batch IDs), and the various `## Ned finalization report` lines from prior cron passes. Filter validated across **four consecutive cron passes** (pass #10, #11, #13, #24) and **three distinct low-signal comment classes** with 100% skip accuracy. Also: this pass noticed `references/recurring-batch-suppress-2026-06-29.md` TL;DR still said "DO run `finalize_task.sh`" even though the 5a.5 gate (added pass-17) supersedes that advice — patched the TL;DR to put 5a.5 silent-protocol FIRST, demote finalize-run to a fallback for batches where 5a.5 is NOT eligible, and add a Batch B exception pointer back to this file. 5a.5 4-of-4 + 5a.7a-bis 4-of-4 → `[SILENT]`. No `finalize_task.sh`. No state mutation.
- **2026-06-29 ~16:15Z** — Fifteenth pass; same 10 IDs, all Backlog. Ran `anchor_5a5_item3_scorer.py` against GRO-485 a fourth time. Scorer returned `verdict=SILENT`, canonical qualifying comment still the 12:01Z one (4.23h old, <6h threshold satisfied). Most-recent anchor comment was the same 15:18Z `finalize_task.sh` boilerplate already validated-skipped in pass #13. Skipped past three distinct low-signal classes cleanly (finalize_task.sh boilerplate at 15:18Z, Ned-style quick acknowledgment at 14:42Z, older `## Ned finalization report` lines at 13:27Z and 11:40Z) and surfaced the 12:01Z full-marker canonical. 5a.5 4-of-4 + 5a.7a-bis 4-of-4 → `[SILENT]`. No `finalize_task.sh` invoked. No state mutation. Operational note for future passes: when invoking the scorer from a fresh terminal session, run `source /home/ubuntu/.hermes/profiles/orchestrator/.env` before invoking it — the script reads `LINEAR_API_KEY` from the environment and does not parse `.env` files itself (already documented in the scorer docstring §Invocation gotchas, item 3).

- **2026-06-29 ~17:25Z** — Twenty-seventh pass; same 10 IDs, all Backlog. Ran `anchor_5a5_item3_scorer.py` against GRO-485. Scorer returned `verdict=SILENT`, canonical qualifying comment still the 12:01Z one (5.4h old, <6h threshold satisfied). Textbook canonical 5a.5 pass — no deviation from recipe. 5a.5 4-of-4 + 5a.7a-bis 4-of-4 → `[SILENT]`. No `finalize_task.sh` invoked. No state mutation. Confirmed the cron-session invocation pattern works cleanly: `set -a; source /home/ubuntu/.hermes/profiles/orchestrator/.env; set +a; export LINEAR_API_KEY; python3 .../anchor_5a5_item3_scorer.py --anchor GRO-485 --batch-ids GRO-484,GRO-485,GRO-486,GRO-487,GRO-488,GRO-490,GRO-492,GRO-499,GRO-500,GRO-502 --age-threshold-hours 6` returned clean JSON verdict (`5a5_item3_satisfied: true`, `qualifying_comment.createdAt: 2026-06-29T12:01:31.056Z`, `age_hours: 5.4`, `verdict: SILENT`). Total ~6 tool calls: 1 skeleton read + 1 .env source check + 1 label/state probe + 1 scorer invocation + 1 verdict read + 1 final `[SILENT]` reply. Batch B has now recurred **27 times today** without either of Michael's standing cures landing. Recipe continues to fire cleanly; expect Batch B to recur indefinitely until one of the cures lands.

## 5a.5 item [3] programmatic verification

Item [3] of the checklist above (the qualifying anchor comment) used to be a hand-rolled scoring loop in the agent's `execute_code` block. As of pass #10 (2026-06-29 ~14:30Z) it's codified as `scripts/anchor_5a5_item3_scorer.py`.

The script walks all comments on the anchor, scores each against three flags (`names_all_batch_ids`, `has_standing_cure`, `has_lane_map`), picks the most recent one that satisfies all three AND is <6h old, and emits a JSON verdict (`SILENT` / `FULL_REPORT`). Use this BEFORE the recipe decision so the check is reproducible instead of memory-bound.

```bash
LINEAR_API_KEY=*** python3 scripts/anchor_5a5_item3_scorer.py \
  --anchor GRO-485 \
  --batch-ids GRO-484,GRO-485,GRO-486,GRO-487,GRO-488,GRO-490,GRO-492,GRO-499,GRO-500,GRO-502 \
  --age-threshold-hours 6
```

**Pitfall observed pass #10 (2026-06-29 ~14:30Z):** the most recent comment on GRO-485 was a `## Ned finalization report` boilerplate posted by `finalize_task.sh` itself — that comment has `agent:` (lane map) but does NOT name all 10 batch IDs and does NOT contain standing-cure language. A naive "newest comment is canonical" read would have failed 5a.5 item [3] and broken the SUPPRESS recipe. The scorer's job is to skip past boilerplate comments and find the most recent comment that was actually written to satisfy item [3].

**Reinforced pass #11 (2026-06-29 ~14:44Z):** the same boilerplate-skipping logic was needed against a *different* class of low-signal comment — a short Ned cron acknowledgment at 14:42Z that confirmed "still holding" but did not enumerate all 10 batch IDs. The scorer correctly walked past it and surfaced the 12:01Z canonical. This is a second-class low-signal pattern (Ned-style quick acknowledgment without the full marker set), distinct from pass #10's `finalize_task.sh` boilerplate. Both are correctly skipped; both classes will recur in future passes.

## Detector selector (when to apply this recipe vs. the canonical 9-step pattern)

Run these checks in order:

1. Apply the lane-filter query (`references/linear-lane-filter-query.md`) — **as a co-find / partition-audit only**:
   ```graphql
   query {
     issues(
       filter: {
         labels: { name: { eq: "agent:ned" } }
         state:  { name: { nin: ["Done", "Cancelled"] } }
       }
       first: 30
     ) { nodes { identifier state { name } labels { nodes { name } } } }
   }
   ```
   This is **NOT** the authoritative scanner feed. The active scanner feed is the explicit 10-ID list in the cron preamble. Use the lane-filter only to detect residual state drift on the 10 batch IDs; ignore the 30-issue superset (other `agent:ned` issues in In Review/In Progress/Canceled/Duplicate are prior work, not the current misroute).
2. Confirm **all 10 Batch B IDs are present** in the scanner feed (signature-overlap is not enough — partial overlap = fresh misroute, fall through to the 5a-vs-5-discriminator).
3. Confirm Batch B anchor (`GRO-485`) has ≥2 prior dequeue/triage comments AND the most recent one is <6h old. **Identity note:** these comments are authored under `user.name == "Michael Gulden"` (the Ned persona's Linear identity), not under any literal "Ned" user. When querying, filter on `body` content (`misroute` / `out of lane` / `relabel` / `dequeued` / `no finalize_task.sh`) — do not filter on `user.name`.
4. **When in doubt:** grep the most recent comment on `GRO-485` for `"no finalize_task.sh"`. If present, Batch B recipe applies regardless of signature match. Dequeue notes on the anchor are the authoritative recipe.

## Partition audit (5a.1 / 5a.2)

After posting the anchor comment (if 5a.5 doesn't fire), run the lane-filter partition query to detect residual state drift. Any issue in `In Review` or `Done` is residual drift from a prior pass — reverse it, post a brief reversal note on the drifted issue (not the anchor). For Batch B the observed drift baseline is `{Backlog}` for all 10 — any state outside that set is drift.

## See also

- `references/recurring-batch-suppress-2026-06-29.md` — Batch A quick reference (different anchor: GRO-537)
- `references/recurring-misroute-batch-playbook.md` — canonical two-batch playbook
- `references/linear-dequeue-graphql-recipe.md` — anchor comment GraphQL shape
- `templates/systemic-misroute-dequeue-comment.md` — boilerplate for the Batch B anchor acknowledgment