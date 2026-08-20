# OKF location map pattern — Prismatic Ingestion Queue session (2026-07)

Use this when a project repo does not contain a first-class `okf/` tree but the session creates or updates durable OKF records in the central hub.

## Problem observed

During the Prismatic Governance Dashboard Ingestion Queue repair, the app repo (`prismatic-engine`) had no local `okf/` tree on `deploy-fresh`. The durable closeout correctly landed in the OKF hub (`growthwebdev-knowledge`), but the user pointed out that future agents still need a repo-local map to find it.

## Durable pattern

1. Land the canonical OKF record in the hub repo:
   - local hub: `/home/ubuntu/work/growthwebdev-knowledge`
   - GitHub hub: `https://github.com/mbgulden/growthwebdev-knowledge`
   - project index: `okf/projects/<project>.md`
   - project records: `okf/projects/<project>/...`
2. In the project repo that lacks `okf/`, add a small map file in an existing docs area, e.g.:
   - `docs/okf-map.md`
3. Link the map from the project README under governance/reports/docs.
4. The map should include:
   - canonical local hub path;
   - GitHub hub URL;
   - hub master index path;
   - project index path;
   - any specific closeout/incident record path from the session;
   - verification boundary and known caveats that future agents must not miss.
5. Verify the map against the hub's remote branch, not just a possibly dirty/stale local hub checkout:
   - `git show origin/main:okf/index.md`
   - `git show origin/main:okf/projects/<project>.md`
   - `git show origin/main:okf/projects/<project>/<record>.md`
6. Run a fresh `/tmp/hermes-verify-*` script that checks:
   - changed map/README files exist;
   - README link resolves locally;
   - map contains the hub local path, GitHub URL, index paths, and specific record path;
   - hub `origin/main` contains the referenced OKF docs;
   - worktree is clean after merge;
   - verifier file is cleaned up.

## Pitfalls

- Do not create duplicate project closeouts in the app repo just because no local `okf/` tree exists.
- Do not stop after landing the hub OKF record; add a repo-local breadcrumb if future agents will start in the app repo.
- Do not trust a dirty local hub checkout for existence checks; use `git show origin/main:<path>` for durable readback.
- Watch for Hermes auto-checkpoint WIP commits during iterative doc work. Before opening the PR, squash/reset to a proper `[Fred] ... (#ISSUE)` commit and verify the committed tree.
