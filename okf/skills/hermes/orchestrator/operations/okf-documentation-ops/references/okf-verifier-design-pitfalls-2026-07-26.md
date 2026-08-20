# OKF Verifier-Design Pitfalls (real bugs that have shipped)

A working OKF verifier needs to be right about conventions, content, and runtime. Below are the bugs that have actually shipped during the journal-pe-integration + pe-cron-workflow-gaps builds (2026-07-26). Each one was discovered by running the verifier against a known-passing artifact. Fix them on the first write so the next verifier doesn't repeat them.

## 1. `git_path` is repo-relative, not OKF-relative

**Symptom:** every OKF doc appears "broken" because the verifier miscompares the durable form with the OKF-internal form.

**Cause:** the OKF root is `okf/`, so every file's repo-relative path is `okf/projects/<slug>/index.md`. The verifier checked against the OKF-relative form `projects/<slug>/index.md` and reported every doc as broken.

**Fix:** the verifier must check `git_path == f"okf/{rel}"`, not `git_path == rel`. The `rel` variable should be the path under `okf/`; the `f"okf/{rel}"` form is the durable, repo-relative form.

**Forward rule:** every OKF doc's `git_path` frontmatter field uses the repo-relative path (`okf/projects/<slug>/index.md`), and `resource` ends with the same repo-relative path.

## 2. Forbidden-marker strings are checked literally

**Symptom:** a risk register's `Observable signal` field gets flagged as a credential leak because it documents "what to watch for" using literal prefixes like `ghp_`, `xox[abp]-`, etc.

**Cause:** the verifier's forbidden-marker check is a literal substring match. Putting `ghp_` inside backticks inside a Markdown prose paragraph still triggers the match.

**Fix:** use **category wording** in OKF artifacts when documenting what to watch for. Examples:

- ❌ `Any entry whose pre-persist body matches a known secret pattern (\`api_key=\`, \`Bearer \`, \`ghp_\`, \`xox[abp]-\`, etc.)`
- ✅ `Any entry whose pre-persist body matches a known GitHub-style credential pattern (redacted category in this artifact; raw prefix intentionally withheld)`

The category is what the agent needs to know; the literal prefix is what the verifier needs to not see.

**Forward rule:** OKF artifacts never include literal credential prefixes, even inside backticks, even as "what to watch for" examples.

## 3. Section-heading patterns must match what you actually wrote

**Symptom:** a verifier looks for `§2.1` and the doc has `### 2.1 HTTP ...` — the verifier fails to find the section.

**Cause:** the verifier hardcoded a prose-style section reference (`§2.1`) when the doc used a Markdown heading (`### 2.1`).

**Fix:** pattern-match against the exact Markdown heading text. Examples:

- `re.search(rf"###\s*{sect_num}\s+\w", text)` — matches `### 2.1 HTTP ...`.
- Avoid prose references like `§2.1`, `Section 2.1`, `(2.1)` in the verifier — they drift from the actual headings.

**Forward rule:** the verifier searches for the same heading shape the doc author actually wrote.

## 4. `depends_on_siblings` is a sequence, not a parallel

**Symptom:** an agent picks up two sibling tasks marked as `depends_on_siblings` simultaneously and produces two PRs that conflict.

**Cause:** the verifier documented "ship together as one PR" but didn't say "in this order, sequentially".

**Fix:** the convention is:

- `depends_on_siblings: [GRO-NNNN, GRO-NNNN]` — sequential; pick up only after earlier tasks have merged.
- `depends_on_siblings: none (first task in epic)` — pick up freely.

Document this in the verifier-side note AND in the task description. Use the empty-list form (`none (first task in epic)`) for the first task in an epic to signal it can be picked up freely.

## 5. `agent:in-progress` is a runtime signal, not a built-in feature

**Symptom:** an agent picks up a task already in progress, edits the same files, and produces conflicting changes.

**Cause:** adding a label named `agent:in-progress` is meaningless without a claim protocol that says "atomically add this label before reading source code; remove it before handoff".

**Fix:** define the protocol in the same place you define the label. The full spec is in `linear-handoff-build-out/references/distributed-execution-header.md` and `okf/standards/references/distributed-execution-multi-agent-task-pickup.md`. The TL;DR for the verifier:

- An agent must run a label check before pickup.
- An agent must atomically add `agent:in-progress` before reading source code.
- An agent must remove `agent:in-progress` and add `agent:needs-human-review` before handoff.

The verifier should check that these labels exist on the workspace (via `issueLabels(first: 100)`) and that the tasks reference the protocol in their description.

## 6. Verifier bugs deserve explicit audit-log notes

**Symptom:** a verifier fails on the first run, the agent patches the docs, and the docs are now wrong because the verifier was the broken layer.

**Cause:** the agent assumed "verifier passes = docs right; verifier fails = docs wrong". Both directions can be wrong.

**Fix:** when the verifier returns failures on the first run, **fix the verifier first** and explicitly note which layer was wrong in the audit log. Example audit log line:

```
ad-hoc verification FAILED (13 failures)
  - projects/.../index.md: git_path 'okf/...' != 'projects/...'
  → verifier anti-pattern: miscompared repo-relative vs OKF-relative forms
  → patched verifier (skill: okf-documentation-ops §17)
```

**Forward rule:** verifiers and docs are both code. Both deserve review. Run the verifier against a known-passing artifact first to confirm the verifier's conventions are right before relying on its output.

## 7. Dynamic-field assertions fail silently on zero-counts

**Symptom:** the verifier prints `0 unique daily source citations` for a recap that's clearly citing many sources. The verifier doesn't fail; it just looks broken.

**Cause:** the verifier extracts dynamic fields (timestamps, citation IDs, changed paths) with a regex and counts them — but if the regex is wrong or the field shape drifted, the count is silently zero.

**Fix:** any time a verifier counts dynamic fields, the assertion must:

1. Check that the expected collection is non-empty.
2. Print the actual extracted values when reporting.
3. If the count is zero, fail loudly with the regex that was tried.

**Forward rule:** "0" is a verifier bug, not a passing result. Always print what was extracted.

## 8. Inline `execute_code` verifiers are sometimes better than `/tmp/hermes-verify-*.py`

**Symptom:** a `/tmp/hermes-verify-*.py` script gets created, runs, gets deleted, but a post-turn verification guard still flags it as an additional changed path because the file was named in a Linear description.

**Cause:** `tempfile.mkstemp(prefix="hermes-verify-", suffix=".py", dir="/tmp")` is the standard pattern, but the harness sees the name (not the file) and flags it as a residue.

**Fix:** for ephemeral verifiers (post-write artifact verification), prefer inline `execute_code` runs that don't create a file artifact. The harness's changed-path tracking then has nothing to flag. Reserve `/tmp/hermes-verify-*` for cases where the artifact is large enough that the harness cap forces a real file, or where the user explicitly asks for a reusable script under the skill.

This is captured in `okf-documentation-ops` §18.

## Pitfalls

- Do not assume the verifier's conventions match yours. Run it against a known-passing artifact first.
- Do not assume `git_path` is OKF-relative. The OKF standard is repo-relative.
- Do not assume literal forbidden markers inside backticks are exempt. They aren't.
- Do not assume prose-style section references match Markdown headings. They don't.
- Do not assume "0" is a passing count. Print the actual values.
- Do not assume `/tmp/hermes-verify-*.py` is harmless. Inline `execute_code` is often better.
- Do not assume the agent can self-approve to Done on a multi-agent epic. `agent:peer-review-blocked` is required.