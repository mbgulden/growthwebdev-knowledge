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

# Compact Verification Output

Use this skill whenever you write or run verification for another agent or yourself: tests, verifiers, audits, Lighthouse, pytest, build checks, production checks, or detector marker scripts.

## Core rule

Verification has two channels:

1. **Machine/log channel** — detailed stdout/stderr goes to a file or artifact.
2. **Conversation channel** — chat/Linear receives only a compact proof packet.

Long logs are artifacts. Chat gets the receipt.

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

For temporary detector scripts, create the file with an actual `/tmp/hermes-verify-*` path (prefer `tempfile.NamedTemporaryFile(prefix='hermes-verify-', dir='/tmp', delete=False)`), run it, then remove it:

```bash
LOG=/tmp/kai-name-verify.log
VERIFY=$(python3 - <<'PY'
import tempfile, os
f = tempfile.NamedTemporaryFile(prefix='hermes-verify-name-', suffix='.py', dir='/tmp', delete=False, mode='w')
f.write('''#!/usr/bin/env python3\n# verifier body here\n''')
f.close(); os.chmod(f.name, 0o700); print(f.name)
PY
)
python3 "$VERIFY" >"$LOG" 2>&1
code=$?
rm -f "$VERIFY"
echo "cleanup=PASS verifier_removed=$VERIFY"
exit $code
```

When a post-edit detector keeps saying “no canonical command detected,” make the verifier output explicit `VERIFY_COMMAND=<exact command>` lines before each subprocess run, and include the final compact packet after the checks. Do not rely on a prior hand-run test log; rerun the checks inside the temp verifier against the changed paths. If the guard names specific changed files, make those exact paths the verifier scope and include at least one behavior assertion that exercises the changed contract, not only `py_compile`/pytest. If the guard names supporting/transient files such as `/tmp/*.txt` prompt or snippet artifacts, assert those exact files exist and contain the expected markers too; guard-listed `/tmp` files are part of the verification scope even if they are not repo files. If the larger PR also touched dashboard HTML/JS but the guard lists only Python paths, satisfy the guard with the exact listed Python paths and a separate inline dashboard-marker assertion only when needed; do not put `.html` files into `ruff check`. If a first temp verifier has a syntax/quoting bug, invalid fixture, wrong scope, or the platform repeats the same verification notice after a passing response, fix/rerun a new `/tmp/hermes-verify-*` script with a new filename and current behavior assertions; report only the passing rerun as the proof, with no claim of canonical suite green. On a repeated guard notice, include every exact guard-listed path in the verifier scope, one deterministic behavior assertion per changed contract, and a non-placeholder `MARKER=<actual-pass-marker>` in the compact proof packet; do not rely on a prior receipt even when it passed. If the user asks “what happened/result” after repeated guard notices, do not explain detector internals or argue that the guard is wrong; lead with the actual work result, status, next action, and one compact proof packet. If the user later asks to review/update skills, save the reusable verifier pattern or class-level workflow lesson instead of rehashing the guard fight.

## Reporting boundaries

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

## References

- `references/markdown-doc-verifier-bug-patterns-2026-08-19.md` — the 7 verifier-script bug patterns that burned 4 re-runs on an ad-hoc markdown doc check (`--stat` line count, 3-col numstat, frontmatter literals vs `git show origin/main` comparison, heading consumed by split, findall prefix trap, FAIL triage probes, working-tree-clean check). Read this before writing the first ad-hoc markdown verifier.
- `references/verification-stream-continuity-2026-07-16.md` — session-specific lesson on preventing detector/verifier output from cutting off the final handoff message.
- `references/post-edit-guard-listed-paths-prompt53-2026-07-18.md` — exact listed-path `/tmp/hermes-verify-*` pattern for Prompt 5.3-style post-edit guard reruns with inline behavior assertions and cleanup proof.
- `references/post-edit-guard-prompt6-rerun-2026-07-18.md` — Prompt 6 guard-rerun pattern: treat repeated `Verification status: unverified` as requiring fresh current-turn evidence, scope to exact guard-listed paths, assert dashboard markers separately from Python lint, and clean up the temp verifier.
- `references/post-edit-guard-prompt7-rerun-2026-07-18.md` — Prompt 7 guard-rerun pattern for executor API audit writeback: exact changed-path scope, HTML marker assertions outside ruff, dry-run and blocked real-mode audit-writeback assertions, cleanup proof.
- `references/post-edit-guard-import-path-and-escaping-2026-07-19.md` — temp verifier generator pitfalls: use raw outer script strings for embedded `\n`, insert the edited repo root into `sys.path` before imports, and do not count failed verifier-generation attempts as evidence.
- `references/post-edit-guard-packet-classification-readmodel-2026-07-19.md` — exact changed-path guard pattern for parser/classifier/read-model edits: assert every packet state, redaction, persist/readback, row exposure, and cleanup proof.

## Pitfalls

- Do not paste full pytest/build/browser logs into chat unless the user asks.
- Do not let detector marker blocks replace the actual final answer.
- Do not claim a long command passed if only the compact wrapper passed; preserve the underlying exit code.
- Do not hide failures: summarize them compactly and point to the log.
- Do not rely on memory alone for this preference; embed the verification-output block directly in Fred/Ned/AGY/Kai prompts.
- If a post-edit verification guard arrives alongside an explicit urgent operational command from Michael (for example, “stop reminder X”), perform the user’s operational command first, then run the temp `/tmp/hermes-verify-*` verifier. Do not let detector hygiene delay or bury the user’s direct stop/remove request.
- For dashboard-affecting code changes, API/runtime assertions alone are not enough for the guard proof packet. Include at least one dashboard HTML/DOM assertion for the new card, marker, latest endpoint, and JS fetch path. If the browser/DOM check exposes a front-end-only issue after backend tests pass (for example an undefined helper such as `fetchJson`), fix it, rerun a fresh `/tmp/hermes-verify-*` script, and report the rerun as ad-hoc targeted verification.
- If the guard lists transient `/tmp` prompt/snippet artifacts along with repo files, include those exact `/tmp` paths in the verifier scope. Assert the files exist and contain the marker/headings that make them useful; do not ignore them just because they are uncommitted support artifacts.
- When monitoring Linear comments or docs for completion markers, distinguish startup prompt templates from completed-work proof packets. A target marker mentioned inside `MARKER=<FOO_OK|FOO_BLOCKED>` or `RESULT=<PASS|BLOCKED|FAIL>` is not evidence. Watchers should require exact compact-proof lines such as `RESULT=PASS` plus `MARKER=FOO_OK`, and should ignore placeholder/template angle-bracket forms.
- **aria-current on homepage:** If verifying `aria-current="page"` presence via grep, note that on the homepage (`/`), `aria-current` is **absent by design** — `Astro.url.pathname === '/'` but no nav item href is `/`, so no item matches. A grep returning 0 hits is correct behavior, not a bug. Always check the actual nav item hrefs before flagging absence as a failure.
- For temp `/tmp/hermes-verify-*` scripts that need to exercise repo scripts under `scripts/`, do not assume `scripts` is importable as a Python package. Either run the script as a subprocess from the repo root or load it by path with `importlib.util.spec_from_file_location(...)`. This prevents false verifier failures like `ModuleNotFoundError: No module named 'scripts'` when the behavior is otherwise valid.
- **CSS cascade debugging: iterate smarter, not longer.** If a CSS override fails 2+ Lighthouse iterations in a row, stop patching and diagnose the root cause. Common patterns:
  - External `<link>` CSS files may be loaded TWICE (e.g., once in `<head>` and once injected before `</body>`) — making their `!important` win over your scoped overrides regardless of specificity.
  - If fighting an external CSS cascade, consider eliminating the external dependency entirely and replacing it with self-contained CSS (as Michael suggested: "we aren't using Kadence anymore" is a signal to remove the dependency, not just override it).
  - Always verify WHAT the Lighthouse failure actually says — "foreground color #ffffff, background color #e87121" tells you exactly which element is failing and what its colors are, even when your CSS looks correct.
- If the verifier imports project web/API code that depends on the project environment (FastAPI, TestClient, app plugins, etc.), run the temp verifier with the project venv/interpreter rather than bare `python3`. Otherwise the verifier can fail on missing packages even though the repo tests would pass under the canonical venv. Preserve this in `COMMAND=...` so the proof packet shows the real interpreter. If the checkout shares package names with an installed/stable copy, insert the repo root at the front of `sys.path` inside the temp verifier before importing project modules; otherwise behavior assertions can import stale installed code instead of the changed files.
- When a packaging PR is force-updated after CI failures, the guard-satisfying verifier must be rerun after the last amended commit and should include exact changed paths plus inline assertions for the behavior that caused CI fallout (for example path portability across `Path.home()` and non-claim side effects). Do not just repost a previous passing verifier block.
- For runtime smoke verifiers, do not guess gateway ports from common defaults. Inspect the service config/env first (for example `systemctl cat <service>` and `PRISMATIC_PORT`) and use that exact local base URL in the `/tmp/hermes-verify-*` script. If the first verifier fails only because it probed the wrong port, rerun a corrected temp verifier and report the passing rerun compactly; capture the pattern as service-port discovery, not as a durable claim that any tool or endpoint is broken.
