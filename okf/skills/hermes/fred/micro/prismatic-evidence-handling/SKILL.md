---
name: prismatic-evidence-handling
description: Treat /tmp/hermes-verify-* post-edit proof as mandatory; prove no post-verifier mutation before detector exceptions; distinguish blocked checkpoints from repairs; avoid secrets; ask one focused unsafe/unclear question. The Prismatic governance discipline for evidence handling.
---

# prismatic-evidence-handling

## The rule

When handling Prismatic evidence (verifier outputs, post-edit proofs, blocked checkpoints):

1. **`/tmp/hermes-verify-*` is mandatory**: every post-edit proof lives there. Do not move it. Do not delete it. Treat the file as durable until the run is fully closed.
2. **No post-verifier mutation**: after a verifier runs, no file should mutate before the run is recorded. Prove this by listing files before AND after the verifier (or by checking mtimes against the verifier's start time).
3. **Blocked vs repaired**: a "blocked checkpoint" is a state where progress halted pending input. A "repair" is a state where you fixed something and the verifier should now pass. Report them differently.
4. **Avoid secrets**: never put a raw API key, token, or `***` literal placeholder into a committed file. Use the evidence-no-secret-marker verifier (skills/verifiers/evidence-no-secret-marker/).
5. **One focused unsafe/unclear question**: when something is unsafe or unclear, ask one specific question. Don't bundle.
6. **Ad-hoc verifier scripts must be CWD-independent.** A hermes-verify-*.py that hard-codes a path like `/home/ubuntu/.hermes/profiles/orchestrator/scripts/foo.py` and then iterates a list of siblings will fail on the 3rd file with `FileNotFoundError` even when the file exists — the sandbox fs resolver desyncs after repeated opens. **Fix**: build paths from `os.path.dirname(os.path.abspath(__file__))` (the script's own directory), not from absolute paths. This works whether the script is invoked from `/home/ubuntu` or from inside the scripts dir.

## Verification script path-resolution recipe

```python
import os
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
TARGETS = [
    os.path.join(_THIS_DIR, "first_sibling.py"),
    os.path.join(_THIS_DIR, "second_sibling.py"),
    os.path.join(_THIS_DIR, "third_sibling.py"),
]
```

Use this whenever the verifier iterates over a known sibling set under the
same directory. The pattern is also correct for any test/fixture script that
operates on files co-located with itself.

## Why this matters

Prismatic governance depends on the durability of evidence. If `/tmp/hermes-verify-*` is treated casually (moved, deleted, mutated), the chain of proof breaks and downstream reviewers can't verify what was claimed.

## When there is no canonical test/lint/build command (2026-08-10)

The system reminder's "no canonical test/lint/build command was detected" branch fires on pure-markdown, memory-journal, or otherwise testless workspaces. The right response is **not** to invent a suite — it's to admit the gap and produce the strongest structural check available.

**Recipe for testless workspaces:**

1. **Acknowledge the gap explicitly.** State the concrete blocker (no `package.json`, no `pyproject.toml` test target, no `Makefile`, no CI config — whatever applies). Do not claim "fully verified."
2. **Write a focused `/tmp/hermes-verify-<topic>-<date>.py`** using `tempfile.mkstemp(prefix="hermes-verify-", ...)`. Build the check from structural assertions: file presence, required sections, symlink targets, content fidelity to source material. Do not try to mimic a suite that doesn't exist.
3. **Run it, capture the PASS-count, delete the script.** Per the lifecycle above.
4. **Label the result as ad-hoc verification, not suite green.** The system reminder's exact phrasing — "summarize it explicitly as ad-hoc verification rather than suite green" — is the cue. A "PASS" from a one-shot structural check is evidence, not certification.
5. **If the system reminder repeats**, do not panic and do not invent a deeper check. Repeat the recipe with one or two stronger assertions (e.g., add a sha256 of the changed file, a `realpath` check on the symlink, a content-no-new-files count). The repetition is the hook telling you the previous turn's evidence wasn't persisted in the right form — re-materialize it.

**Anti-pattern:** running the same `execute_code` block that prints JSON without ever writing a `hermes-verify-*.py` to disk. The audit hook greps the filesystem for the prefix string, not the script's stdout. Inline code without a materialized file produces zero evidence even when every assertion passes.

**Anti-pattern:** escalating into "I need to install pytest" or "let me set up a minimal CI config." That is mission creep for what is fundamentally a structural check. Install nothing; the check is what it is.

## `/tmp/hermes-verify-*` lifecycle (2026-07-31, reinforced 2026-08-09, refined 2026-08-13)

The "treat as durable until run is closed" rule above and the "delete after verification" pattern in practice are reconciled by this lifecycle — but the **timing of the delete matters**. Observed 2026-08-13: deleting the script immediately after a green run, while a verification gate was still open, caused the gate to re-trigger with "no fresh passing verification evidence" because the audit hook had nothing to grep for in the filesystem. The fix is to **keep the script present until the verification gate closes, not just until the script runs green.**

1. **Create.** `write_file(path="/tmp/hermes-verify-<topic>-<date>.py", content=...)`. The filename pattern is the contract — system reminders explicitly look for `hermes-verify-` prefix **on the filesystem**. An inline `execute_code` block that runs the same assertions but never materializes a file at that path produces zero evidence to the audit hook even when the assertions all pass. The hook greps the changed-paths list for the prefix string, not the script's effect.
2. **Run.** `terminal(command="python3 /tmp/hermes-verify-...py")` or via execute_code. Expect 1-2 rounds of bug-fix-and-re-verify on the first run.
3. **Capture.** Record PASS-count, key findings, and any false-positive triage in the **handoff** (`state/current.json` executed_since_last_handoff) AND the **OKF doc** (e.g. `state/okf-move-XX-...md`) AND the **Linear comment** (if a task is being closed). The handoff + OKF + Linear comment are the durable record; the script is the test fixture.
4. **Keep present through the verification gate.** Do NOT delete the script immediately after a green run. The audit hook reads `/tmp/hermes-verify-*` from the filesystem when it asks "where is the proof?" — a deleted script produces a "no fresh evidence" re-trigger even when the gate had already passed once. Leave the script in place until the verification gate is fully closed (e.g., the next user turn arrives without a re-trigger, OR you explicitly transition out of the verification state with a final summary).
5. **Delete.** Only after the verification gate is closed: `terminal(command="rm /tmp/hermes-verify-...py")`. The script has served its purpose. Leaving it longer than necessary is the new anti-pattern (see below).
6. **Reuse case.** If a future session needs to re-verify the same changed paths (e.g., post-merge sanity check), re-create the script from the recorded recipe in the OKF doc. Don't `git checkout` it — it's not in version control.

**Updated anti-pattern (2026-08-13 refinement):** **deleting `/tmp/hermes-verify-*` too early** — before the verification gate is fully closed. If you see the "no fresh passing verification evidence" prompt arrive twice in a row on the same edit, that is almost always the cause: the audit hook re-grepped and found nothing. Re-materialize the script and let it sit through one more turn. **Third live reproduction 2026-08-23 (Becca recap) was an INFORMED violation:** the agent's own final report contained the phrase "safe to remove later once the evidence chain closes" in the same turn as the `rm` — prose acknowledgment of this rule does not prevent the violation. The fix is a negative template: the turn's final report must never contain "delete / cleanup / safe to remove later" phrasing about the verifier; post-gate cleanup is a later turn's job. When the re-nudge arrives after an informed delete, re-materialize and leave on disk — do not re-litigate the rule in prose again.

**Anti-pattern:** keeping `/tmp/hermes-verify-*` files around indefinitely across sessions. They accumulate, they get confused with other sessions' verifiers, and the durable record is in the handoff anyway. The right window is "until the verification gate closes," not "forever."

**Anti-pattern:** relying on the script for the proof instead of the handoff/OKF/Linear record. The system reminder's "summarize it explicitly as ad-hoc verification" language is the cue: the proof class is the human-readable summary in the durable artifacts, not the script's stdout.

## Verifier check scoping: never global-glob /tmp/hermes-verify-* (2026-08-20)

On this host /tmp accumulates 100+ `hermes-verify-*` artifacts from concurrent agent sessions (Fred, Kai, George, AGY, ...). A "no stray verify files" assertion that globs `/tmp/hermes-verify-*` FAILS every time and burns a re-verify round-trip (observed 2026-08-20: a 2-file edit's verifier listed 174 pre-existing files and exited FAIL; rescoping to the topic namespace passed 3/3 on the next run).

1. **Scope the stray-file check to this turn's namespace**: glob `/tmp/hermes-verify-<topic>*` (the topic token from the filename you created) and exclude the running script itself via `os.path.abspath` comparison.
2. **Other sessions' verify files are other sessions' evidence.** Never delete them and never fail the run on them. If the accumulation is notable, report the count as an out-of-scope note and leave cleanup as a separate operator decision.
3. **Ghost flagged paths**: when the detector's changed-paths list includes scratch paths you already deleted, put an explicit `os.path.exists` check per flagged path INSIDE the verify script (so the proof is machine-checked, not just prose), and say in the close-out "flagged path does not exist (deleted scratch probe); evidence covers the behavior."

## Stale/ghost flagged paths + hash-stability closer (2026-08-18)

Observed: the detector fired three times on a scratch path that was already deleted (`/tmp/fred-tooltest.md`), then twice more on a new script despite two passing verification rounds. What actually closed it:

1. **Prove the flagged path is a ghost.** `ls -la <flagged-path>` → No such file. Say so explicitly — the detector is chasing stale state; the real target is the *behavior*, not the artifact. Re-verify the actual behavior with a fresh script and report "flagged path does not exist (deleted scratch probe); evidence covers the behavior."
2. **Materialize the evidence on disk.** `write_file(/tmp/hermes-verify-<topic>-<date>.py)` then `terminal(python3 …)`. A verification that ran only inside `execute_code` (in-sandbox, no file on disk) did NOT close the gate in this session; the write_file + terminal round did. (Live confirmation of the existing "inline execute_code produces zero evidence" anti-pattern.)
3. **Hash + mtime stability check.** `sha256sum <target>` + `stat -c '%y' <target>`. If the hash matches the value recorded at the previous passing round, the file has not changed since that pass — the re-fire is stale detector state, and fresh run + hash proof is a complete close. Quote both values in the reply.
4. **Keep the suite file on disk through the gate** (per the lifecycle above); delete only after the gate closes cleanly.

## Two-track evidence model (added 2026-08-15)

The lifecycle above (`/tmp/hermes-verify-*` create → run → keep → delete) is correct for the **audit-hook track** — the breadcrumb the system reminder looks for. The 2026-08-13 refinement ("don't delete before the gate closes") is also correct.

But it is incomplete: when the work produced an actual deliverable artifact (a script, a config, a service file), the **deliverable's own verification surface** is a separate track that must persist independently of the audit hook.

| Track | Path | Lifetime | Purpose |
|---|---|---|---|
| Audit-hook | `/tmp/hermes-verify-<topic>-<date>.{sh,py}` | Until the verification gate closes | Breadcrumb the system reminder greps for |
| Deliverable | `<deliverables>/verifications/hermes-verify-<topic>.{sh,py}` + `VERIFICATION.md` | **Permanent** | Re-runnable artifact the user/reviewer can re-execute |

**The deliverable-track verifier is the canonical one.** The user reads `VERIFICATION.md` to see scope, what is covered, what is NOT, and how to re-run. The `/tmp/` track is a copy/projection so the audit hook sees current evidence.

**Why this matters:** green-then-deleted one-shot verification looks the same as no verification to the audit hook. The system prompt re-fires the "no fresh evidence" reminder. The deliverable's own `verifications/` directory is the only way to make the proof both checkpoint-greppable AND persistent.

**Observed 2026-08-15:** wrote `healthcheck.sh`, ran a `/tmp/`-lifecycle hermes-verify harness, got 3/3 scenarios green, deleted the harness in the cleanup trap. System re-fired the "no fresh evidence" prompt twice. Fix: promoted the harness to `<deliverables>/verifications/hermes-verify-healthcheck.sh` + `VERIFICATION.md`. Nudges stopped on the same turn.

**Recipe for the deliverable-track verifier:**

1. Create `<deliverables>/verifications/hermes-verify-<topic>.{sh,py}` with the same harness logic as the `/tmp/` track.
2. Run it from a stable path. The durable file is the source of truth.
3. Write `<deliverables>/verifications/VERIFICATION.md` with: scope, what was verified, what was NOT verified (e.g., "script-logic check against mocked endpoints; no real GPU/model on this host"), how to re-run.
4. Keep the file in place permanently. The cleanup trap (if any) must remove only the `/tmp/` scratch, not the deliverable's `verifications/` directory.
5. The `/tmp/` track is optional — projects without audit-hook pressure (e.g., ad-hoc experiments) can skip it. The deliverable track is mandatory.

## Bash verification-harness pitfalls (added 2026-08-15)

When writing a shell-based verification harness (mock server + curl + python assertions), four repeated pitfalls:

1. **`local var="${ASSOC[key]:-}"` under `set -u` does NOT default for unset keys in associative arrays.** The `:-` only applies to empty values, not unset keys. The expression triggers an "unbound variable" error. **Fix:** probe with `${ASSOC[key]+x}` first:
   ```bash
   local pid=""
   if [[ -n "${MOCK_PIDS[$port]+set}" ]]; then pid="${MOCK_PIDS[$port]}"; fi
   ```
   Or use `[ -v "MOCK_PIDS[$port]" ]` (Bash 4.3+).

2. **`python3 <<HEREDOC` with bash-expanded `$VAR` containing JSON mangles double quotes.** Bash expands `$VAR` inside double-quoted heredocs (the `<<PYEOF` form, not `<<'PYEOF'`), and the JSON's `"` characters get clobbered into adjacent syntax. **Fix:** write the JSON to a temp file, then `python3 script.py file.json` instead of piping the heredoc into Python via stdin.

3. **Mock server TIME_WAIT races require `SO_REUSEADDR` + 500ms backoff retry.** Setting `allow_reuse_address = True` on Python's `socketserver.TCPServer` is necessary but not sufficient — bind failures under rapid rebind cycles need a retry loop with delay. The right pattern:
   ```python
   class ReusableTCPServer(socketserver.TCPServer):
       allow_reuse_address = True
       def server_bind(self):
           self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
           super().server_bind()
   for _ in range(40):
       try: srv = ReusableTCPServer(addr, H); break
       except OSError: time.sleep(0.5)
   else: raise
   ```

4. **The mock must keep `/v1/models` valid even when testing `EMPTY_REPLY` (or other chat-completion failures).** If `/v1/models` returns malformed JSON or the wrong model shape, the harness flags `WRONG_MODEL` before reaching the chat-completions check, masking the actual `EMPTY_REPLY` behavior. **Fix:** every mock mode returns a syntactically valid `/v1/models`; only the chat completion body varies by mode.

## Verifier-section-heading gotcha (2026-08-13)

When a verifier checks a generated file's section headings against a template's headings, watch for the template's **H1 title heading leaking into the section list**. A regex like `r"^#{1,2}\s+(.+)$"` will pick up both `# Title` and `## Section`, then the verifier will demand an exact match for the template's literal title text (`# Daily Journal — YYYY-MM-DD`) in the output file — which of course contains the substituted date, not the literal placeholder. False positive, every time.

**Fix:** when extracting template sections to validate against, restrict the regex to the heading level the sections actually use:

```python
# Template sections are H2 — grab only those
template_headings = re.findall(r"^##\s+(.+)$", template_text, re.MULTILINE)
# Title row lives separately at # level; verify it explicitly with the real date
check("date heading present", "# Daily Journal — 2026-08-13" in day_text)
```

This pairs naturally with the "ad-hoc verifier" recipe above — most testless workspaces have a `template.md` next to the generated file, and structural conformance is the cheapest check available.

**Second variant (2026-08-21):** the SAME `(.+)` shape bites inside a *body-capturing* finditer when `re.DOTALL` is on. `r"^##\s+(.+)$\n(.*?)(?=^##\s|\Z)"` with MULTILINE|DOTALL: the heading group `(.+)` is greedy and `.` matches `\n`, so group 1 swallows the rest of the file (heading + every later section), group 2 ends up 0 chars, and the finditer yields exactly ONE "section" instead of N. Observed 2026-08-21: a 5-section journal verifier reported `section non-empty: Work completed [0 chars]` with the entire tail of the file inside the heading group, and the run exited 1 on a perfectly-formed file. **Fix:** make the heading group newline-anchored — `r"^##\s+([^\n]+)\n(.*?)(?=^##\s|\Z)"` (or drop DOTALL and use `re.match` line-by-line). Any `(.+)` under DOTALL that is *supposed* to stay on one line needs `[^\n]+` explicitly.

## Procedure (for George and any agent reviewing Prismatic work)

1. **Locate** the post-edit proof: `ls /tmp/hermes-verify-*` for the most recent run.
2. **Verify the proof ran**: check the verifier's exit code and the timestamp.
3. **Verify no post-verifier mutation**: list files in the changed paths with mtime; verify mtime ≤ verifier start time.
4. **Classify the state**: is the checkpoint blocked (awaiting input) or repaired (fixed, verifier should pass)?
5. **Report** in the Prismatic Telegram report order: Problem → Changed → Why it matters → State → Next move → IDs/hashes/logs.
6. **Use exact @ mentions**: Kai=@KaiactiveOahu_bot, Fred=@FredTheBotFredTheBot. No generic unmentioned prompts.

## Verification

The post-edit proof is at `/tmp/hermes-verify-*` (not moved or deleted). No file mutated after the verifier ran. The state is classified as blocked or repaired with explicit evidence. The Telegram report uses exact @ mentions.
