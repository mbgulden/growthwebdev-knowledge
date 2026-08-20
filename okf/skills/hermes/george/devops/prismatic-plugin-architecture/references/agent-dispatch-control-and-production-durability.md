### Telegram lane bridge before durable assigned-agent dispatch

When Michael wants George to coordinate Kai/Fred before durable Prismatic assigned-agent dispatch is ready, use focused Telegram lane groups as an interim dispatch/control surface:

```text
George control/DM
→ Kai group for golden-path prompts and proof
→ Fred group for adjacent hardening prompts and proof
→ George audits, paces, and recommends next actions
→ Michael authorizes merges/deploys/real side effects
```

Use one exclusive marker per lane to prevent duplicate work. Current session lane targets are:

- Kai: `Prismatic Kai`, `telegram:-5338154051`.
- Fred: `Prismatic Fred`, `telegram:-5167970174`.

Important Hermes/Telegram gotcha: outbound `hermes send` to a group proves only write access. Inbound responses require the profile's `telegram.allowed_chats` to include the group id, gateway restart/reload after config changes, and BotFather group privacy disabled if normal group messages should be visible. Keep `require_mention=true` initially and have users mention/reply to the target bot to avoid recursive/noisy group behavior. Restarting the active gateway from inside its own Telegram session is blocked; run `hermes --profile <profile> gateway restart` or the relevant `systemctl restart ...` from an external shell.

Use the Telegram bridge only as the interim human-readable dispatch surface. The durable target remains Prismatic-native assigned-agent queue/preflight/context-pack/result-writeback. Details: `references/telegram-lane-dispatch-bridge-2026-07-19.md`.


Critical Telegram bot-to-bot limitation: a George bot message visible in a group may not be delivered as an inbound update to Kai/Fred bots. For reliable group wake-up, either Michael sends/copies the final activation line as a human, or use the filesystem agent bus bridge. When using group prompts/status anyway, address agents with exact handles every time: Kai `@KaiactiveOahu_bot`; Fred `@FredTheBotFredTheBot`. Avoid generic `Kai, please...` / `Fred, please...` dispatches because they may be visible but not actionable.

### Assigned-agent wake dispatch recovery

When Michael asks to restore task dispatch after AGY/Linear queue recovery, do **not** frame the target as AGY-only and do **not** restore uncontrolled always-on worker behavior by default. The desired workflow is event-triggered assigned-agent wake-up: a Linear issue/event enters the durable queue, the system resolves the intended agent from metadata/assignee/labels, preflights that exact agent, wakes/dispatches exactly that agent for exactly that task, then writes result/blocker evidence back to Linear and dashboard.

Use these review gates after durable queue/drain proof:

- `ASSIGNED_AGENT_RESOLVER_OK` — `agent:kai`, `agent:fred`, `agent:agy` and equivalent assignment metadata resolve correctly; unknown/ambiguous/disabled agents fail closed to `needs_manual_review`.
- `PER_AGENT_PREFLIGHT_OK` — the resolved agent exists, is enabled, has valid runtime/model/provider config, supports the task type, and passes dependency/stage rules before launch.
- `ASSIGNED_AGENT_WAKE_DISPATCH_OK` — exactly the resolved agent wakes/claims the one intended task; no batch launch, default-agent spillover, or cross-agent stealing.
- `ASSIGNED_AGENT_RESULT_WRITEBACK_OK` — Linear/dashboard show target agent, routing source, preflight state, dispatch state, result/blocker, and retry/recovery status.
- `ASSIGNED_AGENT_DISPATCH_RECOVERY_OK` — queue/drain, resolver, preflight, one-task execution, and result writeback all pass. Do not claim this if only AGY works.

AGY can remain the first proof target when recovering from the known model/config failure, but the architecture should support Kai, Fred, AGY, and future named agents through the same assigned-agent resolver/preflight/wake/writeback contract. If Ned-style always-on workers are discussed, keep them optional/future unless explicitly requested and guarded by pause/stop controls, max claim count, rate limits, dependency guards, and dashboard-visible claim ownership. Session detail: `references/assigned-agent-wake-dispatch-2026-07-15.md`.

### George review/closeout lane when Fred is productive

When Fred is actively building Prismatic slices, George should usually **not** open a competing implementation branch. George's highest-value lane is: independently verify Fred's PR/report, merge/deploy after Michael authorizes, run runtime/public/browser proof, create the next executable prompt, and prepare review packets so Fred can keep building.


When Prismatic durable assigned-agent dispatch is not ready, use **Telegram lane groups as a temporary dispatch bridge**: separate Kai/Fred groups, George live-checks state, writes verified `.md` prompt artifacts, sends them to lane-specific Telegram targets, then audits returned proof packets before next dispatch. Sending to groups only proves outbound access; inbound group replies need BotFather privacy disabled, group IDs in each profile's `telegram.allowed_chats`, gateway reload/restart, and sometimes remove/re-add after privacy changes. For setup commands, service pitfalls, and current lane IDs, see `references/telegram-lane-dispatch-bridge-2026-07-19.md`.

### Filesystem agent bus bridge before durable dispatch

When Telegram bot-to-bot delivery is unreliable but Michael wants George/Kai/Fred coordination now, use `/home/ubuntu/prismatic-agent-bus` as an interim filesystem context-pack bus. The active implementation lives at `/home/ubuntu/prismatic-agent-bus/bin/prismatic_agent_bus.py` with systemd timers `prismatic-agent-bus-kai.timer`, `prismatic-agent-bus-fred.timer`, and `prismatic-agent-bus-george-audit.timer`.

Dispatch shape:

```bash
python3 /home/ubuntu/prismatic-agent-bus/bin/prismatic_agent_bus.py dispatch \
  --agent kai \
  --marker ONE_AGENT_OPERATOR_VERIFICATION_LOOP_OK \
  --task-file /home/ubuntu/prismatic-kai-dispatch-ONE_AGENT_OPERATOR_VERIFICATION_LOOP_OK-2026-07-19.md
```

The bus writes `TASK.md`, `PACKET_CONTRACT.md`, `CONTEXT.json`, and `STATUS.json` under `inbox/<agent>/<task_id>/`, atomically claims tasks by moving them to `claimed/<agent>/`, and expects `outbox/<agent>/<task_id>/RESULT.md`. The George auditor must not merely notify on outbox files; it must write `/home/ubuntu/prismatic-agent-bus/audits/<agent>/<task_id>/GEORGE_AUDIT.md` with `MARKER=GEORGE_BUS_RESULT_AUDIT_OK`. Current implementation performs fast deterministic pickup audit of packet fields plus local log/branch/commit references, then mirrors the audit-ready path to Telegram. Default side-effect policy in `CONTEXT.json` keeps merge/deploy/Linear/GitHub/auto-merge/bulk/production restart false. Telegram is only the status mirror; the filesystem is the machine handoff channel. Verify with:

```bash
python3 -m py_compile /home/ubuntu/prismatic-agent-bus/bin/prismatic_agent_bus.py

python3 /home/ubuntu/prismatic-agent-bus/bin/prismatic_agent_bus.py verify
systemctl list-timers --all 'prismatic-agent-bus-*' --no-pager
```

The `verify` command performs a George-only dry-run canary; it does not launch Kai/Fred LLM work. Expected marker: `FILESYSTEM_AGENT_BUS_BRIDGE_OK`. This is still a bridge, not canonical Prismatic assigned-agent dispatch. Session implementation detail: `references/filesystem-agent-bus-bridge-2026-07-19.md`.

For Michael's “keep going / always on” governance-lane requests, add a conservative autopacer on top of the filesystem bus rather than bulk-dispatching or granting side effects. Use `/home/ubuntu/prismatic-agent-bus/state/governance-backlog.json` plus `prismatic-governance-autopacer.timer` to dispatch one North-Star-aligned marker per Kai/Fred lane only when the lane is idle, and advance only after filesystem result plus George audit artifact. Expected marker: `GOVERNANCE_ALWAYS_ON_AUTOPACER_OK`. Detailed pattern: `references/governance-autopacer-filesystem-bus-2026-07-19.md`.

For human-facing always-on monitor output, avoid raw service tables unless Michael asks for proof. Michael wants the update to be easily scannable: top line with overall boring-build %, then a table of major boring-stuff sections with % complete, then `Now / next`, then a compact timeline of markers. Include % estimates for the whole boring section/backlog, not a claim that a current task or code is fully complete. Keep proof packets available separately for verification requests.


When Michael asks whether this governance/autopacer/bus work is actually live and **100% production ready**, run a production governance readiness audit instead of trusting the monitor's percent. Compare live state against `docs/north-star.md`, `docs/okf-evidence-map.md`, `research/rubric-inventory-matrix.md`, and `docs/prismatic-production-durability-standard.md`. Treat a host-level filesystem bus as live/interim unless it is first-class PE Core/dashboard/API, has assigned-agent resolver/preflight/wake/writeback proof, clean PR/deploy/rollback/browser proof, and a closed 10/10 rubric evidence ledger. Use `BLOCKED` when P0 production gaps remain. See `references/production-governance-readiness-audit-2026-07-19.md`.

When Michael asks for a comprehensive Prismatic Engine architecture/production-readiness audit against North Star/OKF docs, audit four planes before scoring: doctrine/docs, source architecture/tests/routes, durable runtime checkout/state/services, and public/operator dashboard/API/browser proof. Separate developer-preview/local-first readiness from hosted/public production readiness. P0 checks include unauthenticated public Gateway operational APIs, missing-signature webhook behavior, dirty/detached runtime with untracked source, assigned-agent markers without live result/writeback rows, non-hermetic tests that depend on ambient credentials, fragmented state/backup gaps, dashboard-vs-systemd truth drift, and incomplete `TBD`/`REVIEW_PENDING` rubric ledgers. Use a dimension scorecard and explicit non-claims. See `references/prismatic-production-readiness-audit-2026-07-20.md`.

For live-system production durability audits, additionally treat the deployment itself as evidence. Check every systemd unit/timer `WorkingDirectory` and executable, runtime checkout SHA plus `git status --porcelain`, dirty/untracked source drift, local-vs-public route parity, anonymous public stateful API behavior, webhook missing-signature behavior, security headers, exact documented command reproducibility without ad-hoc `PYTHONPATH`, and backup/restore proof. Do **not** let GitHub CI green, local smoke markers, or a rendered dashboard close P0 hosted-readiness gaps. If public internal APIs are anonymous, webhooks fail open on missing signatures, or production depends on mutable development checkouts, report `BLOCKED`. Detailed closure gates: `references/production-durability-live-system-audit-2026-07-20.md`.

If Michael then says to continue always-on boring governance work, convert the audit P0s into the next backlog layer rather than stopping at the completed safe-mode backlog. Append class-level next tasks, clear lane `complete` state only after adding those tasks, force-run the autopacer once, verify claimed workers/result-packet state, and update the human monitor's denominator/sections so it does not keep saying 100% after new production-integration work is added. See `references/always-on-governance-backlog-extension-2026-07-19.md`.

If Michael specifically asks to make the **governance dashboard UI complete, tested, portable, and durable**, do not answer from the backlog or monitor percent alone. Immediately run local/public dashboard route probes, governance/agent API probes, dashboard visual QA, public/release smoke, focused dashboard/API tests, inline JS `node --check`, and a browser DOM/console check. Classify as `PARTIAL` unless clean merge/deploy/rollback/source-readback plus browser/mobile proof exists. Add explicit backlog gates for API contract, UI completion audit, and portable durable visual QA, then update the human monitor denominator. See `references/governance-dashboard-ui-readiness-guard-2026-07-19.md`.


When Michael asks for a **read-only Prismatic UI / Command Center production-readiness audit with rendered browser proof**, audit rendered UX, API hydration parity, public auth/exposure boundaries, runtime/source durability, mobile usability, accessibility semantics, no-op/dry-run labeling, and North Star Golden Flow fit before scoring. Keep it read-only: do not exercise POST controls or mutating dashboard actions without explicit authorization. Treat unauthenticated public operational APIs/source previews, public/local route mismatches, detached dirty runtime, or unlabeled no-op controls as P0 production-readiness blockers. Use desktop+mobile screenshots/DOM/console proof and a compact `BLOCKED|PARTIAL|PASS` packet with explicit non-claims. See `references/ui-command-center-production-readiness-audit-2026-07-20.md`.

When Michael asks for a **complete architectural + UI Command Center production-readiness audit** before comparing other model reports or writing a Linear master plan, audit four planes before planning: doctrine/docs, source architecture/tests/routes, durable runtime/deployment, and public/operator browser proof. Explicitly check hosted auth boundary, dirty runtime source, service working directories, GitHub CI unit scope, orphan test collection, dashboard API 404s, mobile/workspace rendering scale, agent writeback truth, and state/backup recovery. Create the downloadable full report and short execution digest early and update them incrementally so the platform tool-call ceiling cannot erase the artifact. See `references/command-center-production-readiness-audit-2026-07-20.md`.

When Michael provides Gemini/Claude/other-model Prismatic audit docs and asks George to reconcile them with dashboard/control-center readiness, treat the model reports as **claims to verify**, not evidence. Export/save/hash the source docs, classify each report's evidentiary trust, reject wrong-project/path/route contamination, and translate only verified or directionally useful themes into real-system closure gates. Run a fresh read-only public dashboard/control audit alongside the reconciliation: rendered desktop/mobile proof, local/public route parity, static control inventory, real/dry-run/no-op control classification, systemd source-readback, git cleanliness, and auth/header probes. Always deliver both a full report and a short execution digest. Do not prioritize imagined 100 ms telemetry/DAG/cgroup/seccomp control planes before auth, webhook fail-closed behavior, clean pinned runtime, public adapter parity, and normal operator Golden Flow. See `references/model-audit-reconciliation-control-center-2026-07-20.md`.

If Michael challenges a Prismatic master plan with “base it on what we have built” or similar, immediately convert the plan into a **built-first preservation plan**, not a greenfield architecture plan. Inventory existing source/runtime/dashboard/plugin/assigned-agent/release/security assets, assign each KEEP/RECONNECT/HARDEN/COMPLETE/GENERALIZE/REPLACE-SURGICALLY/RETIRE-AFTER-PROOF, and make `BUILT_ASSET_PRESERVATION_MAP_OK` the first executable gate before implementation. Every future prompt touching existing systems should include `EXISTING_ASSETS_REUSED`, `EXISTING_CONTRACTS_PRESERVED`, `SURGICAL_CHANGES`, `CALLER_USAGE_SEARCH`, `STATE_MIGRATION`, and `ROLLBACK_PATH`. See `references/built-first-master-plan-revision-2026-07-20.md`.

If Michael says the public dashboard loads but “I don’t see anything new,” triage visibility as a three-plane problem: live shell/HTML, public API hydration/proxy exposure, and merge/deploy/runtime completeness. New cards can be present but subtle; tab UI can be live while its public API 404s; and newer panels can exist only as dirty/untracked dev work absent from the durable runtime. Verify local vs public routes, browser tab/console state, runtime checkout HEAD, and dirty/untracked work before answering. See `references/live-dashboard-visible-change-triage-2026-07-20.md`.


If Michael authorizes the current bandaid method for dashboard/governance before the full governance build is done, preserve first, then patch narrowly: save dirty dev diff/untracked files and nginx/runtime before edits; add missing public proxy exposure such as `/api/plugins/` when local API is 200 but public is 404; copy only the current agent-governance status module/route/panel/tests into the durable runtime checkout; restart/reload intentionally; verify local+public dashboard, plugin governance API, agent governance API, browser DOM, and console. Report runtime as intentionally dirty bandaid and create a worktree/branch preservation map before any cleanup. Do not delete/reset dashboard/governance/Fred/Kai worktrees until useful work is ported or explicitly archived. Marker used: `GOVERNANCE_DASHBOARD_BANDAID_CLOSEOUT_OK`.

If Michael turns that bandaid/audit into “have Kai and Fred execute all plans” and explicitly authorizes Linear work, create a real Linear epic/child tree instead of a flat task dump, but keep execution paced through the safe filesystem bus. Use class-level epics such as durable dashboard closeout, PE Core assigned-agent governance, OKF/percent auditor, branch cleanup runway, and portable dashboard visual QA. Every child issue should include an OKF block (`Objective → Key Result → Function → Evidence → Promotion Decision`) and default to `needs_approval` for real side effects. After creation, re-query Linear and verify identifiers, parent links, project, and labels; repair wrong/stale labels with `issueUpdate` full `labelIds` if needed. Then append only the next Kai/Fred markers to `/home/ubuntu/prismatic-agent-bus/state/governance-backlog.json`, clear stale complete flags, run the autopacer once, and recalculate monitor percentages with the new denominator. Count only `PASS` as done; show `PARTIAL` separately. If Michael asks for auditor “AO,” make the meaning explicit; current pattern interprets AO as an auditor acceptance-output packet with OKF delta, percent delta, proof links, non-claims, and next promotion decision. Details: `references/linear-governance-plan-percent-okf-auditor-2026-07-20.md`.

If Michael escalates from a plan into a full **built-first OKF program** — OKF docs, Linear epics/children, assigned batches, and personal George review of completions — use the richer program pattern in `references/built-first-okf-linear-review-requeue-2026-07-20.md`. Key additions beyond normal Linear planning: create the OKF reference docs first, verify all Linear parent/label/state links by re-query, preflight AGY before any bulk dispatch, keep future work `dispatch:paused`, use at most one Fred and one Kai filesystem-bus bandaid task while AGY is blocked, require `requires_program_review=true`, and treat George review as substantive independent evidence review rather than deterministic packet-shape audit. Only `PASS` unlocks dependents; `PARTIAL`/`FAIL`/`BLOCKED` creates a narrow repair child under the same epic and preserves useful artifacts.

### Prompt4 assigned-agent packet gate reconciliation

When the Prompt4 monitor reports `BLOCKED_PACKET_PRESENT` even though a later AGY/Fred PASS exists, do not diagnose raw AGY OAuth as the primary fault. Audit three separate layers: raw CLI execution, launch/result reconciliation, and aggregate Linear packet-state logic.

The correct packet-state rule is **latest valid recognized packet per required agent**, ordered by Linear `createdAt` plus packet line position. Pair each `MARKER=` with its nearest preceding `RESULT=` line so mixed comments containing multiple packet blocks do not make an unrelated PASS supersede a blocked marker. A later valid PASS supersedes historical blockers without deleting them; retain `superseded_blocked` counts for audit. A newer blocker still wins.

For the historical GRO-3952/GRO-3954 Prompt4 contract:

- Fred and AGY are required dispatched-agent packets.
- George remains manual/verifier and is not a required dispatched-agent packet until a separate launcher/resolver task implements that path.
- Fred's recognized closure may be the canonical queue marker, original acceptance marker, explicit supersession marker, or the verified PR-ready packet; current PR mergeability remains a separate concern.
- AGY uses `AGY_PACKET_FIXTURES_REPAIR_HINTS_OK` / `_BLOCKED`.
- `COMPLETE` must explicitly state that Prompt5 is not automatically unlocked.


Result reconciliation must inspect terminal AGY launch rows when a durable output log exists. If a completed/blocked/failed row contains a valid packet but comment writeback was missed, write/emit it once; if the marker already exists, remain idempotent. Do not create new duplicate blockers for old terminal rows with no packet.

AGY auth on this host can be profile-home scoped. A direct George-shell `agy --print` may request login while `HOME=/home/ubuntu/.hermes/profiles/kai/home agy --print ...` succeeds. Report the execution HOME boundary without exposing OAuth URLs/codes. This raw canary is supporting evidence only; the gate still requires packet/reconciler/monitor proof.

Expected fix marker: `GEORGE_AGY_PREFLIGHT_GATE_FIX_OK`.

### George unified always-on audit control plane

Treat “always on” as scheduled/event-driven durability, not a continuously running LLM session. Keep separate authority levels:

1. 30-second deterministic filesystem pickup audit — packet shape and directly checkable local references only.
2. 2–15 minute read-only change/heartbeat monitors.
3. 5-minute semantic built-first reviewer — artifact acceptance and literal `PROMOTION_DECISION=` contract.
4. Prompt/workflow gates such as Prompt4 — exact scoped agent packet state only.
5. Full runtime/public/browser audits — change-triggered or explicitly requested.

Use `~/.hermes/profiles/george/scripts/prismatic_audit_control_plane.py` as a silent-on-no-change reconciler. It writes `reports/audit-control-plane/latest.json` and `latest.md`, alerts on inactive timers/services, stale cron heartbeats, pickup gaps, missing semantic reviews, or Prompt4 regression, and remains read-only. A review artifact that exists but predates the literal `PROMOTION_DECISION=` field is `nonconforming` coverage debt, not the same as a missing/pending review.

Do not use the legacy 35-marker `prismatic-agent-bus/audits/okf/okf_percent_ledger_latest.json` as the current percentage. It is stale and unscheduled. Current progress comes from the live Linear-derived built-first monitor denominator. Keep Jules/Ned result-audit lanes explicit as coverage gaps until implemented.


For generalized AGY completed-work semantic review, do not trust the product gate's `merge_ready` label as an operator decision. Review every live `/api/agy/completed-work` record on two axes: (a) policy coherence — agent, packet classification, proof result, changed files, eligibility, integration marker, and no real side effects; and (b) promotion durability — source artifact exists, proof log survives, source branch ref survives, non-claims are complete, and evidence is runtime rather than fixture/canary-only. `merge_ready` with missing source/log/branch becomes `HOLD_MISSING_DURABLE_EVIDENCE`, not promotion. Correct malformed rejection can be `ACCEPT_REJECTION`; test fixtures can be accepted only as policy fixtures. Write one review artifact per completed-work ID with literal `PROMOTION_DECISION=` and keep the reviewer read-only. George's current implementation is `~/.hermes/profiles/george/scripts/prismatic_agy_completed_work_reviewer.py`, invoked by the 10-minute audit control plane.

For targeted Telegram lane dispatch through a one-shot cron, a due job can execute and auto-remove after the scheduler/list readback still appears stale. Before retrying, verify both `~/.hermes/profiles/<profile>/cron/output/<job_id>/` and `~/.hermes/profiles/<profile>/logs/agent.log` for `delivered to telegram:<chat>` evidence. Do not create a replacement job merely because `last_run_at` has not refreshed yet. If an identical wake is delivered twice, send one exact-mention deduplication correction telling the agent to treat both messages as one task, reuse any existing worktree/branch, and emit one closeout artifact.

### George proactive coordination / event watcher lane

When Michael asks George to coordinate Kai/Fred/AGY proactively or be “always on,” use a staged coordination model rather than uncontrolled worker behavior.

Approved coordination policy:

- George may proactively read repo/runtime/PR/API state, write Kai/Fred prompts, verify reports, flag stale PRs, and recommend merge order.
- George must wait for explicit authorization before merges, production deploys/restarts beyond authorized closeout, real Linear/GitHub side effects, bulk/autopilot dispatch, or closing/deleting PRs.

Immediate safe implementation: a read-only silent-on-no-change Hermes cron watcher (`cronjob(no_agent=True, script=...)`) that checks selected PRs, repo/runtime HEAD, gateway service state, completed-work/dry-run routes, queue, and signals. Empty stdout means no alert; changed state emits a compact Telegram proof packet. This is event-like polling, not true webhook-native dispatch.

Future target: Prismatic-native events should wake a George review queue item when Kai/Fred/AGY completed-work packets, PR dry-runs, CI-green PRs, runtime head changes, or route marker changes occur. George then verifies evidence and generates the next Kai/Fred prompt or merge-readiness packet, still without real side effects unless Michael authorizes them.

Lane split to avoid branch soup:

```text

Kai = golden path / valid completed-work spine
Fred = adjacent boring hardening, e.g. invalid packet repair queue
George = verification, traffic control, prompt preparation, stale-PR guard
```

Use one owner per marker. Good immediate markers:

```text
Kai → ONE_AGENT_OPERATOR_VERIFICATION_LOOP_OK
Fred → INVALID_PACKET_REPAIR_QUEUE_OK
George → GEORGE_OPERATOR_PROOF_REVIEW_OK
```

Do not allow multiple agents to attack the same broad “completed-work integration” blob. Future multi-agent/overnight gates remain blocked until the dependency markers are real. Session detail: `references/george-proactive-coordination-event-watcher-2026-07-19.md`.


If a report/audit is large, do not hand Michael/Fred a giant blob as the primary artifact. Produce a short execution cheat sheet first:

```text
status → do-first sequence → A/B/C/D source buckets → exact commands → red flags → full-audit appendix link

```

For completed-work integration, preserve the staged boundary:

```text
contract classifier
→ fixture API/dashboard status
→ real packet ingestion/persistence
→ Linear/dashboard writeback
→ clean PR create/update
→ PR verification gate
→ optional safe merge policy later
```

Never collapse these into "auto-merge is done". Classifier/ingestion/read-model slices are useful but are still not clean PR creation, verification gate, production proof, or auto-merge.

For merge/deploy closeout:

1. Verify PR state/CI and dependency order.
2. Merge only after Michael authorizes.

3. Update durable runtime checkout, not a random mutable dev checkout.
4. Restart relevant services.
5. Prove local routes, public routes, browser dashboard visibility, and console state.
6. Report explicit non-claims.

Pitfalls from the 2026-07-17 dashboard/completed-work runway:

- `gh pr merge --delete-branch` can merge the PR but fail deleting a local branch held by a worktree; always re-query PR state before retrying.
- Stacked PRs can be mergeable against a feature base but not ready for `main`; merge/deploy dependency PRs first, then rebase/retarget the stacked PR.
- Direct-run repo scripts like `python3 scripts/foo.py` need repo-root import handling if they import `prismatic.*`; a CLI proof that only passes with ad-hoc `PYTHONPATH` is not a clean direct-run proof.

Session detail: `references/dashboard-completed-work-runway-2026-07-17.md`.

### Agent CLI context-pack optimization for AGY/Jules

When optimizing agent “memory” for assigned-agent CLI dispatch, do **not** frame the solution as more prompt stuffing or assumed persistent model memory. Use a **context-pack + packet-contract** pattern:

```text
small launch prompt
+ durable context-pack files

+ exact completed-work/proof packet contract
+ CLI-specific launch/capture/reconcile wrapper
+ conservative BLOCKED fallback when output is malformed or missing
```

When preparing follow-up prompts from this work, live-check PR state immediately before packaging the handoff. If AGY/Jules context-pack PRs have already merged, do **not** send a stale “review/merge these PRs” prompt. Instead pivot Kai/Fred to the next narrow gate: `AGY_COMPLETED_WORK_INTEGRATION_GATE_OK` — completed-work packet ingestion, validation/classification, persisted/readable state, dashboard/API/Linear-ready summary, and manual merge policy preserved. If a downloadable `.md` prompt was already created with stale PR states, regenerate or patch it and verify the artifact before sending.

Fred's completed-work skill-pack work is useful as a shared output contract (`agent/source_path/changed_files/proof/non_claims/marker` plus compact proof packet lines), but report it precisely: repo docs/tests and dispatcher prompt injection do **not** prove every live agent profile has new skills installed.

For AGY CLI, prefer a small `agy --print` prompt that points to durable context files, narrow `--add-dir` usage, `--log-file`/stdout capture, model preflight canaries, and a wrapper that appends `RESULT=BLOCKED` when exact packet lines are absent. Suggested marker: `AGY_CLI_CONTEXT_PACK_OK`.

For Jules CLI, live-check `jules --help` / `jules new --help` before designing dispatch. The installed Jules CLI may be async/session-based (`jules new`, `jules remote list --session`, `jules remote pull --session`) rather than AGY-style print/log mode. Do not assume unsupported flags such as `--issue`, `--task`, `--print`, `--log-file`, `--add-dir`, or `--model`. Persist Jules session handles and reconcile pulled results into the same completed-work packet contract. Suggested marker: `JULES_CLI_SESSION_CONTEXT_PACK_OK`.

Session detail: `references/agent-cli-context-pack-optimization-2026-07-18.md`; Jules-specific implementation detail: `references/jules-cli-session-context-pack-2026-07-18.md`.

### AGY CLI context packs / standardized output

When optimizing AGY CLI dispatch, keep Michael/Kai's work-packet theory intact: durable context lives in files; stdout/chat gets only the compact standardized result packet. The preferred AGY launch shape is:

```text

assigned-agent event
→ tiny `agy --print` prompt
→ durable context directory added with `--add-dir`
→ `CONTEXT_PACK.md`, `WORK_PACKET.md`, `PACKET_CONTRACT.md`
→ exact completed-work packet lines on stdout/log
→ wrapper appends conservative `RESULT=BLOCKED` if AGY exits without exact packet markers
→ launch record stores context-pack paths and expected/blocked markers
```

Implementation guardrails:

- Keep the `agy --print` prompt small: point to the context/work packet files instead of embedding long instructions.
- Include shared skill-pack state, AGY skill-pack state, packet contract version, expected success marker, blocked marker, proof shape, and explicit non-claims in `WORK_PACKET.md`.
- Add only the repo/worktree and the context-pack directory via `--add-dir`; do not expose unrelated large folders.
- Redact token-like assignment text before writing context files.
- Store context-pack metadata in launch records so dashboard/writeback/raw-output repair can reconcile later.
- Verify with a fake AGY binary that emits no packet: the wrapper must still append a blocked packet and preserve context-pack paths.

Expected marker for this class of change: `AGY_CLI_CONTEXT_PACK_OK`.


### Jules CLI session context packs / standardized output

When optimizing Jules dispatch, do **not** copy the AGY `--print`/`--log-file` shape. Live-check the installed Jules CLI first. On this host Jules is async/session-based and supports `jules new`, `jules remote list --session`, and `jules remote pull --session`; it does **not** support AGY-style `--issue`, `--task`, `--print`, `--log-file`, `--add-dir`, or `--model` flags.

Preferred Jules launch shape:

```text
assigned-agent event
→ `CONTEXT_PACK.md`, `WORK_PACKET.md`, `PACKET_CONTRACT.md`
→ tiny `jules new <compact prompt>` pointing at those files
→ optional `PRISMATIC_JULES_REPO=owner/repo` maps to `jules new --repo owner/repo <prompt>`
→ session capture log records context/work packet paths and skill-pack state
→ launch record stores context-pack metadata and reconcile hint
→ later reconciler uses `jules remote list --session` + `jules remote pull --session <id>`
→ pulled result is normalized into the same completed-work packet contract
```

Implementation guardrails:

- Keep Jules work bounded to review/test/QA unless the task explicitly authorizes broader async implementation.

- Store session capture log, expected/blocked markers, context-pack paths, and `jules remote ...` reconcile hint in `launch_records.execution_context`.
- Preserve the shared completed-work proof shape so Jules output can flow through the same raw-output repair/dashboard/Linear writeback gates as AGY/Fred/George/Kai.
- Redact token-like assignment text before writing context files.
- Verify with a fake Jules binary that fails if unsupported flags are used; assert `jules new` is used and no `--issue`, `--task`, `--print`, `--log-file`, or `--model` appears.

Expected marker for this class of change: `JULES_CLI_SESSION_CONTEXT_PACK_OK`.

### AGY bulk-dispatch failure prevention for rubric/RC task trees

Large PE rubric/RC task trees are dependency-staged products, not a flat pool of independent AGY jobs. Before dispatching them:

1. **Preflight the target agent model/config with one tiny task.** A stale model alias can make every sandbox abandon before the agent reads the task. Known AGY failure signature from 2026-07-14: `invalid --model "gemini-3.5-flash-high"`, available model names were display-style strings such as `Gemini 3.5 Flash (High)`, and logs showed `dispatch.tokens.actual_input=0` / `actual_output=0`.
2. **Do not put every future-stage issue on `dispatch:ready` at once.** Stage the sequence: scorecard baseline → supplemental audit coverage → cohesive app stitching → RC1 audit → blocker fixes/release proof. Use paused/dependency labels or comments for post-pass/RC tasks until predecessor evidence exists.
3. **Use task-type-aware sandbox guards.** Research-only tasks can forbid long tests/builds, but audit/release-proof tasks must be allowed to run bounded clean checkout, install, smoke, build, and test commands. A generic “do not run git clone / pip / pytest / npm” guard conflicts with RC1 portability proof.
4. **Classify zero-token abandons as dispatch failures, not agent work failures.** If the sandbox has only ignore files, task handoff docs, `STARTED.md`, and an auto-generated abandoned result, no real task work happened. Reset Linear state after fixing dispatch config rather than interpreting the abandoned result as evidence.
5. **Do not over-scope dispatch recovery as AGY-only.** Michael expects the old useful behavior restored: work assigned/labeled for Kai wakes Kai, Fred work wakes Fred, AGY work wakes AGY, and always-on workers like Ned can claim eligible work safely. Model this as `Linear/task event → durable queue → agent resolver → per-agent preflight → safe dispatch/wake-up → execution result → dashboard state`.
6. **Add multi-agent proof gates when dispatch generally is in scope:** `AGENT_RESOLVER_OK`, `PER_AGENT_PREFLIGHT_OK`, `MULTI_AGENT_DISPATCH_CONTRACT_OK`, and, before Ned-style always-on operation, `ALWAYS_ON_WORKER_SAFETY_OK`.
7. **Guard always-on workers.** Require enabled-agent allowlists, clear routing rules, per-agent preflight, dependency/stage guards, one-task proof before batch mode, rate/max-claim limits, dry-run, dashboard-visible claim/running/completed/failed states, operator pause/stop, no secret leakage, and no cross-agent task stealing unless explicitly configured.

Session-specific details and evidence live in `references/agy-dispatch-failure-rc1-rubric-2026-07-14.md`.


### Assigned-agent wake dispatch recovery

After queue/drain/preflight recovery, do **not** leave the architecture AGY-only. Michael's desired workflow is assigned-agent wake dispatch: tasks assigned/labeled for Kai wake Kai, Fred wakes Fred, AGY wakes AGY, and unknown/ambiguous routing returns `needs_manual_review` without waking anyone. This is distinct from uncontrolled always-on worker behavior.

For recovery work, prove the staged markers in order: durable queue, bounded drain, dispatch preflight, dashboard operator proof, assigned-agent resolver/preflight/wake behavior, then exactly one AGY canary task. The AGY canary may use the installed `agy --print ... --model "Gemini 3.5 Flash (High)" --log-file ...` shape; if AGY logs do not expose token counters, accept equivalent nonzero proof (`prompt_length`, `task_payload_bytes`, `result_text_bytes`, result artifact, Linear writeback, and `no_other_tasks_launched`). Only after the canary and behavior proof pass may you claim `ASSIGNED_AGENT_DISPATCH_RECOVERY_OK` / `DASHBOARD_DISPATCH_INGESTION_READY_OK`, and even then report it as **ad-hoc targeted recovery proof, not canonical full suite green**. Do not bulk redispatch; first review the canary work product, then dispatch only the next approved small stage.

Detailed session pattern, Ned caveat, markers, and post-canary staging live in `references/assigned-agent-dispatch-recovery-2026-07-15.md`.

### Production durability standard / live route repairs

When a Prismatic-managed production route, dashboard, plugin page, gateway API, or public operator surface is broken/blank/stale, treat the incident as a **production durability** problem, not only a route bug. Michael's standard is: production must live durably. Live services must not depend on a mutable multi-agent development checkout being on the right branch.

For production-facing fixes, enforce this ladder:

```text
clean production-safe branch/worktree
→ local gateway/service reproduces the problem
→ patch in reviewed branch, not mutable live checkout
→ local route/API/browser proof passes

→ path safety/security checks pass
→ merge in dependency order when authorized
→ update durable runtime checkout, not mutable dev checkout
→ intentional deploy/restart/reload
→ public/authenticated route proof passes
→ browser/console proof attached
→ production source/worktree remains durable and clean
```

When Michael explicitly asks to merge/deploy dashboard/operator PRs, re-check PR state/CI first, merge in dependency order, update the durable runtime checkout, run targeted compile/smoke checks, restart services intentionally, verify local routes before public routes, then click the relevant dashboard tab in browser and inspect console errors. If `gh pr merge --delete-branch` fails because a local branch is checked out in another worktree, verify whether the PR actually merged before retrying. If a follow-on PR becomes unmergeable because main advanced, update the PR branch from `origin/main`, rerun targeted verification, push, then merge. Detailed pattern: `references/dashboard-source-audit-merge-deploy-2026-07-17.md`.

Hard rules to embed in Fred/AGY/Kai/Ned/Jules prompts:

- fix from a clean production-safe branch/worktree;
- stop relying on the mutable shared worktree for production;
- make user-facing pages robust even if CDN scripts fail;
- preserve path safety and block traversal;
- verify local gateway before public route;
- restart/deploy production intentionally;
- provide screenshot/browser proof;

- never claim a production route is fixed from code/static checks alone.

For `/workspace-tree`-class failures, first verify local gateway routes before nginx/public debugging, and prevent black pages by shipping visible no-JS/dependency-failure fallback or a self-contained no-CDN shell. Workspace-tree APIs must resolve only under configured workspace roots and block traversal. Use precise reporting: `Standard installed ≠ workspace-tree fixed`, `workspace-tree fixed ≠ all production risks eliminated`, and focused route verification is not full dashboard suite green.

Session details, markers, and reusable prompt language live in `references/production-durability-standard-2026-07-15.md`.

### Post-standard/runway goal prompts for Fred

When Michael asks for the next Fred prompt after a Prismatic standard, production route repair, or dispatch-recovery milestone, produce an executable goal prompt rather than a loose plan. Prefer a Telegram-deliverable `.md` doc. The prompt should execute in order, start with prerequisite/fallout checks and a live runway audit, then select the next 1–3 tasks from evidence. If the full scope is too large, instruct Fred to complete at least Step 1 and Step 2 with proof and return the exact next action. Include final markers and a required return-packet table. Session pattern: `references/post-durability-runway-goal-prompts-2026-07-16.md`.

When a PR branch has advanced beyond its original description, make PR closeout the first step before starting the next task: update the PR body/Linear writeback so scope, files changed, tests, markers, and non-claims match the current branch. Do not let Fred continue to the next runway slice while the active PR still says "docs-only" or otherwise under/over-claims what landed. Use compact verification output from the `compact-verification-output` skill by default.

## Linear API polling burn / event-driven dispatch recovery

When Michael asks about Linear API limits, over-polling, rate-limit burn, dispatcher recovery, event-based dispatch, webhook queues, or assigned-agent wake behavior, run a **live source-and-runtime audit** before proposing fixes.

Required audit shape:

1. Query Linear with a minimal safe GraphQL request and record only rate-limit headers — never print token values.
2. Inspect active services/timers/processes and the durable runtime checkout, not only the mutable dev worktree.

3. Count dispatcher Linear call paths per cycle. Broad calls such as `setup_pipeline_issues()`, `route_dispatch_ready_issues()`, per-agent `get_issues_with_label(...)`, `recover_stalled_agy()`, and `detect_origin_completions()` can exceed the request cap even while idle.
4. Parse dispatcher/gateway/consumer logs separately. Dashboard local route polling is noisy but is not Linear API burn unless the route internally calls Linear.
5. Inspect webhook/event/queue state: webhook endpoints, event bus, `linear_webhook_queue.db`, drain script, drain timer/service state, and any event consumer.
6. Rank existing branches/worktrees into reuse buckets for Fred; do not rebuild before checking the prior assigned-agent / ingestion-queue branches.

Use staged recovery markers rather than one vague “fix polling” task:

```text
LINEAR_RATE_LIMIT_CIRCUIT_BREAKER_OK
DISPATCHER_POLLING_BUDGET_OK
LINEAR_WEBHOOK_QUEUE_ACTIVE_OK
ASSIGNED_AGENT_EVENT_DISPATCH_OK
LINEAR_EVENT_DRIVEN_DISPATCH_RECOVERY_OK
```

Pitfalls:

- Do not claim event-driven dispatch is active just because `/api/gateway/linear` or `/webhooks/linear` exists.
- Do not add new broad Linear pollers or increase `get_issues_with_label` scan frequency.
- Do not enable a masked/old webhook drain timer until its service path points at the durable runtime checkout and queue proof passes.

- Do not expose Linear tokens/API keys; report only header names/counts/reset timestamps. Watch for `systemctl cat` output leaking `Environment=LINEAR_API_KEY=...`; sanitize logs before reading/reporting them.
- If Linear request-count remaining is low but complexity remaining is high, optimize request count first.
- After a rate-limit circuit breaker slice lands, keep the closeout narrow: verify PR/CI/runtime head, `/api/gateway/linear/rate-limit`, old-poller disabled/gated, no poll process, no dispatcher log growth, and focused tests. Do **not** collapse Slice 1 into webhook queue, assigned-agent event dispatch, or full event-driven recovery.
- After a dispatcher polling-budget slice lands, verify the deployed runtime exposes `polling_budget` through the actual implemented status/rate-limit endpoints. Do not fail the slice just because a guessed standalone endpoint such as `/api/gateway/dispatcher/polling-budget` is absent/405 if `/api/gateway/linear/rate-limit` and `/api/gateway/dispatcher/status` carry the required `DISPATCHER_POLLING_BUDGET_OK` marker and fields. Keep non-claims explicit: webhook queue active and assigned-agent dispatch are still future slices.
- After a Linear webhook queue slice lands, verify deployed runtime APIs (`/api/gateway/webhooks/queue/status` and `/api/gateway/webhooks/queue`), durable source `linear_webhook_queue.db`, focused queue tests, dashboard JS syntax, old-poller gate state, and cooldown deferral semantics (`deferred_rate_limit`, zero dispatch attempts, drain counts include `deferred=1`). Do **not** collapse this into `ASSIGNED_AGENT_EVENT_DISPATCH_OK`; exact-agent resolver/preflight/wake remains the next slice.
- After an assigned-agent event-dispatch slice lands, verify the exact changed paths (`prismatic/dispatcher.py`, `prismatic/ingestion_queue.py`, `scripts/drain_webhook_queue.py`, and assigned-agent tests), deployed `/api/gateway/webhooks/queue/status` with `assigned_agent_marker=ASSIGNED_AGENT_EVENT_DISPATCH_OK`, routing/preflight/dispatch fields (`target_agent`, `routing_source`, `resolver_status`, `preflight_status`, `claim_owner`, `run_id`, `last_error`), Kai/Fred/AGY resolver tests, ambiguous/unknown/claimed/cooldown fail-closed tests, old-poller gate state, and focused runtime tests. Do **not** collapse this into `ASSIGNED_AGENT_RESULT_WRITEBACK_OK`; live Linear mutations/result writeback remain the next slice unless explicitly proven and authorized.
- If another agent reports a stale detector repeat after a valid proof, run one fresh scoped `/tmp/hermes-verify-*` verifier against the exact changed paths and live runtime markers, remove it, and emit only the compact proof block. Do not ask for repeated narrative reruns or broaden scope unless the scoped verifier fails.
- If Michael asks whether to send an older digest while Fred is iterating, provide a refreshed next-slice prompt that reflects the latest deployed marker instead of recycling stale instructions.

Session details: `references/linear-api-polling-burn-event-dispatch-2026-07-17.md`, `references/linear-rate-limit-circuit-breaker-closeout-2026-07-17.md`, `references/dispatcher-polling-budget-closeout-2026-07-17.md`, `references/linear-webhook-queue-closeout-2026-07-17.md`, and `references/assigned-agent-event-dispatch-closeout-2026-07-17.md`.

## Telegram lane bridge for interim Kai/Fred/George coordination

When Michael wants George to proactively coordinate Kai and Fred before durable Prismatic assigned-agent dispatch is fully ready, use Telegram lane groups as an interim dispatch surface — but keep Prismatic as the eventual source of truth.

Use focused groups, not one all-agent room:

- Kai lane: `Prismatic Kai`, delivery target `telegram:-5338154051`.
- Fred lane: `Prismatic Fred`, delivery target `telegram:-5167970174`.
- George/DM/control lane: Michael-facing status, merge-readiness, blockers, and authorization requests.


Lane ownership pattern:

```text
Kai = golden-path implementation spine
Fred = bounded adjacent hardening
George = prompt pacing, verification, PR/runtime/dashboard/API audit, stale-branch guard
Michael = explicit authority for merges/deploys/real side effects
```

George may proactively read state, write prompts, send lane prompts, verify reports, flag stale PRs, and recommend merge order. George must wait for explicit Michael authorization before merging PRs, production deploy/restart beyond authorized closeout, real Linear/GitHub side effects, bulk/autopilot dispatch, or closing/deleting PRs.

Telegram setup gotchas:

1. Sending to a group proves write access only; inbound replies require `telegram.allowed_chats` and Telegram BotFather group privacy/read settings.
2. Add each group id to the correct Hermes profile, e.g. George gets both lane groups, Kai gets the Kai group, Fred gets the Fred group.
3. In BotFather, disable Group Privacy for each bot that must read normal group messages; remove/re-add the bot if needed.
4. Restart/reload the profile gateway after config changes. Hermes blocks a gateway from restarting itself from inside that same gateway session; restart George externally, or start Kai/Fred replacement gateways with `hermes --profile <profile> gateway run --replace` when authorized.
5. Keep `require_mention=true` initially and ask participants to mention the target bot explicitly to prevent noisy/recursive responses.


Dispatch prompt pattern:

```bash
hermes send --to telegram:-5338154051 --subject 'KAI DISPATCH — <MARKER>' \
  'Kai, please take this Prismatic lane task. Full prompt attached. Return the required compact proof packet in this group. MEDIA:/absolute/path.md'

hermes send --to telegram:-5167970174 --subject 'FRED DISPATCH — <MARKER>' \
  'Fred, please take this Prismatic lane task. Full prompt attached. Return the required compact proof packet in this group. MEDIA:/absolute/path.md'
```

Verify prompt artifacts before sending with a small `/tmp/hermes-verify-*` required-marker/no-secret scan. Keep one owner per marker, e.g. Kai gets `ONE_AGENT_OPERATOR_VERIFICATION_LOOP_OK`; Fred gets `INVALID_PACKET_REPAIR_QUEUE_OK`; George verifies both before pacing next work.

A read-only event watcher can approximate event-based coordination until Prismatic owns durable wake dispatch. Session details and exact config commands live in `references/telegram-lane-dispatch-bridge-2026-07-19.md`.
