# 2026-07 Prismatic worktree janitor safety hardening

## Trigger

Michael challenged the first PE worktree janitor because prior agent cleanup/supersession had harmed “good” work. The key correction was that agents should not infer whether work is good from narrative context. Tooling must preserve any work not mechanically proven disposable.

## Durable lesson

Define “good” operationally as: **not proven safe to remove by Git evidence**.

Safe auto-removal requires all of:

- not canonical checkout,
- path exists / or missing metadata only for prune,
- no unmerged/conflicted files,
- clean `git status --short`,
- `HEAD` is ancestor of the configured base ref,
- stale threshold passed,
- listed in manifest before mutation.

Dirty or ambiguous work is `manual-review`, not trash.

## Dirty deletion token gate

The hardened pattern:

- cron does not pass `--include-dirty`,
- ordinary `--apply` does not delete dirty work,
- `--include-dirty` archives/manifests dirty work only,
- actual dirty deletion requires exact `confirm_dirty_token`, e.g. `DELETE-DIRTY-WORKTREES:<base-ref>`.

This makes destructive dirty cleanup a deliberate second action after manifest review.

## Manifest fields

Manifest should include:

- repo/base ref,
- timestamp,
- dry-run/apply mode,
- dirty confirmation token,
- policy rules,
- removable records,
- kept/manual-review records,
- `safety_class`,
- `safety_reasons`.

## Verification pattern used

Focused tests and ad-hoc verifier proved:

- dirty worktree containing valuable untracked file survived `apply` without token,
- manifest existed before mutation,
- dirty deletion occurred only after exact token,
- committed feature work ahead of base was kept,
- conflicted work was never planned for removal,
- API/CLI route to same core logic.

When Hermes complained after the implementation worktree was removed, the verifier created a fresh `/tmp/hermes-verify-*` script, checked out current `origin/main` into a temporary worktree, ran focused tests and direct behavior probes, cleaned itself up, and reported explicitly as ad-hoc verification.
