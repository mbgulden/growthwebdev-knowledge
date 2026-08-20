# AOT Ad-Hoc Verification Guard Pattern

Use this when Hermes reports `Verification status: unverified` after AOT code/script/report edits and no canonical test/lint/build command was detected.

## Goal

Produce fresh, real verification evidence for the changed behavior without pretending a full suite passed. This is especially important for operational scripts and generated private reports where no project test harness exists.

## Pattern

1. **Create a temporary verifier under `/tmp` using an OS-safe tempfile path.**
   - Filename prefix must start with `hermes-verify-`.
   - Prefer Python `tempfile.mkstemp(prefix='hermes-verify-', suffix='-<topic>.py', dir='/tmp')` rather than hand-building a path.

2. **Verify the actual changed behavior, not just file existence.**
   Typical checks for AOT report/research scripts:
   - `py_compile.compile(..., doraise=True)` for changed Python files.
   - AST/text assertions for the specific bugfix or workflow behavior, e.g. Ubersuggest page tools use `{'page': url}` rather than `{'url': url}`.
   - Run deterministic render/transform scripts against existing fixture/raw data.
   - Assert expected output files exist, are non-empty, and contain key evidence strings.

3. **When two worktrees were involved, verify both.**
   - Exploratory/mixed worktree and clean PR worktree can drift.
   - Compile/run/check both roots when the guard lists changed paths in both.
   - For scripts copied between worktrees, assert script contents match exactly.
   - Generated reports may differ only because they include root-specific absolute paths; do not require byte-for-byte equality unless the generator is path-independent.

4. **Clean up transient artifacts.**
   - Remove the `/tmp/hermes-verify-*` script after running.
   - Remove generated `__pycache__/` directories before final status.
   - Re-run `git status --short` in the PR worktree to confirm no transient files remain.

5. **Report the scope honestly.**
   - Say “focused ad-hoc verification passed.”
   - Do **not** call it “full suite green” or “canonical tests passed” unless a real project suite/lint/build command also ran.

## Example checks to include

- Changed scripts compile.
- Repo-root detection is repo-relative (`Path(__file__).resolve().parents[1]`) and does not hard-code an exploratory path.
- Key API/tool arguments match the learned contract.
- Renderer writes under the current worktree root.
- Report/brief/PR body contain the expected evidence and caveat text.

## Repeated/exact-path guard pattern

When Hermes repeats an `unverified` prompt after a final report, treat it as a fresh requirement, not as something to argue away from prior evidence:

1. Create a brand-new `/tmp/hermes-verify-*` script with `tempfile.mkstemp`.
2. Include **every exact path** listed by the guard, including `/tmp/*-pr.md` PR body files and stale/legacy worktree paths.
3. If the work was already merged, compare flagged repo files against canonical `main` in the primary worktree to prove the flagged worktree matches what actually shipped.
4. If a verifier fails, classify the failure:
   - **Real implementation issue** — fix it, open/merge a small follow-up PR if the shipped repo needs the fix, then rerun verification.
   - **Verifier wording/marker mismatch** — inspect the file, update the verifier to match the actual wording while keeping the behavioral assertion, then rerun.
5. Do not weaken assertions just to pass. Keep checking the behavior the user cares about: generated output, idempotence, policy trigger presence, canonical-main parity, PR-body caveats, and no secret patterns.
6. Report the final passing run explicitly as focused ad-hoc verification, and mention any important failed-run lesson only if it changed the artifact or workflow.

## Pitfalls

- A verifier can mutate generated artifacts by re-running render scripts. If this happens, inspect whether the mutation is expected and commit/amend it if it belongs in the PR.
- `py_compile` creates `__pycache__`; always remove it before final status.
- A failed first verifier is useful evidence. Fix the verifier or the code, rerun, and only summarize the final passing run plus the important failure lesson.
- For document/policy checks, marker assertions must match real Markdown/case (`Do **not** force...` vs `Do not force...`) while still proving the intended doctrine exists.

## Git-diff / frontmatter assertion bugs that produce FALSE FAILs (2026-08-19, Phase 2 decision doc)

Three consecutive verifier versions against ONE clean markdown commit each failed on a script bug, not a doc bug. Before treating any verifier FAIL as a real problem, check it against this list:

1. **`git diff --numstat` is 3 columns** (adds, dels, file). Asserting 2 columns yields "malformed" on a perfectly good additions-only diff. Split on `\t`, expect `len == 3`, assert `cols[1] == "0"`.
2. **`git diff --stat` includes a summary line** (`1 file changed, 33 insertions(+)`). Counting lines from `--stat` overcounts changed files. Use `--name-only` for file-set checks.
3. **Case-sensitive marker checks.** File has `type: Decision`; asserting `"decision"` fails. Same for headings: `"full-branch"` in the body failed because the only occurrence is `## Addendum 2 — Full-branch census...`. Either match the exact string as written in the file, or compare case-insensitively.
4. **`re.findall(pattern)` returns the matched pattern text, not the surrounding heading.** `re.findall(r"## (.*)", text)` with a bad pattern returns the pattern's own captures — to inspect headings, iterate `line for line in text.splitlines() if line.startswith("## ")` and keep the full line.
5. **Splitting on a heading consumes the heading.** `text.split("## Addendum 2 — Full-branch census", 1)[1]` is the body WITHOUT that heading, so asserting a word that only appears in the heading (e.g. "Full-branch") against the body will fail. Assert body-only words (`"all remote branches"`) or search the un-split text.
6. **Frontmatter values need `.strip()`** — `l.split(":", 1)` leaves trailing whitespace on values; `==` comparisons then fail.
7. **The guard's "last output" may be from an OLDER script version.** The verification flag re-emits the last recorded run; if you've since re-run a corrected script, the flag text is stale. Confirm the displayed output matches your latest script before debugging a FAIL, and remember every new edit re-stales the flag — re-run after the final commit, not after an intermediate one.

Net effect on 2026-08-19: a +57/-0 additions-only doc change to one decision file needed 4 verifier iterations before a clean 12/12 green — 100% of the failures were assertion bugs, 0% were doc defects.
