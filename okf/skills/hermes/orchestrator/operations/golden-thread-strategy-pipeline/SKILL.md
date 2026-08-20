---
name: golden-thread-strategy-pipeline
description: Run Daily Golden Thread style research → strategy → task creation → execution pipelines for stalled projects, with orchestrator research/execution, Fred synthesis, Linear task creation, and verified reporting.
---

# Golden Thread Strategy Pipeline

## When to Use

Use this skill when a cron/job/session asks to:
- Pick a stalled project from the project registry.
- Research assumptions/competitors/gaps.
- Synthesize strategy into concrete Linear tasks.
- Execute at least one task through AGY or another execution gauntlet.
- Produce a structured Golden Thread report.
- **Answer a portfolio-wide "what gaps need filling?" question with a ranked table and one next action.** See `references/portfolio-gap-analysis-2026-07-27.md`.
- **Run a self-critique when the user asks "what gaps are there in your profile / what can you optimize?"** See `references/agent-self-review-2026-07-27.md` for the structured 8–12 axis shape and top-3 commitment pattern.

## Core Workflow

1. **Select the project from durable sources first**
   - Read `/home/ubuntu/work/project-registry.json`.
   - If Linear is available, query current non-done issues.
   - If Linear is temporarily rate-limited, continue from registry + local cached issue context, then retry Linear mutations later before reporting failure.
   - Pick the project with the oldest/stallest `next_action`; apply the requested revenue/project priority tiebreakers.

2. **Build a structured research input**
   Include:
   - Project name, slug, template/type, current state, next action.
   - Linear issue identifiers/descriptions available from live API or local cache.
   - Current artifacts: repo path, deployed URLs, docs, package metadata, README, Dockerfile, known status.
   - Explicit assumptions to challenge.
   - Known competitors.
   - Required JSON schema for research output.

3. **Run orchestrator research in parallel where possible**
   Typical split:
   - Assumption challenge.
   - Strategy discovery.
   - Gap analysis.

   Save raw outputs and exits under:
   `/home/ubuntu/work/research/orchestrator-outputs/{project-slug}-{date}-{kind}.raw`

4. **If an orchestrator research call times out, reduce scope and rerun**
   - Ask for fewer strategies/claims.
   - Demand JSON only.
   - Cap word count.
   - Prefer a smaller targeted prompt over abandoning the phase.

5. **Synthesize with evidence checks**
   - Parse orchestrator JSON, but treat it as untrusted self-report.
   - Verify high-impact claims against local files, terminal evidence, or web evidence when available.
   - Correct orchestrator hallucinations in the final synthesis rather than repeating them.
   - For outbound/revenue projects, reconcile registry `next_action` against canonical pipeline/tracker docs, CRM/export files, and launcher/email assets before creating any fresh-send task. A stale registry action can cause duplicate outreach or wrong-recipient sends; stale tracker text can also falsely imply emails were sent. **Never mark outbound emails sent/contacted or create active follow-up schedules without Michael's explicit confirmation that he sent them.** Treat reconciliation as the revenue-protecting action when sources disagree. See `references/ai-consulting-outreach-reconciliation-2026-07-08.md`.
   - When outbound is blocked on Michael's manual send and reconciliation confirms zero sent/contacted records, convert the next pipeline move into send-safe enablement: partner kit, Michael-only send checklist, CTA path, and signal tracker. Do not create another agent-send or follow-up task. See `references/ai-consulting-msp-channel-activation-2026-07-09.md`.
   - For AI Consulting when both MSP/channel and direct vertical speed are unproven, prefer a Michael-only split-test checklist (for example 5 MSP leads vs 5 direct legal/healthcare leads) over assuming either channel wins. Keep CRM sent/contacted counts unchanged and define 7-day reply/intro/booked-audit/explicit-no thresholds. See `references/ai-consulting-split-test-manual-send-2026-07-23.md`.
   - Build a strategy comparison matrix with revenue/speed/alignment/risk.
   - Create falsifiable assumption tests.

6. **Create Linear epics/tasks with exit criteria and rubrics**
   For broad strategy items, create class-level epics plus child tasks rather than a flat task dump. Each epic and child task must include:
   6. **Create Linear tasks with rubrics and exit criteria**
      Each generated task must include:
      - Title.
      - Project/team IDs if known.
      - Concrete implementation description.
      - A four-part rubric:
        - Unit.
        - Integration.
        - Revenue.
        - Assumption.
      - An explicit **Exit criterion**. For this user, `Done` is not code completion or doc completion; `Done` means the exit criterion is satisfied with evidence.

      **For any task that becomes part of a Linear epic tree, use the seven-field description shape defined in `linear-handoff-build-out`:** parent exit criterion (verbatim), epic exit criterion (verbatim), first step, rubric, target path, acceptance test IDs, plan reference. Tasks shorter than this are non-conformant. The seven-field shape is not just for "feature" epics — it is the default for every Linear task that has a parent epic and an exit criterion.

      **One-approval gate between OKF docs and Linear mutation:** when a strategy naturally flows into a Linear epic + child tasks, write the OKF artifacts first (standard, project index, decisions with Owner + Acceptance Test IDs, risk with named owners + observable signals, HANDOFF.md), verify, then pause **exactly once** for approval, then create the full Linear tree in one batched mutation. Do not pause between OKF docs and Linear mutation, do not re-confirm scope after each phase, and do not ask "approve?" twice. See `okf-documentation-ops` §16 and `linear-handoff-build-out`.

      **Cold-start fitness is a first-class acceptance criterion.** A build-out is not done when the files exist; it is done when a different agent can pick it up cold via the HANDOFF.md read order + the seven-field task descriptions. Michael has explicitly asked "is there enough documentation?" after a build that looked complete — that question is the trigger to extend the bundle, not to declare it done. See `okf-documentation-ops` §6.

   If Linear rate-limits mid-creation, do not claim completion. Write an idempotent continuation script that upserts by title, preserves parent-child links, and prints created/updated identifiers. Schedule a one-shot retry after the reset window and report the partial state plus blocker.

7. **Execute the top task through AGY or directly when the task is infrastructure/demo-gate work**
   - Use AGY for execution if the job requires it.
   - Include the full task JSON and rubric.
   - Tell AGY to return pass/fail with terminal evidence.
   - For distribution/first-user readiness gates, prefer a deterministic repo script plus fresh-install smoke over agent self-report. See `references/distribution-readiness-gate-2026-07-08.md`.
   - For demo-wedge tasks, produce a replayable fixture plus artifact bundle before attempting live credentialed Linear/GitHub/AGY paths. The fixture should show trigger → governed route → bounded work → verification → cleanup, and should generate a 90-second script, capture checklist, evidence JSON, and feedback package. See `references/proof-loop-demo-wedge-2026-07-08.md`.
   - For verified-execution-contract tasks, define the evidence payload and Done gate before wiring dashboards/status moves. Include explicit verification status, scope, failure category, commands/artifacts, side effects, cleanup status, and blocker fields. Add fixture examples for success/partial/blocked/failed and a negative test proving `Done` is rejected without verified evidence. See `references/verified-execution-contract-2026-07-08.md`.
   - After the evidence schema exists, wire the contract into operator-visible run surfaces (`AgentRunRecord`, reports, `/runs` payloads) so `status=completed` without proof appears as `verification_status=self_reported` + `done_gate_result=not_done`, not as Done. See `references/run-record-evidence-surfacing-2026-07-08.md`.
   - For stale blocker closeout, live-check Linear first, implement only the missing acceptance slice, publish via a clean PR if needed, post exact evidence, move only evidenced issues to Done, and remove stale routing labels (`dispatch:ready`, `agent:peer-review`, `agent:needs-human-review`) that would keep completed work surfacing as blocked. See `references/blocker-closeout-linear-pr-2026-07-09.md`.
   - For backlog watchdog outputs where multiple `dispatch:ready` issues are blocked by prerequisite chains, load `linear-backlog-routing-governance`. Model the downstream → prerequisite graph explicitly, release only chains whose prerequisites are already completed, hold chains with unmet prerequisites, and schedule a one-shot retry if Linear rate-limits live mutation.
   - For Active Oahu static mirror / AI SEO runs where the registry still says DNS cutover or live 404 recovery is urgent, first reconcile with fresh apex+mirror HTTP checks and local DNS/Page audit evidence. If cutover is already complete, update the registry and pivot tasks toward CRO: styled booking CTAs, conversion signal tracking, and revenue-risk bucketing of broken references. See `references/active-oahu-dns-cro-reconciliation-2026-07-11.md`.
   - For Active Oahu CRO tasks based on an older inline CTA audit, do not patch source HTML directly from the stale report. First run a no-edit classification pass that verifies all CTA rows, exact anchor drift, locale drift, live destination status/redirects, and revenue-priority patch order; only then create/execute implementation tasks. See `references/active-oahu-cro-cta-reconciliation-2026-07-20.md`.
   - For Sentinel ITAD / hardware resale runs where manual selling and automation tickets are both active, live-check Linear and inventory first, then prefer a manual listing proof packet over building converter/dashboard tooling before a sale exists. Include a Michael-only publish checklist, revenue math, canonical inventory citations, and a deterministic artifact verifier; never publish live marketplace listings or mark items sold from the cron pipeline. See `references/sentinel-itad-manual-resale-proof-2026-07-22.md`.
   - For "stop and survey the project field before acting" recon requests, use the briefing-artifact shape (TL;DR, verified-snapshot table, active-cluster with strategic role, source-of-truth map, where-are-we, where-going, three bounded next moves with `dispatch:ready` deltas, explicit what-is-NOT-urgent list, verification packet). See `references/sentinel-itad-live-recon-and-linear-api-gotchas-2026-07-27.md` for the worked Sentinel example plus the Linear API filter-schema gotchas the recon hit (`ProjectFilter.team` doesn't exist; use `Project.slugId` not `slug`; `IssueFilter.identifier` doesn't exist — filter through project then match client-side).

8. **Handle orchestrator execution timeouts safely**
   If orchestrator execution times out after starting background commands or gives partial self-report:
   - Rerun a bounded verification-only orchestrator call.
   - Explicitly say: no background processes, no edits unless required, bounded foreground checks only, JSON only.
   - Then independently verify the orchestrator claims before reporting.

9. **Report with links and evidence**
   Include:
   - Selected project.
   - Assumption challenges: confirmed/challenged/false with evidence.
   - Strategy comparison matrix.
   - Winning strategy and why.
   - Linear tasks created, with identifiers linked.
   - Execution result with four rubric checks.
   - One-sentence forward momentum.

10. **Promote durable evidence into OKF**
   - Hermes profile `output/` files and Telegram document-cache copies are temporary delivery/session artifacts, not canonical storage.
   - For Prismatic/OKF governance work, put the durable copy in OKF:
     - incident/remediation evidence → `okf/audits/incidents/YYYY-MM-DD-slug.md`
     - operational audits / recurring scan evidence → `okf/audits/YYYY-MM-DD-slug.md` or an existing audit subfolder
     - strategy, architecture, operating docs → `okf/operations/YYYY-MM-DD-slug.md`
     - standards/rubrics → `okf/standards/slug.md`
   - After writing a durable OKF artifact, run a focused `/tmp/hermes-verify-*.py` checker against the artifact itself and report it as ad hoc targeted verification, not suite-green.
   - If a post-turn verification nudge asks for a temporary verifier, create it with an OS-safe `tempfile` path/prefix (for example `tempfile.mkstemp(prefix="hermes-verify-", suffix=".py", dir="/tmp")`) from a terminal command, run it, then remove it in the same command. Avoid `write_file` for these temporary `/tmp` verifiers when possible, because the verifier itself can be reported as an additional changed path and trigger another verification loop.
   - If the verification nudge repeats, rerun the same focused temporary-verifier pattern against the exact changed paths named by the nudge, and explicitly label the result as **ad-hoc targeted verification, not suite green**. Include the verifier output and the cleanup fact in the reply; do not assume a previous final-answer summary satisfied the detector. Prefer machine-legible verifier output with `status`, `verification_type`, `checked_paths`, `runtime_command`, and `evidence_path`. Make sure the wrapper imports every module it uses (for example `json` if it prints cleanup JSON) so a passing inner verifier is not followed by a wrapper `NameError`; see `references/hde-surface-validator-and-repeat-verifier-nudge-2026-07-17.md` and `references/ai-consulting-split-test-manual-send-2026-07-23.md`.
   - If changed Markdown/report artifacts mention secret-provider placeholders, avoid literal credential prefixes even when redacted or illustrative. Verifiers may flag strings like Stripe/GitHub/Google/token prefixes inside prose. Use neutral wording such as “credentials are unset or redacted” and rerun the exact changed-path verifier; see `references/verification-nudge-secret-marker-and-changed-paths-2026-07-18.md`.
   - If an OKF/report artifact documents a verifier that scanned another file for forbidden claims, do **not** embed the exact forbidden phrases in the durable artifact when the artifact verifier checks for those phrases. Use category labels in the artifact (`unsupported full compliance phrasing`, `unverified customer velocity proof`, etc.) and keep exact strings in transient `/tmp/hermes-verify-*` output or raw evidence paths. Otherwise the artifact can fail its own no-forbidden-marker check. See `references/okf-artifact-forbidden-marker-verification-2026-07-21.md`.
  - When the changed path is an OKF/report artifact, verify the artifact's own contract rather than the final chat-delivery shape: required OKF sections, selected project, research paths, assumption/strategy tables, Linear IDs, rubric evidence, guardrails, verification commands, and absence of placeholders. Do not require mobile links or final-response headings unless the artifact itself promises them. See `references/okf-artifact-verification-nudge-2026-07-16.md`.
   - When creating inline `/tmp/hermes-verify-*` scripts through `terminal()`, avoid literal `&` characters anywhere in the command body, including Python string literals and expected Markdown headings. The terminal foreground guard can misread a harmless ampersand inside heredoc text as shell backgrounding. Verify such headings by checking adjacent substrings separately or building the ampersand with `chr(38)`. If the guard fires, retry once with the same verifier logic but remove the literal ampersand; see `references/temp-verifier-ampersand-guard-2026-07-15.md`.
   - When the verifier script under test is itself a Python CLI that you just edited, the verifier MUST also clear the CLI's sibling `__pycache__/` (or run the verifier with `python3 -B`) before asserting round-trip behavior. Stale bytecode silently shadows the edited source and produces a green verifier against the wrong code. See `agent-operations/session-state-handoff/references/python-cli-pitfalls.md` pitfall #3.
   - The verifier wrapper shell snippet MUST import every module it uses (`json`, `os`, `sys`, `subprocess`, `tempfile`, `shutil` at minimum). A missing `import json` makes the wrapper `NameError` AFTER the inner verifier prints PASS, and the post-turn detector reads the run as failed even though the inner contract held. Same reference file, pitfall #7.
   - When the verifier exercises an argparse CLI, define the four global flags (`--profile`, `--agent`, `--path`, `--archive`) on the top-level parser and re-emit them in canonical order BEFORE the subcommand in `main()`. `parents=[…]` on subparsers silently re-defaults user-supplied pre-subcommand globals and your verifier "fails" against a CLI that would otherwise be correct. Same reference file, pitfall #1.
   - If AGY edits files but times out before returning final rubric evidence, switch to bounded direct verification: inspect only the intended changed paths, remove scratch/debug artifacts, run the smallest tests that exercise the task rubric, post/persist evidence, and report AGY as timed out rather than self-reported PASS. If a post-turn verification nudge names a canonical command such as `npm run build`, run that exact command too and report its exit/output as fresh verification evidence even if targeted tests already passed. See `references/darius-star-telemetry-execution-and-build-verification-2026-07-14.md`.
   - If AGY execution exits 0 but includes scratchpad/progress chatter such as “I am waiting for…”, treat the claimed PASS as untrusted until direct repo verification proves the rubric. For playable demos/browser games, verify existing implementation before creating new feature work; if AGY claims a feature is missing but live files show it exists, create a regression gate instead of duplicate implementation. See `references/darius-star-playtest-telemetry-closeout-2026-07-17.md`.
   - If the OKF repo has unrelated dirty changes, do not commit opportunistically; report the path and git state.

   11. **Remediate AGY Golden Thread cron deltas from full rows, not digest headings**
    - A Telegram cron delivery that only says `Gaps Detected / Security/Credential Bleeds / Remediation Paths` is a trigger, not evidence.
    - If AGY exits 0 but says it is waiting for a background task, treat the message as scratchpad/non-evidence. Recover real rows, live-check Linear, and patch the no-agent wrapper to strip waiting/progress chatter while preserving real tables. See `references/agy-golden-thread-scratchpad-and-linear-routing-cleanup-2026-07-13.md`.
    - Recover the full rows from scheduler/session output or rerun the no-agent script once in foreground before mutating anything. For `AGY Golden Thread Project Review`, first check `~/.hermes/profiles/orchestrator/cron/output/<job_id>_*.txt` and the deterministic wrapper `~/.hermes/profiles/orchestrator/scripts/agy_golden_thread_delta.py`.
    - For Golden Thread Daily Digest failures, prefer a deterministic read-only no-agent script over a fragile LLM prompt when the digest contract is stable. Use `/home/ubuntu/work/project-registry.json`, explicit `gh -R owner/repo` commands, remove missing skill dependencies, set the cron workdir to `/home/ubuntu/work`, and verify via scheduler run plus `/tmp/hermes-verify-*`. The daily digest reports; a separate sync job should own registry mutation.
    - Verify every AGY-cited Linear issue live; correct hallucinated or stale identifiers in the final artifact. If the cron output shows Linear hydration as `None`/`0` for many projects while live Linear has issues, create a separate remediation for the hydration/rendering bug instead of trusting the stale fields.
    - For registry drift, update `/home/ubuntu/work/project-registry.json` to active live issues and record known-bad references when useful.
    - When Michael asks to build remediation paths into Linear, create/update classed remediation issues with a stable prefix such as `AGY REMEDIATION —`, attach them to the most specific Linear project, route AGY-executable work via `agent:agy` + `dispatch:ready` + the appropriate AGY model label, and post short audit comments on the source issues named by the rows.
    - Apply explicit operator overrides before routing AGY remediation rows. Active Oahu no longer uses Weglot: remediation should remove legacy Weglot plugin markup/scripts/styles/API initializer blocks while preserving static English/Japanese navigation and booking CTAs; do **not** externalize/configure Weglot keys or reintroduce Weglot. The Active Oahu FareHarbor item-ID/product-grid row is paused unless Michael reopens it; suppress/update stale registry or cron rows instead of creating fresh FH/product-grid work. See `references/active-oahu-weglot-and-paused-fareharbor-remediation-2026-07-22.md`.
    - If credential-bleed language appears, also inspect local `.git/config` remotes for tokenized GitHub HTTPS URLs and strip credentials without printing values. For local `.env` or scratch-config secret bleeds, replace plaintext provider values with environment-variable references such as `api_key_env: GEMINI_API_KEY`, remove any plaintext backup created during editing, document external dashboard/API rotation that cannot be performed from the host, and verify the evidence artifact itself does not contain secret/token prefixes. See `references/agy-golden-thread-remediation-2026-07-09.md`, `references/agy-golden-thread-linear-remediation-2026-07-12.md`, and `references/agy-gt-linear-auth-routing-and-secret-hygiene-2026-07-18.md`.
    - When mutating Linear from AGY Golden Thread rows, distinguish raw Linear API keys from OAuth tokens: raw `LINEAR_API_KEY` is sent as the `Authorization` header value without `Bearer`; OAuth tokens use `Bearer`. If team-local label lookup does not show routing labels like `agent:agy`, query workspace-global `issueLabels(first: 250)`. If `issueSearch(term:)` is unsupported in the active schema, stop retrying search and use issue-number lookups or create a bounded owner-routed issue with duplicate risk documented. See `references/agy-gt-linear-auth-routing-and-secret-hygiene-2026-07-18.md`.

## Pitfalls

- **Do not stop at research.** These jobs require at least one concrete execution attempt unless impossible.
- **Do not trust orchestrator JSON blindly.** The orchestrator may hallucinate file versions, missing modules, or execution state. Verify critical claims.
- **Do not execute stale outbound next actions directly from the registry.** For outreach tasks, first compare canonical pipeline docs, CRM/export data, and send-launcher/email assets. If they disagree, create/execute a reconciliation task before any fresh-send task.
- **Do not turn a manual-send blocker into agent-send work.** If no emails have been sent and Michael is the required sender, build send-safe enablement instead: a Michael-only checklist, a partner/offer kit, a CTA path, and a signal tracker. Verify CRM `sent/contacted` counts remain unchanged after execution.
- **Do not trust an orchestrator artifact PASS without deterministic checks.** Re-check required sections, revenue CTA, assumption signals, and side effects yourself. For Markdown artifacts, treat `TODO`/`TBD` as placeholders, but do not confuse normal checklist boxes (`- [ ]`) with unfinished placeholders.
- **Do not accept a self-consistent verifier PASS as ground truth when the artifact is supposed to mirror reality.** A verifier that only checks "JSON parses + required keys present + formula gates" will PASS on factually-wrong values: a placeholder tracking ID (`G-AOT-PLACEHOLDER`), invented event names that don't exist on the live site, URL paths that don't resolve, dates that conflict with canonical sources. `44/44 PASS` on a JSON file means nothing if the verifier never asked "is this value true to the live site?" For any artifact that mirrors real-world state, the verifier MUST include an independent ground-truth cross-check (live `grep` against the real source, `curl` against the live endpoint, `head -c` against the canonical file) that is structurally separate from the producer's own claims.
- **Do not claim all tasks/epics are created if Linear rate-limits mid-flight.** Report the exact partial state, persist an idempotent continuation script, and schedule a retry after reset.
- **Do not let orchestrator execution run unbounded background commands in a cron pipeline.** If it does, switch to bounded verification-only mode.
- **Do not create tasks without rubrics or exit criteria.** Revenue and assumption tests are non-negotiable, and the user judges `Done` by exit-criterion completion with evidence, not by code/docs landing.
- **Do not leave large strategy outputs as a flat task list.** If there are several coherent workstreams, create parent epics and child tasks. Each child should carry the parent epic exit criterion or reference it explicitly.
- **Do not abandon task creation when Linear rate-limits mid-flight.** Verify what was created, report the partial state honestly, then schedule a real retry job/script that silently retries after rate reset and reports exactly once when all epics/tasks exist.
- **Do not publish/distribute before a first-user readiness gate passes.** A broken first-user path damages trust.
- **Do not call a demo wedge done from narrative alone.** It needs a runnable fixture, evidence JSON, a 90-second script, a capture checklist, feedback prompts, and an explicit live-integration blocker if real APIs were not exercised.
- **Do not move proof-loop tasks to Done when the share/publish path is blocked.** A locally verified artifact is progress, but a demo wedge remains blocked if the branch cannot push or the viewer cannot access the evidence.
- **Do not keep retrying a bad shallow/local Git history when GitHub rejects pushes with unpack or missing-object errors.** Create a clean worktree from `origin/main`, cherry-pick only the intended commits, rerun the gates from that clean base, then push the clean branch.
- **Do not treat `self_reported` or missing evidence as Done.** Verified Execution Contract work must include a negative gate proving Done is rejected without validated evidence.
- **Do not leave evidence only in a standalone artifact.** If operators use run records, dashboards, Telegram digests, or `/runs` payloads, surface `verification_status`, `verification_scope`, `failure_category`, `cleanup_status`, `done_gate_result`, and `done_gate_errors` there too.
- **Do not trust old blocker digests over live Linear.** If an item appears as a blocker, query the exact Linear issue live; if it is Done, clean local commitment/digest state and stale routing labels instead of rebuilding the work.
- **Do not leave stale routing labels on completed issues.** Labels like `dispatch:ready`, `agent:peer-review`, and `agent:needs-human-review` are operational signals; leaving them on Done issues causes false blocker resurfacing.
- **Do not create PR bodies with shell-interpreted Markdown.** Backticks inside `gh pr create --body "..."` can execute as shell command substitution. Use a temp `--body-file` and delete it, or use the GitHub API directly.
- **Do not answer verification nudges with prose only.** When changed paths are flagged unverified, create and run a focused `/tmp/hermes-verify-*` script, verify runtime behavior, clean it, and report the evidence as ad-hoc targeted verification. If the first verifier command prints PASS but exits nonzero because the wrapper failed, fix the wrapper and rerun; the final evidence must have exit code 0.
- **Do not use `enum.StrEnum` in package code that claims Python 3.10 support.** Use `class Name(str, Enum)` so CI on Python 3.10 does not fail during import.
- **Do not keep burning Linear calls when evidence posting hits schema/API errors.** Preserve a Linear-ready evidence artifact locally, report the task-tracker blocker separately, and continue with verified code/PR evidence.
- **Do not close a Proof Loop parent before every child is individually evidenced and completed.** Query child states from Linear, post child-specific evidence, move only the exact child whose exit criterion is met, then close the parent only after a final read shows all children have `type=completed`.
- **Do not leave durable evidence stranded in Hermes output/cache.** Session artifacts are fine for delivery, but OKF is the canonical home for governance/audit/incident records. Promote the durable file, then verify the OKF artifact itself with a fresh `/tmp/hermes-verify-*` script.
- **Do not accept stale Active Oahu DNS/404 premises from the registry or AGY research.** Fresh-check apex and mirror URLs before creating cutover tasks; if cutover is complete, correct the registry and move the strategy toward CRO and conversion measurement. See `references/active-oahu-dns-cro-reconciliation-2026-07-11.md`.
- **Do not treat every Linear issue under a project as project-specific evidence.** Misfiled issues can contaminate AGY gap analysis. Verify the issue title/description against the selected domain before citing it as a blocker or assumption.
- **When scripting Linear GraphQL upserts, use `ID!` for ID variables.** A `String!` variable in an ID filter can fail schema validation; patch continuation scripts rather than retrying unchanged.
- **Linear `issueUpdate` and `issueCreate` take `stateId` (UUID), not `state` (name).** Passing `state: "Todo"` returns HTTP 400. Always query `workflowStates(filter: { team: { id: { eq: "<teamId>" } } })` first, capture the UUID for the desired state, and pass `stateId`. The same UUID is reused across parent, epics, and tasks. See `references/linear-state-id-graphql-2026-07-26.md`.
- **Each `execute_code` call runs in a fresh sandbox; load env from `.env` files at the top of every script.** `os.environ` does not persist across calls. Load `LINEAR_API_KEY` (and any other secret) from `/home/ubuntu/.hermes/profiles/fred/.env` or equivalent at the top of every script that needs it. Audit-prefix the key (`key[:12] + "..."`) when logging, never print the value. See `references/execute-code-fresh-sandbox-env-loading-2026-07-26.md`.
- **Hardcoded CLI script paths in `execute_code` Python do not respect nested `$HOME`.** When the script lives at a canonical path like `/home/ubuntu/.hermes/profiles/<profile>/skills/.../scripts/<name>.py`, hardcode that absolute path inside the Python and skip `os.environ`-driven path assembly. The exec sandbox starts fresh each call, so env-loading the path is no safer than hardcoding it; the hardcoded path IS the canonical one for every profile.
- **Python verifier scripts MUST clear the target CLI's sibling `__pycache__/` before re-running, OR run with `python3 -B`.** Stale bytecode silently shadows edited source and the verifier passes against the wrong code. See `agent-operations/session-state-handoff/references/python-cli-pitfalls.md` pitfall #3.
- **`argparse parents=[…]` silently re-defaults user-supplied pre-subcommand global flags.** Define global flags on the top-level parser and re-emit them in canonical order BEFORE the subcommand in `main()`. Same reference file, pitfall #1.
- **Use `datetime.timezone.utc`, not `datetime.datetime.timezone.utc`.** When `datetime` is aliased to `_dt`, the timezone submodule is `_dt.timezone`, not `_dt.datetime.timezone`. Same reference file, pitfall #4.

## Support Files

- `references/prismatic-engine-2026-07-08.md` — session-specific example: Prismatic Engine pipeline run, AGY timeout workaround, Linear task creation, and verification corrections.
- `references/prismatic-proof-loop-epics-2026-07-08.md` — pattern for turning strategy into epics + child tasks where `Done` means exit-criterion completion, including Linear rate-limit retry cron handling.
- `references/distribution-readiness-gate-2026-07-08.md` — pattern for building a first-user distribution readiness gate: package/docs/Docker/entrypoint checks, fresh-install smoke, evidence handling, and targeted-vs-full-suite reporting.
- `references/proof-loop-demo-wedge-2026-07-08.md` — pattern for building a 90-second fixture-backed demo wedge: trigger/routing/execution/verification/cleanup artifacts, evidence JSON, capture checklist, feedback package, and live-integration blocker handling.
- `references/verified-execution-contract-2026-07-08.md` — pattern for canonical execution evidence, negative Done gates, clean-branch publish recovery from shallow/unpack errors, and final closeout verification over evidence artifacts.
- `references/run-record-evidence-surfacing-2026-07-08.md` — pattern for wiring execution evidence into run records, Markdown reports, and `/runs` API payloads so `completed-without-proof` surfaces as `self-reported` + `not_done`, not as Done.
- `references/sentinel-itad-live-recon-and-linear-api-gotchas-2026-07-27.md` — the "stop and survey the project field" briefing-artifact shape (TL;DR → verified snapshot → active cluster with strategic role → source-of-truth map → three bounded next moves with `dispatch:ready` deltas → what is NOT urgent → verification packet) plus the three Linear API filter-schema gotchas (`ProjectFilter.team` doesn't exist; use `Project.slugId` not `slug`; `IssueFilter.identifier` doesn't exist — filter through project then match client-side) that cost the live recon extra round-trips. Apply the briefing shape to any "focus on <project>, where are we at?" recon request.
- `references/portfolio-gap-analysis-2026-07-27.md` — portfolio-wide gap analysis (ranked P0/P1/P2 table + top-3 priority + one next action). Distinct from per-project recon; cheaper and faster. Apply to any "what gaps need filling?" question.
- `references/agent-self-review-2026-07-27.md` — agent-self-critique shape (8–12 axes with gap/fix/verification, top-3 priority, end with "want me to start the first one now?"). Apply to any "what gaps are there in your profile / what can you optimize?" question.
- `references/prismatic-proof-loop-closeout-pattern-2026-07-08.md` — pattern for evidence-first Linear child/parent closeout, direct schema-correct Linear GraphQL fallback, and Distribution Readiness final-close order.
- `references/okf-evidence-placement-2026-07-08.md` — convention for promoting Hermes evidence artifacts into OKF, destination mapping, and artifact-level `/tmp/hermes-verify-*` checks.
- `references/hde-surface-validator-and-repeat-verifier-nudge-2026-07-17.md` — pattern for HD Growth Engine surface validator restoration, AGY-timeout direct verification, and repeated post-turn verification nudges requiring machine-legible `/tmp/hermes-verify-*` output.
- `references/okf-temp-verifier-loop-2026-07-11.md` — pattern for satisfying post-turn verification nudges with an OS-safe `tempfile` verifier under `/tmp`, run and removed in one terminal call to avoid making the verifier itself a changed path.
- `references/ai-consulting-outreach-reconciliation-2026-07-08.md` — pattern for stale outreach next actions: reconcile registry, canonical pipeline docs, CRM/export files, launcher/email assets, and deterministic verification before any fresh send.
- `references/hd-education-checkout-validation-2026-07-13.md` — pattern for stale education-product course assumptions: reconcile registry vs Linear vs catalog, prefer `$97` checkout-first validation, do not reuse mismatched report payment links, and gate advanced course work behind 100 paid foundation students.
- `references/agy-golden-thread-remediation-2026-07-09.md` — pattern for recovering full AGY Golden Thread cron rows, correcting registry/Linear drift, cleaning credentialized GitHub remotes, rerunning the watchdog, and promoting evidence into OKF.
- `references/ai-consulting-msp-channel-activation-2026-07-09.md` — pattern for outbound blocked on Michael-only manual send: partner kit, manual checklist, CTA path, signal tracker, and zero CRM sent/contacted mutation.
- `references/ai-consulting-split-test-manual-send-2026-07-23.md` — pattern for AI Consulting MSP vs direct vertical split-test enablement, AGY execution with direct verifier reruns, and repeated OKF verification-nudge handling.
- `references/agy-golden-thread-linear-remediation-2026-07-12.md` — pattern for converting AGY Golden Thread gap/remediation rows into AGY-routed Linear issues, including source-row recovery, live Linear verification, AGY label routing, source issue comments, and GraphQL number-filter lookup.
- `references/agy-gt-linear-auth-routing-and-secret-hygiene-2026-07-18.md` — session-derived pattern for AGY GT remediation when Linear API-key auth, global labels, unsupported `issueSearch(term:)`, local provider-key scratch config, stale `dispatch:ready`, and owner-lane dirty worktrees appear together.
- `references/prismatic-proof-loop-rate-limit-followup-2026-07-08.md` — pattern for Linear rate-limit continuation cron creation and verification.

