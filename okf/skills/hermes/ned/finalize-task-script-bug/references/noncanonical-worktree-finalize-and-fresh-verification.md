# Non-canonical worktree finalization + fresh verification

## Trigger
Use this when finalizing Ned tasks outside `/home/ubuntu/work/prismatic-engine`, especially HD Platform temp worktrees such as `/home/ubuntu/work/hd-platform-gro3999`, or when the system/user says fresh verification evidence is missing after code edits.

## Lesson
`finalize_task.sh` is still the required atomic safety net, but it defaults to `/home/ubuntu/work/prismatic-engine` unless the repo is passed explicitly. Its lock-unlock log can also be misleading for repos where locks were acquired as `ned`: the script may log legacy `prismatic-engine` owner unlocks while `ned` locks remain.

## Required pattern

```bash
PRISMATIC_REPO_ROOT=/home/ubuntu/work/<repo-or-worktree> \
FINALIZE_LOCK_FILES='path/one path/two .' \
bash ~/.hermes/profiles/ned/scripts/finalize_task.sh GRO-XXXX ned/GRO-XXXX ned
```

After finalize, verify and clean up instead of trusting the log:

```bash
node /home/ubuntu/.antigravity/swarm.js status
node /home/ubuntu/.antigravity/swarm.js unlock <path> ned
```

If Linear state matters, read it back after finalize. In one HD Platform run, finalize logged `GRO-3999 → In Review`, but a later Linear read showed `In Progress`; an explicit team-scoped `issueUpdate` to the GrowthWebDev `In Review` state corrected it. Trust read-back, not the transition log.

## Fresh verification nudge pattern
If the system/user reports `Verification status: unverified` after code edits, immediately rerun the named verification command in the repo and summarize concrete stdout facts. Do not rely on earlier build output, PR text, or prior claims.

For HD Platform sitemap/build work, the relevant verification was:

```bash
npm run build
python3 - <<'PY'
from pathlib import Path
import xml.etree.ElementTree as ET
root = Path('dist')
ns = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
locs = [e.text for e in ET.parse(root/'sitemap.xml').findall('.//sm:loc', ns)]
blocked = {
  'https://humandesignengine.com/affiliates.html',
  'https://humandesignengine.com/affiliates/dashboard.html',
  'https://humandesignengine.com/cron-health',
  'https://humandesignengine.com/cron-health/',
  'https://humandesignengine.com/cron-health.html',
  'https://humandesignengine.com/landing-index.html',
  'https://humandesignengine.com/landing-',
  'https://humandesignengine.com/buy-report.html',
  'https://humandesignengine.com/success.html',
}
bad = [loc for loc in locs if loc in blocked or '/cron-health/' in loc]
redirects = (root/'_redirects').read_text().splitlines()
required = {
  '/affiliates /affiliates/signup.html 301',
  '/affiliates/ /affiliates/signup.html 301',
  '/affiliates.html /affiliates/signup.html 301',
  '/landing-index.html / 301',
}
missing = sorted(required - set(redirects))
aff = (root/'affiliates.html').read_text()
dash = (root/'affiliates'/'dashboard.html').read_text()
print('sitemap_count', len(locs))
print('bad_sitemap_entries', bad)
print('missing_required_redirects', missing)
print('affiliates_html_redirect_target_present', '/affiliates/signup.html' in aff)
print('dashboard_noindex', 'noindex' in dash.lower())
if bad or missing or '/affiliates/signup.html' not in aff or 'noindex' not in dash.lower():
    raise SystemExit(1)
PY
```

Report the actual values (for example: `bad_sitemap_entries []`, `missing_required_redirects []`) so the next reviewer can see proof, not vibes.
