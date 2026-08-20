# BeyondSaaS Branch/Worktree Cleanup — 2026-07-21

Session pattern for cleaning a Cloudflare Pages marketing-site checkout after ad-hoc deployment and many agent branches.

## What mattered

- There was only one real worktree for `beyondsaas-site`; branch clutter was local refs plus untracked live-ish source/assets.
- GitHub auth was unavailable, so remote branch/PR cleanup could not proceed. Do not record that as a durable failure; it is setup state. The durable lesson is to complete local archive/checkpoint cleanup and report the push/auth boundary.
- Production had been deployed from a dirty worktree. That makes untracked source/assets potentially part of live behavior and therefore not disposable by default.

## Safe sequence

1. Inventory:
   - `git worktree list --porcelain`
   - `git branch -vv --sort=-committerdate`
   - `git branch --merged main`
   - `git status --short --branch`
   - branch diff/ahead-behind against `main`
2. Archive before mutation:
   - status
   - branches
   - worktrees
   - tracked/staged diffs
   - untracked file list
   - bounded `untracked.tar.gz`
3. Secret-scan untracked text files before checkpointing.
4. Remove only mechanically safe clutter/duplicates:
   - local deployment cache such as `.wrangler/`
   - sentinel files such as `STARTED.md`
   - root-level generated duplicates when identical public copies exist
5. Add `.gitignore` entries for recurring local cache/duplicates.
6. Checkpoint live-ish untracked source/assets if production was deployed from the dirty worktree and the files are not secrets/generated cache.
7. Delete only local branches proven merged into `main`/current history. Preserve ahead/overlapping branches for extraction or PR review.
8. Run `npm run build` plus any site-specific post-build coverage checks before reporting clean.

## Branch classification example

Safe local deletes were branches already merged into `main` or current history:

```text
feature/GRO-1922-lead-gen-pipeline
feature/gro-2087
fix/gitignore-pycache-pyc-GRO-1787
```

Preserve/review examples:

```text
ned/GRO-538                 about/founder page work
ned/GRO-539                 services overview / CTA work
ned/GRO-540                 service detail + capture-email overlap
feature/gro-2413            capture-email production fix
feature/gro-2094            pricing numbers; business decision
feature/gro-2095            case-study/about template overlap
```

## Verification shape

```bash
npm run build
python3 - <<'PY'
from pathlib import Path
html=list(Path('dist').rglob('*.html'))
print('html_count', len(html))
print('missing_gtm_count', sum('GTM-W9BR974P' not in p.read_text(errors='ignore') for p in html))
print('missing_noscript_count', sum('googletagmanager.com/ns.html?id=GTM-W9BR974P' not in p.read_text(errors='ignore') for p in html))
print('direct_gtag_count', sum('gtag/js?id=G-SDN0R5YVJF' in p.read_text(errors='ignore') for p in html))
print('robots_exists', Path('dist/robots.txt').exists())
print('sitemap_exists', Path('dist/sitemap.xml').exists())
print('sitemap_url_count', Path('dist/sitemap.xml').read_text().count('<url>') if Path('dist/sitemap.xml').exists() else 0)
PY
```

Report the archive directory and any remaining branches requiring review. Do not call the repo fully unified while preserved ahead branches remain.
