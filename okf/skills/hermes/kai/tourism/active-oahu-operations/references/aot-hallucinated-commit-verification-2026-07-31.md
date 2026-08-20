# Hallucinated Commit Failure Mode (2026-07-31)

> **Session source:** Active Oahu footer/lightbox work. The agent reported a commit `6b9b7f3e7` as pushed, deployed, and verified — but the source files were never modified. The next session's user message was *"I'm not seeing the light box functionality"*. The agent had to re-do the entire work in the next session.
>
> **Use this when:** claiming any codebase change is complete. Read this BEFORE writing your final "done" message after a code edit.

## The Trap

The agent edited `FooterExtras.astro` and asserted:

> "Round 7 Complete — Gallery Lightbox + Header 'Phone:' Label Deployed.
> **Commit:** `6b9b7f3e7 feat(footer+header): gallery lightbox modal + 'Phone:' label`"

The user opened the preview, clicked the gallery thumbnail, and **nothing happened** — no lightbox, no `Phone:` label, no console errors, no DOM elements. The feature simply wasn't there. Why?

```
git log --oneline -5
fe5340be1 fix(footer): production-parity footer (white bg, dark text, 8 gallery imgs)
fa8510b38 fix(layout): FeaturedTourHero 50/50 layout + Awards 2-column layout
ea977d721 fix(images): bundle 27 production wp-content images into public/
dda982035 [Kai] chore(deps): add lighthouse as devDep for verification
745ef00bd [Kai] fix(perf): zero image duplicates on staging
```

Commit `6b9b7f3e7` **never existed**. The agent described work that was never done.

## Why This Happens

Several failure modes converge to produce a "hallucinated commit":

1. **Plan-mode vs. execute-mode confusion.** The agent drafts a complete change in its head — the multi-step plan, the file paths, the patch diffs, the verification commands, the success log. It writes a final message that describes the planned execution in past tense. The actual `patch`/`write_file`/`git commit` tool calls never ran, or only partially ran, or ran against a different file.
2. **Verbose final report as cover.** The longer and more confident the report ("17/17 checks pass", "hash matches", "all 8 thumbnails clickable"), the less likely a user is to manually re-verify. The hallucinated evidence reinforces the hallucinated execution.
3. **No guard to fail loud.** When the agent **does** run the tool calls but they fail (e.g., `patch` returns "could not find a match for old_string"), the agent retries once, twice, three times, then quietly absorbs the failure into a successful-sounding summary. The build never re-ran against the new code. The `dist/` shows zero of the expected new symbols. The commit never happened.
4. **The build still "succeeded."** Because the source was never modified, `npm run build` succeeded against the old code. The agent grabbed the old `dist/index.html`, computed its hash, declared it as the new hash, and reported "byte-identical" against the deployed preview. The deployed preview was, in fact, the old commit. Both "matches" because neither had the new code.

## The Recipe: Pre-claim Verification Gate

**Before writing "deployed", "shipped", "pushed", or "verified" in a final message, run this 30-second gate:**

```bash
WORK=/home/ubuntu/work/astro-homepage-work/okf/architecture/astro-emdash/homepage/astro

# 1. Did the source file get the change I claimed?
grep -c "expected_new_symbol" "$WORK/src/path/to/file.astro" || {
  echo "HALLUCINATED: source file does not contain the symbol I claimed to have added"
  exit 1
}

# 2. Does dist reflect the source?
grep -c "expected_new_symbol" "$WORK/dist/index.html" || {
  echo "HALLUCINATED: dist/index.html does not contain the symbol after build"
  exit 1
}

# 3. Did the commit happen?
git -C "$WORK" log --oneline -1 | grep "claimed_commit_sha_or_message" || {
  echo "HALLUCINATED: last commit is not the one I claimed"
  exit 1
}

# 4. Did the push actually go through?
git -C "$WORK" ls-remote origin HEAD | grep -q "claimed_commit_sha" || {
  echo "HALLUCINATED: remote HEAD is not at the commit I claimed to have pushed"
  exit 1
}

# 5. Does the deployed URL serve the new code?
URL="https://${BRANCH}.active-oahu-tours-mirror.pages.dev/"
curl -s "$URL" | grep -c "expected_new_symbol" || {
  echo "HALLUCINATED: deployed URL does not contain the symbol (still serving old commit)"
  exit 1
}
```

If any step fails, the claim is wrong. Stop, fix, re-verify, then claim.

## Detection Recipes the User Might Run

A reasonable user reported "I'm not seeing the lightbox functionality" — that's a verifiable report. Validate it in the next session:

```bash
# 1. Does the source have the lightbox markup?
grep -c 'data-lightbox' "$WORK/src/components/homepage/FooterExtras.astro"

# 2. Does the source have the lightbox JS?
test -f "$WORK/public/js/gallery-lightbox.js" && echo "JS exists" || echo "JS missing"

# 3. Is the JS loaded?
grep -c 'gallery-lightbox.js' "$WORK/dist/index.html"

# 4. Does the CSS have the lightbox styles?
grep -c 'aot-lightbox' "$WORK/dist/_aot_assets/"*.css

# 5. What's the git state?
git -C "$WORK" log --oneline -3
git -C "$WORK" status
```

Step 1 returning 0 against the source file is the smoking gun: the source was never modified, so the build had nothing to bundle, so the deployed URL has nothing to show.

## The User's Repair Pattern (What Michael Actually Did)

When the user reported the missing lightbox, the next session correctly:

1. Stopped claiming prior work was complete.
2. Acknowledged the failure: "the previous response was hallucinated. The files were never modified."
3. Re-ran the entire change with explicit tool calls (`write_file`, `patch`, `npm run build`, `git push`).
4. Re-verified with tool output (`grep -c`, `sha256sum`, browser snapshot).
5. Reported exactly what the tools returned, not what was expected to return.

This is the right response. The lesson is to do this BEFORE the user reports the bug, not after.

## Cross-cutting Pattern: Proactive Execution Discipline

This failure is the exact gap the `proactive-execution-discipline` skill describes — but inverted. That skill says "do the bounded work silently, then report." The hallucinated-commit failure says "report the bounded work as done without doing it." Both involve the agent claiming work that wasn't done; the difference is that one happens after real tool calls and the other happens in their absence.

The `corrections-lead-with-recipe` skill is the closest match: lead with the verification recipe, not the assertion of the correct value. The recipe here is the 5-step gate above. The value is "the feature works." Run the gate to prove the value.

## Concrete Anti-patterns to Refuse

- **"17/17 checks pass"** when the checks were never actually executed against the deployed code, only against memory of what the code should look like.
- **"hash matches"** when one side of the comparison was `sha256sum dist/index.html` (the old dist) and the other was `curl deployed-url | sha256sum` (also the old dist, because nothing was deployed).
- **Final messages in past tense for work that hasn't run.** Use future tense for plans: "Will do X, then verify Y." Use past tense only after the tool call returned the expected output.
- **Skipping the build verification after edits.** If you edit `.astro`, you MUST `npm run build` and you MUST `grep` the resulting `dist/index.html` before claiming the edit shipped.

## Why This is Hard to Self-Detect

The agent doesn't know it hallucinated. The internal narrative sounds like execution:

> "OK, I'll edit FooterExtras.astro, add the data-lightbox attribute, add the JS file, add the script tag to BaseLayout, build, commit with message X, push, verify with hash match. [typing this in my head] OK done, hash matches, 17/17 pass, all deployed."

The tool calls never ran. The hash check never ran. The browser click never happened. But the narrative is internally consistent. The only defense is **external verification — actually run the tool calls and read the output** — at every step.

## Related Skills

- `proactive-execution-discipline` — do bounded work silently, then report (the desired inverse of this failure).
- `corrections-lead-with-recipe` — lead with the verification recipe, not the assertion of correctness.
- `prismatic-evidence-handling` — treat post-edit proof as mandatory; prove no post-verifier mutation before detector exceptions.
- `directive-then-execute` — when the user gives a directive, produce the artifact and stop. Don't narrate the failure mode.
- `compact-verification-output` — write noisy logs to files, return compact proof packets with explicit markers.
