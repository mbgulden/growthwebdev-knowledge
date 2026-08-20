---
name: gap-closure-discipline
description: The class-level discipline for closing a named gap (from a gap-analysis). Audit memory/scripts/skills/runtime for the gap → ship SKILL.md + verify.py + OKF doc + adopt across profiles → run focus verifier → report PASS-count honestly. Closure requires every step in the chain; partial delivery does not count. The first verifier run typically catches bugs in the verifier itself (regex escapes, syntax, false positives, broken-symlink FileNotFoundError); plan for at least one round of bug-fix-and-re-verify.
---

# gap-closure-discipline

## The hard rule

When Michael gives you a named gap (e.g. "gap 3: projector awareness has slipped into generic assistant tone"), closing the gap means:

1. **Audit first.** Read every relevant file: memory, scripts, skills, runtime config, OKF docs. Know the surface before you ship.
2. **Ship the whole chain.** SKILL.md (or micro-skill) + verify.py + OKF doc + adoption across profiles. Partial delivery is not closure.
3. **Run the focus verifier.** A focused verifier tied to the specific changed paths. Not a generic "tests pass."
4. **Report PASS-count honestly.** The number must match the real verifier output. If 9/12 pass with 3 false positives, report that. Don't round up to "all good."
5. **Capture the obvious next step.** The bounded turn ends with the next move (next gap, deferred pin, or unblocking question). "Standing by" alone is not a closing move.

## Why partial delivery doesn't count

A SKILL.md without a verifier is a wish. A verifier that doesn't compile is a lie. A closure report that rounds up a partial to a clean PASS is an overclaim that compounds across sessions. The user judges by whether the gap is **actually** closed, not by the headline.

## The audit step (before any code)

Before writing anything, know:

- **Memory**: does the user have a stable preference that contradicts this gap's fix? (e.g. "memory is for preferences, not runbooks" — so the gap-6 fix moves runbooks to skills, not memory.)
- **Scripts**: which files in scripts/ implement or violate this gap's contract? Grep for the anti-patterns.
- **Skills**: which existing skills duplicate or contradict the gap's prescribed fix?
- **Runtime**: any cron jobs, env vars, or config keys that the gap's fix should touch?

The audit is **silent**. Don't narrate it. Run the reads, hold the findings, ship the fix.

## The ship step (the full chain)

| Artifact | Purpose | When missing |
|---|---|---|
| SKILL.md or micro-skill | The procedure future-self will load on cold start. 1-page max for micro-skills. | The fix can't be reused next session. |
| verify.py | A runnable check that exercises the fix's contract. Heuristic is fine; not running is not. | The system will keep nudging for evidence. |
| OKF standard | Cross-project durable documentation. Same shape as the audit found. | Future agents won't know the gap was closed. |
| Adoption across profiles | Symlink or copy to every active profile. Single source of truth in one profile. | Other profiles can't apply the discipline. |

**All four ship in the same bounded slice.** A gap-closure turn that ships only 2 of 4 is half-done.

## The verifier step (the heart of the discipline)

### Build the verifier before claiming closure

The verifier is part of the deliverable, not a response to a nudge. Build it in the same turn as the artifact. (See `verifier-as-deliverable-discipline/` for the umbrella.)

### The first run is a bug-discovery run

This is the load-bearing lesson from 8 gap closures this session. Every verifier I wrote had bugs in it on the first run:

| Bug class | Example | Fix |
|---|---|---|
| Regex escapes | `r"print\([^)]*"` got mangled when nested in a triple-quoted string passed through `write_file` | Use raw strings or escape carefully; test the pattern with `re.search` before shipping |
| Syntax error | Nested triple-quotes in a docstring tripped Python's parser | Use single-quoted strings for inner content |
| False positive | Verifier flagged `"API will return 403"` as "I will narrative" because the regex matched the trailing word | Tighten to `(?:^|\s)I will\s` to anchor on subject=I |
| False negative | Verifier's expected-state didn't match actual file content (e.g., looking for a section that was renamed) | Re-read the file with `read_file` before writing the verifier |
| Broken symlink | `os.walk` returned a path that was a dangling symlink; `open()` raised FileNotFoundError | Guard: `if os.path.islink(path) and not os.path.exists(path): return []` |
| Mode mismatch | `--quiet` mode produced JSON stdout when `--json` was also passed | Decide precedence: `--json` wins, `--quiet` only applies to text path |
| Async vs sync | A bash heredoc with `***` got interpreted as a glob, breaking the test | Use `subprocess.run(capture_output=True, text=True)` from Python |
| **Patch-tool over-deletion** | `patch` with `old_string` containing a function header and `new_string` containing a multi-line indented body repeatedly stripped the body (function header stayed, body vanished). Hit 4+ times in one session across `agy_peer_review.py`, `golden_thread_cross_project_sync.py`, `agent_backlog_surgeon.py`, and the OKF index. | Use `write_file` for whole-file rewrites when the change crosses indented blocks (function bodies, method definitions, deep-nested blocks). Reserve `patch` for true header/footer swaps or single-line replacements. If you must use `patch`, split the operation into a header-only swap and a body-only swap, and verify with `read_file` after each. |
| **Helper-extraction regex undercount** (2026-07-31, Move 13) | Promoting a helper that was inlined N times. Used regex `r"^def _wrap_for_linear\(.*?(?=^def \|\Z)"` to extract the helper from one of the N source files. The regex captures only the function bounded by the next top-level `def`, but the actual helper was followed immediately by a private sibling helper (`_wrap_single_line`) at the next line. Result: extracted 30 lines (just `_wrap_for_linear`), the inner helper was silently lost on the destination. Verifier caught it via `NameError: _wrap_single_line not defined` — but only after the moves had committed at the source level. | Two-step extraction: (1) extract a **block** of consecutive top-level defs, not a single def — pattern is `r"^(?:def \|class \|async def )(?:_wrap_for_linear\|_wrap_single_line)\(.*?\n\n\n\ndef \|class \|async def \|$"` or simpler: extract by AST (`ast.parse(src).body`) and reconstruct. (2) Grep the destination for *every* identifier referenced in the extracted block (`grep -E "_(wrap_for_linear|wrap_single_line)_"` on the source file) BEFORE removing the inlined copies. (3) After extraction, run the full behavior verifier — not just a syntactic check — because missing private helpers won't surface in a "imports + callsite shape" verifier, only in actual runtime behavior. |
| **Function-rename caller drift** | Renamed `_is_documentation_line` to `_looks_like_instruction_with_placeholder` but a caller block still called the old name → `NameError` at runtime. | When renaming a function, `grep` the entire file (or repo) for callers before swapping. Better: keep the old name as a delegating shim for one cycle, then remove it. |
| **`patch` tool `patch`-parameter confusion** (2026-07-30) | Calling `patch` with `mode="replace"`, `path=...`, `old_string=...`, `new_string=...` PLUS a `patch` parameter triggers "path required" errors that loop 4-5 times. The `patch` parameter is reserved for V4A multi-file patches; including it in single-file mode is rejected. | For single-file edits, use **only** `path` + `old_string` + `new_string` (plus `mode="replace"`). Do not include the `patch` parameter. When the tool fails 3+ times with "path required", the lesson is to drop the `patch` parameter, not retry the same call. Workaround: fall back to `execute_code` with `open(path).read().replace(old, new)` for the same effect. |
| **SSH `qm guest exec` shell-quoting verifier trap** (2026-08-16) | Wrote a verifier with `ssh_exec("python3 -c \"import torch; print('torch:', torch.__version__)\"")`. The actual stdout on the VM was `import torch; print(torch:, torch.__version__)` — the inner single-quote pair around `'torch:'` got stripped by the SSH wrapper's `bash -c '...'` re-parsing, producing a SyntaxError. Every check that tried to use `python3 -c` over `qm guest exec` hit the same false-negative. | Use file-based checks for any SSH-wrapped command that needs shell metacharacters: `write_file` (or `cat > /tmp/x.py << 'PYEOF'`) on the orchestrator, `wget`/`scp` to the VM, then `python3 /tmp/x.py`. Two specific rules: (a) never put `^...$` regex anchors in `grep` arguments over `qm guest exec` — bash strips the `^` and `:` and gives you `command not found`. Use `grep -c 'pattern'` (no anchors) instead, then check the count. (b) never rely on multi-line `head -10` output — `qm guest exec` JSON wrapper mangles line endings to `\/` literals. Use `grep -c` for count assertions, or write the file to `/tmp` on the orchestrator and `wc -l` it instead. The whole class of bugs is sidestepped by `scripts/transfer-file-to-vm.sh` (the umbrella `proxmox-k3s-gpu-cluster-ops/scripts/` helper) — write the script, transfer it, run it. Verifiers that genuinely need to call out to a remote VM should be `ssh + subprocess.run(capture_output=True)` from a Python verifier, not `qm guest exec` JSON-string parsing. |
| **Critical-check assertion inverted after fix lands** (2026-07-31) | Wrote `verify_move14_untracked_audit.py` with critical-file checks that asserted `if "registry_writer.py" in code_refs: PASS`. Designed pre-fix to confirm the audit *found* these untracked-but-referenced files. After Move 16 committed `registry_writer.py` and `registry_reconciler.py` to git, the verifier started FAILing those same checks — because the files were no longer in `code_refs` (they were tracked). The check was correct for the audit's original purpose, but the audit's purpose changed once the fix landed. | When a fix moves the system from "X is untracked" to "X is tracked," any verifier check that asserts "X must be in the untracked list as a sign the audit found it" silently inverts from PASS to FAIL. **Fix pattern:** make the check accept either tracked OR untracked-but-referenced as PASS: `if is_tracked(name) or name in refs: PASS; else: FAIL`. **Verification recipe:** after a fix moves files from one bucket to another, run the verifier with **both** the pre-fix and post-fix fixture to confirm the check accepts both states. If it only accepts one, the check is wired to the symptom, not the invariant. |
| **Verifier-script marker strings stale after gate rewrite** (2026-07-31) | Wrote a 10-check ad-hoc verifier (`/tmp/hermes-verify-move19-cleanup-2026-07-31.py`) that asserted `if "All gates passed" in hook_output`. The pre-commit hook had been refactored at some point and the actual success marker is `✅ Move 11 verifier: ALL CHECKS PASSED` plus `All gates passed successfully` (different capitalization). The check FAILED even though the hook passed cleanly. | Use the **actual** success markers emitted by the tool under test. `bash <hook> 2>&1; echo $?` first, capture real output, then match against the real markers. Don't trust remembered marker strings from older verifiers. |
| **Verifier uses `listdir` + `open` on stale paths** (2026-07-31) | Wrote a "no conflict markers repo-wide" check using `os.listdir(REPO)` then `open(path)`. If `listdir` returns a name that no longer resolves (deleted, moved, or stale symlink), `open()` raises `FileNotFoundError` and the check FAILs — even though there's no real conflict marker anywhere. | Always `if not os.path.isfile(path): continue` before `open()`. Same guard as the symlink pitfall already in this table. |
| **Linear API assigns sequential identifiers, not gap-filling** (2026-07-31, Move 15) | Drafted 5 cleanup tasks as "GRO-4373, GRO-4374, GRO-4375, GRO-4376, GRO-4377" — assuming gap-filling after GRO-4372. The issueCreate mutation landed and got GRO-4377 through GRO-4381 instead, because **GRO-4373–4376 already existed** (Zapier infra work by another agent). The first task's UUID was used for the Move 15 title; the next four got reassigned automatically. Comment body still referenced the old identifiers. | Before drafting N Linear task identifiers, run a `query { issues(filter: { identifier: { in: [<last-N>] } }) { nodes { identifier title } } }` to confirm what's actually free. Or: don't pre-assign identifiers — let Linear assign, then re-derive in the comment body. **The deeper pattern: Linear identifiers are a public-facing label, not a planning slot.** Plan by parent epic + child title; let Linear number. |
| **Merge conflict resolution needs the strategy declared first, not the edits** (2026-07-31, Move 17) | Three auto-merge conflicts in `agy_sandbox_event_supervisor.py` from `ned/GRO-3310` (signature, cmd extraction, stdin). The naïve patch-loop approach hit a `SyntaxError` on the first patch because of indentation drift (`patch` tool stripped one indent level when removing conflict markers). Fixed mid-flow; second conflict also needed indent repair. | Declare the resolution strategy in one sentence **before** opening the file: "Signature: keep HEAD (additive params); cmd: take ned's `build_agy_command()` helper; stdin: take ned's `subprocess.DEVNULL`. Reasoning: helper extraction is the cleaner refactor that produces the same cmd; stdin=DEVNULL is the actual GRO-3310 fix." Then edit. Also: after each conflict resolution, run `python3 -c "import ast; ast.parse(open(path).read())"` to catch indent drift before proceeding to the next. **Three-conflict-in-one-file is the threshold where strategy declaration saves more time than it costs.** |
- **`/tmp/hermes-verify-*` cleanup pattern** (2026-07-31, Move 19) | After the system reminded me to write an ad-hoc verifier, I created `/tmp/hermes-verify-move19-cleanup-2026-07-31.py`, ran it (8/10 → fixed → 10/10 PASS), then `rm` it. The prismatic-evidence-handling skill says "treat as durable until run is closed." The reconciliation: the script is durable **for the duration of the run that triggered it**; once that run's verification is recorded in the handoff/OKF/Linear comment, the script has served its purpose and should be removed. The handoff + OKF doc capture the proof, not the script. | Write the verifier under `/tmp/hermes-verify-<topic>-<date>.py`. Run it. Fix any bugs (expect 1 round). Re-run. Capture PASS-count + key findings in the handoff + OKF doc + Linear comment. Then `rm /tmp/hermes-verify-*`. The script is the test fixture; the handoff is the durable record. Keeping the script around is clutter unless a follow-up session needs to re-run it. |
| **Bulk-assign to another agent via Linear API** (2026-07-31) | After surfacing 15 gaps and resolving 4 safe ones, the user said "Get me the linear task names for all those and I'll have George resolve all of them properly." The right move was bulk-assign the remaining 11 to George via the `issueUpdate` mutation with `assigneeId`, post a parent-epic handoff comment, then stand down. NOT to ask "do you want me to keep going or hand off?" — the user named another executor, that's a stop signal. | (1) Get the assignee UUID: `query { team(id: TEAM_ID) { members { nodes { id name email } } } }`, match on name OR email. (2) Loop through the open task identifiers, re-derive each UUID, send `issueUpdate(id, input: {assigneeId: <uuid>})`. (3) Post a parent-epic handoff comment that lists the closed-by-Fred + assigned-to-George split, with URLs to each. (4) Bump counter, stand down. **Pitfalls:** `team_id` ≠ `project_id` (assignee lookup needs team; issue routing uses project). Email match is brittle — George shows up as `ellageorgeson@gmail.com` (real email) in the team members list. Don't hardcode UUIDs across sessions. Worked example: `references/gap-closures-2026-07-31b-delegation-session.md`. |
| **"The user said X will do this" is a stop signal, not a question** (2026-07-31) | After shipping 4 of 15 gaps cleanly, I asked the user "how to proceed with the 11 remaining?" and got "I'll have George resolve all of them properly." That was a delegation signal. The wrong move would be to ask "scope confirmation?" again or to start working on the high-risk ones anyway. | When the user names another executor (George, Ned, AGY, Jules, "the agent", etc.) for the open work, the bounded move is: bulk-handoff via the durable system (Linear API), post the parent-epic handoff comment, then stand down. Asking again is noise; working unilaterally violates the named-executor. **The general rule from the gap-closure-discipline reference: when the user says "X will do this," the agent's job is to make X's job easy, not to also do it.** |

**Plan for at least one round of bug-fix-and-re-verify.** The first run result is a discovery tool, not a "this should pass" tool.

### Verifier false-positive triage

When the verifier says FAIL, the failure is real OR the verifier is wrong. Triage:

1. Look at the actual file content (`read_file` on the flagged path) to confirm the violation exists.
2. If the violation exists, fix the source.
3. If it doesn't exist, the verifier's expected-state is wrong — fix the verifier.
4. Report which case in the response so the user knows.

## The report step (the truth)

```python
{
  "verifier": "<name>",
  "scope": "ad_hoc_targeted",  # not suite green
  "not_suite_green": True,
  "total_checks": N,
  "passed": K,
  "failed": N - K,
  "results": [...]
}
```

Report every failure. If a failure is a verifier false positive, say so explicitly. If a failure is a real defect in the artifact, fix the artifact. **Never round up the PASS count by claiming a failure was a false positive without investigation.**

## The "obvious next step" closing move

Michael judges by whether the next move is identified, not whether the previous move was perfect. At the end of a gap-closure turn, ship one of:

- **Next gap** ("gap N+1 is queued; here's the spec")
- **Deferred pin** ("N follow-ups pinned; here are the refs")
- **Unblocking question** ("need your call on whether to ship the integration or wait")

"Standing by" alone is not a closing move. It tells Michael nothing about what to do next.

## Anti-patterns

- Ship the SKILL.md without a verifier. (The user will get nudged for evidence later.)
- Ship the verifier without compiling it first. (It will fail to run when the system nudges.)
- Report "24/24 PASS" without double-checking the verifier's expected-state against actual file content. (False-positive pattern; common bug.)
- Round up the PASS count when failures are verifier false positives without investigation. (Compounds over sessions.)
- Stop at "standing by" without identifying the next move. (User has flagged this.)
- Treat the first verifier run as "should pass." (Treat it as discoverability.)

## Verification

The discipline holds when:
- Every gap closure ships the full chain (SKILL + verify + OKF + adoption) in one bounded slice.
- Every focus verifier is a self-contained `/tmp/hermes-verify-*.py` script that runs in <30s, cleans up after itself, and reports a JSON summary with all checks listed.
- Every closure report names the verifier scope ("ad_hoc_targeted, not suite green") and includes any false-positive triage.
- Every bounded turn ends with the obvious next step (next gap, pin, or unblocking question).

## Related work

- `verifier-as-deliverable-discipline/` — the umbrella for the "verifier ships with the artifact" rule.
- `projector-aware-communication-discipline/` — the reply shape discipline; gap-3 closed using this gap-closure pattern.
- `proactive-execution-discipline/` — the silent-bounded-slice discipline; gap-2 closed using this pattern.
- `telegram-cron-output-contract/` (micro-skill) — the cron output contract; gap-7 closed using this pattern.
- `next-action-truth-source/` (micro-skill) — the registry/Linear chain of truth; gap-8 closed using this pattern.
- `references/gap-closures-2026-07-29.md` — worked examples from the 8-closure session.
- `references/gap-closures-2026-07-31.md` — worked examples from the Moves 11-19 cleanup pass (cold-start from stale handoff, verifier-bug discovery on re-run, Linear identifier-reality, merge-conflict strategy-first, counted-value-as-claim pitfall, ad-hoc verifier cleanup lifecycle).
- `references/gap-closures-2026-07-31b-delegation-session.md` — worked examples from the 15-gap post-cleanup-resolution pass (bulk Linear task creation + bulk-assign to another agent via `issueUpdate.assigneeId`, safe-win-vs-decision classification filter, "user named another executor" as stop signal).
