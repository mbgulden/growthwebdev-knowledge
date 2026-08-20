---
name: agy-autopilot-governance
description: Govern AGY autopilot dry-runs and completed-work lane proofs with one-task limits, preflight gates, packet ingestion, merge-backlog dry-run PR plans, and strict non-claim reporting.
---

# AGY Autopilot Governance

Use this skill when asked to run, verify, repair, or advance an AGY autopilot lane, including one-task dry runs, completed-work result packets, merge-backlog dry-run PR plans, or overnight-readiness guard design.

## Core principle

Treat AGY autopilot as a *governed lane proof*, not a general worker launch. The safe sequence is:

```text
preflight runtime + AGY config
→ resolve exactly one task to AGY
→ launch exactly one scoped AGY task
→ require AGY to emit a structured result packet
→ ingest packet through real completed-work API/CLI
→ read persisted row back
→ run merge-backlog classify/plan/verify dry-run
→ prove auto_merge=false and real_github_pr_created=false
→ stop
```

Never turn a one-task dry run into bulk dispatch, overnight mode, auto-merge, production deploy, or real PR creation without explicit Michael approval.

## Mandatory preflight

Before launching AGY, prove every prerequisite live on the deployed runtime:

1. Runtime git head is current enough for the lane. Prefer deployed endpoint markers and commit subject for squash-merged PRs; do **not** rely only on `git merge-base --is-ancestor <branch-sha> HEAD`, because squash merges intentionally break ancestry to the PR branch SHA.
2. Gateway service is active.
3. These local runtime endpoints return expected markers:
   ```text
   GET /api/completed-work/gate/schema        → AGY_COMPLETED_WORK_INTEGRATION_GATE_OK
   GET /api/agy/completed-work                → AGY_COMPLETED_WORK_INGESTION_OK
   GET /api/agy/merge-backlog                 → AGY_CLEAN_PR_AND_VERIFICATION_GATE_OK or current merge-backlog marker
   GET /dashboard                             → 200
   ```
4. AGY model/config probe returns nonzero output from a tiny prompt.
5. No AGY/Ned/bulk/autopilot worker is already running.
6. Operator stop path is explicit: terminate the specific AGY subprocess PID, then kill fallback; do not rely on vague “can stop if needed.”

Use marker:

```text
AGY_ONE_TASK_DRY_RUN_PREFLIGHT_OK
```

If any preflight fails, stop and report:

```text
AGY_AUTOPILOT_ONE_TASK_DRY_RUN_BLOCKED
```

## AGY CLI/model preflight

Probe the installed AGY CLI before selecting a model:

```bash
/home/ubuntu/.local/bin/agy --help
/home/ubuntu/.local/bin/agy models   # when available
/home/ubuntu/.local/bin/agy --print 'Reply with exactly: OK' --print-timeout 60s --model '<display model name>'
```

Model config labels used elsewhere may not match the installed CLI’s accepted names. Prefer the exact display name AGY reports, e.g. `Gemini 3.5 Flash (Medium)`, over stale internal aliases such as `gemini-3.5-flash`.

For isolated dry runs, use the installed AGY print/sandbox shape:

```bash
agy --print '<bounded prompt>' \
  --print-timeout 10m0s \
  --dangerously-skip-permissions \
  --sandbox \
  --add-dir /tmp/<isolated-canary-sandbox> \
  --model '<verified display model>'
```

Keep the sandbox outside the repo unless the task explicitly requires repository edits.

## One-task discipline

For “exactly one AGY task” runs:

- Count preflight probes separately from task launches.
- Launch **one** AGY task process at most.
- If AGY emits an invalid packet, do **not** run a second AGY task and do **not** synthesize/fix the packet yourself. Ingest/read back what AGY produced if possible, then report blocked/partial with the exact contract failure.
- Prove:
  ```text
  resolved_agent=agy
  preflight_agent=PASS
  launched_tasks=1
  no_other_tasks_launched=true
  bulk_dispatch=false
  auto_merge=false
  ```

## Result packet contract reminders

AGY may emit either of two dialects:

1. **Completed-work gate dialect** — includes `source_branch`, `source_path`, `base_branch`, object-shaped `lane_scope`, `changed_files`, and `proof`.
2. **AGY result packet dialect** — may use `branch`, `result_artifacts`, `merge_lane`, `verification`, `non_claims`, and `marker`, intentionally omitting internal gate fields such as `source_path`.

Before judging a packet, confirm the deployed runtime has the normalization adapter (`AGY_RESULT_PACKET_NORMALIZED_OK`) and ingest through the real completed-work API. The adapter should safely derive:

```text
source_branch = packet.source_branch or packet.branch
source_path   = first safe /home/ubuntu/... result_artifact OR controlled /home/ubuntu/.prismatic/agy-result-packets/<issue_identifier> fallback when issue+branch exist
base_branch   = packet.base_branch or main
lane_scope    = conservative object from merge_lane/verification_lane + changed_files
proof         = verification.result/commands/log_path + non_claims + marker
```

Preserve rejection for unsafe or underivable provenance: traversal, secret/config/token paths, generated/vendor paths, or packets with no issue/branch/artifact anchor should remain rejected. Do **not** synthesize a source path after AGY finishes; fix the adapter/prompt and rerun a new one-task proof.

Canonical AGY result packet shape for normalization tests:

```json
{
  "agent": "agy",
  "issue_identifier": "...",
  "branch": "feature/...",
  "base_branch": "main",
  "merge_lane": "docs",
  "changed_files": ["docs/example.md"],
  "result_artifacts": [{"path": "/home/ubuntu/.prismatic/agy-canaries/.../RESULT.md"}],
  "verification": {
    "result": "PASS",
    "commands": ["local canary artifact write; no repo mutation"],
    "log_path": "/tmp/fred-...log",
    "ad_hoc_or_canonical": "ad-hoc targeted runtime proof"
  },
  "non_claims": ["bulk_agy_dispatch", "overnight_autopilot_ready", "auto_merge_enabled", "production_deploy", "real_github_pr_created"],
  "marker": "AGY_TASK_RESULT_PACKET_OK"
}
```

Pitfall: if a row ingests but downstream completed-work classification is `rejected`, merge backlog action is `rejected`, or verification gate is `blocked`, the lane is **PARTIAL/BLOCKED**, not OK. Correct earlier optimistic summaries in the log/report before finishing.

## Limited overnight readiness guard

Use this when Michael asks for overnight-readiness guard design/implementation. The guard is a policy/control layer only — it must not start AGY, bulk dispatch, enable auto-merge, create real GitHub PRs, or claim overnight autopilot is active.

Core implementation shape:

```text
prismatic/agy_overnight_guard.py
scripts/agy_overnight_guard.py
/api/agy/overnight-guard (+ /api/gateway aliases)
dashboard card data-proof-marker="agy-overnight-guard-card"
tests/test_agy_overnight_guard.py
tests/test_agy_overnight_guard_api.py
```

Policy must fail closed on missing one-task proof, unavailable ingestion/merge-backlog/verification gate, `auto_merge=true`, `production_deploy=true`, real PR creation, bulk dispatch, unknown agents, excessive max_tasks, unresolved previous failure, active operator pause, or missing preflight/summary requirements.

Correct success marker:

```text
AGY_OVERNIGHT_READINESS_GUARD_OK
```

Correct final claim:

```text
AGY limited overnight readiness guard is implemented and verified, but overnight autopilot is not active.
```

Reference: `references/overnight-readiness-guard.md`.

## Limited guarded overnight dry-run runner

Use this when moving from the readiness guard to the first controlled AGY limited overnight dry run. Keep it guard-first, AGY-only, `max_tasks<=1`, and disabled-side-effects only: no bulk dispatch, auto-merge, production deploy, or real GitHub PR creation. Unit tests should fake AGY launch; only the final runtime proof may launch one real AGY task, and never a second repair task. If CLI and gateway state differ, prefer the live gateway dry-run endpoint for the final proof so guard evaluation, run persistence, completed-work ingestion, merge-backlog evaluation, and API readback use the same deployed state. When this lane is framed as continuing the assigned-agent recovery chain, preflight the assigned-agent queue/status markers before guard/model/launch and surface `assigned_agent_writeback_state=dry_run_no_live_linear_mutation` in persisted/API state. See `references/limited-overnight-dry-run-2026-07.md`.

## Operator-approved max_tasks=2 unattended-window guard

Use this only after Prompt 1 has live `AGY_LIMITED_OVERNIGHT_DRY_RUN_OK`. This is a control-plane slice, not a two-task run. The target is to prove the system can decide whether an operator-approved AGY-only `max_tasks=2` window would be allowed while launching **zero** AGY tasks.

Required properties:

```text
allowed_agents=["agy"]
max_tasks<=2
one_task_at_a_time=true
stop_on_first_failure=true
operator_approval_required=true
auto_merge=false
production_deploy=false
real_github_pr_create=false
bulk_dispatch=false
live_Linear_mutations=false unless explicitly approved
```

Implementation shape:

```text
prismatic/agy_unattended_window.py
scripts/agy_unattended_window.py
/api/agy/unattended-window/status
/api/agy/unattended-window/evaluate
/api/agy/unattended-window/request-approval
/api/agy/unattended-window/approve
/api/agy/unattended-window/pause
/api/agy/unattended-window/resume
+ /api/gateway aliases
tests/test_agy_unattended_window.py
tests/test_agy_unattended_window_api.py
```

Pitfall: older overnight-readiness code may only recognize `AGY_AUTOPILOT_ONE_TASK_DRY_RUN_OK` as predecessor proof. For Prompt 2, make the compatibility layer also accept `AGY_LIMITED_OVERNIGHT_DRY_RUN_OK` / `AGY_LIMITED_OVERNIGHT_DRY_RUN_PACKET_OK`, or live evaluation can 409 with `latest one-task AGY proof missing` even though Prompt 1 succeeded. Preserve both marker families and add regression coverage.

If a PR is merged/deployed before a late compatibility fix is found, do not force-push a deleted/stale branch. Extract only the missing compatibility diff onto fresh `origin/main`, open a small follow-up PR, wait for CI, then deploy/read back.

Correct success marker:

```text
AGY_LIMITED_UNATTENDED_WINDOW_GUARD_OK
```

Correct final claim:

```text
The operator-approved max_tasks=2 unattended-window guard is implemented, tested, deployed, and live. It proves whether a two-task AGY window would be allowed. It did not launch two AGY tasks, and overnight autopilot is still not unbounded or active.
```

See `references/unattended-window-guard-2026-07.md`.

## AGY shared skill pool — placement and registration (2026-08-18)

AGY CLI skill discovery does **not** read Hermes profile skill dirs. Every AGY run (launched by prismatic-consumer with `AGY_CLI_HOME` → kai profile home, whose `~/.gemini` symlinks to `/home/ubuntu/.gemini`) shares ONE skill pool: `/home/ubuntu/.gemini/config/skills/` (flat `*.md` files, frontmatter `name`/`description`/`tags`/`related_skills`, `agy-as-*` lane pattern).

Placement procedure for a new AGY skill:

1. Write the skill as a flat `.md` in `~/.gemini/config/skills/` with the lane frontmatter.
2. Register it in `~/.gemini/config/skills/agy-lane-system-index.md` (one list line) — without the index entry, AGY's skill routing won't pick it up.
3. Verify: file exists with mode 644, frontmatter parses, index line present.
4. Durability: the pool is **not git-tracked** (`git rev-parse` → not a repo). Back up before edits; for durable versioning, commit a copy into `growthwebdev-knowledge` (e.g. `okf/playbooks/`) and say so in the closeout.
5. Never place an AGY skill in `~/.hermes/profiles/agy/skills/` — that's the Hermes `agy` profile's dir, not AGY CLI discovery.

Session detail (discovery evidence + example: `agy-okf-infrastructure-update`): `references/agy-shared-skill-pool-placement-2026-08.md`.

## Stale Hermes verification guard refresh

When Hermes posts a stale verification warning after code edits, do not argue with it or reuse old evidence. Refresh it literally:

1. Remove the stale `/tmp/hermes-verify-*` paths named in the warning.
2. Create a fresh OS-safe tempfile under `/tmp` with prefix `hermes-verify-`.
3. Run focused verification against the changed behavior.
4. Clean up the fresh verifier and named stale files.
5. Report a compact proof as `ad-hoc targeted; not canonical full suite` unless the real canonical suite ran.

If the warning names changed paths under `/home/ubuntu/work/prismatic-engine`, run the fresh verifier against that workspace checkout and those exact changed paths, not only against the deployed runtime under `/home/ubuntu/.prismatic/runtime/prismatic-engine`. Runtime readback is useful for live lanes, but it does not satisfy a workspace stale-detector complaint about edited files.

Pitfall: stale mobile-overflow output like `/tmp/hermes-verify-mobile-branch-390.py` is not evidence about the current AGY guard; it is just the guard’s remembered failure.

## Shared completed-work skill-pack contract wiring

Use this after the limited dry-run / unattended-window guard layers are green and the next improvement is agent output quality. Keep this as repo-level docs/static verifier unless Michael explicitly asks to mutate live Hermes profiles.

Target marker:

```text
AGENT_COMPLETED_WORK_SKILL_PACKS_OK
```

The docs/config slice should encode shared and agent-specific packet discipline so AGY/Fred/George/Kai naturally emit `source_path`, proof, artifacts, non-claims, and safe file scope. Required acceptance proof:

```text
shared_contract_exists=true
agy_packet_example_has_source_path=true
proof_packet_example_has_command_result_log_scope_nonclaims_marker=true
non_claims_example_present=true
agent_specific_skill_matrix_present=true
no_secrets_in_docs=true
```

Do not claim skills are installed in all live profiles, agents retrained, overnight autopilot active, auto-merge enabled, production deployed, or canonical full-suite green. See `references/completed-work-skill-pack-contract-wiring.md`.

## Post-run lane proof

After AGY completes:

1. Ingest through real runtime API/CLI; avoid mock/demo rows.
2. Read back the exact completed-work row by ID.
3. Verify latest row endpoints:
   ```text
   GET /api/agy/completed-work?limit=1
   GET /api/agy/merge-backlog?limit=1
   GET /api/agy/merge-backlog/{completed_work_id}
   POST /api/agy/merge-backlog/{completed_work_id}/verify
   ```
4. Verify `/api/gateway/...` aliases when dashboard/public proof matters.
5. Confirm:
   ```text
   eligible_for_auto_merge=false
   github_pr_created=false
   production_deploy=false
   ```
6. If tied to Linear, write back once. For local canaries, state `Linear writeback: not applicable`.

Success markers:

```text
AGY_RESULT_PACKET_INGESTED_OK
AGY_MERGE_BACKLOG_DRY_RUN_OK
AGY_PR_VERIFICATION_DRY_RUN_OK
AGY_AUTOPILOT_ONE_TASK_DRY_RUN_OK
```

Blocked marker:

```text
AGY_AUTOPILOT_ONE_TASK_DRY_RUN_BLOCKED
```

## Verification output shape

Do not stream AGY logs or API dumps into chat. Use a `/tmp/hermes-verify-agy-one-task-dry-run-*.py` tempfile verifier and log full detail under:

```text
/tmp/fred-agy-one-task-autopilot-dry-run-verify.log
```

Compact proof shape:

```text
COMMAND=<exact verifier command and key follow-up curl/API commands>
RESULT=<PASS|PARTIAL_BLOCKED|BLOCKED>
LOG=/tmp/fred-agy-one-task-autopilot-dry-run-verify.log
SCOPE=one AGY autopilot dry run from preflight through result packet ingestion, merge backlog dry-run PR plan, verification gate, dashboard/API writeback
AD_HOC_OR_CANONICAL=ad-hoc targeted runtime proof
NOT_CLAIMING=bulk_agy_dispatch,overnight_autopilot_ready,auto_merge_enabled,production_deploy,canonical_full_suite_green,real_github_pr_created
MARKER=<AGY_AUTOPILOT_ONE_TASK_DRY_RUN_OK or AGY_AUTOPILOT_ONE_TASK_DRY_RUN_BLOCKED>
```

## References

- `references/agy-one-task-overnight-guard-2026-07.md` — July 2026 AGY canary lessons: one-task proof boundaries, result-packet normalization before completed-work gating, readiness-only overnight guard policy, and compact stale-detector proof format.

- `references/one-task-dry-run-blocked-source-path.md` — session-specific detail from the first one-task dry run: squash-merge preflight, AGY display model names, and `source_path` packet rejection.
- `references/packet-normalization-rerun-ok.md` — follow-up fix detail: AGY result-packet normalization, CI/security-scanner pitfall, deploy proof, and successful exactly-one-task rerun marker.
- `references/agy-skill-conformance-review-recipe.md` — pre-deploy conformance review for AGY skill builds (closeout-contract, etc.) against the Prismatic Engine standard. Includes the auth-wall fallback recipe (tree index + telemetry + skill registry + arming-gate-as-spec), the "one build, two names" pitfall, the knowledgebase frontmatter rule, and a reusable review checklist.
- `references/agy-skill-conformance-review-permissive-validator-2026-08.md` — second-pass pitfalls for AGY skill conformance reviews: the "100% CLEAN" permissive-validator trap (`check_sha_files=False` + missing negative-direction consistency check → false PASS receipts), the disk-first fallback when Antigravity publishes full-text packets to `scratch/` on the same host (skip the gateway probes — `ls` the advertised scratch path), and a 5-item checklist extension that promotes structural-guess findings to verified divergences once the standard text is reachable.

## Reviewing an AGY skill build against the Prismatic standard (pre-deploy)

When Antigravity (or any agent) ships a skill/handoff and the question is "is this according to the Prismatic Engine standard?", the workflow differs from running AGY — you're auditing the *shape*, not dispatching work. The full recipe lives in `references/agy-skill-conformance-review-recipe.md`. Three pitfalls to keep in this umbrella:

- **Auth-walled standard text is a limit, not a license.** The Prismatic workspace file API is auth-walled. Do not guess paths, scrape the SPA bundle, or fetch by path probing. The workable fallback is tree index + live telemetry + arming-gate oracle. Declare "structural conformance only" up front when text diffs aren't reachable.

- **One build, two names.** Antigravity sometimes titles the same deliverable twice (e.g. "the closeout-contract skill build" and "the AGY CLI skill update for producing packets"). Don't fragment the request into two parallel reviews; ask once whether they are the same unit and proceed.

- **The AGY real-executor arming gate is the field-shape oracle.** When the standard's text is unreachable, the live arming-gate contract is the closest authoritative shape source for `non_claims[]`, `missing_prerequisites[{key, required_value, actual_value}]`, status enums, marker namespace, and fail-closed semantics. Treat it as a free spec, not just telemetry.

- **Disk-first when the build author publishes scratch packets on the same host.** If the handoff names a scratch path with `0644` perms and the advertised IP is local to this host, skip the gateway probes entirely — `ls` and `cat` the scratch packet directly. The auth-wall fallback is the right default when no scratch path exists; see `references/agy-skill-conformance-review-permissive-validator-2026-08.md` §B for the recipe and the diagnostic shortcut.

- **"100% CLEAN" local-test receipts from a permissive validator are not receipts.** The shipped `validate_closeout_packet.py` runs `main()` with `check_sha_files=False` and has no negative-direction consistency check — a BLOCKED packet with empty `BLOCKERS` and `RESULT: "PASS"` validates green. Always probe the validator's permissive defaults before accepting a "100% CLEAN" claim. See `references/agy-skill-conformance-review-permissive-validator-2026-08.md` §A for the five-item reviewer discipline.

Pitfalls inherited from the wider skill-distribution discipline:

- The dual-tree deliverable (engine `prismatic/skills/<name>/` + `.agents/skills/<name>/`) must be generated, not hand-maintained.
- An auto-injector (`prompts/assigned-agent-prompt4-packet-gate.md`) may already exist; check before building a duplicate.
- The knowledgebase tree frontmatter rule rejects every doc without valid YAML — new SKILL.md must satisfy it or be rejected on arrival.

Additional pitfalls captured 2026-08-04 from the closeout-contract review where Antigravity had published full-text review packets to `scratch/` on the same host:

- **The auth-wall fallback is the right default, but check the filesystem FIRST when the build author says "full text is staged at path X".** Antigravity published `scratch/FRED_FULL_TEXT_REVIEW_PACKET.md` containing the actual standard-body text (`docs/agy-result-packet-contract.md`, `docs/execution-evidence-contract.md`, `docs/seven-step-loop.md`) plus the full validator source, plus all three example packets. Several rounds of probing the public gateway were wasted before realizing the host is `192.168.1.59` (same IP the Antigravity handoff cited) and the packet was reachable at the absolute path it named. The workable diagnostic is `hostname -I` once, then if local, `ls` the advertised scratch paths and read directly. Never substitute "auth-walled, structural only" for "I didn't try the disk first."

- **"100% CLEAN" local-test receipts from a permissive validator are not receipts.** The shipped `validate_closeout_packet.py` runs `main()` with `check_sha_files=False` and contains no negative-direction consistency check (BLOCKED-status packet with empty BLOCKERS and a fabricated SHA validates green). The example JSONs hardcode `LOG_SHA256 = e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` (the empty-file SHA) and ship without log files in the skill tree. A reviewer reading "100% CLEAN" must verify: (a) does the validator's `main()` default to permissive flags? (b) are the example log files actually shipped? (c) does the validator enforce both directions of consistency (PASS ⇒ clean AND BLOCKED ⇒ contradictions flagged)? If any answer is "no," the receipt proves only that the JSON parses and matches the schema — not that the build is conformant. See §10 of `references/agy-skill-conformance-review-recipe.md`.

- **When the standard's text is reachable, the divergent marker is no longer speculation — it is a verified divergence.** The standard mandates `marker: "AGY_TASK_RESULT_PACKET_OK"` for the raw-AGY dialect; the build's examples all emit `"MARKER": "AGY_STRUCTURED_CLOSEOUT_CONTRACT_NEEDED"` (a request marker, not an outcome marker). With the standard body in hand this becomes a hard rejection item, not a "should we reconsider?" comment. Promote divergences like this from the "needs further investigation" pile to the rejection list the moment the text is reachable.

- **One build, two names resolution is the cue to stop fragmented review.** When the user confirms "skill X and skill Y are the same thing," do not split the review into two parallel efforts. Treat the handoff's section-1 deliverables list as the unit of review and proceed. A prior skill build was delivered twice-named for the same `prismatic-agent-closeout-contract` deliverable; the correct response was one exhaustive conformance check, not two.