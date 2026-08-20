# Sustained SILENT-CRON subset + cadence irregularity playbook (Pass-N+47..53, 2026-06-30)

**Codified from Pass-N+47 through Pass-N+53** — sustained cron passes on a **stable 4-ID SILENT-CRON wrong-lane subset** that emerged after a feed-shrink dropped 6 SUBSUMED-by-GRO-2981 in-lane items. The subset (GRO-2998/2999/3011/3012) has been byte-identical across 7 consecutive passes (Pass-N+47..53); the recipe scaled cleanly across both sub-15-min cadences (Pass-N+48→49 at 10 min, Pass-N+52→53 at 11 min) and an irregular cadence (Pass-N+47→48 at 2h 27min due to runtime-failed ticks). Four refinements surfaced (three original + one new from Pass-N+53):

## Refinement 1 — Pass-N+31 filename rule needs a sibling rule for "when neither shifts"

The Pass-N+31 filename rule (codified 2026-06-29 ~22:44Z) says: "When both shift, shift both." Pass-N+49 exercised the inverse: when the scanner feed is byte-identical to the prior pass on BOTH LOW and HIGH (LOW=2998 HIGH=3012 same as Pass-N+48), the filename stays identical to the prior pass's filename.

**Canonical filename rule (full):**

```
filename_low = current_scanner_feed.lowest_gro_id
filename_high = current_scanner_feed.highest_gro_id
N = branch_commit_count_on_ned_gro-485-triage-pass-1 + 1

if (filename_low != prior_pass.filename_low) AND (filename_high != prior_pass.filename_high):
    # BOTH SHIFTED — Pass-N+31 case
    filename = f"gro-{filename_low}-{filename_high}-batch-routing-{N}th-pass-infra-findings.md"
elif (filename_low != prior_pass.filename_low) XOR (filename_high != prior_pass.filename_high):
    # ONE SHIFTED — original Pass-N+21 sub-case
    # Shift only the changed segment; keep the unchanged segment from prior pass
    filename = f"gro-{filename_low if filename_low != prior_pass.filename_low else prior_pass.filename_low}-{filename_high if filename_high != prior_pass.filename_high else prior_pass.filename_high}-batch-routing-{N}th-pass-infra-findings.md"
else:
    # NEITHER SHIFTED — Pass-N+49 case
    # Filename is byte-identical to prior pass's filename (only N changes)
    filename = f"gro-{filename_low}-{filename_high}-batch-routing-{N}th-pass-infra-findings.md"
```

**Codified as a single decision tree:**
- Both shifted → shift both (Pass-N+31)
- One shifted → shift only the changed (Pass-N+21)
- Neither shifted → keep both (Pass-N+49; only N in the suffix increments)

The ordinal counter in the filename (`Nth-pass`) is the rotation signal; the LOW+HIGH segments track the CURRENT scanner feed, not the prior pass's.

## Refinement 2 — Anchor cascade vs single-anchor discipline

The current SKILL.md frames anchor freshness as a single anchor (lowest-GRO-ID of the prior pass, age <6h). Sustained-feed passes like Pass-N+49 actually have an **anchor cascade** to track:

| Anchor | Age (Pass-N+49) | Role | Coverage |
|--------|------------------|------|----------|
| Pass-N+48 commit `8e4317ba` at 13:01Z | ~10 min | **Controlling anchor** | Names all 4 boundary IDs explicitly |
| Pass-N+47 commit `a6211321` at 10:34Z | ~2h 37min | **Boundary-ID-covering anchor** | Names GRO-2998 + GRO-3012 explicitly (boundary IDs) |
| Pass-N+46 anchor on GRO-2990 at 10:27Z | ~2h 44min | Supersession anchor | Names GRO-2990..3012 (full 10-ID range pre-shrink) |

Both (a) the controlling anchor AND (b) the boundary-ID-covering anchor are valid freshness proofs for the rotation-equivalence ratchet's criterion (c). The cascade is the ratchet's load-bearing durability mechanism — single-anchor framing undersells it.

**Canonical criterion (c) formulation (revised):**

Criterion (c) HOLDS if ANY of the following is true:
- **(c.1) Controlling anchor:** the most recent commit on `ned/gro-485-triage-pass-1` is <6h old AND explicitly names all current-feed IDs (or all current-feed boundary IDs in a feed-shrunk case).
- **(c.2) Boundary-ID-covering anchor:** any prior commit on `ned/gro-485-triage-pass-1` within the past 6h explicitly names the lowest and highest GRO-IDs of the current feed (boundary IDs only — middle IDs may be covered transitively if they share a partition with the boundary IDs).
- **(c.3) Cascading anchor chain:** there exists a chain of commits where each commit's anchor names either the lowest or highest GRO-ID of the current feed, and the chain covers the full 6h window.

In practice, (c.1) is the most common case; (c.2) is the Pass-N+49 case; (c.3) is rare but covers cross-day cascades.

## Refinement 3 — Cadence irregularity within a sustained-feed chain

Pass-N+47→48 gap: 2h 27min (irregular, due to runtime-failed ticks at 11:01Z + 11:24Z + 11:51Z + 12:28Z + 12:48Z that didn't commit)
Pass-N+48→49 gap: 10 min (back to sub-15-min cadence)

The Pass-N+25 lightweight 3-step ratchet recipe scaled cleanly to BOTH intervals. The 5-condition gate is interval-agnostic:
- Prior anchor freshness: absolute 6h window, not relative to cadence
- Names all feed IDs: structural requirement, not cadence-dependent
- Feed byte-identical: structural requirement, not cadence-dependent
- SUBSUMED/wrong-lane holds: structural, not cadence-dependent
- Rotation-equivalence ratchet (a)+(b)+(c): structural, not cadence-dependent

**Codification:** when a prior pass has an irregular cadence (>30 min gap), the current pass should NOT skip the freshness check just because the anchor is "old." The threshold is 6h absolute, not relative to the cadence. The recipe's interval-agnosticism is a feature, not a bug: it lets the cron recover from runtime failures (OOM kills, scheduler stalls, sibling-agent lock contention) without re-running the full disposal recipe.

**Document the cadence observation explicitly in the audit doc's "Cadence observation" line.** Pass-N+48's commit message noted: "cadence observation ~2h 27min gap (longer than sub-15-min Pass-N+44..47 cadence due to 11:01Z + 11:24Z + 11:51Z + 12:28Z + 12:48Z runtime-failed tick attempts not committing — recipe scales cleanly to irregular intervals when conditions hold)." Future reconstructors reading the chain will see the cadence patterns and can correlate with scheduler/runtime logs.

## Refinement 4 — Alert-staleness verification probe (NEW — Pass-N+53, 2026-06-30 ~13:45Z)

The Pass-12 probe-skip protocol (and the implicit pattern across Pass-N+48..52) skips infra probes (GPU/disk/locks/Tailscale) on SILENT-pass execution because the ratchet's (a)+(b)+(c) criteria are STRUCTURAL and don't require re-probing infrastructure every pass. That protocol is correct as far as it goes — but **for SILENT-CRON subset issues specifically, the alert itself (the cron job the issue names) is a load-bearing claim that should be spot-checked periodically, not structurally trusted.**

Pass-N+53 ran a single fresh probe on the alert's subject — the cron jobs named in the 4 SILENT-CRON issues:
- **`faf8d91da716` AGY Sandbox Supervisor** (the subject of GRO-3011/3012): `pgrep -af agy_sandbox_event_supervisor` → returned PID 2892010 alive running `python3 -u agy_sandbox_event_supervisor.py --cron-mode --from-linear --max-concurrent 3 ...` since at least 2026-06-30 09:41Z. The `event_supervisor_run_*.json` files in `/archive/agy_sandbox_results/` are being actively produced.
- **`fred-persistent-monitor` Fred Persistent Factory Monitor** (the subject of GRO-2998/2999): `pgrep -af fred_persistent_monitor` → returned PID 2959434 alive. `tail -5 ~/.hermes/profiles/orchestrator/inbox/heartbeat.log` → `[2026-06-30 13:44:53 UTC] alive=True new_results=0 failures=0` (5-min cadence, clean).

**Result:** Both cron jobs ARE HEALTHY right now. The `last_status="error"` field on both cron job entries (the trigger for the "silent-failing" Linear title) is stale — it records the 06:59:47 tick that hit the 7200s timeout (the monitor is designed to run continuously for 48h, but cron ticks it as a 7200s-bounded job, so it WILL trip timeout repeatedly; new monitor instance auto-restarts on the next cron tick). The classifier that built the `[SILENT-CRON]` titles read `last_status="error"` as "still failing" when in fact the most recent ERROR was a self-recovering timeout, not a true outage.

**Why this matters:** the sustained-suppress ratchet holds structurally regardless of whether the alert is real or stale. But the **standing-cure narrative** in the audit doc and Linear comment thread is different for "stale false positive" vs "real persistent failure":
- **Stale false positive:** the cure is to update the Tier-1 silent-failure watchdog's classifier to ignore `last_status="error"` when a newer process is alive + heartbeat-clean. The cure lives in the orchestrator's watchdog/aggregator scripts, not in the cron jobs themselves.
- **Real persistent failure:** the cure is to fix the cron job itself (e.g. extend timeout, fix restart logic).

Knowing which one we're dealing with shapes the standing-cure ask to Michael. Pass-N+48..52 carried the standing-cure text as if it were a real persistent failure (the watchdog hasn't run for hours / days). Pass-N+53's fresh probe revealed the more accurate narrative: it's a classifier false positive on a self-recovering timeout pattern.

**Codification — alert-staleness verification protocol:**

| Pass count on the SILENT-CRON subset | Recommended probe action |
|--------------------------------------|--------------------------|
| Pass-N+47 (first sighting) | Run full infra probe (GPU/disk/locks/Tailscale) + alert-subject probe (pgrep on the named cron jobs + heartbeat log tail). First sighting = unknown whether real or stale. |
| Pass-N+48..52 (sustained, ~1-5 passes in) | Skip infra probes per Pass-12 protocol. Skip alert-subject probe too IF the prior pass already verified alert subject is healthy. Probe-skip applies to both kinds of probes. |
| Pass-N+53..+60 (sustained, ~6-10 passes in) | Run alert-subject probe on EVERY Nth pass where N is divisible by 5-10 (i.e., spot-check every 5-10 passes). This catches the case where the alert became stale since the last spot-check. |
| Pass-N+60+ (very sustained) | Same as 53-60. The probe cadence doesn't change with pass count; the question is just whether the alert became stale. |

**Probe cost:** ~1 tool call per spot-check (`pgrep -af <subject> && tail -5 <heartbeat_log>`). Negligible vs the audit-doc + commit cost (~5 tool calls).

**Update to standing-cure text:** when the alert-subject probe reveals health (PID alive + heartbeat clean), the audit doc's standing-cure section should explicitly note "the alert is a Tier-1 watchdog classifier false positive on a self-recovering 7200s timeout pattern, NOT a real persistent failure" and reframe cure (b) as "patch the Tier-1 silent-failure watchdog to ignore `last_status=\"error\"` when a newer process is alive + heartbeat-clean" rather than "patch the GRO-559 dispatcher." This is a meaningful refinement — Pass-N+48..52 standing-cure text was less precise.

**Cross-reference:** the alert-staleness probe is structurally distinct from the Pass-12 infra probes (GPU/disk/locks/Tailscale) and the Pass-N+25 ratchet criteria (a)+(b)+(c). All three coexist on the SILENT-CRON subset passes: ratchet checks structural consistency, Pass-12 skips infra re-probes, alert-staleness probe verifies the alert subject is still healthy. Each has a different cadence and purpose.

## Pass-N+47 → ... → Pass-N+53 evidence trail

| Pass | Time | Filename | Commit | Anchor used | Verdict |
|------|------|----------|--------|-------------|---------|
| N+47 | 10:34Z | gro-2990-3012-batch-routing-47th-pass-infra-findings.md | `a6211321` | Pass-N+46 on GRO-2990 at 10:27Z (~7 min) | SUPPRESS |
| N+48 | 13:01Z | gro-2998-3012-batch-routing-48th-pass-infra-findings.md | `8e4317ba` | Pass-N+47 at 10:34Z (~2h 27min, names boundary IDs) | SUPPRESS |
| N+49 | 13:11Z | gro-2998-3012-batch-routing-49th-pass-infra-findings.md | `e400e162` | Pass-N+48 at 13:01Z (~10 min) + Pass-N+47 cascade (names boundary IDs) | SUPPRESS |
| N+50 | 13:23Z | gro-2998-3012-batch-routing-50th-pass-infra-findings.md | `a82913fc` | Pass-N+49 at 13:11Z (~12 min) + cascade | SUPPRESS |
| N+51 | 13:28Z | gro-2998-3012-batch-routing-51st-pass-infra-findings.md | `505afb9b` | Pass-N+50 at 13:23Z (~5 min) | SUPPRESS |
| N+52 | 13:34Z | gro-2998-3012-batch-routing-52nd-pass-infra-findings.md | `176e773e` | Pass-N+51 at 13:28Z (~6 min) | SUPPRESS |
| N+53 | 13:45Z | gro-2998-3012-batch-routing-53rd-pass-infra-findings.md | `79e71a2e` | Pass-N+52 at 13:34Z (~11 min) + alert-subject probe (NEW) | SUPPRESS |

The 4 SILENT-CRON items remain on `agent:ned` with `Backlog` state across all passes — Michael has not acted on the standing cure since the watchdog auto-filed them at 2026-06-29T15:54Z. Pass-N+53 added an alert-subject probe (per Refinement 4) which confirmed both cron jobs are alive and heartbeat-clean — refining the standing-cure narrative from "real persistent failure" to "Tier-1 watchdog classifier false positive on a self-recovering 7200s timeout pattern."

## Standing cure (verbatim from Pass-N+47/Pass-N+48, still open)

Two-path remediation ask:

(a) **Relabel the 4 SILENT-CRON items to their correct lanes:**
- GRO-2998 + GRO-2999: drop `agent:ned`, add `agent:fred`
- GRO-3011 + GRO-3012: drop `agent:ned`, add `agent:orchestrator`

(b) **Patch the GRO-559 dispatcher lane-content filter** to drop `agent:ned` when no correct co-label exists AND no description-narrative justification supports the label. This is the durable cure (orchestrator lane work).