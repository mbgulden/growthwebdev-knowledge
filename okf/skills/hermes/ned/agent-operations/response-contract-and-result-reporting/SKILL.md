---
name: response-contract-and-result-reporting
description: Use when answering Michael's simple requests, reporting completed work, or summarizing build/fix/deploy/task outcomes. Encodes the fast-path vs deep-verification response contract, result-link requirements, and golden-thread Next Step behavior.
---

# Response Contract & Result Reporting

## When to use

Use this skill for any interaction where the agent is:

- Answering a simple conceptual, editorial, advisory, or preference question.
- Reporting the result of a completed task, project, deploy, code change, Linear issue, cron/job change, artifact generation, or investigation.
- Deciding whether to use tools immediately or answer first.
- Summarizing verification evidence for Michael.
- Operating in YOLO/autonomous mode and deciding whether to stop or continue.

## Core contract

Michael wants the best of both modes:

1. **Fast path for simple asks** — if the request is conceptual, editorial, advisory, or answerable from the current conversation, answer directly without unnecessary tool fan-out.
2. **Deep path for live/build/fix/deploy work** — if the request depends on live state, files, APIs, infrastructure, git, Linear, deployment, or generated artifacts, use tools and verify before claiming success.
3. **Result-first reporting** — do not bury the outcome in procedural narration. Lead with the actual result and the link/artifact Michael can open.
4. **Golden-thread next step** — every completed task/project/report needs a concise `Next Step` section that aligns with the task/project/goal vision.
5. **YOLO continuation** — when YOLO mode is active, do not stop complacently after one increment; keep executing along the next-step path until blocked, unsafe, complete by the larger goal, or requiring approval.

## Decision rule: fast path vs deep path

### Fast path: answer immediately

Use the fast path when the user asks for:

- Explanation: “What does this mean?”
- Rewriting, naming, copy, messaging, summarization of pasted content.
- Strategic/advisory guidance that does not require current external state.
- Preference or process questions.
- Lightweight prioritization or recommendation based on already-visible context.

Fast-path answer requirements:

- Keep it concise.
- Do not run tools unless live state is genuinely needed.
- If useful, add: “I did not inspect live state.”
- Give the answer first, not the reasoning trail.

### Deep path: inspect, act, verify

Use tools when the user asks to:

- Build, fix, deploy, test, verify, audit, check current status, inspect files, mutate Linear/GitHub/Cloudflare/cron/config, or diagnose infrastructure.
- Answer a question whose truth depends on current files, system state, API state, git history, logs, or external services.
- Confirm whether a just-referenced prior result is actually done, especially when the message is a reply/quote from an earlier agent output. Use the visible quote, session history search, and live checks before saying there is no active task/context.

Deep-path requirements:

- Gather prerequisite context before acting.
- Parallelize independent reads/checks where possible.
- Verify the actual result before reporting success.
- If blocked, say blocked plainly and include the exact blocker plus the next action.

### Lane override on a parked decision

When the agent has parked a sensitive item behind a "Michael decides" gate (per the multi-source-reconciliation-packet decision table) and Michael replies with a lane-override phrase such as:

- "pull it into your lane"
- "figure it out yourself"
- "you should know what to do with it"
- "decide and tell me what you did"

the override is scoped: inspect the item with **metadata only**, do not copy, do not display contents, do not stage, do not push. If the item is a file, use `os.listdir` + `os.lstat` (no `open().read()`) plus a SHA-256 hash to bind a tamper-evident receipt, then act per the override. The full pattern, the empty-file sentinel, and the defensive `.gitignore` comment live under `multi-source-reconciliation-packet/references/2026-07-stat-only-sensitive-file-resolution.md`.

After acting, update both packet documents (full + Telegram-safe) to replace the decision-row heading with "RESOLVED YYYY-MM-DD", post a structured comment to the parent Linear issue, run a fresh `/tmp/hermes-verify-*-resolution.py` ad-hoc verifier, delete the verifier, and report the resolution in the response. Do not exceed the override — if the metadata reveals the file is non-empty or carries private context, stop and report back.

## Final report format

For completed work, use this shape unless the user requested a different format:

```md
✅ Done: <plain-English outcome>

**Open it:** [Result/artifact link](https://...)  <!-- omit only if no artifact exists -->

**Changed**
- <short bullet>
- <short bullet>

**Verified**
- <real command/API/check result>
- <deployment/status/test evidence>

**Next Step**
- <one concise action aligned with the task/project/goal golden thread>
```

For partial or blocked work:

```md
🟡 Partial / 🔴 Blocked: <plain-English state>

**Impact**
- <what this means>

**Evidence**
- `<command/check>` returned `<specific result>`

**Needed**
- <specific approval/input/fix required>

**Next Step**
- <the next golden-thread action once unblocked, or the safe action already taken>
```

## Link and artifact requirements

If the work produces, modifies, or references something Michael can inspect, include a clickable link or deliverable in the final answer.

| Artifact type | Required final surface |
|---|---|
| Linear issue | Markdown link to the issue/dashboard URL |
| GitHub PR | PR URL |
| Deployment/live app | Live URL and/or deployment URL |
| Cloudflare Pages deploy | Deployment URL/status link |
| Workspace file | Workspace-tree markdown link when applicable |
| Generated file/media | `MEDIA:/absolute/path` or direct artifact link |
| Cron/job | Job name, job ID, and delivery target |
| Screenshot/report | Attached media or artifact link |

When exporting Markdown for Telegram sharing, prefer an ASCII-safe `.md` variant if the content includes smart quotes, arrows, emoji status labels, or if Michael shows any mojibake in pasted output. Verify the artifact has no non-ASCII characters or mojibake markers before delivering it. See `references/2026-07-telegram-markdown-mojibake-safe-export.md`.

Avoid final answers that only say “updated config,” “ran deployment,” or “fixed it” without exposing the thing Michael should open.

## Verification clarity

Verification should be concrete and scoped:

- Name whether verification was **focused/ad-hoc** or the **full canonical suite**.
- Include exact commands/checks when useful, but do not dump noisy logs.
- Separate remaining caveats from blockers.
- Never imply a full verification suite passed when only a focused check ran.
- Never imply a workflow/pre-flight gate is healthy just because a lower-layer smoke test passed. For AGY/Antigravity, separate raw CLI auth/model connectivity, signed/programmatic wrapper execution, dispatcher launch state, queue/preflight fields, blocked packets, and downstream writeback gates. If George or another monitor reports a gate blocked, inspect that gate before contradicting it. See `references/2026-07-agy-auth-vs-preflight-layering.md`.
- If the user says the verification did not check the thing that broke, treat that as a first-class workflow failure: acknowledge the exact missed behavior, add/strengthen the test so that behavior would fail next time, rerun the relevant canonical command, and report the new assertion scope instead of defending the previous green result.
- If Hermes reports that edited code lacks detected canonical verification, create a temporary verifier under `/tmp` using an OS-safe `tempfile` path with filename prefix `hermes-verify-`, run it against the changed behavior, clean it up when possible, and explicitly report it as **ad-hoc verification**, not suite green. See `references/2026-07-hermes-ad-hoc-verification-contract.md`.
- If the implementation worktree was removed or the canonical checkout is dirty/locked, the verifier should create its own temporary checkout/worktree from the current target ref (usually `origin/main`) and test the merged behavior there. Set test-required environment values inside the verifier before imports (for example API auth/state vars) so the probe matches the repository's own test assumptions. See `references/2026-07-ad-hoc-verification-after-worktree-removal.md`.
- If Hermes repeats an unverified-code warning for stale/removed paths, do not argue with the warning. Rerun a fresh `/tmp/hermes-verify-*` ad-hoc verifier against current target ref, remove the verifier script, and summarize the result as ad-hoc verification. When the task is about safety tooling, include a direct behavior proof, not only the repository's focused tests.
- If the warning names a specific canonical verification command, run that exact command from the relevant workspace before summarizing. Example: if it says `npm run build`, run `npm run build`, read/repair failures, and report the build/postbuild result separately from any ad-hoc probes. Also confirm temporary verifier/updater scripts are removed when they are listed as changed paths. If the warning lists changed Python files in both a runtime checkout and a temporary promotion worktree, run the canonical command in the runtime checkout and also `py_compile` the named Python files in both paths so the import/syntax fix is actually covered.
- If a repeated verification nudge lists a stale `/tmp/hermes-verify-*` path as a changed path, the fresh verifier should explicitly assert that stale temp file is absent, then remove it again after the run. Report that cleanup as part of the ad-hoc verification evidence; do not let an old temp script keep re-triggering the warning.
- **Verification-only system nudges on documentation-only edits:** when the listed changed paths are pure Markdown / docs / packet artefacts (no source, no JS, no JSON config), the canonical build command is not actually verifying the changed path. Run the canonical build once (it confirms the repo still compiles) and then write a focused `/tmp/hermes-verify-*` artifact verifier that asserts (a) the new Markdown markers/sections, (b) ASCII safety if the file is meant for Telegram delivery, and (c) no credential-shaped strings appear. Run it, delete it, report `PASS` with the verifier output. State explicitly that the verifier confirms the artefact is intact and sane — not that the documentation is correct in a business sense. Example: a HDE reconciliation packet Markdown patch triggered a `npm run build` nudge; running only `npm run build` would have passed for unrelated reasons while silently obscuring that the patch wasn't actually verified. The honest answer was a focused artifact verifier. See `references/2026-07-doc-only-edit-verification-nudge.md`.
- Treat verification-only system nudges as exactly that: do not resume implementation, add unrelated changes, or broaden scope. Run the requested verification with tools in the current turn, repair only if it fails, and then stop. Do not answer by repeating the previous verification summary from memory; a repeated unverified warning means the platform did not detect fresh evidence, so create/run a new `/tmp/hermes-verify-*` script that itself runs the named canonical command (for example `npm run build`) and also asserts the changed artifacts/RESULT markers, then delete the verifier and report the fresh run. Prefer a direct `terminal()` invocation for the verifier wrapper when the platform is trying to detect fresh evidence; an `execute_code()` wrapper that internally calls terminal may produce real evidence but still fail the platform's canonical-command detector. If the named command fails only because a fresh worktree has no dependencies (for example `astro: not found` before `npm ci`), install with the repository's canonical lockfile command (`npm ci`) and rerun the exact verification command before reporting. **After the verifier evidence, include one short plain-English recap of what actually changed and whether it happened** so Michael is not left with only tool mechanics. Do not continue an older goal from compacted context after a verification-only nudge; wait for the next user instruction. See `references/2026-07-verification-nudge-scope-control.md`, `references/2026-07-repeated-verification-nudge-canonical-wrapper.md`, and `references/2026-07-repeat-npm-build-verification-nudge.md`.
- If the implementation is locally verified but intentionally blocked by a lane guard or safe-push rejection, verification nudges still require fresh canonical evidence in the edited worktree; they do **not** authorize bypassing the guard or marking the issue green. If dependencies are missing in a temp worktree, restore them with the repo's normal install (`npm ci` when a lockfile exists), rerun the named command, update the RESULT file if it is one of the changed paths, then run a fresh `/tmp/hermes-verify-*` artifact verifier and report `verified locally; still lane-blocked`. See `references/2026-07-lane-blocked-wip-verification-nudge.md`.
- **Python `src/` package verification in a temporary worktree:** run both installation and pytest from the target worktree, not from the supervisor's default cwd. Use `cd <worktree> && <venv>/bin/python -m pip install '.[dev]' && <venv>/bin/python -m pytest -q`. A collection-time `ModuleNotFoundError` after a successful `pip install` can simply mean pip packaged the wrong repository because the install command ran from the wrong cwd. Recreate the venv or reinstall from the actual target worktree, rerun pytest, and report the passing test count; do not characterize the resolved collection error as a code failure.
- **Repeated pytest verification nudge for a `src/` package:** if the platform continues to surface an earlier bare-system-Python collection failure after a successful venv run, create a fresh venv, activate it, install `.[dev]` from the target checkout, then invoke the literal `pytest -q` command directly in that activated shell. This produces fresh canonical pytest evidence while preserving the honest diagnosis: the initial failure was an uninstalled-package environment boundary, not a source defect. Remove the temporary venv after the successful run.
- **Fresh-clone isolation proof for `src/` packages:** do not make `PYTHONPATH` point at `src/` merely to collect tests; that defeats the import-boundary claim. First record the clean `env -u PYTHONPATH python3` import-spec result, then create a disposable venv inside the clone, install `.[dev]` from that clone, and run `<venv>/bin/python -m pytest -q`. Remove the venv before the final clean-status check (or ensure it is ignored). This separates an expected uninstalled-package collection failure from a real standalone-package failure while keeping the clean-room evidence honest.
- **Post-finalization verification nudges on standalone `src/` projects:** a bare system-Python `python3 -m pytest` may fail collection only because the project is not installed. Do not edit source to mask that bootstrap failure. Create an isolated `/tmp` venv, install `.[dev]` from the target checkout, then rerun the exact pytest command through that venv. When the changed paths include Markdown evidence or a `RESULT.md`, pair the green suite with a fresh temporary `/tmp/hermes-verify-*` artifact verifier that asserts required result markers and scans the report text for credential-shaped strings; remove the verifier and confirm a clean branch before reporting. This is focused/ad-hoc verification unless it is the repository's documented canonical suite.
- When Michael replies to a prior completion report asking whether the job is done or whether more tool calls are needed, treat the quoted/replied-to report as active context, not as an empty fresh session. If the answer depends on live state, inspect the source repo/site/API immediately and give a yes/no with evidence. Do not make him restate the task.
- For verification-only nudges on generated reports or evidence artifacts, the fresh `/tmp/hermes-verify-*` script should validate the artifact itself: parse JSON, check required fields and status semantics, check the Markdown for the same recommendation/evidence, and scan the artifact text for token/API-key/DB-URL shaped secrets. Report this as artifact-level ad-hoc verification, not application suite green.
- **Cron extraction/report variant:** when Hermes keeps flagging edited code after finalization because it did not detect a canonical command, rerun the same focused canonical pytest/build command directly from the edited worktree and create a fresh `/tmp/hermes-verify-*` script that also asserts the supporting evidence artifacts are present and current (for example `/tmp/issue-batches/<ISSUE>_RESULT.md`, updated docs/examples, and the rewritten import paths in the edited tests). Report the rerun as **ad-hoc verification of the changed behavior**, include verifier cleanup status, and do not broaden scope beyond the named changed paths unless the rerun fails. See `references/2026-07-cron-repeated-ad-hoc-verification-with-result-artifact.md`.
- **Repeated cron verification nudge:** each new `unverified` prompt requires a newly observable verification event, even if the prior turn already ran the suite successfully. Create a disposable venv, install the target project's documented dev extras from the target worktree, invoke the literal requested command (for example `pytest -q`) directly in that shell, then run a newly named `/tmp/hermes-verify-*` artifact assertion. Remove both temporary artifacts and report only the fresh pass count, artifact assertion result, and cleanup status. Do not resume implementation or restate stale verification as fresh evidence.
- **Installed-wheel proof path pitfall:** a virtual environment may live beneath the fresh-clone directory. When proving a non-editable wheel import, do not assert that `module.__file__` contains no clone-directory substring; the valid installed path can be `<clone>/.venv/.../site-packages/...`. Instead assert that the resolved import path is under that venv's `site-packages` and not the repository's `src/` tree, then separately verify package resources with `importlib.resources`. This avoids a false source-leakage failure while preserving the actual standalone-install contract.

Good:

```md
**Verified**
- Focused check: `npm run build` passed.
- Live URL returned HTTP 200.
- I did not run the full e2e suite.
```

Bad:

```md
Everything should be good now.
```

## Golden-thread Next Step behavior

Every completed task/project/report should include a `Next Step` section.

The next step must:

- Align with the specific task/project/goal vision, not generic “monitor” filler.
- Preserve the golden thread: what moves this work closer to the intended outcome?
- Be short and actionable.
- Indicate whether the agent already continued because YOLO mode was active.

Examples:

```md
**Next Step**
- Golden path: publish the verified deployment link into the Linear issue and move only the evidenced child issue to Review.
```

```md
**Next Step**
- Golden path: use the new response contract in fresh profile sessions so simple asks stay fast while deploy/fix work remains verified.
```

## YOLO mode

When Michael indicates YOLO/autonomous execution is active:

- Continue executing the golden-thread next step instead of stopping after the first completed increment.
- Keep going until one of these boundaries appears:
  - destructive/irreversible action,
  - credentials or explicit approval needed,
  - task exits the current agent lane,
  - live risk is high,
  - no safe next action remains,
  - the larger goal is actually complete and verified.
- Still report the final state with `Next Step`; if YOLO stopped at a boundary, name the boundary.

## Pitfalls

- Do not over-verify simple advice/editorial requests.
- Do not under-report real operational work; Michael should not need to ask “where is the result?”
- Do not substitute process jargon for the actual result link/artifact.
- Do not claim “done” without clear verification scope.
- Do not use the `Next Step` section as generic boilerplate; tie it to the specific golden path.
- If a PR merge or automation auto-moves a Linear issue to Done but acceptance criteria remain blocked, report it as **Partial**, move/comment the issue back to the correct state when you have permission, and name the external blocker. A merged safety wrapper/dry-run is not the same as completed operational cleanup.

## References

- `references/2026-07-response-contract-and-golden-next-step.md` — session-specific source notes from Michael's correction that prompted this skill.
- `references/2026-07-verification-human-outcome-recap.md` — how to answer verification-only platform nudges with both fresh verifier evidence and a plain-English statement of what actually changed/happened.
- `references/2026-07-cron-post-final-verification-nudge.md` — cron/post-finalization variant: when Hermes flags stale verification after a task was already finalized, rerun the exact named command, add a fresh `/tmp/hermes-verify-*` acceptance/artifact verifier, confirm clean git/result artifact, and do not broaden scope unless verification fails.
- `references/2026-07-gro4001-cron-verification-nudge.md` — concrete HD Platform OG/social-image verification nudge example: rerun `npm run build`, assert generated OG/Twitter tags with a fresh temporary verifier, remove the verifier, report the external PR-check caveat, and stop without broadening scope.
- `references/2026-07-gro4008-production-smoke-verification-nudge.md` — production checkout/report smoke example: after finalization, rerun `npm run build`, run the focused smoke verifier, add a `/tmp/hermes-verify-*` artifact verifier for RESULT/source safety markers, and preserve `verified implementation; not green` semantics when live report delivery still returns HTML fallback.
- `references/2026-07-agy-auth-vs-preflight-layering.md` — AGY/Antigravity readiness layering: raw `AUTH_OK` and signed wrapper success prove CLI auth, not Prismatic pre-flight health; inspect dispatcher/queue/blocked-packet/writeback gates before reporting green.
- `references/2026-07-doc-only-edit-verification-nudge.md` — verification-nudge handling for documentation-only edits: when the listed changed paths are pure Markdown / docs / packet artefacts, run the canonical build once for context but rely on a focused `/tmp/hermes-verify-*` artifact verifier that asserts Markdown markers, ASCII safety, and no credential-shaped strings; delete the verifier; state the verification scope clearly.
