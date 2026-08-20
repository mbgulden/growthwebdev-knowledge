---
name: peer-review-before-merge
description: Pattern for getting code peer-reviewed by an AI agent before merging. Use when shipping any non-trivial code change to the prismatic-engine repo. Triggers on "review this PR", "before I merge", "is this code ready", "peer review pattern", or when opening a Phase 2/3 PR.
---

# Peer Review Before Merge — How to Ship Quality Code via Claude

## When to use

Use this pattern when:
- You have a PR open on `mbgulden/prismatic-engine` (or any prismatic-engine fork)
- The PR contains code changes (not just docs)
- You want a real AI review before merging
- You want to catch security bugs, logic errors, and design issues before they reach `deploy-fresh`

This pattern worked successfully across 5 PRs in Phase 2 (Gaps 4, 5, 7, 8). It surfaces 2-3 critical/high bugs per PR on average that would have shipped otherwise.

## Why it works

- **claude-sonnet-4-6 has different blind spots than me** — it catches regex ReDoS, path traversal, race conditions, docstring lies, false tests, severity-handling gaps, and missing exports
- **Two rounds of review** (initial + re-review after fixes) dramatically improves code quality
- **Reviews are reproducible** — same PR + same prompt ≈ same findings
- **Cost is low** — ~10-15K tokens per review cycle, well worth catching real bugs

## The 6-step pattern

### Step 1: Open the PR

```bash
gh pr create --repo mbgulden/prismatic-engine \
  --base deploy-fresh \
  --head <your-branch> \
  --title "[Phase X / Gap Y] <short description>" \
  --body "<markdown description>"
```

PR body should include:
- Reference to the plan doc (e.g. `okf/operations/plan.md`)
- List of what changed (files + LOC)
- Honest caveats — what you didn't do, what might be broken
- Test count and pass rate
- A "Request" section listing what to focus the review on (edge cases, design choices, etc.)

### Step 2: Write the initial review prompt

Save to `/tmp/review_pr_NN.md` where NN is the PR number. Template:

```markdown
You are a senior code reviewer for the Prismatic Engine. Review PR #NN:
https://github.com/mbgulden/prismatic-engine/pull/NN

<One-paragraph context: what does this PR do?>

Repository root: /home/ubuntu/work/prismatic-engine

### What was added

<Bulleted list of files with brief descriptions>

### Review against these criteria

- Correctness: <specific claim to verify>
- Edge cases: <list of edge cases to probe>
- Security: <specific security checks>
- Test coverage: <what should be tested>
- API design: <ergonomics questions>
- Integration: <how does it interact with existing code>

### Steps

1. cd /home/ubuntu/work/prismatic-engine && git fetch origin <branch>
2. git checkout <branch>
3. Read the files
4. Run tests: python3 -m pytest <test_path> -v
5. <Specific probes to run>
6. Check the public API surface (verify __all__ in __init__.py matches imports)
7. Write a verdict

### Output format

## Review Verdict: <APPROVE|REQUEST_CHANGES|NEEDS_DISCUSSION>

### Strengths
- bullet 1

### Issues Found
- bullet 1 (severity: critical/high/medium/low)

### Recommendation
- one paragraph

Be thorough but pragmatic. Catch real bugs.
```

### Step 3: Run the review

```bash
cd /home/ubuntu/work/prismatic-engine
agy --model claude-sonnet-4-6 --dangerously-skip-permissions \
  -p "$(cat /tmp/review_pr_NN.md)" 2>&1 | tail -100
```

Output ends with `## Review Verdict: <APPROVE|REQUEST_CHANGES|NEEDS_DISCUSSION>` followed by findings.

**The full review is saved to a path like** `~/.gemini/antigravity-cli/brain/<id>/prNN_review.md`. Copy it to `okf/operations/prNN-review-feedback.md` for the record.

### Step 4: Post the verdict to the PR

Use the **`prismatic-engine-review-bot`** GitHub App to post the review
(so GitHub accepts approvals from agents other than you). The token
fetcher is at `/home/ubuntu/bin/prismatic-engine-bot-token`.

```bash
# One-time setup (you do this, not the agent):
#   1. Create the App at https://github.com/settings/apps/new
#   2. Install on mbgulden/prismatic-engine only
#   3. Save credentials to ~/.config/prismatic-engine-bot.env:
#        export GH_APP_ID=YOUR_APP_ID
#        export GH_INSTALLATION_ID=YOUR_INSTALLATION_ID
#        export GH_APP_PEM_PATH=$HOME/.config/gh/prismatic-engine-review-bot.pem
#   4. chmod 600 ~/.config/prismatic-engine-bot.env

# Then post the review (the bot token replaces your mbgulden token):
export GH_TOKEN=$(prismatic-bot)  # short alias for /home/ubuntu/bin/prismatic-bot

# Approve (only valid when fixes have been pushed and re-review passed):
gh pr review <NN> --repo mbgulden/prismatic-engine --approve --body "<verdict summary>"

# Or request changes:
gh pr review <NN> --repo mbgulden/prismatic-engine --request-changes --body "<verdict summary>"

# Or just comment (no approve/request-changes):
gh pr comment <NN> --repo mbgulden/prismatic-engine --body "<verdict summary>"
```

**Why the bot exists:** GitHub blocks a user from approving their own PR
("Review Can not approve your own pull request"). When you (Michael)
push the code, the bot must be the second reviewer — otherwise we have
to fall back to the "post comment + merge" workaround documented in
PR #46 history.

### Step 5: Fix or merge

**If `APPROVE`:** merge with `gh pr merge <NN> --repo mbgulden/prismatic-engine --squash --delete-branch`

**If `REQUEST_CHANGES`:**
1. Save the review feedback to `okf/operations/prNN-review-feedback.md`
2. Address each finding. **Severity order matters:**
   - **critical/high**: must fix before merge (e.g. false-safe in security path)
   - **medium**: should fix; can acknowledge if fix would require big architectural change
   - **low**: nice-to-have; fix if cheap, otherwise track as follow-up
3. **For acknowledged findings (medium that needs big fix):** document honestly in the commit message — "Bug N (medium, X): NOT FIXED in this commit — would require Y. Tracked as known limitation." Don't paper over.
4. Add regression tests for any bug found (the test should fail without the fix)
5. Run tests: `python3 -m pytest <test_path> -v`
6. Run full suite to confirm no regressions: `python3 -m pytest prismatic/`
7. Commit fixes: `git -c user.email=fred@growthwebdev.com -c user.name="Fred" commit -am "<fix description>"`
8. Push: `git push origin <branch>`
9. Go to Step 6 (re-review)

### Step 6: Re-review focused on fixes

Save a re-review prompt to `/tmp/rereview_pr_NN.md`:

```markdown
You are a senior code reviewer for the Prismatic Engine. This is a RE-REVIEW of PR #NN:
https://github.com/mbgulden/prismatic-engine/pull/NN

The initial review returned REQUEST_CHANGES with N findings. The author has
committed fixes. Your job: verify the fixes are correct and surface any
remaining issues.

Repository root: /home/ubuntu/work/prismatic-engine
Branch: <branch>
Latest commit: <hash>

### Initial findings (must verify fixes)

<For each finding from initial review:>

- **ISSUE-N (severity):** <description>
  Fix: <what the author claims to have done>
  Verify: <how to confirm the fix works>

### Steps

1. cd /home/ubuntu/work/prismatic-engine && git fetch origin <branch>
2. git checkout <branch>
3. git log --oneline -3
4. Read <relevant files>
5. Run tests: python3 -m pytest <test_path> -v
6. Live probe: <specific Python one-liner to verify>
7. Edge cases to probe: <list>
8. Surface any NEW issues introduced by the fixes

### Output format

## Review Verdict: <APPROVE|REQUEST_CHANGES|NEEDS_DISCUSSION>

### Verification of Initial Findings
- ISSUE-N: <FIXED / NOT FIXED / PARTIALLY FIXED> — one sentence

### New Issues Introduced
- bullet (severity: critical/high/medium/low) — only if real

### Strengths
- bullet

### Recommendation
- one paragraph

Be honest. If all findings are fixed and no new critical/high issues, say APPROVE.
```

**Re-review finding types:**
- **"FIXED"** — clean fix, no new issues
- **"PARTIALLY FIXED"** — partial fix + new issue introduced by the patch (common!)
- **"NOT FIXED"** — author thought they fixed but didn't
- **"ACKNOWLEDGED"** — author documented non-fix honestly

**Re-reviews frequently surface NEW LOW findings** even after all initial findings are addressed. These are non-blockers but worth fixing in a follow-up commit before merge (e.g. PR #39's lock-scope was technically correct but the docstring overstated it — fixed in a follow-up commit).

**If re-review returns APPROVE:** merge immediately.

**If re-review returns REQUEST_CHANGES with new findings:** address them, commit, push, then run a SECOND re-review. Don't loop more than 3 times — if findings keep recurring, merge with a follow-up Linear issue instead.

## Probes that catch real bugs

These patterns have caught issues in past reviews:

### Path traversal probes
```python
# Run after writing any path-check code
from prismatic.quality import check_workdir
result = check_workdir(['prismatic/quality/../../etc/passwd'], 'prismatic/quality')
assert not result.passed, 'BUG NOT FIXED'
```

### ReDoS probes
```python
import time
huge_input = "pattern_here\n" * 10000
start = time.time()
for _ in range(100):
    my_function(huge_input)
elapsed = time.time() - start
assert elapsed < 5.0, 'Too slow — possible ReDoS'
```

### False-test detection
```bash
# Search for tests that don't actually test what they claim
grep -rn "def test_.*_persists_to_disk" tests/ | xargs grep -L "assert.*exists\|assert.*open\|assert.*read"
```

### Docstring lie detection
```python
# For every function, check docstring vs implementation
import ast
tree = ast.parse(open('module.py').read())
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        doc = ast.get_docstring(node)
        # Compare doc claim with actual behavior
```

### Counter race condition check
```bash
# Look for file-based counters without locking
grep -rn "json.dump\|_save_counter" scripts/ | grep -v "fcntl\|LOCK_EX"
```

### Severity-handling gaps (Gap 4 lesson)
```python
# When adding new severity levels, ALWAYS add a test case for that level
# to TestComputeVerdict or equivalent — without it, the level may
# silently produce wrong verdicts (e.g. medium → APPROVE).
result = compute_verdict([QualityFinding(severity="new_level", ...)])
assert result.verdict == EXPECTED  # not silent-fallthrough
```

### Public API completeness check
```python
# After adding new constants/symbols to a module:
from prismatic.<module> import (
    <new_constant_1>, <new_constant_2>, ...  # every new public symbol
)
# If any ImportError: update __init__.py
```

## Honest caveats

1. **Reviews take 3-5 minutes** — not instant. Plan accordingly.
2. **Claude sometimes hallucinates** the response (says it ran tests when it didn't). Always verify by reading the review artifact at `~/.gemini/antigravity-cli/brain/<id>/prNN_review.md`.
3. **GitHub API limitations (mitigated via bot):** `gh pr review --approve`
   fails with "Can't approve your own PR" when run as `mbgulden`. The
   fix is the **`prismatic-engine-review-bot`** GitHub App — its
   installation token is what we pass to `gh` via `GH_TOKEN=$(prismatic-bot)`.
   See Step 4 for setup. With the bot in place, PRs get a real ✅
   APPROVE badge from a non-author identity.
4. **Reviews don't catch everything** — they catch code bugs, not design issues. Architecture review still needs Michael.
5. **Re-reviews can have findings the initial missed** — this is normal. Don't be alarmed; budget time for a follow-up commit.
6. **Cost is real** — ~10-15K tokens per review. Worth it for critical code, but don't review every PR.

## Examples

- **PR #33 (Phase 1 Quality Gates):** REQUEST_CHANGES → 9 findings → all fixed → APPROVED → MERGED
- **PR #35 (Phase 2 Gap 7 Failure Classification):** REQUEST_CHANGES → 8 findings → all fixed → APPROVED → MERGED
- **PR #36 (Phase 2 Gap 5 Smoke Test):** REQUEST_CHANGES → 3 findings → all fixed → APPROVED → MERGED
- **PR #38 (Phase 2 Gap 4 Real PR Reviewer):** REQUEST_CHANGES → 4 findings (1 critical + 1 high + 2 medium) → 3 fixed, 1 acknowledged → APPROVED → MERGED
- **PR #39 (Phase 2 Gap 8 Pipeline Orchestrator):** REQUEST_CHANGES → 4 findings → all fixed → re-review surfaced 1 LOW follow-up (lock-scope narrower than docstring claimed) → fixed in follow-up commit → APPROVED → MERGED

## Related skills

- `second-opinion-on-design` — design question reviews
- `push-protection-secret-fixtures` — when push protection blocks fixtures
- `prismatic-phase2-quality-gates-shipped` — Lessons A-L from actual Phase 2 implementation; Lesson H captures the test-name-vs-assertion pattern
- `autonomous-execution-discipline.md` — when to act vs ask
