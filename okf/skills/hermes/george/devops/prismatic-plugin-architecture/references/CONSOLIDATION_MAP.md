# Prismatic Plugin Architecture Skill Consolidation Map

Consolidated: 2026-07-23

The former `SKILL.md` was 100,244 bytes and 1,043 lines. Its detailed sections were mechanically extracted by original line boundary, with only `read_file` line-number prefixes removed. The compact `SKILL.md` now routes to these files.

| Reference | Original lines | SHA-256 |
|---|---:|---|
| `governance-security-and-public-readiness.md` | 68–182 | `6fc8a8ca2aaa053167830793cd06f18d1779d690c1594428cd1a01e2846c2838` |
| `planning-audits-and-release-candidates.md` | 183–356 | `2847a476191d6f342301284424bf0fa30b30f44be59c4c86c807e826da1502dc` |
| `agent-dispatch-control-and-production-durability.md` | 357–780 | `175d02ece6cb7f663c3962a5ef05433a60525ab3bcfed00a590faf1e7c98e4e6` |
| `merge-governance-and-pr-triage.md` | 781–813 | `7c77de57fced95c57cdbb2aff9cd3a6e5cf5325e0103ad2f1b402ee84307404f` |
| `pwp-dashboard-and-ingestion-integration.md` | 814–971 | `a205e874fd52a5c019bf1164959eace4c7833d7d9981dd2efbce6e9fbbf6e136` |
| `release-engineering-and-verification.md` | 972–1043 | `0759a1a8b91c795047b949fa7178660ab9d580eabb05589cd2dd5cea98a181e1` |

Post-consolidation checks:

- `SKILL.md` loads through `skill_view`.
- Main file is 10,656 bytes, below the 100,000-character skill limit.
- All six references are non-empty and expose their expected first section boundary.
- Linked-file discovery includes all six references.
- Installed-distribution portability guidance is now summarized in the main skill.

Granular historical reference files that already existed were retained; none were deleted.
