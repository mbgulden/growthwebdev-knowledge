---
name: linear-backlog-routing-governance
description: Audit and remediate Linear backlog routing when dispatch-ready issues are blocked by unmet prerequisites, stale labels, completed dependencies, or rate-limited Linear API access.
category: operations
---

# Linear Backlog Routing Governance

Use this skill when a backlog watchdog, morning digest, or user flags Linear issues as blocked/stale, especially when `dispatch:ready` items have prerequisites that may or may not be complete.

## Core principle

Do **not** make the queue look cleaner by pretending work is done. Separate three cases:

1. **Prerequisite is truly complete** — Linear state is completed, and evidence/comment exists or was already posted.
2. **Prerequisite is still incomplete** — downstream issue must not remain `dispatch:ready`; hold it and explain the unmet blocker.
3. **Prerequisite state is unknown** — do not guess. Use live Linear if available; if Linear is rate-limited, schedule a retry and report the concrete blocker.

## Workflow

0. **When the user asks for comprehensive epics/tasks and immediate remediation**
   - Create a parent launch/governance epic plus child issues grouped by real blocker class, not one issue per observation. Use explicit P0/P1 priority in titles and write exit criteria into each child.
   - When converting an approved strategy/plan into Linear, preserve the plan’s phases as dependency-ordered children: put the plan title/location, product decision, privacy/non-goals, and success metric in the parent; put concrete deliverable, dependencies, and exit criteria in each child.
   - Link evidence artifacts and audit notes in the parent and children so later agents can verify without re-reading the entire session.
   - Apply the named agent owner label to **every** parent/child requested by the user. To prevent premature parallel execution, mark only the first truly unblocked foundation slice `dispatch:ready`; mark dependent children `dispatch:paused` with their dependency in the description. Do not label a task ready merely because it was created.
   - Read back the created tree live: parent/child relationship, project, agent-owner labels, and ready/paused routing must all match the approved sequence. Clean up temporary mutation/verifier scripts afterwards.
   - Put only the parent epic in-progress initially if it represents active orchestration; put the first few directly actionable P0 children in-progress/dispatch-ready and leave downstream/blocked items in Todo.
   - Then roll directly into resolving the highest-risk P0s. Do not stop after creating Linear structure when the user explicitly says to “roll into resolving” or “wire everything up.”
   - Keep parent epics open until child exit criteria are evidenced; never close the parent because a subset of runtime smoke tests passed.

1. **Recover the exact blocker graph**
   - Read the watchdog/digest output first.
   - Extract downstream issue → prerequisite issue(s).
   - Treat natural-language “blocked by” notes as hypotheses until verified against Linear state.
   - For broad no-agent backlog gap tables, distinguish true ownerless/unrouted gaps from already-routed work. If an issue already has `dispatch:ready`, `dispatch:paused`, or a concrete owner label (`agent:fred`, `agent:agy`, `agent:jules`, `agent:kai`, etc.), do not repeat it to Michael as an unresolved gap; verify the routing and leave it to the owner lane unless labels conflict with explicit guardrails. See `cron-failure-remediation/references/nightly-backlog-gap-routing-and-transient-backup-retry.md`.

2. **Query current Linear state**
   - For each downstream and prerequisite issue, collect:
     - identifier
     - title
     - workflow state name/type
     - labels
     - latest useful comment/evidence when available
   - Prefer one batched GraphQL query when possible to avoid rate pressure.
   - When using the local `linear_api_compat.linear_call()` shim, normalize response shape before concluding a query returned no rows. In this environment the shim may return the GraphQL `data` object directly (`payload["issues"]["nodes"]`) rather than a top-level `{ "data": ... }` wrapper.
   - When calling Linear GraphQL directly, distinguish credential type before building the `Authorization` header: raw `LINEAR_API_KEY` is sent without `Bearer`, while OAuth tokens use `Bearer`. Validate a minimal issue-number query before running mutation batches. If team-local label lookup misses routing labels, query workspace-global `issueLabels(first: 250)`. If `issueSearch(term:)` is unsupported, switch to issue-number lookup or create a bounded owner-routed issue rather than retrying the same failing search. See `references/linear-api-auth-and-global-label-lookup-2026-07-18.md`.

2a. **For full open-task audits and AGY routing triage**
   - Live Linear can return a much larger non-completed backlog than a factory digest's narrowed queue lens. State both numbers plainly if they differ.
   - Separate `AGY-ready now`, `Candidate to hand to AGY`, `Actually needs Michael`, `Human-review label cleanup/triage`, `Other-agent ready`, and `Fred-ready/orchestration`.
   - Treat `agent:needs-human-review` as a triage signal, not proof Michael is needed. Only mark `Actually needs Michael` for explicit manual send/publish/recording, approval/decision, credential/billing/access, or named Becca/Ella/Michael feedback blockers.
   - Avoid broad keyword overreach: generic `post`, `publish`, or `review` in long descriptions can be technical work, not a user blocker. Prefer title + explicit blocker wording.
   - Produce a compact Telegram summary plus full Markdown/CSV artifacts, then verify artifact row count/buckets/no-secret-smoke with a `/tmp/hermes-verify-*` script.
   - See `references/open-task-agy-routing-audit.md`.

2aa. **For handoff-contract dispatch preflight slices**
   - Keep schema/semantic validation in a reusable module and make the CLI a thin wrapper; do not duplicate a second validator for runtime preflight.
   - Wire the smallest assigned-agent launch-boundary preflight and activate it only for explicit embedded handoff payloads (`handoff_packet`, `handoff_contract`, or `handoff`) so ordinary dispatch behavior is unchanged.
   - Fail closed with clear states: invalid handoffs are `blocked`, empty/ambiguous target agents are `needs_manual_review`, and no agent launches until the packet is fixed.
   - Land this primitive before any AGY completed-work integration gate, then reuse it to classify completed work as merge-ready / clean-rebuild / blocked / superseded / manual-review.
   - For repeated stale-verification reminders on this class of work, emit the exact plain-text proof block with the detector's changed paths and marker rather than escalating verbosity. See `references/handoff-contract-dispatch-preflight.md`.

2ab. **For post-canary staged AGY dispatch**
   - Treat dispatch/canary proof and output acceptance as separate gates. A successful one-task canary means staged work may be possible; it does not mean the PR/artifact is merge-worthy.
   - Review the AGY output PR normally against the Linear acceptance criteria before opening the next stage. If the output is incomplete, post exact fixes to GitHub + Linear and keep the issue in review.
   - When fixing scorecard/rubric outputs, do not invent baseline scores. Use `TBD by <baseline issue>` and make evidence commands/expected markers explicit until the baseline task runs.
   - Only after the canary output is merged/accepted should the next small stage be marked ready. Never bulk-redispatch the backlog from a canary proof.
   - Preserve assigned-agent wake semantics when routing is involved: Kai -> Kai, Fred -> Fred, AGY -> AGY, unknown/ambiguous -> manual review.
   - After launching a controlled small stage, review each output as a normal deliverable. If outputs are blocked, pause redispatch labels, post exact fixes, and split/replace mixed-scope PRs rather than merging because dispatch succeeded.
   - See `references/post-canary-staged-agy-dispatch-review.md` and `references/controlled-two-task-agy-output-cleanup.md`.

2b. **When Michael directly disposes audit results**
   - Treat direct calls like “already done,” “cancel it,” “make it an OKF doc,” and “move the rest to AGY” as authoritative queue governance.
   - Cancel stale/done issues and remove operational `agent:*`/`dispatch:*` labels so they cannot be reprocessed.
   - Convert doc-only items to OKF/Fred work, land the durable OKF artifact from a clean worktree, and post the OKF evidence back to Linear.
   - Route remaining executable work with `agent:agy` + `dispatch:ready`, then run a second readback/cleanup pass because dispatchers may immediately move items to In Progress while leaving stale `agent:needs-human-review` labels attached.
   - See `references/user-directed-linear-agy-routing-cleanup.md`.

2c. **Clean `agent:needs-human-review` sludge as a governance batch**
   - When Michael approves this cleanup, query the current open NHR queue live; do not rely on the earlier audit count because the queue can grow while you work.
   - Treat `agent:needs-human-review` as a triage signal, not proof Michael is needed. Keep it only for explicit manual send/publish, recording/interview/audio, credential/billing/access, approval/decision, or named Michael/Becca/Ella feedback blockers.
   - For true blockers: keep `agent:needs-human-review`, add `dispatch:paused`, and remove `dispatch:ready`.
   - For non-blockers: remove `agent:needs-human-review`, remove stale peer/paused labels, add `dispatch:ready`, and route to the correct executable lane (`agent:agy`, `agent:jules`/implementation fallback, `agent:fred`, existing owner, or peer review).
   - Run a second live readback and cleanup pass. Dispatchers may immediately move routed issues to In Progress and reattach/retain NHR, and new NHR issues may appear after the first preflight.
   - Verify until the only remaining open NHR issues are true blockers with `dispatch:paused` and without `dispatch:ready`.
   - See `references/needs-human-review-sludge-cleanup.md`.

2d. **After dispatch recovery/canary proof: move to staged output review, not bulk redispatch**
   - When recovery markers are accepted (queue/drain/preflight/wake/canary/writeback), treat that as permission for **staged controlled work only**, never backlog-wide redispatch.
   - First review the canary agent's actual output PR/artifact as a normal deliverable. Do not merge merely because the dispatch path worked.
   - Review the deliverable against the issue acceptance criteria and the user's explicit review checklist. For scorecard/rubric work, require per-item `Current Score`, `Target Score`, `Evidence`, `Gap`, `Blocker`, `Owner`, and `Next Action` fields, not just a 10/10 inventory.
   - Treat calendar-dependent tests as a release blocker even when current CI is green: any freshness/window fixture with a literal date must freeze the production clock or derive its timestamps from one frozen UTC instant. Re-run the focused test independently before accepting the PR.
   - If the PR is not good enough, keep the Linear issue in review, post exact fixes to GitHub + Linear and do **not** open the next dispatch stage.
   - When the authenticated GitHub identity authored the PR and cannot submit a formal “request changes” review, post the same blocking feedback as a normal PR comment, mirror the exact blocker to Linear, and keep the issue in review.

   - Run live readback after comments/merge decisions: PR state, Linear state/comment, changed file scope, and whether recommended next-stage issues were untouched.
- If a controlled stage produces useful but blocked output, do the cleanup actively: create owner-lane replacement PRs, close superseded mixed PRs, rerun verification under the correct owner, and only then move Linear to Done.
   - Before launching a follow-on stage after successful output acceptance, run a short post-stage drift cleanup: remove stale `dispatch:ready` from completed upstream issues, park local WIP branches without deleting them, and reset the active worktree to a clean base.
   - During a manual controlled runner, remove `dispatch:ready` from the selected issues before launch and add `output:requires-verification` so the regular dispatcher cannot duplicate the run and the result remains review-gated.
   - If AGY pushes a branch but does not open a PR, open the PR yourself, post the link to Linear, and keep the issue in `In Review`. If Linear drifts back to `In Progress`, correct it back to `In Review` with a comment.
   - See `references/staged-dispatch-output-review.md`, `references/controlled-two-task-agy-output-cleanup.md`, and `references/post-stage-drift-two-task-stage.md`.
      - For the follow-on step after a canary output is accepted, launch only the explicitly named next issues with a hard-guarded runner, capture per-issue proof artifacts, and move results to review rather than Done. See `references/controlled-two-task-agy-stage.md`.

2e. **After production durability repair: run the runway audit before resuming backlog**
   - Treat accepted production markers as a new starting gate, not permission to resume from memory.
   - First rerun the fallout gate: systemd `WorkingDirectory`, runtime checkout branch/head/clean state, local `/workspace-tree`, safe preview, and traversal block.
   - Redact any saved `systemctl cat` artifact because service units can include secrets.
   - Then run live repo/GitHub/Linear audit. If dev `main` is ahead with WIP auto-checkpoint commits, park them on a backup branch and reset `main` to `origin/main` before starting new work.
   - Select 1–3 next Fred tasks from evidence; start only the first narrow branch. Do not bulk-dispatch.
   - See `references/post-durability-runway-audit-and-first-slice.md`.

   3. **Classify each chain**
   - If **all prerequisites are completed**:
     - downstream should have `dispatch:ready`
     - remove stale `agent:needs-human-review` / `agent:peer-review` if they only represented the old blocker
     - keep/add the correct owner label, often `agent:fred` for infrastructure/governance follow-ups unless another owner is already present
   - If **any prerequisite is incomplete**:
     - downstream should **not** have `dispatch:ready`
     - add/keep `agent:needs-human-review` or the appropriate hold label
     - comment with the exact unmet prerequisites
   - If a **prerequisite itself is completed**:
     - remove stale `dispatch:ready`, `agent:peer-review`, `agent:needs-human-review`
     - add/keep `agent:done`

4. **Apply changes conservatively**
   - Never move a prerequisite to Done unless you have direct evidence for its exit criteria.
   - It is safe to clean labels from an issue Linear already marks completed.
   - It is safe to release a downstream issue only when every prerequisite is already completed.
   - It is safe to hold a downstream issue when any prerequisite is not completed.

5. **Handle Linear rate limits as a first-class state**
   - If Linear returns rate-limit errors, stop repeated live mutation attempts on the exhausted credential.
   - Before deferring, check whether the profile has a fresh Linear OAuth token (`linear_oauth_token`, `oauth_token`, or `LINEAR_OAUTH_TOKEN` in the usual credentials/env files). Linear accepts OAuth as `Authorization: Bearer <token>` and it may have separate budget from the raw `LINEAR_API_KEY`.
   - If OAuth works, rerun the deterministic retag/mutation path with `LINEAR_API_KEY="Bearer <token>"` or equivalent request headers, then verify live Linear labels.
   - If both credentials are rate-limited/unavailable, write or reuse a deterministic retry script that performs the same classification after reset.
   - Schedule a one-shot cron after the reset window.
   - Report: what is ready to release, what remains blocked, and whether live mutation was applied via API key, OAuth fallback, or scheduled retry.

6. **Mitigate persistent Linear API leaks after budget work is “Done”**
   - If rate limits persist even though the LinearBudget/dispatcher work appears complete, do **not** redo broad research first.
   - Check for the active burn source in this order:
     - live poller processes (`pgrep -af 'prismatic-engine serve|prismatic.dispatcher|dispatcher.py'`), especially `prismatic-engine serve` with `PRISMATIC_POLL_INTERVAL=30` and `LINEAR_API_KEY` in `/proc/<pid>/environ`
     - **user-systemd** units as well as system units. `systemctl is-active prismatic-dispatcher.service` can be inactive while `/home/ubuntu/.config/systemd/user/prismatic-dispatcher.service` is running under `user@1000.service`. Use `XDG_RUNTIME_DIR=/run/user/1000` and `DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus` for `systemctl --user ...` from non-login shells.
     - high-frequency no-agent jobs still calling Linear directly
     - raw `urllib.request`, `urlopen`, `requests.post`, `curl`, or `https://api.linear.app/graphql` usage outside the shared budget gate
     - cron schedule contradicts the job name or `paused_reason` (for example a “daily safety-net” still running every 5 minutes)
   - Emergency mitigation for a confirmed poll-driven dispatcher is: terminate only the exact poller PID, disable the user unit, and add a reversible `ConditionPathExists=/home/ubuntu/.prismatic/allow-poll-dispatcher` drop-in so accidental starts skip until an operator creates the allow-file. Verify no log growth and no exact poller process. See `references/user-systemd-poll-dispatcher-linear-burn.md`.
   - Patch sibling legacy scripts together so every `query_linear()`/`linear_gql()`/ad-hoc shell helper routes through the shared compatibility shim / budget gate with caller-specific `cron.*` attribution.
   - For shell crons, add/use a thin CLI wrapper that reads `{query, variables}` from stdin and calls the same shim; do **not** keep raw `curl https://api.linear.app/graphql` in scheduled scripts.
   - Prefer reducing broad pollers to daily safety-net cadence when webhook/event/delta-cache paths are primary.
   - Make the fix permanent-permanent: add a guard script that scans **enabled active cron jobs** for raw Linear GraphQL usage and schedule it as a recurring no-agent cron. The guard must fail on future bypasses and allow only explicit exceptions such as the shim itself, token refresh, inactive legacy scripts, or documented one-off migrations.
   - Document the policy in OKF/standards so future dev follows the budgeted shim until a better central provider exists.
   - See `references/linear-api-leak-cron-fleet-2026-07.md` for the July 2026 cron-fleet mitigation pattern, permanent guard, and verifier.

6a. **When the active burn is dispatcher polling, stop the poller before redesign**
   - Distinguish **request-count exhaustion** from GraphQL complexity exhaustion using live `x-ratelimit-*` headers.
   - Check both system and user systemd scopes; the poller can be a user unit even when the system unit is inactive.
   - For an emergency stop, disable the poll-driven dispatcher and add a reversible `ConditionPathExists=/home/ubuntu/.prismatic/allow-poll-dispatcher` gate instead of deleting the unit. Keep gateway/event-consumer/merge services running when healthy.
   - The first durable code slice is a shared Linear request-count circuit breaker: record response headers, detect `RATELIMITED`, persist cooldown until reset, skip broad dispatcher polling during cooldown, and expose state in gateway/dashboard.
   - Do not spend the last Linear requests on exploratory broad audits. Mock Linear in verification and use local runtime/API readback.
   - See `references/linear-event-driven-dispatch-recovery-2026-07.md`.

6b. **Make dispatcher polling a bounded safety net, not the primary path**
   - Keep the old 30-second poller disabled/gated while implementing the fallback. Do not remove the `ConditionPathExists=/home/ubuntu/.prismatic/allow-poll-dispatcher` kill switch unless replacing it with an equal or stronger gate.
   - Add a per-cycle Linear GraphQL budget around dispatcher `gql()` calls. Budget exhaustion must skip remaining broad scans and write visible status; it must not create a crash loop.
   - Add TTL caching for broad label/team scans such as `get_issues_with_label(...)`; track cache hits/misses in status and return copies from cache.
   - Pace broad scan sections independently: pipeline setup, route/capability scan, agent scans, stalled recovery, and origin-completion detection should not all run every fallback tick.
   - Respect the Slice 1 rate-limit circuit before every broad fallback scan: if cooldown is active, spend zero additional Linear requests and mark `rate_limit_cooldown_active=true`.
   - Surface `polling_budget` in dispatcher and Linear rate-limit APIs with `max_calls_per_cycle`, `last_cycle_calls`, `calls_by_source`, cache hit/miss summary, `skipped_sections`, `last_skip_reason`, and cadence values.
   - Verify with mocked/no-live-Linear focused tests plus runtime API readback. Do not claim webhook queue activation or assigned-agent event dispatch from this slice.
   - See `references/dispatcher-polling-budget-safety-net-2026-07.md`.

6c. **Restore assigned-agent event dispatch without cross-agent stealing**
   - Start this slice only after the rate-limit circuit breaker, bounded polling safety net, and durable Linear webhook queue are already proven.
   - Implement a single resolver that maps durable queue/webhook metadata to exactly one intended known agent (`kai`, `fred`, `agy` minimum). Missing, conflicting, or unknown metadata must fail closed to `needs_manual_review` with zero wakes.
   - Treat known-but-disabled agents as resolved targets that fail preflight (`blocked_preflight`) rather than waking another agent. Never fall back from one agent lane to another.
   - Preflight the exact resolved agent before wake: row not already claimed/running/completed, agent enabled, launcher/runtime available enough, and shared Linear cooldown gate closed.
   - Persist operator-visible routing/preflight/dispatch fields on the queue row: `target_agent`, `routing_source`, `resolver_status`, `preflight_status`, `dispatch_status`, `claim_owner`, `run_id`, `last_error`, `updated_at`.
   - Fixture proof should use dry-run/stub launchers: `agent:kai` wakes only Kai, `agent:fred` only Fred, `agent:agy` only AGY, ambiguous/missing/unknown/disabled/claimed/cooldown wakes nobody.
   - Keep result/blocker writeback as a separate next slice unless actual agent completion/result writeback is implemented and proven; do not claim `ASSIGNED_AGENT_RESULT_WRITEBACK_OK` from resolver/wake proof alone.
   - See `references/assigned-agent-event-dispatch-recovery-2026-07.md`.

6d. **Persist assigned-agent result/blocker writeback safely**
   - Start this slice only after exact-agent resolver/preflight/wake is proven. The contract is: `agent run result/blocker → durable queue/run state → dashboard/operator visibility → explicit dry-run Linear writeback proof → retry/recovery status → no live mutation unless authorized`.
   - Persist result/writeback/retry/recovery fields on durable queue rows: `result_status`, `result_summary`, `blocker_summary`, `writeback_status`, `writeback_mode`, `writeback_preview`, `writeback_at`, `retry_status`, `retry_count`, and `recovery_status`.
   - Default to dry-run Linear writeback. Store the exact comment/update preview as operator-visible proof and report `linear_mutation=False`.
   - Completed results should become `completed/not_required/completed`; blocker results should become `blocked/blocked_until_operator_review/blocked`; failed results should become `failed/retry_eligible/failed_retryable`.
   - Retry must be explicit: move the row back to `pending`, increment `retry_count`, and set `retry_status=retry_requested`, `recovery_status=queued_for_retry`.
   - If live Linear writeback is requested without explicit authorization, fail closed with `blocked_live_unauthorized` and prove zero live mutation.
   - Expose `result_writeback_marker=ASSIGNED_AGENT_RESULT_WRITEBACK_OK` and latest result/writeback/retry fields through the queue status API/dashboard surface.
   - See `references/assigned-agent-result-writeback-recovery-2026-07.md`.

6e. **Finish assigned-agent recovery with one integrated controlled-task proof**
   - After resolver/preflight/wake and result/blocker writeback slices are separately proven, add a final recovery marker that exercises the whole chain for exactly one controlled queued task: resolver → preflight → exactly-one wake → dry-run result writeback.
   - The target marker is `ASSIGNED_AGENT_DISPATCH_RECOVERY_OK`. Do not claim it from separate slice proofs alone; the verifier must call the integrated helper/path and assert all phases are true in the same run.
   - Use temp state and a clearly controlled fixture identifier, usually `agent:kai` or another explicit known agent. Assert `chain_proof=resolver:true,preflight:true,wake:true,result_writeback:true`.
   - Expose `dispatch_recovery_marker=ASSIGNED_AGENT_DISPATCH_RECOVERY_OK` in the queue status API/dashboard surface so operators can see the combined recovery gate is present.
   - Keep non-claims explicit: no live Linear mutations, no old poller re-enabled, no bulk redispatch, no canonical full-suite green unless the full suite actually ran.
   - See `references/assigned-agent-dispatch-recovery-integrated-proof-2026-07.md`.

7. **Verify before reporting done**
   - `LINEAR_WEBHOOK_QUEUE_ACTIVE_OK` proves durable webhook intake, bounded drain, and API/dashboard visibility only; it does not prove exact-agent wake/dispatch.
   - Persist `/api/gateway/linear` and `/webhooks/linear` issue events into `linear_webhook_queue.db` (or a clearly documented equivalent) with an idempotency key, identifier, action/type, received time, raw/sanitized payload, and dispatch status.
   - Make duplicate fixture events idempotent: exactly one durable row and no duplicate dispatch work.
   - Keep drain bounded (`--max`/once semantics). Tests should inject a stub dispatch function to prove exactly one intended attempt without live Linear mutations.
   - Check the shared Linear rate-limit circuit before drain dispatch attempts; cooldown must record a deferred/blocked status such as `deferred_rate_limit` and make zero dispatch calls.
   - Expose queue depth, pending/processed/status counts, latest event identifier/status, `last_drain_at`, `last_drain_result`, source, and marker in API/dashboard.
   - Do not unmask/enable `prismatic-webhook-drain.service` or timer until `ExecStart` points at the runtime checkout or stable venv, never the mutable dev worktree.
   - See `references/linear-webhook-queue-active-2026-07.md`.

7. **Verify before reporting done**
   - For code/scripts: run `python3 -m py_compile` on changed Python entrypoints and the focused pytest/test command that covers the changed behavior when one exists.
   - Create an OS-safe temp verifier under `/tmp` using `tempfile` with a `hermes-verify-` filename prefix; do not hand-pick a reusable verifier path.
   - The temp verifier should import or execute the changed code against a small fixture that proves the exact contract under discussion. For cron/health-noise fixes, include one active failure and paused/retired/disabled historical failures, and assert only the active failure escalates while archive records are suppressed.
   - Mock Linear states to test both release and hold paths:
     - completed prerequisites are cleaned and marked `agent:done`
     - complete downstream chains get `dispatch:ready`
     - incomplete downstream chains lose `dispatch:ready` and get a hold label
     - explanatory comments are generated
   - For API-leak mitigation, mock the Linear shim instead of making live Linear calls; assert each patched cron routes through the shared budget gate and forwards GraphQL variables unchanged.
   - If a post-edit verifier/system reminder says the workspace is unverified, rerun fresh verification in the current turn; do not rely on previous-turn evidence. Summarize the temp verifier path, key assertion/output, focused test/compile output, and cleanup result.
   - When CI lint fails outside the PR diff while local lint passes, reproduce the **release installation surface** in a clean temporary venv (`pip install -e '.[release]'`) and run the exact CI lint/format file list. Ambient tools can hide dependency/config drift. If an unbounded lint dependency resolved a newly incompatible release, constrain its compatible range narrowly, verify the resolved version plus exact CI commands in a new clean venv, and wait for CI on the new head before accepting. Do not mass-format unrelated files merely to green a feature PR. See `references/clean-release-lint-drift.md`.
   - For an incremental journal collector, verify same-inode truncate/rewrite rotation—not merely file-size shrinkage. Persist a trailing cursor-anchor hash, reset to offset zero on anchor mismatch, dedupe normalized events by a stable content key, and quarantine malformed operational lines outside recaps. See `references/incremental-journal-cursors.md`.
   - Before treating a live event index as canonical, measure stable-ID coverage, duplicate-key rate, event/source distribution, and legacy-vs-new rows. Passing cursor tests prove new input only; legacy rows without stable IDs are unverified and must be backed up and isolated before any rebuild or current-health claim.
   - Before activating an evidence-cited recap against a real event index, run one bounded live-render smoke from a neutral working directory (so imports resolve to the installed runtime, not a nearby worktree). Assert: rendered claims are capped, every displayed claim has an evidence ID, the CLI result returns compact counts rather than a full ID array, and daily/weekly artifact sizes remain operationally bounded. Audit quarantine signal quality too: banners/decorative output must not become a second unbounded log store. If an oversized local recap was already written, preserve it under a repair backup before regenerating only after the corrective PR clears review/CI. See `references/journal-corpus-integrity-and-recap-bounds.md`.
   - For Fred/Kai/AGY verifier runs where output can get long, write detailed logs to `/tmp/<agent>-<issue>-<topic>-verify.log` and print only a compact marker packet to chat/stdout. Include `CANONICAL_TEST_LINT_BUILD_COMMAND=...`, `AD_HOC_VERIFICATION=PASS|FAIL`, exact `changed_paths_checked`, `NOT_CLAIMING=...`, `cleanup=PASS|FAIL`, and the final marker as plain-text `KEY=VALUE` lines when detectors are sensitive. See `references/compact-verification-output.md`.
   - When the slice's changed paths include a Python CLI (`scripts/*.py`), the verifier MUST also clear `__pycache__/` next to the edited script (or run with `python3 -B`) before the round-trip. Stale bytecode shadows the edited source and produces green output against the wrong code. The verifier wrapper itself MUST import every module it uses (`json`, `os`, `sys`, `subprocess`, `tempfile`, `shutil`) so a missing import doesn't `NameError` AFTER the inner verifier prints PASS. See `agent-operations/session-state-handoff/references/python-cli-pitfalls.md` pitfalls #3 and #7.
   - Review time-sensitive regressions for a hidden live-clock dependency even when CI is green: if production code compares against `datetime.now()` (or equivalent) and a fixture hard-codes a "fresh" date, freeze the same clock in the test or derive fixtures from a frozen instant. A test that only passes on the current calendar date is a blocking review finding. After fixing it, rerun focused tests and wait for CI on the **new head commit** before merging.
   - If a stale detector lists exact changed paths, rerun a fresh `/tmp/hermes-verify-*` verifier scoped exactly to those paths; JSON-only summaries may be missed, so emit the compact plain-text block. If the detector repeats, stop elaborating and emit only the final plain-text `KEY=VALUE` block with `AD_HOC_VERIFICATION=PASS`, the exact absolute `changed_paths_checked` list from the reminder, and `cleanup=PASS`. See `references/repeated-stale-detector-compact-proof.md`.
   - Clean up the temp verifier and explicitly label this as **ad-hoc targeted verification**, not full-suite green.

8. **Respect repo lane governance before pushing or PR creation**
   - Before editing or cherry-picking into a repo, compare the target files against the active agent's lane ownership. If the fix touches out-of-lane files, it is fine to inspect and locally verify when asked to review, but do not bypass hooks or force-push.
   - If the lane guard blocks push/PR, treat that as the correct governance outcome: post Linear evidence/self-review with the local branch/commit, verification scope, and the exact lane blocker, then route to the owner lane or request an explicit exception.

## Reporting format

Use a concise table:

| Downstream | Prerequisites | Action |
|---|---|---|
| GRO-XXXX | GRO-YYYY, GRO-ZZZZ | Release as `dispatch:ready` |
| GRO-AAAA | GRO-BBBB | Hold; remove stale `dispatch:ready` |

Then include:

- Linear mutation status: applied / scheduled / blocked
- verification scope: ad-hoc targeted vs canonical suite
- any remaining true blockers

## Pitfalls

- Do not close parent epics early just because children moved.
- Do not let completed prerequisites keep `dispatch:ready`; they will be re-processed noisily.
- Do not keep downstream `dispatch:ready` when a prerequisite is not completed; this creates churn and false blocker reports.
- Do not treat session history as proof of current Linear state when Linear is accessible. Use live Linear first.
- Do not burn Linear API quota with many tiny calls if a batched query can answer the state graph.
- Do not assume `IssueFilter.identifier` exists in every Linear schema. If a lookup by issue key fails schema validation, query by team key plus numeric `number` instead, e.g. `issues(filter:{team:{key:{eq:"GRO"}}, number:{in:[575,653]}}, first:20)`. Capture the schema-safe query pattern, not the transient validation failure.

## References

- `references/linear-blocker-retagging-2026-07.md` — session-derived pattern for retagging a six-issue blocker graph, including rate-limit retry and ad-hoc verifier shape.
- `references/open-task-agy-routing-audit.md` — pattern for auditing the live non-completed Linear backlog into AGY-ready, AGY-candidate, Michael-needed, stale human-review, other-agent, and Fred orchestration buckets without over-routing noisy `agent:needs-human-review` labels.
- `references/user-directed-linear-agy-routing-cleanup.md` — pattern for applying Michael’s direct queue-disposition calls: cancel done/stale issues, convert doc-only work to OKF, route remaining work to AGY, clean stale NHR labels, and verify live Linear + OKF evidence.
- `references/needs-human-review-sludge-cleanup.md` — class pattern for reducing noisy `agent:needs-human-review` queues: preserve true Michael blockers, route non-blockers to executable lanes, run second-pass drift cleanup, and verify only paused true blockers remain.
- `references/handoff-contract-dispatch-preflight.md` — pattern for converting a handoff contract/schema/CLI validator into a narrow assigned-agent dispatch preflight gate with exact compact verification and non-claims.
- `references/post-canary-staged-agy-dispatch-review.md` — after recovery/canary proof, review the canary output PR/artifact normally before opening the next stage.
- `references/post-durability-runway-audit-and-first-slice.md` — after production durability/live-route repairs, rerun fallout proof, audit live repo/GitHub/Linear state, park dirty/ahead dev `main` before branching, select the next Fred sequence from evidence, and start only one narrow slice.
- `references/controlled-two-task-agy-stage.md` — hard-guarded follow-on dispatch for only the explicitly approved next issues, with per-issue artifacts and review-gated outputs.
- `references/controlled-two-task-agy-output-cleanup.md` — pattern for cleaning a controlled two-issue AGY stage after output review: pause redispatch on blocked outputs, create owner-lane replacement PRs, close mixed/superseded PRs, and verify before Linear Done.
- `references/linear-credential-surface.md` — distinguish Linear API key, OAuth token, OAuth client credentials, and webhook secret before diagnosing alerts or claiming Linear access is broken.
- `references/linear-api-auth-and-global-label-lookup-2026-07-18.md` — direct Linear GraphQL quirk note: raw API keys do not use `Bearer`, routing labels may require global `issueLabels`, and `issueSearch(term:)` may be unsupported.
- `references/linear-event-driven-dispatch-recovery-2026-07.md` — emergency stop and Slice 1 pattern for Linear request-count exhaustion caused by dispatcher polling: user-systemd kill-switch, shared circuit breaker, dashboard/API state, and no-live-Linear verifier.
- `references/dispatcher-polling-budget-safety-net-2026-07.md` — Slice 2 pattern for making remaining dispatcher poll fallback bounded, TTL-cached, cadence-controlled, dashboard-visible, and verified without live Linear calls.
- `references/assigned-agent-event-dispatch-recovery-2026-07.md` — Slice 4 pattern for exact assigned-agent resolver/preflight/dry-run wake proof across Kai/Fred/AGY without cross-agent stealing, broad polling, bulk redispatch, or live Linear mutations.
- `references/assigned-agent-result-writeback-recovery-2026-07.md` — Follow-on slice pattern for durable agent result/blocker state, dry-run Linear writeback previews, retry/recovery fields, and no live mutation without authorization.
