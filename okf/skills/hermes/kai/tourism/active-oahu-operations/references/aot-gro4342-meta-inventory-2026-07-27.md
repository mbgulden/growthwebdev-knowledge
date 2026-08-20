# GRO-4342: Site-Wide Content/SEO Inventory (2026-07-27)

## What Was Done

**Created GRO-4342 in Linear** (team: GrowthWebDev) and executed a full crawl of **306 HTML files** (EN + JA).

**Output artifacts:**
- `/tmp/aot_inventory/full_inventory.json` — 306-page raw JSON
- `/tmp/aot_inventory/inventory.csv` — CSV summary
- `/tmp/aot_inventory/REPORT.md` — markdown report
- `/home/ubuntu/work/active-oahu-business/okf/ops/inventory/aot-site-inventory-2026-07-27.md` — saved report
- `/home/ubuntu/work/active-oahu-business/okf/ops/inventory/aot-site-inventory-2026-07-27.csv` — saved CSV

## Key Findings

### 🔴 HIGH — Missing Meta Descriptions (7 pages → 5 fixed)
Original inventory said 7 pages missing meta descriptions. After investigation:
- Awards page: **already had description** — inventory regex was wrong (missed `name="description" content="..."` ordering)
- JA 404: missing → fixed
- adventure-guide/index.html: missing → fixed
- 3 redirect target pages: missing → fixed
- wp-content template: skipped (not user-facing)

**Key lesson:** Inventory regex must handle **both** `name="description" content="..."` AND `content="..." name="description"` attribute orderings, or it produces false positives.

### 🟡 MEDIUM — Short Descriptions (128 pages)
17 activity + 34 rentals + 57 JA + 16 other + 4 guide. 9 activity pages were expanded from 12–96 chars to 120–158 chars via PR #115.

### 🟡 MEDIUM — oahu-snorkel-tour Has No FareHarbor Gap
`activities/oahu-snorkel-tour/index.html` is a redirect page ("This snorkel tour has moved. Redirecting to Sharks Cove..."). No booking link = intentional. Not a gap.

### 🟡 MEDIUM — 9 Activity Pages Without hreflang
These have no Japanese counterpart — hreflang would be invalid without creating JA versions first. Excluded from fix scope.

### ✅ Verified Already Correct
- H5→H3 heading hierarchy: 0 H5s remaining
- Trust badges: 162 pages have TripAdvisor badge
- FareHarbor booking: All except 1 redirect page have links
- Schema types: Organization + TravelAgency + WebSite present

## Fixes Deployed (PRs #114, #115)

### PR #114 — 5 pages with meta descriptions added
| Page | Type |
|------|------|
| ja/404.html | Japanese 404 |
| adventure-guide/index.html | Redirect page |
| chinamans-hat-kayak-tour/index.html | Redirect target |
| kaneohe-bay-sandbar-kayak/index.html | Redirect target |
| stand-up-paddleboard-rental/index.html | Redirect target |

### PR #115 — 9 pages with improved meta descriptions
| Page | Before | After |
|------|--------|-------|
| aloha-aina-e-bike-adventure | 12 chars | 158 chars |
| chinamans-hat-kayak-rentals | 13 chars | 145 chars |
| chinamans-hat-oahu-kayak-tours | 17 chars | 128 chars |
| chinamans-hat-self-guided-oahu-kayak-tour | 23 chars | 142 chars |
| rainforest-guided-hike | 38 chars | 154 chars |
| activities/index.html | 96 chars | 153 chars |
| chinamans-hat-kayak-complete-self-guided-tour-guide | 50 chars | 147 chars |
| kayak-snorkel-hike-adventure | 66 chars | 133 chars |
| lanikai-beach-self-guided-e-bike-snorkel-adventure | 92 chars | 143 chars |

## Inventory Script Pattern

```python
#!/usr/bin/env python3
"""Site-wide SEO inventory — reusable for future audits."""
import glob, re, json

BASE = '/home/ubuntu/work/active-oahu-tours-mirror/site'

def has_meta_desc(content):
    """Handles both attribute orderings."""
    m1 = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']+)["\']', content, re.IGNORECASE)
    if m1: return True
    m2 = re.search(r'<meta[^>]*content=["\']([^"\']+)["\'][^>]*name=["\']description["\']', content, re.IGNORECASE)
    return bool(m2)

def get_meta_desc(content):
    m1 = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']+)["\']', content, re.IGNORECASE)
    if m1: return m1.group(1)
    m2 = re.search(r'<meta[^>]*content=["\']([^"\']+)["\'][^>]*name=["\']description["\']', content, re.IGNORECASE)
    return m2.group(1) if m2 else ''
```

## Git Push Refspec for New Remote Branches

When a squash-merged commit exists locally but was never pushed (pre-push hook blocked it), push the specific commit to a new branch:

```bash
# Push a specific local commit to a new remote branch
git push origin <sha>:refs/heads/feature/new-branch-name -f

# Example: push commit eac60c879 to new branch feature/gro-4342-fix-meta-descs
git push origin eac60c879:refs/heads/feature/gro-4342-fix-meta-descs -f
```

## Linear State ID Workaround

When `team(id: "...")` workflowStates query returns empty states (Linear API quirk with certain team IDs):

1. Query issues directly to find the issue ID, then use workflow states from a parent/team query
2. Or: use `issueUpdate(id: "<issue_id>", input: {stateId: "<state_uuid>"})` with the state UUID found by listing workflow states on a different query path
3. If state update fails, post evidence comment and move on — state transitions are nice-to-have, not blocking
