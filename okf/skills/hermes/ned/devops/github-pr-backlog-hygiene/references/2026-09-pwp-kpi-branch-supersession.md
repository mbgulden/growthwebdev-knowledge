# PWP KPI branch supersession finding — 2026-09-13

Session-specific instance of the "N ahead ≠ unique work" pattern in
`/home/ubuntu/work/prismatic-pwp-ubersuggest-auth` (repo: mbgulden/prismatic-engine).

## Ask
"Open a review PR for Phases 4.1–4.6" on branch `ned/pwp-publish-kpi-tracker`
(tip `8d5e8630`, 2026-07-25, "Phase 4.6 F6 Zapier webhook").

## State at check time
- 21 ahead / 625 behind `origin/main`; local == remote; tree clean; no open PR.
- Merge-base dated 2026-07-24; main advanced 625 commits since (6 weeks of parallel work).
- `git merge-tree` showed 2 conflicts in files main also modified.
- 2-dot diff tip-to-tip showed ~88k "deletions" — misleading; it counts main's
  625 unrelated commits. 3-dot diff (branch's own delta) was clean adds only.

## Determination (evidence)
- Blob-hash path→blob comparison of `prismatic/shipped_plugins/pwp/` (both
  `capabilities/provision_site` and `capabilities/publish_kpi_tracker` present on main):
  **38/53 files byte-identical** branch vs main; **0 files branch-only**.
- 15 files differed; def-superset check over all 15: **zero branch-unique
  functions/classes**. Branch-only lines were (a) 4.2 modal CSS that main
  **inlined** into a self-contained `funnel_form.py` (150 lines + CSRF +
  4.3 edit-prefill), (b) demo-runtime data keys main moved elsewhere,
  (c) stale imports/paths.
- Every feature marker (F1 funnel, F5 preview, F6 zapier, F8 fareharbor)
  confirmed present on `origin/main`. Main additionally shipped 4.7 KPI
  dashboard, 4.8–4.10, Phase 5.0, PWP-P2 `provision_site`, credentials
  centralization, portability fixes — all merged via main commits (incl. PR #410).

## Outcome
- **No PR opened.** A `main ← branch` PR would add nothing and regress 15
  files to older July implementations (superseded funnel form, pre-credentials
  centralization, pre-portability).
- Recommendation delivered to Michael: retire the branch (delete needs his
  approval per branch-deletion rule) or leave untracked. Handoff's "PWP KPI
  second slice" next-step was already satisfied by main's Phase 5.0.

## Reusable takeaway
When a feature branch is months behind main and its phase markers all appear
on main, the work likely landed independently (different commit path). Verify
with blob-hash path comparison + def-superset before opening any PR; report
the supersession with main-side commit evidence instead.
