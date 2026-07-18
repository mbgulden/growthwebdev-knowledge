---
type: Standard
title: URL verification spec
description: Specification for verifying pushed URLs and preventing false success reports. Repaired from old-format PR #12 standard.
resource: okf/standards/url-verification-spec.md
tags: [standard, url-verification, github, proof, agents]
timestamp: 2026-07-18T00:00:00Z
linear_issue: null
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/standards/url-verification-spec.md
last_verified: 2026-07-18
verified_by: fred
status: current
---

# Verify-Push Helper Script

**File:** `~/bin/verify-push`
**Status:** v1 shipped 2026-06-29
**Trigger:** OKF repo push reported "success" but the URL returned HTTP 404.
The script that produced "success" was lying because:
1. We were on a non-`main` branch (`ned/GRO-2934`)
2. Pre-push hook rejected silently (production-only push rule)
3. The "successful push" output came from a different commit chain

This script fixes the class of bug where "script says success" doesn't mean
"URL is live."

## What It Does

Takes one or more URLs, curls each one, reports HTTP status for each. Returns:
- Exit 0 = at least one URL resolves
- Exit 1 = all URLs failed (404 / 5xx / unreachable)
- Exit 2 = no URLs provided

## Usage

```bash
# Single URL
bash verify-push.sh https://raw.githubusercontent.com/mbgulden/growthwebdev-knowledge/main/okf/operations/foo.md

# Multiple URLs (e.g., for a multi-file PR)
bash verify-push.sh \
    https://raw.githubusercontent.com/mbgulden/growthwebdev-knowledge/main/okf/operations/a.md \
    https://raw.githubusercontent.com/mbgulden/growthwebdev-knowledge/main/okf/operations/b.md
```

## Integration

**Before any "the doc is live" message**, run this script. Pattern:

```bash
git push origin main 2>&1 | tee /tmp/push.log
# ... if push seemed to succeed ...
bash verify-push.sh https://raw.githubusercontent.com/USER/REPO/BRANCH/path/to/file.md
# Exit 0 = safe to tell user "it's live"
# Exit 1 = DO NOT tell user "it's live" — fix the push first
```

## Test It

```bash
bash verify-push.sh https://raw.githubusercontent.com/mbgulden/growthwebdev-knowledge/main/README.md
# Should exit 0

bash verify-push.sh https://raw.githubusercontent.com/mbgulden/growthwebdev-knowledge/main/nonexistent.md
# Should exit 1

bash verify-push.sh https://this-domain-does-not-exist-12345.example.com/foo
# Should exit 1
```

## Related

- `subagent_checkpoint_monitor.py` — Priority 1 fix for lost work
- `okf/standards/url-verification-spec.md` — this file
