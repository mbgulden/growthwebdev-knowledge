# AOT retired third-party artifact PR merge pattern — 2026-07-22

## Trigger

Use this pattern when an AOT PR removes legacy vendor artifacts from the static mirror, such as old Weglot scripts/styles/assets, retired widgets, or stale WordPress plugin exports.

## Key lesson

Separate **body artifact removal** from **edge/header policy cleanup**:

- Body scans should inspect rendered HTML/file contents for vendor tokens such as `weglot`, `cdn.weglot`, `wp-content/plugins/weglot`, or `wg_`.
- Header checks may still show vendor domains in Cloudflare-managed CSP/response-header transforms. That is real evidence, but it is a different layer from static mirror artifact removal. Do not treat CSP header references as proof the PR failed unless the PR was supposed to edit Cloudflare header rules.
- If headers still reference the retired vendor, record it as a separate edge-header/CSP follow-up.

## Review + merge sequence

1. Confirm PR state live:

```bash
gh pr view <PR> --repo mbgulden/active-oahu-tours-mirror \
  --json number,title,state,isDraft,mergeable,mergeStateStatus,baseRefName,headRefName,url,statusCheckRollup,files,commits
```

2. Create a clean temporary PR-head worktree for review:

```bash
git fetch origin main pull/<PR>/head:pr-<PR>-review
git worktree add /home/ubuntu/work/aot-pr<PR>-review pr-<PR>-review
```

3. Run focused verification before merge. For Weglot-style cleanup, include:

```bash
python3 -m py_compile scripts/remove_legacy_weglot.py
python3 scripts/remove_legacy_weglot.py --dry-run site
python3 - <<'PY'
from pathlib import Path
import re, sys
pat = re.compile(r'(weglot|cdn\.weglot|wp-content/plugins/weglot|\bwg[_-])', re.I)
remaining=[]
for p in Path('site').rglob('*'):
    if p.is_file() and p.suffix.lower() in {'.html','.pdf','.css','.js'}:
        try:
            txt = p.read_text(errors='strict')
        except UnicodeDecodeError:
            continue
        if pat.search(txt):
            remaining.append(str(p))
print('remaining_vendor_files=', len(remaining))
if remaining:
    print('\n'.join(remaining[:50])); sys.exit(1)
PY
```

Also smoke representative language-switcher pages so cleanup does not remove static English/Japanese navigation.

4. Merge only when checks are clean/mergeable and focused verification passes.

5. Post-merge, verify GitHub reports `MERGED` and capture merge commit.

6. Run live **body-content** token smokes on all public entry points:

```bash
for u in \
  'https://activeoahutours.com/' \
  'https://www.activeoahutours.com/' \
  'https://active-oahu-tours-mirror.pages.dev/'
do
  echo "--- $u"
  curl -sSL "$u" | grep -Eio 'weglot|cdn\.weglot|wp-content/plugins/weglot|wg[_-]' | head -20 | wc -l
done
```

Expected for a successful Weglot body cleanup: `0` matches for each URL.

7. Add a Linear evidence comment even if the issue is already in Done. Include PR URL, merge commit, pre-merge check status, focused verifier scope/log, live body-token results, and the boundary/non-claim.

8. Clean up temporary review worktree and local review branch:

```bash
git worktree remove /home/ubuntu/work/aot-pr<PR>-review
git branch -D pr-<PR>-review
```

## Reporting boundary

Call this **focused ad-hoc verification + live token smoke**. Do not claim a full Lighthouse/browser suite unless one actually ran.

## Pitfalls

- Do not use `grep` on response headers as the body-artifact proof. Headers can still contain Cloudflare CSP references to retired domains.
- Do not confuse preview deployment success with production verification.
- Do not skip `www.activeoahutours.com`; verify redirect plus final body.
- Do not let invalid/inherited shell `GH_TOKEN` stop the review if an approved profile-scoped GitHub PAT is available; load the token into the command environment without printing it.
