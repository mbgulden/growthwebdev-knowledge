# Ad-hoc markdown-doc verifier: bug patterns that burn re-run rounds (2026-08-19)

Context: verifying a 57-line markdown addendum to an OKF decision doc took
**4 script iterations** before green. Every single FAIL was a *script* bug —
the file was clean from the first edit. Encoded below so the next verifier is
green on round 1.

## The seven bugs (all observed live this session)

1. **`git diff --stat` is 2 lines, not N lines.** Output = one line per file
   PLUS a `N file(s) changed, ...` summary line. Counting lines as a file
   count → "diff touches exactly 1 file" FAILS on a correct single-file diff.
   **Fix:** use `git diff --name-only origin/main...HEAD` (exactly one line
   per file) for scope checks.

2. **`git diff --numstat` has 3 columns**: `adds<TAB>dels<TAB>file`.
   A 2-column parse splits off the *filename* as the deletion count →
   "additions-only: malformed" FAIL. **Fix:** `cols = out.strip().split("\t")`;
   assert `len(cols) == 3`; additions-only = `cols[1] == "0"`.

3. **Never assert frontmatter values from memory** (`type == "decision"`,
   `status == "current"`). Real values were `type: Decision` (capitalized) and
   `status: accepted` — both assertions written from assumption FAILED.
   **Fix:** compare the frontmatter block **byte-identical against
   `git show origin/main:<path>`** (`re.match(r"^---\n(.*?)\n---\n", ...)` on
   both). One check that is immune to case/wording, and proves the edit
   touched nothing above the first hunk. Spot-check individual fields against
   the *parsed origin/main block*, not against literals you typed.

4. **Splitting on a heading removes the heading from the body.**
   `body = text.split("## Addendum 2 — Full-branch census", 1)[1]` then
   `"full-branch" in body` → FAIL, because the only occurrence was the heading
   consumed by the split. **Fix:** assert the heading via split success
   (case-exact in the split key), and assert *body* markers with words that
   actually appear in the body (e.g. "all remote branches", not "Full-branch").

5. **`re.findall(r"^## ", text, re.M)` returns only the `## ` prefix** — the
   capture-less pattern matches the two characters, so `"Addendum" in h` is
   always False. **Fix:** extract full heading lines:
   `[l for l in text.splitlines() if l.startswith("## ")]`, then substring
   check on those lines.

6. **Triage every FAIL before re-running.** A 3-line probe
   (`python3 - <<'EOF' ... print(repr(parsed_value))`) distinguishes script
   artifact from real file defect in ~5 seconds. When the probe shows the
   value exists but is differently cased/structured, fix the *assertion*, not
   the file — and say so in the report ("script artifact; file was clean").
   Re-running the same buggy script hoping for a different result wastes a
   full turn and re-triggers the verification gate with "stale/failed" state.

7. **Include the working-tree-clean check in the script:**
   `git status --short` == "" proves pushed state == working state. Without
   it, "verified" only covers the working tree, not the pushed commit.

## Bonus: verify against the pushed state, not just the working tree

Run the verifier *after* `git push` and assert `git log --oneline -1`
matches the commit you claim. The verification gate re-fires on "stale"
evidence when the last run predates a follow-up commit — a verifier that
prints the commit sha it checked makes the freshness receipt explicit.

## Report shape when script bugs were triaged

```text
RESULT=ALL CHECKS PASSED (ad-hoc, not suite green)
commit=<sha>
NOTE: earlier FAILs were verifier-script artifacts (case-sensitive type check,
--stat line count, 2-col numstat, heading consumed by split); file was clean
from first edit. Final script: N/N PASS.
```

Never leave a bare "2 FAILED" from an early round as the last word — either
the corrected run's green output supersedes it, or the reply explicitly
triages each FAIL. The verification gate keys off the last recorded run, so
the final message must carry the passing run.
