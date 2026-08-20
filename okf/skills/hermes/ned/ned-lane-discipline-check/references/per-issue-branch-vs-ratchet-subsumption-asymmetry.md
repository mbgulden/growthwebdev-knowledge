# Per-issue branch vs ratchet-branch subsumption asymmetry (Pass-N+48, 2026-06-30 ~12:14Z)

**Codified from the GRO-2995 cron pass.** The Pass-N+44 codification listed GRO-2995 as row 5 of the canonical telemetry-wiring-subtask auto-routing example, flagged ⚠️ "subsumed by GRO-2981 (Vertex telemetry write path runs in orchestrator poller; Ned lane lacks the poller boundary)". That classification is correct for the **scanner-rotation-disposal** pass on the `ned/gro-485-triage-pass-1` ratchet branch — but is **WRONG** for the **per-issue-branch pickup** on `ned/GRO-2995` where genuine in-Ned's-lane work exists. This asymmetry was the load-bearing new finding from this pass and corrects a misclassification that would have caused a suppression-with-subsumption on a legitimate task.

## The two pass types are structurally distinct

| Property | Ratchet branch pass (`ned/<GATE>-triage-pass-1`) | Per-issue branch pass (`ned/GRO-XXXX`) |
|---|---|---|
| **Trigger** | Scanned scanner feed showing 10 mixed `[Ned]`/`[SILENT-CRON]` issues | Single-issue pickup with branch pre-positioned by cron |
| **Branch** | `ned/<GATE>-triage-pass-1` (single-day log) | `ned/GRO-XXXX` (per-issue feature branch) |
| **Recipe** | Pass-N+19 actual-execution OR Pass-N+25 lightweight ratchet | 9-step commit-early skeleton from `ned-autonomous-task-loop` |
| **Output** | Audit doc + commit on ratchet branch + `[SILENT]` | Real implementation commits + `finalize_task.sh` |
| **Subsumption verdict** | Most `[Ned]` items are subsumed by a prior Ned investigation | Each `[Ned]` item must be re-evaluated on its own merits |
| **Work product** | Per-pass audit doc (`scripts/ops/gro-<low>-<high>-batch-routing-Nth-pass-infra-findings.md`) | Source code + tests + finalize evidence |

**The Pass-N+44 subsumption table applies to the ratchet branch ONLY.** When the same issue ID appears on a per-issue branch with prior in-progress commits, you must evaluate in-lane execution potential independently.

## Why GRO-2995 is in-lane on the per-issue branch

GRO-2995 acceptance criteria (3 items):
1. Add writer method `record_vertex_spend(project_id, model, region, credits, operation, recorded_at)` to `prismatic/vertex_telemetry.py` — ✅ IN-LANE (Ned owns `prismatic/`).
2. Wire it into every GCP Vertex call site — ⚠️ PARTIALLY OUT-OF-LANE.
3. Verify with `SELECT COUNT(*) FROM gcp_vertex_spend_events WHERE recorded_at > datetime('now','-7 days')` returns > 0 — ✅ verifiable AFTER wiring.

Item 2 is the discriminator. The reference doc (Pass-N+44 + `references/gro-2980-child-wiring-execution.md` §"NOT-YET-EXECUTED recommendations") flagged that the engine doesn't directly call Vertex APIs (verified: `grep -rIn 'vertexai|vertex_ai|GenerativeModel|gemini-2\.5' prismatic/` returns nothing). AGY CLI calls Vertex. So a literal reading of item 2 would say "out of Ned's lane — orchestrator profile's `agy_pool_aware_router.py` / `provider_dispatch.py` / `agy_quota.py`."

**But the reference doc listed three alternative paths within Ned's lane:**
- **Option A** — wire at `vertex_telemetry.py:poll_vertex_quota()` site (within `prismatic/`, Ned's lane)
- **Option B** — wire at `prismatic/dispatcher.py:1489` validation-event site (within `prismatic/`, Ned's lane)
- **Option C** — escalate to Michael

**Option A is in-lane.** The poller that calls `poll_vertex_quota()` → `VertexBillingLedger.record_quota_snapshot()` lives entirely inside `prismatic/vertex_telemetry.py`. The "Vertex call site" wording in item 2 is ambiguous — it could mean (a) "every place that MAKES a Vertex call" (out of lane — AGY does this) OR (b) "every place that RECORDS spend on Vertex work" (in lane — the ledger poller does this). Interpreting it as (b) makes the task in-Ned's-lane and solvable via Option A without any cross-profile writes.

## Diagnostic recipe (Apply before any per-issue PASS judgment)

When a per-issue branch has prior commits AND the issue is `[Ned]` tagged AND the parent issue's prior investigation root-caused the family:

1. **Check Pass-N+44 subsumption table** in `references/telemetry-wiring-subtask-misroute-pattern.md`. If the item is ⚠️ subsumed, **the subsumption only applies on the ratchet branch.** Verify the per-issue branch's state independently.
2. **`git log --oneline HEAD ^main -- <related-files>`** on the per-issue branch — what work has already happened? Are there uncommitted WIP file edits in the working tree (the "committed-but-lost-from-working-tree" pattern documented in `references/gro-2992-lost-wiring-restored-2026-06-30.md`)?
3. **`grep -rIn '<topic>' <ned-owned-lanes>/`** — does any option live entirely within `prismatic/`, `scripts/`, or `plugins/`? If yes, the issue is in-lane for execution. If no, then it IS cross-profile and the Pass-N+44 subsumption applies.
4. **`git status --short`** — distinguish tracked modifications vs untracked files. Per Pass-N+34 working-tree isolation, untracked sibling-owned files must NOT be swept by `git add -A` or `git commit -am`. If `git mv` is needed for lane-compliance test-file placement (`tests/` → `prismatic/` per Pass-N+34), do it explicitly.
5. **Only after all 4 checks pass** apply the 9-step skeleton: lock → branch (already on it) → heartbeat → read → write + commit → test → finalize → push → report.

## Ratchet-branch checklist when a per-issue branch is mid-flight

If both a ratchet pass AND a per-issue branch have related work on the same issue (proven Pass-N+48 case: GRO-2995 has had per-issue WIP across multiple cron ticks while the ratchet branch lists it as ⚠️ subsumed):

- **Per-issue branch** executes Option A regardless of ratchet-branch verdict
- **Ratchet branch** audit doc records: "this issue is genuinely in-flight on `ned/GRO-XXXX` — supersedes Pass-N+44 ⚠️ subsumption marker; the per-issue branch's working tree has Option A wiring uncommitted. Do not finalize from the ratchet side; wait for per-issue finalize to land."
- **Pass-N+44 subsumption table entry** should be amended to "⚠️ subsumed-by-GRO-2981 ONLY on ratchet-branch scanner disposal; per-issue branch `ned/GRO-2995` is executing Option A (Vertex quota poller site) — see Pass-N+48 update"

## Worked example (Pass-N+48, GRO-2995)

Setup:
- Scanner feed contained GRO-2995 as part of the `[Ned]` telemetry-wiring-subtask auto-routing batch
- Pass-N+44 says GRO-2995 is ⚠️ subsumed by GRO-2981
- BUT the cron script pre-positioned `ned/GRO-2995` branch with prior test commits (`ea46d3cd` + `ba117a5e`)
- Working tree on `ned/GRO-2995` has uncommitted additions: 99-line `prismatic/telemetry.py` diff + Option A wiring in `vertex_telemetry.py` + 2 new wiring tests + test-file relocation

Pass-N+44 subsumption would have suppressed with `[SILENT]` and left the WIP orphaned. The Pass-N+48 diagnostic correctly classified GRO-2995 as a per-issue in-flight branch with a legitimate Option A in Ned's lane, and executed the wiring.

## See also

- `references/telemetry-wiring-subtask-misroute-pattern.md` — the ratchet-branch subsumption table; the entry for GRO-2995 needs amending per Pass-N+48
- `references/gro-2992-lost-wiring-restored-2026-06-30.md` — the "committed-but-lost-from-working-tree" regression discovery recipe
- `references/gro-2980-child-wiring-execution-2026-06-30-update.md` §C — Option A's recommended wiring shape (now executed in Pass-N+48)
