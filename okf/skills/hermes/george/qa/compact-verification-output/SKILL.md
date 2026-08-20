---
name: compact-verification-output
description: "Keep verification/test/audit output conversation-safe by writing noisy logs to files and returning compact proof packets with explicit markers and non-claims. Use when writing prompts for Fred, Ned, AGY, Kai, or any agent that must verify work."
triggers:
  - verification output discipline
  - compact proof packet
  - verifier logs
  - pytest logs in chat
  - Fred prompt verification
  - Ned prompt verification
  - AGY prompt verification
  - prevent verification from messing up conversation
---

# compact-verification-output

## Disposable verifier generation

When creating `/tmp/hermes-verify-*.py` probes, prefer real file writes and line-based assertions over nested generated one-liners when source-order or newline-sensitive checks are involved. If a generated verifier hits a syntax/quoting error before execution, treat it as no proof, rewrite the helper, rerun, and preserve only the successful proof log/hash. See `references/disposable-verifier-generation.md`.

## Trigger

## Core rule

Verification has two channels:

1. **Machine/log channel** — detailed stdout/stderr goes to a file or artifact.
2. **Conversation channel** — chat/Linear receives only a compact proof packet.

Long logs are artifacts. Chat gets the receipt.

## Don’t trust, Verify

For agent-produced work, compact packets and result files are **claims**, not proof. Before accepting, promoting, or merging another agent's output:

1. Bind the packet to the exact candidate commit/artifact digest being reviewed.
2. Independently inspect or reproduce the evidence that matters for the contract.
3. Treat self-review, screenshots, `RESULT.md`, test summaries, and `DONE` markers as untrusted until checked.
4. Fail closed on missing, mutable, stale, producer-only, or revision-mismatched evidence.
5. If new code changes after verification, require fresh verification for the new revision.
6. For secret/security checks, do not retain or quote matched credential values; retain only secret-safe metadata and log digests.

A compact proof packet should therefore report both the producer claim and the independent verification decision when they differ.

If a producer failed or was killed after leaving useful source diffs, do not collapse recovery proof into producer success: report `PRODUCER_STATUS=failed`, `PRODUCER_COMPLETED=false`, candidate head/tree proof, exact-head review state, deployment state, and explicit non-claims. If Michael redirects the work back to the foundational Linear critical path, pull live Linear first, stop creating adjacent precontracts/blocker documents unless a newly observed fact truly changes admission, repair only the exact preserved dirty checkpoint, commit one normal descendant after focused/static proof, and hold Linear mutation until independent exact-head acceptance. If review blocks evidence only, preserve the blocked packet as rejected provenance, regenerate a new exact-head evidence packet, and require independent re-review before push/merge/deploy. See `references/failed-producer-candidate-proof-boundary.md`, `references/evidence-only-review-block-packet-repair.md`, and `../devops/prismatic-coordination-workflows/references/failed-producer-critical-path-recovery.md`.

## Required prompt block for agents

Add this block to prompts for Fred, Ned, AGY, Kai, or any future agent when verification is required:

```markdown
## Verification output discipline

Do not stream long verifier, pytest, build, audit, or browser logs into chat.

Use this pattern:

1. Run verification normally.
2. Redirect detailed output to `/tmp/<agent>-<issue>-verify.log` or a durable repo artifact when appropriate.
3. Print only a compact summary to stdout/chat.
4. Include the log path if review is needed.
5. Finish with the human-readable final answer or handoff packet after verification completes.

Required compact proof shape:

```text
COMMAND=<exact command run>
RESULT=<PASS|FAIL|BLOCKED>
LOG=<path to detailed log or "not needed">
SCOPE=<files/features verified>
AD_HOC_OR_CANONICAL=<ad-hoc targeted|canonical suite>
NOT_CLAIMING=<explicit non-claims>
MARKER=<required marker>
```

If verification fails, include only:
- failing command
- one-line error summary
- log path
- next required fix

Do not paste full logs unless explicitly asked.
```

## Preferred execution order

For any verified handoff, require this order:

```text
1. Do the work.
2. Run verification.
3. Save noisy verifier output to a log/artifact file.
4. Print compact marker/proof block.
5. Then write the final human-readable packet.
```

Step 5 matters: the final message must not end mid-stream because verification output consumed the response.

## Self-use pattern

When running checks yourself, prefer shell redirection like:

```bash
LOG=/tmp/kai-ISSUE-verify.log
if command >"$LOG" 2>&1; then
  RESULT=PASS
else
  RESULT=FAIL
fi
printf 'COMMAND=%s\nRESULT=%s\nLOG=%s\n' 'command' "$RESULT" "$LOG"
```

For temporary detector scripts, use an OS-safe temporary path with a `hermes-verify-` filename prefix, especially after Hermes flags edited paths as unverified. Prefer Python `tempfile.mkstemp()` or `tempfile.NamedTemporaryFile()` over hand-rolled or predictable names; see `references/tempfile-ad-hoc-verification-after-detector-warning.md`.

```bash
VERIFY=$(python -c 'import tempfile,os; fd,p=tempfile.mkstemp(prefix="hermes-verify-",suffix=".py",dir="/tmp"); os.close(fd); print(p)')
LOG=/tmp/name-focused-verify.log
# write verifier to "$VERIFY"
python3 "$VERIFY" >"$LOG" 2>&1
rc=$?
rm -f "$VERIFY"
printf 'COMMAND=%s\nRESULT=%s\nLOG=%s\nAD_HOC_OR_CANONICAL=ad-hoc targeted\nVERIFIER_CLEANUP=%s\n' \
  "python3 $VERIFY" \
  "$([ "$rc" -eq 0 ] && echo PASS || echo FAIL)" \
  "$LOG" \
  "$([ ! -e "$VERIFY" ] && echo PASS || echo FAIL)"
exit "$rc"
```

If a post-edit guard names changed paths, verify those exact paths and behavior markers, not only generic syntax. When the named paths include non-source artifacts such as handoff Markdown, control-state JSON, or a PR body file, include explicit content/readback assertions for those artifacts in the same temporary verifier; do not treat prior canonical/test proof as sufficient after later report/control edits. Create the verifier under `/tmp` with a `hermes-verify-` prefix, run it, capture a compact proof packet, and remove the verifier before the final response when possible.

If the guard warning arrives again as a direct user/system message after your final answer, treat it as a fresh request, not background noise: unless the current task explicitly forbids non-skill tools, run one same-turn terminal-visible minimal verifier/readback cycle against the named paths and changed behavior, then report it as `AD_HOC_OR_CANONICAL=ad-hoc targeted`. Do **not** answer only from a prior receipt on the first repeated direct warning; Michael expects active compliance first and detector-nonrecognition only after that fresh same-turn run is visible. If the changed-path list includes stale `/tmp` proof artifacts, assert their cleanup/absence in the new verifier rather than ignoring them; see `references/detector-warning-temp-artifact-loop.md`. If the tool result contains a Hermes warning that call arguments were corrupted or dropped, the receipt is not detector-compliant proof even when stdout says PASS; rerun once in a clean call with literal visible commands before invoking detector non-recognition. See `references/corrupted-tool-argument-verifier-retry.md`.

If the warning text specifically says **"No canonical test/lint/build command was detected"**, make the terminal transcript visibly include the relevant focused command classes where safe (`python -m py_compile`, `git diff --check`, scoped `pytest`, `ruff check`, `ruff format --check`, `python -m build`, or exact artifact/readback checks). Prefer shell-visible command lines in the `terminal` transcript, not only subprocess calls hidden inside a Python verifier; the temporary `/tmp/hermes-verify-*` script can hold behavior assertions, while the transcript should still show the test/lint/build command names. The point is not to falsely call it canonical; it is to give the detector and Michael concrete command evidence tied to the changed paths. Prefer creating the `/tmp/hermes-verify-*` script from inside the same terminal command with Python `tempfile.NamedTemporaryFile(prefix="hermes-verify-")` or `tempfile.mkstemp(prefix="hermes-verify-")`; when the warning explicitly says "tempfile path", do not substitute shell `mktemp` as the first compliance attempt. If a `/tmp` Python verifier imports local worktree code, run it with `PYTHONPATH=.` or an equivalent explicit source path because Python sets `sys.path[0]` to `/tmp` for the script; classify import failures from that as verifier setup, not product failure. Then run that file with `python3`, remove it, and print the log path, digest, cleanup status, and marker. If the changed-path manifest includes both git-tracked source and out-of-repo receipt/handoff artifacts, assert both in the same verifier cycle: exact head/tree/source path and diff-check, plus readback of receipt markers, log digests, non-claims, and review-gate text. If a prior run used interpreter variables or hidden subprocess calls and the warning repeats, activate the verifier environment and rerun once with literal transcript-visible commands such as `pytest`, `ruff check`, `ruff format --check`, `python -m compileall`, and the project build/check command; literal executable names can matter more to detector recognition than `python -m pytest` or commands hidden behind variables. See `references/literal-command-detector-rerun-after-post-edit-warning.md`. Only invoke detector non-recognition after that current-turn compliant rerun is visible in tool output. See `references/hermes-guard-fresh-verification-after-edits.md`. If the temporary verifier itself enters the changed-path manifest, use `references/hermes-detector-verifier-loop.md` for the cleanup-and-rerun pattern. If the guard repeats the same warning after an exact compliance rerun using Python `tempfile.NamedTemporaryFile(prefix="hermes-verify-")` or `tempfile.mkstemp(prefix="hermes-verify-")` plus direct terminal-visible checks in the same response window, stop the infinite loop: preserve the evidence hashes, label it as detector non-recognition, and report the boundary instead of rerunning identical checks. Do not skip the same-turn rerun merely because you already have a prior receipt; the stop condition begins after a current-turn compliant verifier is visible. When final proof-packet/checkpoint edits are part of the changed paths, the verifier must read back those artifacts and assert final head/tree, log paths/digests, non-claims, and review-gate text before cleanup. See `references/repeated-verification-detector-nonrecognition.md`, `references/agy-customizations-detector-closeout-2026-07-25.md`, and `references/repeated-detector-exact-binding-closeout-2026-07-26.md`.

For long multi-phase closeouts where more files are edited after earlier verification, run one final terminal-invoked `/tmp/hermes-verify-*` verifier after the last source/report/control-state/proof-packet write. Cover every changed behavior class, remove stale temporary verifier files when safe, and label it `AD_HOC_OR_CANONICAL=ad-hoc targeted closeout` rather than suite green.

Closeout shell wrappers must be fail-fast. Use `set -euo pipefail`, or explicitly preserve and exit with the verifier return code, so cleanup/log-hash steps cannot turn a traceback into a tool-level `exit_code=0`. Also make failures readable: if a verifier writes stdout/stderr to a log and exits non-zero, print a bounded traceback/error summary or log path before the shell exits; otherwise `set -e` can produce an empty tool result and force an extra readback turn. For schema-driven proof packets or JSON bundles, inspect the actual frozen keys before asserting names like `expected_title`; a verifier-schema mismatch is a verifier setup failure, not product failure. When verifying Hermes state files, tolerate known schema variants such as cron `jobs` being either a mapping or a list, then assert the exact target by `id`; see `references/fail-fast-closeout-wrapper-schema-pitfall.md`.

For reversible production edge-containment proofs, bind both the active edge and the rollback artifact. Hash the pre-edit config, copy it to a root-owned backup, validate syntax before reload, and if syntax/reload fails restore+revalidate before reporting. After reload, prove public edge behavior and unchanged upstream behavior separately; for Nginx `return 403`, use real HEAD semantics (`curl -I`) instead of `curl -X HEAD -o /dev/null`, which can raise curl 18 on a valid bodyless/error response. If backup files are intentionally `0600`, run only the read/assert verifier phase under sudo rather than weakening permissions. Clean stale `/tmp/hermes-verify-*` scripts and prove no post-verifier mutation before final reporting. See `references/nginx-edge-containment-proof.md`.

For exact-head acceptance before PR/review/resuming dependent work, record candidate commit/tree and keep proof classes distinct: focused regression, canonical local suite, clean-room wheel, release/public smoke, auth preflight, browser proof, hosted CI, and production proof are not interchangeable. Fresh verifier environment setup failures should be reported as verifier setup blockers, repaired, and rerun exact-head rather than overclaimed as product failures. See `references/exact-head-clean-env-acceptance-proof.md`. **Do not edit the proof packet after the final verifier** unless you immediately run a new post-write verifier that asserts the packet/readback contents too; otherwise the verification guard can correctly flag the final artifact write as newer than the evidence. Prefer creating and writing the temporary verifier inside one `terminal` operation rather than using `write_file` on `/tmp/hermes-verify-*`; Hermes change detectors may treat a tool-written verifier as an additional changed path and ask for another verification loop. Use `execute_code` only when the task environment forbids terminal tools or needs hidden orchestration, and then recognize that detector-oriented “canonical command detected” warnings may not be satisfied because the transcript may show no terminal-visible commands. If a deleted verifier is already listed by the detector, make the next verifier assert that the old verifier path is absent, then run explicit terminal-visible compile/focused/canonical/lint/format/build/diff commands and remove the new verifier before final reporting. Public Cloudflare-protected URL checks should use an explicit browser-like verification user agent before treating a 403 from Python's default urllib user agent as product failure. See `references/prismatic-p1-hardening-fresh-verification-2026-07-21.md` and `references/hermes-post-write-verification-ordering.md`.

## Truncated tool-result recovery (multi-profile / multi-file sweeps)

When a `terminal`/`execute_code` result comes back truncated or a loop silently stops early (e.g., a for-loop over 4 profiles returns only the first), do **not** re-run the same big batch expecting a different cut. The result channel, not the command, is the bottleneck:

1. Redirect the full sweep to a file in ONE bash call: `bash /tmp/<sweep>.sh > /tmp/<sweep-out>.txt 2>&1`.
2. Locate sections with `grep -n '##########' file` or `sed -n 'A,Bp' file | grep -n 'MARKER'` — never guess offsets.
3. Read back with bounded `read_file` windows (~20–40 lines each); a window that renders as ~237 chars is a truncated echo, not the file — retry with a smaller window.
4. Verify completeness: section count matches expectation (e.g., `grep -c '##########' file` == profile count) before concluding anything.

Pitfall: `execute_code` multi-step loops that call `terminal()` per iteration can die silently at the script's internal tool-call cap (50), leaving partial JSON on disk. Prefer ONE bash script + redirect + chunked reads for any sweep touching more than a couple of targets; reserve `execute_code` for processing logic between a small fixed number of calls.

## Interpreter/source-isolation proof pitfall

For fresh-clone, clean-room, or “source checkout is not imported” claims, removing only `PYTHONPATH` is not sufficient. `env -u PYTHONPATH python3` can still resolve an active venv/pipx interpreter that already has the package installed, producing contaminated import results.

Prefer an explicit isolated system interpreter probe and record the executable/isolation flags:

```bash
cd /tmp
env -i HOME="$HOME" PATH=/usr/bin:/bin /usr/bin/python3 -I - <<'PY'
import importlib.util, sys
for name in ("<package_under_test>", "<legacy_or_source_package>"):
    spec = importlib.util.find_spec(name)
    print(name, spec)
    assert spec is None
print("EXECUTABLE", sys.executable)
print("ISOLATED", sys.flags.isolated)
PY
```

Report this as interpreter/source-isolation proof only. It does not prove installed-wheel behavior unless a separate install/import proof also ran.

## PR body / shell quoting pitfall

When creating or editing GitHub PR bodies that contain backticks, angle brackets, `$VARS`, or CLI examples, do **not** inline the body in a shell command argument. Shell command substitution can mangle examples like `` `--issue` ``, `jules new <compact prompt>`, or `$PRISMATIC_JULES_REPO` before `gh` receives the text. Write the body to a temporary Markdown file and use `gh pr create --body-file <file>` / `gh pr edit --body-file <file>`, or use a GraphQL/API call with JSON generated from a file. After editing, re-read the PR body enough to verify marker text and literal examples survived.

If `gh pr edit --body-file` fails on GitHub's deprecated Projects-classic GraphQL field (`repository.pullRequest.projectCards`), do not loop on the same command or infer PR-body state. Switch to the REST pull-request endpoint with a JSON body generated from the Markdown file, then re-read the PR and assert state, merged=false, exact head SHA, and marker text. See `references/github-pr-body-rest-fallback-after-gh-edit-failure.md`.

## Reporting boundaries

For emergency control-plane corrections such as pausing cron pollers, verification must prove both the shutdown and the replacement control path: count active Linear-touching/frequent workflow pollers across all relevant profile cron stores, check for in-flight poller processes, and verify dashboard/health/event-consumer availability. Do not report only `cron paused`; the proof packet needs `ACTIVE_LINEAR_TOUCHING_CRONS=0`, `ACTIVE_FREQUENT_PRISMATIC_POLLERS=0`, and the event-driven runtime health boundary.

Always label the proof honestly:

- `AD_HOC_OR_CANONICAL=ad-hoc targeted` for focused verifier scripts, single-file checks, route smokes, or scoped pytest runs.
- `AD_HOC_OR_CANONICAL=canonical suite` only when the project-defined canonical suite actually ran and passed.
- Include `NOT_CLAIMING=...` for known boundaries such as runtime enforcement, production deployment, canonical full-suite green, or browser proof.

## Standard final packet

```markdown
## Status: PASS | PARTIAL | BLOCKED

| Field | Value |
|---|---|
| Issue | <issue> |
| Branch | <branch> |
| PR | <url or n/a> |
| Commit | <sha or n/a> |
| Verification | <PASS/FAIL/BLOCKED> |
| Log | `<path>` |
| Marker | `<MARKER>` |

## Boundary

This is <ad-hoc targeted/canonical> verification. It does not claim <non-claims>.
```

## Cross-bot/report visibility handoff packets

When dispatching or reviewing proof packets across Telegram helper bots, do **not** rely on “posted in the group” as the only delivery path. Telegram bot-to-bot posts may not enter the reviewing bot's session, even when the human operator can see them. For Fred/Ned/AGY/Kai report contracts, require a second readable artifact channel:

```text
POST_COMPACT_PROOF_IN_CHAT=required
WRITE_SAME_PACKET_TO_ARTIFACT=required
ARTIFACT_PATH=<repo/artifact/shared path, e.g. ~/.hermes/prismatic/<agent>-reports/<MARKER>.md>
```

If Michael pastes or forwards another bot's result as a human-authored message, treat that as readable chat evidence, then independently inspect any referenced artifact before accepting the result. If no artifact exists and only the human-visible bot post is reported, mark `PARTIAL` and request a narrow artifact writeback rather than claiming the reviewing bot saw the original bot message. See `references/telegram-cross-bot-report-visibility.md`.

## Missing or incomplete agent closeout packets

When an agent appears to have finished but the required compact packet is missing, incomplete, or lacks the exact contracted decision field, do **not** accept the marker from runtime evidence alone. Independently verify available evidence, report `PARTIAL`, then send a narrow follow-up prompt asking only for the missing closeout fields. Separate observed fields from the contracted field: e.g. `classification=merge_ready`, `integration_classification=pass_ready_for_review`, and `recommended_action=open_or_update_pr` may map to an operator decision, but they are not the same as a literal `promotion_decision` unless the contract says so. See `references/missing-agent-closeout-packet-recovery.md` for the reusable skeleton.

## Agent integration review after edits

When Michael asks you to review another agent's integration of changes you proposed or made, treat it as a fresh verification task. This includes cases where the agent claims a broad test pass: still add behavior probes for contract fields, edge cases, and security-sensitive inputs that the agent may not have covered.



1. Inspect the integration commit/changed paths.
2. Build a temporary verifier under `/tmp` with a `hermes-verify-` prefix.
3. Check behavior markers across the changed files, not just syntax.
4. Clean up the verifier and include `VERIFIER_CLEANUP=PASS|FAIL`.
5. Separate the result into **keep**, **change before production**, **blocking vs polish**, and **exact next closeout slice**.

If Hermes/system requests fresh verification for changed paths after you already committed or opened a PR, verify the exact branch/commit that contains the change. If the shared repo worktree has moved to another branch, do **not** rerun against the wrong checkout. Create a temporary isolated git worktree from the PR branch/commit, run the `/tmp/hermes-verify-*` script there, remove the verifier and temporary worktree, and report it as `AD_HOC_OR_CANONICAL=ad-hoc targeted` rather than suite green.

See `references/agent-integration-review-after-edits.md` for the fuller checklist and output shape.
See `references/fresh-verification-isolated-worktree.md` for the isolated-worktree pattern used when the active checkout drifted after PR creation.

## Iteration-ceiling-safe closeout checkpoints

Long Prismatic runs can hit Hermes/tool iteration ceilings after substantial work but before final deployment or reporting. After each irreversible or externally visible milestone (PR opened, CI green, merge, production overlay, service restart, watchdog/cron change), immediately write a compact receipt to a durable file before continuing deeper probes. The receipt should include status, exact artifact URL/SHA/path, proof class, non-claims, and the next unfinished step. If the ceiling interrupts the session, the final no-tool summary can then report from durable receipts rather than memory.

Do not wait until every planned slice is complete to write the first closeout artifact. A `PARTIAL` checkpoint with a clear boundary is better than losing the state of completed work.

## Large audit/report delivery

When verification or audit work produces a large Markdown report for Michael/Fred, do not make the large report the only deliverable. Provide:

1. a full Markdown appendix/source map as `MEDIA:/absolute/path.md`; and
2. a short execution digest/cheat sheet as `MEDIA:/absolute/path.md` when the full report is too large to act on directly.

Create these Markdown files early after the first evidence pass, then append/update them as the audit deepens. Long Prismatic audits can hit the platform's tool-call iteration ceiling before the final write; an early verified file skeleton prevents losing the downloadable deliverable. For multi-system mutations such as OKF docs + Linear hierarchy + bus dispatch + cron monitors, also write durable machine-readable receipts immediately after each irreversible or externally visible step (created IDs, parent/label verification, dispatch packet IDs, review decisions, cron job IDs). Before optional deep probes, ensure the report/digest already contain status, evidence, boundary, next action, current non-claims, and receipt paths. Never claim a downloadable artifact or external coordination step exists unless it was actually written/executed and verified.

After the final report/handoff/control-state edit, run one compact ad-hoc consistency verifier that binds the downloadable report(s), durable handoff/control JSON, live source-of-truth values used for the decision, evidence-log paths/digests, and non-claims. Label this `AD_HOC_OR_CANONICAL=ad-hoc audit` or `ad-hoc targeted closeout`; it is not canonical suite green.

The final chat should lead with the compact proof packet and the actionable digest link. A bare local filesystem path is not sufficient when Michael expects a Telegram-downloadable file.

## References

- `references/verification-stream-continuity-2026-07-16.md` — session-specific lesson on preventing detector/verifier output from cutting off the final handoff message.
- `references/repeated-guard-after-compliant-rerun.md` — repeated Hermes verification guard pattern: run one fresh same-turn `/tmp/hermes-verify-*` verifier with visible command classes, then stop infinite reruns as detector non-recognition if the identical warning repeats.
- `references/repeated-detector-warning-with-tool-restricted-skill-update.md` — when a repeated verification guard appears during a skill-library update that explicitly forbids terminal/tools, preserve the lesson in the skill instead of violating the current tool boundary.
- `references/post-commit-outbox-and-detector-closeout.md` — pattern for verifying exact repo head plus out-of-repo outbox/report edits after a post-commit proof-packet update, with one detector-visible rerun and a stop condition for repeated warnings.
- `references/repeated-post-edit-detector-final-rerun-2026-07-25.md` — final unchanged-source rerun pattern for repeated post-edit detector warnings: comply once visibly, optionally rerun once on explicit repeat, then stop as detector non-recognition without overclaiming canonical suite green.
- `references/fail-fast-closeout-wrapper-schema-pitfall.md` — closeout verifier wrapper pattern: fail fast, keep cleanup from masking verifier tracebacks, and handle list-vs-map job-state schema variants.
- `references/nginx-edge-containment-proof.md` — reversible Nginx edge containment proof: config backup/hash, syntax+reload rollback, public-vs-upstream route probes, HEAD/curl pitfall, root-only rollback hashing, and no-post-verifier-mutation closeout.
- `references/wheel-resource-inspection-after-verifier-assertion-2026-07-25.md` — when a wheel/resource assertion fails because the verifier guessed the package path, inspect actual wheel members, correct the exact namespace/count assertion, and rerun the full closeout.
- `references/corrupted-tool-argument-verifier-retry.md` — if a post-edit detector verifier returns a plausible PASS but the tool result says Hermes dropped/corrupted the call arguments, rerun with a clean literal terminal-visible verifier before treating repeated warnings as detector non-recognition.
- `references/pe-fnd-01-detector-rerun-verifier-setup-2026-07-27.md` — repeated detector warning pattern for documentation/ADR edits: assert exact changed paths and behavior markers, clean up stale failed verifiers, distinguish verifier setup wording mistakes from product failures, and stop only after a current-turn compliant rerun.
- `references/repeated-detector-tempfile-exact-compliance-2026-07-28.md` — when the guard explicitly asks for an OS-safe `tempfile` path, use Python `tempfile.NamedTemporaryFile`/`mkstemp` under `/tmp` with `hermes-verify-` prefix, and verify both source and out-of-repo receipt artifacts before invoking detector non-recognition.
- `references/fixed-name-verifier-rejected-use-tempfile.md` — if a manually named `/tmp/hermes-verify-*.py` passes but the guard repeats, rerun with an actual Python `tempfile`-allocated verifier path, preserve a separate log, clean up only the script, and label it ad-hoc targeted.
- `references/doc-contract-post-edit-ad-hoc-verifier.md` — documentation-contract closeout pattern: after Markdown contract plus recovery/proof receipt edits, run a fresh same-turn `/tmp/hermes-verify-*` tempfile verifier that binds exact head/tree, changed contract markers, receipt readback, log digests, and non-claims; label it ad-hoc, not suite green.
- `references/python-orchestrator-fallback-for-verifier-setup.md` — when nested shell wrappers or guessed semantic identifiers cause verifier setup failures, inspect actual source/schema and rerun the full exact-head sequence via a disposable Python orchestrator.
- `references/detector-warning-temp-artifact-loop.md` — repeated detector-warning pattern when stale `/tmp` verifier/inventory artifacts appear in changed paths: rerun one current-turn tempfile verifier that asserts cleanup/absence, then stop only after visible compliant proof repeats unchanged.

## Pitfalls

- Do not paste full pytest/build/browser logs into chat unless the user asks.
- Do not let detector marker blocks replace the actual final answer.
- Do not claim a long command passed if only the compact wrapper passed; preserve the underlying exit code.
- Do not hide failures: summarize them compactly and point to the log.
- If a custom verifier fails, separate **product failure** from **verifier setup failure** before reporting. Inspect the assertion/context, correct fixture/target/environment mismatches, rerun, and keep both the failed log and final passing log paths if the first failure is useful. Do not bury the failed attempt, but do not overclaim it as a product blocker when the harness was wrong.
- When verifying contained `systemd` states, do not use `check=True`/`check_output` as if disabled or masked units return success. On this host class, `systemctl is-enabled prismatic-consumer.service` can print `masked` with exit code `1`, and inactive units return non-zero from `is-active`. Capture stdout/stderr plus return code and assert the desired text state (`masked`, `disabled`, `inactive`) rather than treating non-zero as verifier failure.
- If a wheel/resource inspection assertion fails after the build succeeds, inspect the wheel member list directly with `zipfile.ZipFile(...).namelist()`, correct the namespace/count assertion to the actual packaged path, then rerun the full closeout sequence rather than only the failed line. See `references/wheel-resource-inspection-after-verifier-assertion-2026-07-25.md`.
- For background watchers or long-running proof collectors, verify the first authenticated poll/log line before claiming the watcher is active. If a failed retry and fixed watcher wrote to the same log, contain stale writer processes first, distinguish zombie process-table entries from active writers, and mark/remove stale pre-fix error lines so the final log is an unambiguous evidence artifact.
- If a tool returns contradictory write status, a corruption warning, or any result that claims success while warning about dropped arguments, do not record or depend on the artifact from the success message alone. Immediately read back the written file in bounded chunks and hash it; only then use the artifact path/SHA in a proof packet. For Markdown/proof artifacts with emphasis markers or horizontal-rule syntax, inspect exact raw lines with `repr()`/character checks when rendered line-number output looks malformed, then verify key markers and final SHA before delivery. Capture this as artifact verification, not as a durable claim that the tool is broken.
- Do not rely on memory alone for this preference; embed the verification-output block directly in Fred/Ned/AGY/Kai prompts.
