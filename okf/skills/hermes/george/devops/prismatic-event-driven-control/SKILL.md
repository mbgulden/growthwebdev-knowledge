---
name: prismatic-event-driven-control
description: Keep Prismatic workflow coordination dashboard/event-driven instead of cron/Telegram/LLM polling; recover from Linear API poller overload and report Prismatic status in Michael's preferred six-part format.
triggers:
  - Prismatic dashboard control
  - Linear polling cron overload
  - event-driven workflow queue
  - Telegram report format
  - active producer gate
  - AGY dispatch pause
  - workflow cron shutdown
---

# Prismatic Event-Driven Control

Use this skill when Prismatic workflow state, Linear task state, Telegram helper lanes, AGY/Fred/Ned/Kai dispatch, or producer admission is being coordinated.

## Core rule

Prismatic workflow control is **dashboard/event-queue first**. Do not use frequent cron jobs, Telegram polling loops, or recurring LLM sessions to constantly poll Linear/task state. If polling exists, it must be narrow, explicitly justified, non-frequent, and not a substitute for the Prismatic dashboard/gateway/event consumer.

## When Michael reports poller overload

Treat excessive Linear-touching cron traffic as a control-plane incident, not a routine cleanup.

1. Inventory active cron jobs across relevant Hermes profiles and shared/orchestrator stores.
2. Identify Linear-touching and frequent Prismatic workflow pollers separately from unrelated one-shot reminders or true watchdogs.
3. Pause/remove offending pollers as directed; do not restart them just to gather more state.
4. Check for already-running poller processes and stop only the offending workflow pollers when safe.
5. Verify the event-driven replacement path: dashboard route, health route, gateway/event consumer/queue process, and current active-producer state.
6. Keep generic dispatch paused until a specific task is admitted through the dashboard/event path.
7. Update handoff/control state so later sessions do not resume cron polling by accident.

## Required proof markers

```text
ACTIVE_LINEAR_TOUCHING_CRONS=<0 or count + reason>
ACTIVE_FREQUENT_PRISMATIC_POLLERS=<0 or count + reason>
DASHBOARD=<url/status>
HEALTH=<url/status>
EVENT_CONSUMER=<running|blocked + evidence>
GENERIC_DISPATCH=<paused|event-driven-only|specific admitted task>
ACTIVE_PRODUCERS=<count>
NOT_CLAIMING=<no deploy/restart/Linear write/cap increase unless explicitly authorized>
```

## Michael-facing Prismatic report order

For Telegram reports, use this order exactly:

1. Problem found
2. What changed
3. Why it matters
4. Current state
5. Exact next move
6. IDs, hashes, and logs for traceability

Behavior and impact come before identifiers. IDs, hashes, commits, PRs, log paths, and digests belong in section 6 unless the user specifically asks for a terse proof block first.

## Boundaries

- Do not merge, deploy, restart services, write Linear, close/delete PRs, or increase producer caps without explicit authorization or an existing policy that clearly grants it.
- Do not admit the next task when the current task has a late `REPAIR`, pre-review merge incident, or unresolved exact-head review.
- When Michael authorizes a repair after a blocked exact-head review, treat it as authorization to proceed through gates, not as authorization to skip them: freeze/hash the exact repair task, prove no existing event/slot/lease, validate the intended admission payload against the deployed task-admission schema, dispatch independent task-contract review, and keep `EVENT_COUNT=0` / `REPAIR_LAUNCHED=false` until the task review is `CLEAN/PASS`.
- For same-worktree repair admissions after a failed cap-1 producer, keep the original task/event boundary separate from the repair task. A `CLEAN/PASS` repair contract and even a reviewed envelope still stop short of POST authorization; only Michael's exact one-event/cap-1 wording admits the event. After admission, use exactly one POST, exactly one ordinary consumer invocation, event-scoped SQLite readback, restored temporary controls, receipt-bound PID/start-tick proof, and a passive `tail --pid` wait. See `references/recovery-contract-to-cap1-admission.md`.
- Do not claim `canonical suite` when only targeted shutdown/event-path verification ran.

## Support references

- `references/dashboard-polling-state-preservation.md` — keep dashboard tabs stable across periodic `fetchData`/WebSocket refreshes with idempotent tab-local render guards and >2-poll rendered proof.
- `references/opaque-workspace-boundary-phase2.md` — containment-to-opaque-ID workspace API gate: deterministic Linear single-create review, explicit registry, openat2/no-symlink filesystem boundary, dashboard deep-link preservation, and separation from deployment/public unblock.
- `references/linear-poller-overload-recovery.md` — concise incident checklist and report skeleton derived from the 13-cron/Linear saturation correction.
- `references/pr-publication-exact-head-confirmation.md` — checklist for publishing an already-clean Prismatic candidate as a PR, confirming the live PR head before merge, blocking successor tasks, and avoiding infinite loops on repeated Hermes verification warnings.
- `references/exact-merge-release-closeout-and-event-admission.md` — durable closeout pattern after `CLEAN_TO_MERGE`: re-check live PR fields, merge, prove merge tree equals reviewed tree, create non-local immutable release checkout, run focused release/package proof, and keep the successor task queued until the real dashboard/event contract is verified.
- `references/dashboard-task-admission-gate.md` — checklist for keeping a contract-ready successor task queued when dashboard discovery exposes only health/read/recovery/no-op dispatcher routes and no authenticated task-admission receipt; includes the pattern of launching a separate read-only admission preflight rather than starting a producer.
- `references/pure-adapter-slice-boundaries.md` — pattern for narrowing provider/gateway/status adapter work into a pure deterministic adapter slice while keeping gateway transport and dashboard admission as separate reviewed tasks.
- `references/stale-outbox-terminal-reconciliation-bootstrap.md` — one-time bootstrap pattern for safely terminalizing a stale oldest outbox/claim row whose source work is already merged, without launching another producer or mutating live state during implementation/review.
- `references/post-merge-authenticated-terminal-reconciliation.md` — post-merge/deployment pattern for using the authenticated reconciliation route safely: immutable release/venv, exact systemd provenance, one-time in-memory operator credential, route-level mutation, SQLite readback, consumer-predicate idle proof, and replay-artifact cleanup.
- `references/cap1-event-admission-and-live-run-proof.md` — event-gate admission pattern for one authorized successor task: backup/narrow/restore policy, one-time credential window, single consumer invocation, event-scoped SQLite readback, receipt-bound tmux/status proof, and no further action while the cap-1 producer runs.
- `references/task-id-schema-and-passive-producer-wait.md` — recovery pattern for admission-schema `422` task-ID rejection, honest compliant internal IDs, zero-side-effect proof before retry, launch-vs-producer-completion distinction, and passive PID-exit wait without polling or inactivity kills.
- `references/failed-producer-exact-tree-merge-boundary.md` — recovery pattern when a cap-1 producer is killed or overclaims `PASS`: preserve failed-producer boundary, salvage only through immutable candidate/review/canonical/clean-room proof, verify merge tree, and hold deployment.
- `references/failed-producer-result-exists-lint-blocker.md` — closeout pattern when a failed producer leaves `RESULT.md` and a committed candidate, but immutable archive reproduction exposes a quality-gate failure such as Ruff; preserve producer failure and mark candidate blocked/review-pending separately.
- `references/failed-producer-live-acceptance-closeout.md` — post-authorization closeout pattern for recovered failed-producer candidates: exact merge-tree match, immutable systemd release, live route/rendered dashboard proof, canonical acceptance through harness/API, deployment ledger, final post-write verifier, and preserved `producer_completed=false` provenance.
- `references/interrupted-cap1-producer-failclosed-recovery.md` — admitted cap-1 producer interrupted before result/commit: classify SIGTERM conservatively, reconcile terminal state fail-closed, preserve dirty worktree via external checkpoint, release exact stale slot only after cleanup proof, and stop for read-only triage/recovery authorization.
- `references/release-activation-drift-gate.md` — read-only provenance gate for merged/staged releases that are not yet the live systemd gateway; inspect loaded `ExecStart`/`WorkingDirectory`, drop-ins, queue/producer state, and report only the deployment authorization point before successor admission.
- `references/immutable-release-systemd-activation.md` — authorized production activation gate for an already-reviewed merged release: pre-state + rollback first, versioned venv/extras proof, release-specific systemd drop-in, gateway-only restart with auto-rollback, post-state DB-preservation/provenance proof, and final `/tmp/hermes-verify-*` closeout.
- `references/artifact-only-producer-boundary-and-wrapper-mismatch.md` — cap-1 artifact-only admission boundary: classify wrapper response-shape failures by event-scoped SQLite proof before retrying, restore temporary controls, hold acceptance on undeclared worktree files, and run a focused `/tmp/hermes-verify-*` handoff/control closeout.
- `references/canonical-agy-run-state-machine.md` — simplification target for AGY orchestration: one canonical run record/state machine, supervisor-owned terminal reconciliation, exact cap-slot release only after cleanup proof, review-pending terminal results, and no added wrappers/proof schemas/manual dispatch ceremony.
- `references/terminal-producer-closeout-and-existing-event-retry.md` — cap-1 existing-event retry and terminal closeout pattern: preserve failed attempt history, fix wrapper/config defects without reposting, bind launch to receipts, and switch stale `running` proof to `completed/review_pending` when terminal artifacts appear.
- `references/post-merge-next-gate-linear-and-successor-freeze.md` — post-merge next-gate pattern: read Linear before writing, prefer comment-only proof if state already projected, freeze/review successor task without admitting or launching it.
- `references/repair-authorization-pre-admission-task-review.md` — when Michael authorizes a bounded repair after a blocked exact-head review, freeze/hash/copy the repair task, validate the intended event payload against the deployed schema, and require independent task-contract CLEAN/PASS before posting the authenticated event.
- `references/recovery-contract-to-cap1-admission.md` — same-worktree recovery pattern after a failed producer: preserve original event boundary, version contract repairs, separate contract/envelope review from explicit POST authorization, handle invalid reviews, validate against deployed parsers with disposable DB, execute one POST/consumer, and attach receipt-bound passive wait.
- `references/contract-clean-vs-admission-envelope.md` — distinguish contract artifact CLEAN/PASS from task-copy/envelope CLEAN/PASS and from explicit one-event/cap-1 admission authorization; includes zero-side-effect and overlapping-recovery invariance checks.
- `references/deployed-admission-contract-drift-and-running-repair-proof.md` — admission closeout pattern when deployed route/schema/auth/response shapes differ from older scripts: validate against live parsers, reconcile SQLite before retry, treat `processed` as canonical consumer success, and prove active repair by checkpoint ancestry rather than fixed HEAD.
- `references/no-repost-repair-admission-to-pr-closeout.md` — end-to-end repair admission closeout after setup drift: no-repost recovery for an existing event, receipt-bound producer terminal proof, immutable/adversarial reproduction, independent exact-head CLEAN/PASS, and exact PR-head readback before merge authorization.
- `references/dirty-checkpoint-recovery-contract.md` — interrupted cap-1 producer with no commit/`RESULT.md` but coherent allowlisted dirty work: refresh Linear authority, reproduce from a `.git`-free archive, compare canonical baseline failures, freeze a no-authority recovery contract, and require fresh review before any task/event/producer.
- `references/dependent-successor-upstream-api-repair.md` — successor-task runway pattern when merged/deployed predecessor topology lacks a required canonical operational API: freeze a bounded upstream implementation-repair contract, review/hash it before any event, validate admission zero-state read-only, and keep the successor unstarted.
- `references/review-merge-factory-bottleneck.md` — when PE review throughput stalls, stop routing ordinary candidates through George manually; use an event-driven review/merge factory with deterministic verification, risk tiers, concurrent immutable reviewers, and explicit merge authorization.

## Pitfalls

- "Cron paused" is not enough proof. Also prove the replacement dashboard/event path is alive or clearly blocked.
- Do not rely on memory alone for Michael's six-part report format; embed it in Prismatic prompts and reports.
- Do not depend on GitHub Actions, GitHub availability, or hosted CI as the Prismatic acceptance authority. Classify hosted CI as `OPTIONAL_HOSTED_SIGNAL`; native dashboard receipts, exact-tree proof, independent review, immutable-release proof, and production proof are the acceptance path.
- If hosted CI is red, first determine whether product tests actually ran. Billing/spending-limit/no-runner/provider outages are optional transport failures, not product verification failures, and should not block Engine progress when native proof is complete.
- Do not revive generic AGY/Fred/Ned/Kai dispatch after cleanup unless the next task is specifically admitted through the event-driven gate.
- After a candidate receives independent exact-head `CLEAN`, pushing/opening a PR is not the end of proof. Confirm the live PR `headRefOid` still equals the reviewed commit and keep successor tasks blocked until PR-head review returns `CLEAN_TO_MERGE`.
- After `CLEAN_TO_MERGE`, merge closeout still needs proof: re-query live PR fields immediately before merge, verify the merge tree equals the reviewed candidate tree, create a durable non-local release checkout with no alternates, and run focused release/package validation before marking the slice accepted.
- A staged durable release is not a deployed runtime. Before admitting any successor through the event gate, compare the live gateway's loaded `ExecStart`/`WorkingDirectory` from `systemctl show` with the expected release. If systemd drop-ins are stacked, use `systemctl cat`/`DropInPaths`; the base unit file alone is not authoritative. If the live gateway is one merge behind, report only the deployment authorization point and keep `NEW_TASK_ADMITTED=false`. See `references/release-activation-drift-gate.md`.
- When Michael authorizes deployment of a staged release, activate it as a bounded gateway-only systemd cutover: prove the versioned venv including runtime extras before touching systemd, write rollback/pre-state first, install a release-specific drop-in, restart only the gateway with auto-rollback, prove loaded runtime provenance/HTTP/DB preservation/legacy containment afterward, write a deployment receipt, then run a final `/tmp/hermes-verify-*` closeout. See `references/immutable-release-systemd-activation.md`.
- If dashboard OpenAPI discovery endpoints are absent, do not infer or invent an event endpoint. Report discovery unavailable, keep the next task `QUEUED_NOT_ADMITTED_EVENT_ONLY`, and prepare a bounded task contract for later verified dashboard/event admission.
- If the dashboard exposes only health/read/status surfaces, recovery-control actions, webhook queue retry/purge, or dispatcher actions that report `accepted_noop`, treat admission as blocked. A successor producer may start only after a durable authenticated admission receipt binds the exact task ID, base commit/tree, task-file SHA-256, producer identity, worktree, and writer cap.
- If Hermes repeats an edit-verification warning after compliant `/tmp/hermes-verify-*` proof on unchanged files, do not loop forever. Rerun once only when proof markers were missing, then label detector non-recognition and continue with the gated workflow.
- If the oldest durable outbox row is stale/retryable but its source work is already merged or accepted, do not invoke the ordinary consumer just to clear it. Treat it as a bootstrap gap: prove source acceptance, zero active producers, empty writer lease, and consumer selection risk; ask for explicit one-time repair authorization; then implement an authenticated terminal-reconciliation path that terminalizes the row without launching a producer, deployment, restart, Linear write, or live DB mutation during review. See `references/stale-outbox-terminal-reconciliation-bootstrap.md`.
- After that repair is merged and deployment is explicitly authorized, preserve production durability: deploy from an immutable release plus versioned venv, verify systemd `ExecStart`/`WorkingDirectory` and health, mutate only through the authenticated route, read back SQLite/lifecycle independently, prove the ordinary consumer predicate no longer selects the stale event, remove one-time request artifacts, and keep unrelated orchestrator/runtime deployment flags separate. See `references/post-merge-authenticated-terminal-reconciliation.md`.
- For a cap-1 successor admission, prove the event by event-scoped SQLite readback and canonical launch receipt. Do not repost because a local response-shape assertion failed; do not count historical claims globally; do not guess tmux session prefixes or manifest filenames; use receipt-bound session/status artifacts. If the deployed schema rejects a semantically valid descriptive task ID with HTTP 422, prove zero durable side effects and restored temporary controls, validate a compliant `<PREFIX>-<NUMBER>` internal ID against the deployed schema, then retry the same bounded slice once. Validate temporary control-auth credentials and request timestamps through the deployed loaders/parsers before POST; live deployments may require fields such as `roles` and whole-second UTC freshness. Also validate live route context headers, response nesting, producer source launcher shape, and consumer CLI flags before admitting or recovering an event; deployed runtime may require an idempotency/admission-context header, nested `record` coordinates, legacy `producer` + single-executable `command` config, and `--policy`/`--identity` consumer flags. Treat canonical consumer `status=processed` plus claim `state=completed` as launch proof; producer completion still requires `harness-run.json`/process result/`RESULT.md` evidence. If a closeout verifier expected `running` but terminal artifacts now show exit/cleanup/result, update state to `completed`/`review_pending` instead of preserving stale running proof. If a running repair producer has already advanced HEAD, prove the blocked checkpoint is an ancestor and the tracked tree is clean; do not require fixed HEAD until terminal closeout. See `references/cap1-event-admission-and-live-run-proof.md`, `references/task-id-schema-and-passive-producer-wait.md`, `references/terminal-producer-closeout-and-existing-event-retry.md`, and `references/deployed-admission-contract-drift-and-running-repair-proof.md`.
- For artifact-only producers, any undeclared worktree mutation is an acceptance hold, not a cleanup chore. Preserve the file while the producer is active, record `ACCEPTANCE_HELD=true`, and wait for durable termination plus independent review before removal/repair. See `references/artifact-only-producer-boundary-and-wrapper-mismatch.md`.
- If an admitted cap-1 producer dies or overclaims `PASS`, do not launder that into success. Preserve `PRODUCER_COMPLETED=false`/exit evidence, recover only by committing an immutable candidate, bind independent reviews to exact head/tree, rerun canonical and clean-room proof, verify merge tree equals reviewed tree, and keep deployment held until explicitly authorized. See `references/failed-producer-exact-tree-merge-boundary.md`.
- If a failed admitted producer still leaves `RESULT.md` and a committed candidate, treat those as salvage inputs, not success. Reconcile receipts, then reproduce from `git archive <candidate-head>` and run quality gates including Ruff; if tests pass but Ruff fails, mark candidate `BLOCKED`/review-pending and preserve `PRODUCER_COMPLETED=false`. Do not mutate source or launch another producer without explicit recovery authorization. See `references/failed-producer-result-exists-lint-blocker.md`.
- If an admitted cap-1 producer terminates before `RESULT.md`/commit, do not turn partial progress into producer success and do not guess the signal source. Classify from runtime evidence (`exit`, `automatic_kill`, `runtime_deadline`, cleanup), reconcile stale `running` state through the canonical fail-closed harness/status path, release only the exact run-bound slot after process-tree cleanup proof, freeze an external patch checkpoint, dispatch read-only triage, and stop for explicit recovery authorization. See `references/interrupted-cap1-producer-failclosed-recovery.md`.
- After a failed admitted producer still leaves no `RESULT.md` or descendant commit but does leave an allowlisted dirty worktree, do not dispatch exact-head review or call it a candidate. First refresh current Linear authority, bind the dirty checkpoint by HEAD/tree/diff/path/blob hashes, reproduce it from a fresh `.git`-free archive, compare canonical failures against the blocked head by failed-test identity, and freeze a no-authority recovery contract for independent review. Focused green plus identical baseline canonical failures means coherent dirty checkpoint only, not producer success or canonical green. See `references/dirty-checkpoint-recovery-contract.md`.
- After a recovered failed-producer candidate is explicitly authorized for deployment, acceptance still requires live production proof and canonical accepted-state write/readback. Preserve `producer_completed=false`, record hosted CI zero-step/billing failures as non-green infrastructure boundaries, use the harness/API path for acceptance rather than direct JSON edits, write a deployment receipt/ledger, and run a final post-write `/tmp/hermes-verify-*` closeout over the receipt, handoff, PR binding, immutable runtime, and live routes. See `references/failed-producer-live-acceptance-closeout.md`.
- When an authorized successor depends on APIs expected from the just-accepted predecessor, first activate/verify the predecessor if that is the successor's base gate, then inspect the actual merged/deployed topology. If a required canonical API is missing, do **not** compensate inside the successor with ad-hoc SQL, duplicated parsers/schedulers, or dashboard-local reconstruction. Freeze a bounded upstream implementation-repair contract, hash/review it before any worktree/event exists, validate admission schema/zero-state read-only only, and keep `EVENT_COUNT=0`, `PRODUCER_COUNT=0`, and `SUCCESSOR_STARTED=false` until gates pass. See `references/dependent-successor-upstream-api-repair.md`.
