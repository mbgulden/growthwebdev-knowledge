# AOT five-move ops run — 2026-07-07

Condensed reusable lessons from a long Active Oahu Tours operations run.

## PR / Linear reconciliation

When reconciling stale `[PR REVIEW]` Linear items:

1. Check live GitHub PR state with `gh pr view <n> --json state,mergedAt,closed,mergeable,mergeStateStatus,url,files`.
2. If `MERGED`, do route/artifact verification, comment Linear with exact evidence, then move the review issue to Done.
3. If `CLOSED` unmerged, classify as superseded/no-longer-actionable; do not revive stale/conflicting branches through the review ticket.
4. If production behavior differs from the closed PR target, record the current production behavior and open a fresh implementation issue only if a behavior change is still desired.

## DNS / Cloudflare Pages gotcha

Do not verify only the apex domain. Always check both:

```bash
curl -sS -I -L https://activeoahutours.com/
curl -sS -I -L https://www.activeoahutours.com/
```

In this run the apex returned `200` but `www.activeoahutours.com` returned Cloudflare `522`. The durable fix was a Cloudflare Page Rule:

```text
www.activeoahutours.com/* -> https://activeoahutours.com/$1
status_code=301
```

After adding it, verify representative paths:

```text
https://www.activeoahutours.com/ -> 200 final=https://activeoahutours.com/ redirs=1
https://www.activeoahutours.com/contact-us/ -> 200 final=https://activeoahutours.com/contact-us/ redirs=1
```

## Branch lane constraints

Prismatic pre-push checks enforce branch prefix lanes:

- `content/` -> Kai lane; acceptable for `site/`, `scripts/`, content/site implementation.
- `feature/` -> Fred lane; acceptable for governance docs, audits, reports, and operations artifacts.

If a push fails because a Kai branch touched governance files (`docs/`, `audits/`, `reports/branch-drift/`), rename/open the branch as `feature/...` rather than bypassing the hook.

## Clean-worktree pattern

For long AOT runs with multiple unrelated outputs, avoid mixing changes in `active-oahu-tours-mirror-1251`.

Preferred pattern:

```bash
git worktree add -b content/<issue-slug> /home/ubuntu/work/<purpose> origin/main
# copy/generate only the scoped files into that worktree
# verify, commit, push, open PR
```

Then clean transient copies from the original mixed worktree and verify the guard-reported paths are clean with:

```bash
git status --short -- <path1> <path2>
```

## Verification guard pattern

When the system reports changed paths but the actual deliverable lives in clean PR worktrees, create `/tmp/hermes-verify-*.py` that checks both:

1. The reported original-worktree paths are clean or intentionally absent after cleanup.
2. The PR worktree contains the intended behavior/artifacts.

Example checks:

- Governance PR: staging-first checklist exists, no-direct-production rule exists, audit/drift reports exist.
- Mobile CTA PR: helper script exists and `py_compile`s; each target page has exactly one CTA marker, route mapping, analytics events, a11y/breakpoint strings.

Label the result as focused ad-hoc verification, not canonical suite green.

## Media / Synology imagery pipeline

For AOT imagery foundation work:

- Existing source metadata artifacts may live under `/mnt/synology-agentic-context/active-oahu/metadata/`.
- Keep NAS originals read-only.
- A metadata-only website candidate index can be safely stored in the private business repo (`active-oahu-business`) rather than the public deploy repo.
- Because the current inventory reports `Photos with GPS = 0`, mark every candidate as `candidate_only_requires_visual_location_subject_review` before publication.
- Before publishing an image as factual place/activity imagery, copy it out of NAS into a workspace and verify subject/location using source path, filename/shoot group, visual landmarks, and/or owner confirmation.
