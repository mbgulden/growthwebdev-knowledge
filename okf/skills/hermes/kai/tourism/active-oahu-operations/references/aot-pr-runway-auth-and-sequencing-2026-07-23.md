# AOT PR Runway: Auth Recovery and Safe Sequencing

## Use case

Reconciling and merging several stale public-mirror PRs where CLI auth is unreliable, PR branches overlap, and Cloudflare Pages must be checked after each merge.

## Safe credential-health pattern

1. Never print, copy into chat, or write a token to a repo/config file.
2. Test candidate credentials only in memory with `GET https://api.github.com/user`; report only valid/invalid and account login.
3. `gh` prioritizes `GH_TOKEN`. An invalid `GH_TOKEN` can shadow a valid GitHub credential/token available elsewhere in the same process.
4. For an individual safe GitHub operation, launch `gh` from a Python subprocess environment that removes `GH_TOKEN` / `GITHUB_TOKEN` and sets `GH_TOKEN` from the already-authorized process credential. Do not persist the override.
5. Confirm the identity with `gh api user --jq .login`, then use normal `gh pr view` / `gh pr merge` commands.

Example (do not log token values):

```python
import os, subprocess
for key in ("GH_TOKEN", "GITHUB_TOKEN"):
    os.environ.pop(key, None)
os.environ["GH_TOKEN"] = os.environ["GITHUB_PAT_KEY"]
subprocess.run(["gh", "pr", "view", "<number>", "--repo", "mbgulden/active-oahu-tours-mirror"], check=True, env=os.environ)
```

## Sequential stale-PR reconciliation

Before each merge:

1. Fetch `main` and the PR head into a clean temporary checkout.
2. Inspect `gh pr view` checks, changed files, diff stat, and `git diff --check`.
3. For bulk HTML tooling, inspect the implementation. Only approve an HTMLParser/DOM-aware approach; do not merge regex-based HTML rewrite scripts, even when their PR checks are green.
4. Run the PR's idempotence check if it has one, plus a narrow behavior verifier against its changed contract.
5. Test against **current** main with `git merge-tree --write-tree main review/pr-<n>` before merging. A GitHub `mergeable: UNKNOWN` result is not a pass; it often needs current-main reconciliation.
6. Merge only clean, scoped PRs. After every merge, fetch/reset the review checkout to `origin/main` and rerun merge-tree for all remaining PRs—the conflict topology changes after each merge.

### Conflict handling

- If a stale PR conflicts across many static-export files, do not force/rebase it in place just to clear a queue.
- Keep its value alive by opening a fresh successor branch from current `main`, porting only verified changes, and closing the stale PR as superseded only after that successor exists.
- If two PRs overlap in a generated script or hundreds of exported pages, merge the smallest safe/non-overlapping fix first, then reassess the broader PRs.

## Deployment verification

- Wait for Pages propagation and verify both `https://activeoahutours.com/` and `https://active-oahu-tours-mirror.pages.dev/`.
- Verify semantic output, not a brittle exact HTML substring whose attribute order/class list can vary. Fetch body with curl and parse it when checking link targets, image attributes, sitemap entries, or visible copy.
- For sitemap/robots changes, verify: `Sitemap:` directive, XML parses, 404 URLs are absent, and both production and mirror serve the expected result.
- For static image dimension fixes, use HTMLParser against affected pages and verify intrinsic file dimensions with Pillow; then check a production page containing the target asset.

## Compact proof packet

Report each merge with PR URL, merge commit, focused local verification, production/mirror verification, and explicit boundaries. Do not call the full site or full Lighthouse suite green unless it actually ran.
