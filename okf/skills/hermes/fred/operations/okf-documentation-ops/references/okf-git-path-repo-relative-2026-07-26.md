---
type: Reference
title: OKF git_path convention — repo-relative, not OKF-relative
description: Frontmatter git_path must be repo-relative (okf/...) not OKF-relative (no okf/ prefix). Verifier must match the same convention.
resource: operations/okf-documentation-ops/references/okf-git-path-repo-relative-2026-07-26.md
git_path: operations/okf-documentation-ops/references/okf-git-path-repo-relative-2026-07-26.md
tags: [okf, frontmatter, git_path, verifier]
timestamp: 2026-07-26
linear_issue: pending
git_repo: growthwebdev-knowledge
last_verified: 2026-07-26
verified_by: fred (ad hoc targeted verification, not suite green)
status: active
---

# OKF `git_path` Convention — Repo-Relative, Not OKF-Relative

## The rule

`git_path` and `resource` in OKF frontmatter are **repo-relative paths**, not OKF-relative.

| Doc location on disk | `git_path` value | `resource` value |
|---|---|---|
| `Hermes-Research/okf/projects/journal-pe-integration/index.md` | `okf/projects/journal-pe-integration/index.md` | `okf/projects/journal-pe-integration/index.md` |
| `Hermes-Research/okf/standards/foo.md` | `okf/standards/foo.md` | `okf/standards/foo.md` |
| `Hermes-Research/okf/index.md` | `okf/index.md` | `okf/index.md` |

If you omit the `okf/` prefix, the file is no longer discoverable from the repo root, and future agents inspecting the hub repo cannot find it.

## Why this bites the verifier

When you write a `/tmp/hermes-verify-*.py` (or inline execute_code) verifier, the natural way to assert `git_path` matches the file location is to walk the OKF tree and compare. There are two conventions you might use:

```python
# WRONG — OKF-relative convention
expected = rel  # e.g. "projects/journal-pe-integration/index.md"
assert fm["git_path"] == expected  # ALWAYS FAILS for correctly-written docs

# RIGHT — repo-relative convention
expected = f"okf/{rel}"  # e.g. "okf/projects/journal-pe-integration/index.md"
assert fm["git_path"] == expected  # matches docs written to the rule
```

The 2026-07-26 session hit this: the first verifier reported 13 spurious failures, all on the `git_path` field. The fix was to compute the expected value with `f"okf/{rel}"`.

## Same rule for `resource`

`resource` should end with the repo-relative path:

```yaml
resource: okf/projects/journal-pe-integration/index.md
```

Not:

```yaml
resource: projects/journal-pe-integration/index.md  # missing okf/ prefix
```

## How to detect the convention drift in bulk

A grep pattern that finds inconsistent docs:

```bash
# In every OKF doc, find frontmatter git_path lines that don't start with "okf/"
grep -rE '^git_path:' /home/ubuntu/work/Hermes-Research/okf/ \
  | grep -vE 'git_path: okf/' \
  | head
```

## Pitfalls

- **Do not write `git_path: projects/...`** thinking the OKF folder is the "root." The repo root is the repo root; OKF is just one directory inside it.
- **Do not write a verifier that checks `git_path == rel`** where `rel` is the OKF-relative walk path. The right comparison is `git_path == f"okf/{rel}"`.
- **Do not strip the `okf/` prefix from existing docs without re-verifying links.** Some index docs may have been written with the OKF-relative convention on purpose; check before bulk-renaming.

## Verification boundary

Ad hoc targeted verification only — not full docs-suite green. This pattern is validated by the 2026-07-26 Journal PE Integration session, where the verifier initially reported 13 spurious failures until the convention was corrected.