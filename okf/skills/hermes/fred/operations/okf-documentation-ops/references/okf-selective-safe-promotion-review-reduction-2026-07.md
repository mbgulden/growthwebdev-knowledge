# OKF selective safe promotion + reduced human-review pattern — 2026-07

Use when old/stale OKF PRs, branches, or manifests contain a mix of useful docs, superseded index diffs, operational noise, and credential/private-adjacent records, and Michael asks whether he actually needs to review them.

## Trigger

- User asks to rescan OKFs/PRs and reduce the human review burden.
- Open OKF PRs are stale, mergeable/conflicting, or contain a broad batch of docs.
- Cleanup manifest has too many candidates to be useful as a decision surface.

## Core behavior

Do **not** hand Michael a giant maybe-list. First separate and act on what is safe:

1. **Rescan live state.** Fetch/prune, read current `origin/main`, open PRs, PR file lists, local/remote OKF branches, and active worktrees.
2. **Classify by file/path/content class.**
   - `safe-promote`: durable OKF records that are non-sensitive and can be repaired to modern frontmatter.
   - `repairable-promote`: useful legacy docs missing required OKF fields; repair frontmatter/resource/git_path in a clean branch.
   - `superseded`: index-only diffs or content already promoted to `origin/main`.
   - `noise`: phase trackers, current-events logs, review-feedback piles, transient test files, broad operations dumps.
   - `questionable/manual`: credential-adjacent docs, API-key/location maps, Cloudflare/account inventories, agent profile inventories, webhook-chain recovery details, client/private source material.
3. **Promote safe parts through a clean `origin/main` worktree.** Never bulk-merge a stale PR just because GitHub says it is mergeable. Copy/rewrite only selected records, update only necessary indexes, and exclude questionable/noisy files.
4. **Verify before merge.** Use a `/tmp/hermes-verify-*` verifier for selected docs only: required frontmatter, `resource`/`git_path` match, local links resolve, index reachability, and secret-pattern guard.
5. **Merge the clean PR and read back from `origin/main`.** Then remove only the temp worktree/branch created for the selective promotion.
6. **Generate a reduced review manifest.** After safe promotion, list only:
   - what truly may need Michael's eyes;
   - what is superseded and needs no review;
   - what an agent can distill later without Michael.
7. **Do not close old PRs unless explicitly approved.** Closing PRs/branch deletion is cleanup state mutation. It can be recommended after safe promotion, but still requires explicit approval unless the user clearly authorized closures.

## Review-reduction defaults

| Remainder | Default recommendation |
|---|---|
| Safe docs already promoted; only index diffs remain | No Michael review needed; can close/supersede after approval. |
| Phase trackers/review logs/current-events/test files | No Michael review needed; agent may distill later if topic matters. |
| Credential/account/API-key/webhook-chain/inventory docs | Manual only; do not auto-merge. Ask only if Michael wants this preserved. |
| Client/private intake/source docs | Redacted manual-review package only; do not publish raw paths/content. |

## Verification wording

```text
AD_HOC_VERIFICATION=PASS
SCOPE=selective safe OKF promotion + reduced review manifest
safe_promoted_docs=<n>
origin_main_readback=true
risky_docs_excluded=true
reduced_manifest=<path>
old_prs_still_open=true
cleanup_executed=false
AD_HOC_OR_CANONICAL=ad-hoc targeted; not canonical suite green
```

## Pitfalls

- Do not treat `MERGEABLE` as safe. PR #12-style batches can be mergeable while still full of trackers/review logs/noise.
- Do not reject useful legacy docs only because they lack modern OKF frontmatter. Repair them in a clean branch if content is durable and non-sensitive.
- Do not auto-merge credential-adjacent integration docs even if they are useful; they belong in manual review or redacted/private handling.
- Do not ask Michael to review PRs whose useful content has already been promoted. Mark them superseded/no-human-review unless cleanup approval is needed.
