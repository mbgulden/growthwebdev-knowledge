# AOT OKF Hub Centralization — Phase 1 (2026-08-19)

Session record for the first hub consolidation. Class-level procedure lives in
SKILL.md "Merging / consolidating docs INTO the hub"; this file keeps the
AOT-specific facts and the open follow-ups.

## Decision

Michael directed centralizing all per-repo AOT `okf/` trees into
`mbgulden/growthwebdev-knowledge` (private) at `okf/hubs/active-oahu/`, with
source repos retired to pointer READMEs. Extends the hub-and-spoke decision
(`okf/decisions/prismatic-okf-hub-and-spoke-map.md`, GRO-3721) but migrates
docs physically — AOT has no single owning app repo.

## Layout that shipped (hub PR #29, branch `content/kai-aot-hub-centralization`)

| Hub section | Source repo (visibility) | Docs |
|---|---|---|
| `business/` | `mbgulden/active-oahu-business` (private) | 21 |
| `seo/` | `mbgulden/aot-seo-knowledge` (private) | 59 |
| `architecture/ governance/ reports/ kai-reports/ audits/ verification/` | `mbgulden/active-oahu-tours-mirror` (PUBLIC) | 19 + ~50 JSON/proto artifacts |

Plus 3 new indices (`hubs/active-oahu/index.md`, `seo/index.md`,
`business/index.md`) + 1 decision
(`hubs/active-oahu/decisions/2026-08-19-aot-hub-centralization.md`).

## Source inventory facts (verified 2026-08-19)

- `active-oahu-tours-mirror-1251`, `-2529`, `aot-gro3645-*`, `aot-gro-558`,
  `aot-business-*`, `aot-gro3640/3649/3665/3718`, `prismatic-engine-gro-*`,
  `hd-platform-*` etc. are **worktrees** of the 3 real AOT repos — counted
  once via `head -1 <dir>/.git` (`gitdir:` line = worktree).
- Only 1–2 docs overlap by basename across AOT repos → fragmentation, not
  duplication.
- `aot-seo-knowledge/okf/.state/ga4_setup.md` and `audits/baseline-2026-06-19/*.json`
  ARE tracked (git ls-files) — they moved with the tree.
- Dirty source state at migration time: mirror `main` had 1 untracked okf file
  (`phase-6-cohort-plan.md`, verified byte-identical in hub); business was on
  WIP branch `content/aot-media-website-ready-index` with 4 untracked okf files;
  seo `master` had 58 modified files. File-set superset check (md + non-md)
  passed 100% for all three before any retirement.

## Incidents / gotchas this session

1. **Live secret in migrated docs.** `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`
   (Google OAuth client secret) + client ID `977861670312-…googleusercontent.com`
   embedded in `seo/integrations/google-analytics-4-setup.md`,
   `seo/audits/baseline-2026-06-19/ga4-gsc-baseline-attempted.md`,
   `google-oauth-extended.md`, `ga4-status-2026-06-19.md`. GitHub GH013
   repository rule rejected the first push. Secret redacted in hub copy to a
   pointer (credential lives at `/home/ubuntu/.config/mcp-gdrive/`). **The
   source repos (esp. aot-seo-knowledge) STILL CONTAIN THE LIVE SECRET** —
   rotation of that OAuth client is a follow-up for Michael/agents; do not
   treat "redacted in hub" as "secret is safe."
2. **Lane hook blocked root index edit.** `okf/index.md` is outside kai's
   lanes (`okf/hubs/`, `okf/standards/`, `okf/projects/*/index.md`,
   `okf/audits/`). The `projects/*/index.md` pattern matches literally as a
   prefix (`f.startswith(d)`) — it does NOT glob-expand. Fix: drop the file
   from the branch, put the exact merge-time one-liner in the commit message
   and PR body (done — PR #29).
3. **Frontmatter normalization script bugs (avoid repeating):**
   - `p.parts[0]` on absolute paths is `/` → provenance fell back to hub repo
     for every doc. Use `p.relative_to(ROOT).parts[0]`.
   - First run mutated the working copy in place; re-copying from source was
     required. Run the normalizer on a throwaway copy or re-copy before retry.
   - awk-based "strip frontmatter then diff" returns false DIFF on source docs
     that already had frontmatter. Line-count arithmetic (src lines + added fm
     lines == hub lines) + `tail -n +N` body diff is the reliable check.

## PRs opened (not yet merged as of 2026-08-19)

- Hub: `mbgulden/growthwebdev-knowledge` **#29**
  `content/kai-aot-hub-centralization` — merge-time follow-up: add the root
  `okf/index.md` Sections line (exact line in commit msg).
- Mirror: `mbgulden/active-oahu-tours-mirror` **#132**
  `content/kai-retire-okf-to-hub-20260819` — okf/ → pointer README (done+verified).
- Business: `mbgulden/active-oahu-business` — **NOT YET OPENED** (was
  mid-verification of 4 untracked WIP files when session hit iteration cap;
  re-verify cleanly, branch from clean base, commit okf/ change only).
- SEO: `mbgulden/aot-seo-knowledge` — **NOT YET OPENED** (same pattern).

## Acceptance check after merges

`mcp_okf_search("active oahu", limit=5)` returns `hubs/active-oahu/**` docs
(needs MCP reload/new session — per-profile index staleness). MCP `status`
doc count jumps from 266 → ~365.

## Phase 2 (unstarted, coordinate with George/Fred)

hd-platform, prismatic-engine, Hermes-Research, sentinel, and remaining
spokes → same procedure.
