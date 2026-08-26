---
name: okf-documentation-ops
description: Create, repair, verify, and land Open Knowledge Format (OKF) documentation in the growthwebdev hub/spoke repos, including closeout records, standards, incident reports, indexes, clean PR hygiene, and ad-hoc verification. Includes the project-hub structure pattern for cold-start fitness and multi-agent handoff.
tags: [okf, project-hub, handoff, multi-agent, cold-start, verifier-design]
---

# OKF Documentation Ops

Use this skill when work needs to become durable, findable OKF documentation rather than a transient chat summary, Linear comment, or commit log. The goal is to land class-level, indexed knowledge with evidence boundaries and a clean Git trail.

## Operating principles

1. **Document the class of learning, not just the one-off narrative.** Prefer project closeouts, standards, incident reports, and indexes over vague session notes.
2. **Use the hub-and-spoke model.** Cross-project standards and indexes live in `growthwebdev-knowledge/okf/`; project-specific details may live in project spoke `okf/` trees when appropriate.
3. **Every OKF doc must be discoverable.** Add or update the relevant master/project/report/standard index in the same change.
4. **Evidence scope must be explicit.** Label ad hoc targeted verification separately from full suite-green, hosted-browser proof, Stripe-live proof, or canonical build/test proof.
5. **Do not pollute PRs.** If the current worktree/branch has unrelated dirty or inherited files, create a clean branch/worktree from `origin/main` and apply only the intended docs/index edits.
6. **OKF docs are not done when they exist — they are done when a different agent can pick them up cold.** "Cold-start fitness" is a first-class acceptance criterion, not a nice-to-have. A bundle with standards, project indexes, and risk registers but no HANDOFF.md, no per-decision Owner, no per-risk observable signal, and no per-task first-step is *non-conformant* even if every file is verified. See `linear-handoff-build-out` for the cross-project build-out shape this principle implies. Michael has explicitly asked "is there enough documentation?" after a build that looked complete — that question is the trigger to extend the bundle, not to declare it done.

## Project-hub structure (the canonical OKF shape for feature builds)

When a feature grows large enough to warrant its own parent epic + child epics + child tasks, the OKF bundle under `okf/projects/<project-slug>/` follows a fixed shape. This pattern emerged from the journal-pe-integration and pe-cron-workflow-gaps builds (2026-07-26) and applies to any future feature handoff.

| File | Purpose | Required content |
|---|---|---|
| `index.md` | Project hub | Parent epic goal + exit criterion; child epic table with **owner + first step columns**; full task inventory with rubric reference; sequencing; pointers to decisions/risks/standards; routing convention reference; cold-start pointer. |
| `HANDOFF.md` | Cold-start recipe | Sections 1–7 (or 1–8 when cross-project dependencies exist): What is this? Where does the work live? Read order (cold start, ~10 minutes)? First concrete action? Stop conditions? Owners? Conventions not to break? (Optional) Cross-project dependencies. |
| `decisions/NNN-<slug>.md` | ADRs | One per major decision. Each must carry `## Owner` and `## Acceptance Test IDs` sections in addition to Context/Decision/Consequences/Reversibility. |
| `risks/<slug>.md` | Risk register | Each risk as a table with `Owner`, `Likelihood`, `Impact`, `Observable signal`, `Mitigation`, `Backout`. Named humans (Michael, George, Becca, ned, fred) for every Owner cell — no generic "team" placeholders. |
| `standards/<slug>.md` (if class-level) | Binding standard | Normative requirements with stable test IDs (`<FEATURE>-TEST-<EPIC_SLUG>-NN`, `<FEATURE>-PERF-<EPIC_SLUG>-NN`, `<FEATURE>-NEG-<EPIC_SLUG>-NN`). |

The project must be linked from `okf/index.md`, `okf/projects/index.md`, and (for decisions) `okf/decisions/index.md` in the same change.

For the full rationale, see `references/okf-project-hub-structure-2026-07-26.md`.

## Verifier-design pitfalls (real failure modes)

These are bugs in my own OKF verifiers that have already shipped. They are easy to repeat; document them so the next verifier gets them right.

1. **`git_path` is repo-relative, not OKF-relative.** A frontmatter verifier that checks `git_path == rel` against an OKF-relative `rel` (e.g., `projects/<slug>/index.md`) will spuriously fail. Check against `f"okf/{rel}"` instead. Example failure mode: every OKF doc appears "broken" because the verifier miscompares the durable form with the OKF-internal form.

2. **Forbidden-marker strings are checked literally.** A risk register's `Observable signal` field may want to document "what to watch for" using literal prefixes like `ghp_`, `xox[abp]-`, etc. The verifier will flag every one of these as a real credential leak. Use **category wording**: "known GitHub-style credential pattern (raw prefix intentionally withheld)". The category is what the agent needs to know; the literal prefix is what the verifier needs to not see.

3. **Section-heading patterns must match what you actually wrote.** I wrote `### 2.1 HTTP ...` and my verifier searched for `§2.1`. The doc was right; the verifier was wrong. Pattern-match against the exact markdown heading text — not against prose references like "§" or "Section N.M".

4. **`depends_on_siblings: [GRO-4222, GRO-4223]` is a sequence, not a parallel.** When listing tasks that "should ship together as one PR", the order matters — earlier tasks block later ones. Use the empty-list form (`none (first task in epic)`) for the first task in an epic to signal it can be picked up freely. Document this convention in the verifier-side note, not just in the task description.

5. **`agent:in-progress` is a runtime signal, not a built-in feature.** Adding a label that means "an agent has claimed this task" is meaningless without the claim protocol that says "atomically add this label before reading source code; remove it before handoff". Define the protocol in the same place you define the label.

When designing a verifier, run it against a known-passing artifact first to confirm the conventions are right. If a verifier returns failures on the first run, fix the verifier before touching the artifact — and explicitly note which layer was wrong in the audit log.

For more verifier-design pitfalls, see `references/okf-verifier-design-pitfalls-2026-07-26.md`.

## Standard workflow

1. **Inventory the documentation gap.**
   - Search existing OKF docs and indexes for the issue/commit/incident names.
   - Decide the proper OKF type: `Report`, `Standard`, `Decision`, `Index`, `Integration`, `Audit`, or project closeout.
   - If multiple listings share a root lesson, create one class-level standard plus concise incident/project records that link to it.
   - If the current project lacks an `okf/` tree but branch names, backup refs, archived worktrees, or hub indexes suggest docs existed, run the treasure-hunt/reconciliation pattern before saying docs are missing. See `references/okf-treasure-hunt-reconciliation-2026-07.md`.

2. **Choose file locations.**
   - Project closeout: `okf/projects/<project-slug>/<topic>-YYYY-MM-DD.md` plus `okf/projects/<project-slug>/index.md` if missing.
   - Cross-project standard: `okf/standards/<standard-slug>.md`.
   - Incident/rollup report: `okf/reports/<topic>-YYYY-MM-DD.md`.
   - Decision: `okf/decisions/<decision-slug>.md`.
   - Keep private/sensitive bundles linked to the appropriate private repo URL rather than a broken local relative path.

3. **Write frontmatter first.** Required frontmatter:
   - `type`
   - `title`
   - `description`
   - `resource`
   - `tags`
   - `timestamp`
   - `linear_issue`
   - `git_repo`
   - `git_path`
   - `last_verified`
   - `verified_by`
   - `status`

   `resource` and `git_path` should match the **repo-relative** OKF path unless the doc is intentionally an external resource. (See the verifier-design pitfalls section above.)

4. **Capture evidence compactly.** Include:
   - commit SHAs / PR numbers / branch readbacks when relevant,
   - exact job IDs for cron incidents,
   - concise verification outputs (`3 passed`, `10 pages built`, `origin/staging = ...`),
   - cleanup status and known workspace residue,
   - explicit verification boundary and remaining launch proof.

5. **Update indexes.** At minimum, update the relevant:
   - `okf/index.md` for major current governance/project closeouts,
   - `okf/projects/index.md` for new project indexes,
   - `okf/standards/index.md` for standards,
   - `okf/reports/index.md` for incident/rollup reports,
   - `okf/decisions/index.md` for cross-project decision folders (point at project subfolders).

6. **Verify before commit.** Use a focused `/tmp/hermes-verify-*` script (or `execute_code` inline) that checks:
   - each new doc exists,
   - required frontmatter fields are present,
   - `resource` and `git_path` match the file path (repo-relative, not OKF-relative),
   - local Markdown links resolve,
   - new docs are reachable from indexes,
   - important evidence markers are present,
   - any discovered broken-link repair is reflected,
   - **no literal forbidden-marker strings** (use category wording),
   - **section-heading patterns** in the verifier match the headings you actually wrote.

7. **Use a clean PR if the current branch is polluted.**
   - If `gh pr view` or `git diff origin/main...HEAD --name-only` shows inherited unrelated files, do not merge it.
   - Close/supersede the polluted PR.
   - Create a clean worktree/branch from `origin/main`.
   - Copy only the intended OKF docs and apply targeted index edits.
   - Re-run the OKF verifier on the clean branch.
   - Push/open/merge the clean PR if allowed.

8. **Post-merge readback.** After merge:
   - Fetch/verify `origin/main` contains the merge commit.
   - Run the verifier against the merged tree or a fresh clone of `origin/main` for changed paths the guard names.
   - Clean temporary worktrees and release locks.

9. **Add a repo-local OKF map when the target repo has no `okf/` tree.** If durable records live in the hub but future agents will start in the project repo, add a small map/breadcrumb in the project repo (for example `docs/okf-map.md`) and link it from the README. Verify the map against the hub's remote branch (`git show origin/main:<okf-path>`) rather than a dirty/stale local hub checkout. See `references/okf-location-map-pattern-2026-07.md`.

10. **For suspected stranded project docs, run a treasure-hunt reconciliation before promotion.** Inventory local branches, origin branches, stale remotes with local refs, attached worktrees, hub branches, and archived local `okf/` directories. Extract hidden docs with `git ls-tree`/`git show` rather than checking out polluted branches. Then dedupe, classify, propose canonical structure, and only promote in small clean PR batches. See `references/prismatic-okf-treasure-hunt-reconciliation-2026-07.md`.

11. **For Batch 2 canonical project promotion, select sources before writing docs.** When the treasure map/classification exists, first create a small `batch2-selected-canonical-records.json` manifest, then synthesize current canonical records from selected sources. Each promoted/current record — including the project index itself — must carry a provenance table, exact ad-hoc verification boundary wording, and an explicit Batch 3 queue for historical/archive/unsafe families. See `references/prismatic-okf-batch2-canonical-project-index-2026-07.md`.

12. **For Batch 3 historical/archive promotion, manifest then quarantine/archive.** After current records are landed, create `batch3-selected-archive-records.json` before writing archive docs. Include every queued family, record all unsafe/private candidates in redacted quarantine form, write curated archive summaries instead of raw branch dumps, keep cleanup blocked, and post-merge verify from `origin/main`. See `references/prismatic-okf-batch3-archive-quarantine-2026-07.md`.

13. **For cleanup-gate work, create an approval manifest only — never cleanup.** After Batches 1–4 land, the next safe step is `/tmp/prismatic-okf-treasure-hunt/manifests/final-cleanup-candidates.json`: classify branches, refs, worktrees, local dirs, duplicate docs, hidden useful/historical docs, and unsafe/private candidates with `cleanup_executed: false`, `approval_required_before_any_cleanup: true`, and `requires_manual_approval: true` on every candidate. Verify durable evidence from remote branches and report cleanup safety as blocked/yellow. See `references/prismatic-okf-cleanup-gate-manifest-2026-07.md`.

14. **Before asking Michael to review stale OKF PRs, reduce the review surface.** Rescan open PRs/branches against `origin/main`, classify files into safe-promote, repairable-promote, superseded, noise, and questionable/manual. Promote only safe/repaired docs through a clean `origin/main` branch, exclude credential-adjacent/private/noisy material, verify with a focused `/tmp/hermes-verify-*` script, then produce a reduced manifest showing only what genuinely needs human eyes. See `references/okf-selective-safe-promotion-review-reduction-2026-07.md`.

15. **For unsafe/private candidates, produce a redacted manual-review package and park it in Linear.** Create only local/private review artifacts, with `publish_or_promote_authorized: false`, `cleanup_authorized: false`, and `manual_review_required: true`. Use `[REDACTED_PATH_###]` markers, no raw content fields, no raw path fields, and broad path hints with no slash/path-like content. If making a Markdown companion, keep its table to exactly review id, source repo, source branch, source head prefix, redacted path marker, hash prefix, and recommended action. After verification, create a paused Linear task for the human review rather than continuing sensitive cleanup inline. See `references/prismatic-okf-unsafe-private-manual-review-2026-07.md`.

## Pitfalls

- Do **not** leave OKF work only in a dirty local branch or Telegram summary.
- Do **not** commit to whatever branch the hub checkout happens to have checked out. The growthwebdev-knowledge working tree can sit on someone else's unpushed local branch (2026-08-20: `content/kai-okf-phase3-spokes`, ahead 2 of origin/main, no remote) — a plain `git commit && git push origin main` there lands nothing and muddies a peer's WIP. Pattern: `git fetch` → `git checkout -b feature/<agent>-<slug> origin/main` → cherry-pick/apply only the intended docs → push the feature branch. Hub main is manual-merge by governance; feature branch + push is the complete landing. Never force-push or move another agent's local branch. **The hub also has a concurrent background writer** (an OKF skill-hub auto-regen / drift-reconciliation process that commits `okf/skills: auto-regen …` and creates `content/*` + `rescue/*` branches on its own). The remote branch will often have moved between your `fetch` and `push`, so a non-fast-forward rejection is *expected* — not an error. Do not merge blindly and do not bare-`--force`: rebuild from a **fresh** `origin/main`, prove your tip is a verified **superset** of the remote tip, then `--force-with-lease` on **your own** `feature/<agent>-*` branch only, and read back from `origin/` (the working tree is unreliable mid-session). The repo's `git config user.name` may be another agent's (it was "Ned") — the lane hook keys off the **branch prefix**, not the author, so `feature/*` → fred → `owner: ["*"]`. See `references/shared-hub-concurrent-writer-landing-2026-08-20.md`.
- Do **not** branch from an old worker branch with inherited audit/plugin files; GitHub may show a huge polluted PR even if the latest commit looked small.
- Do **not** add local links to docs that only exist in a dirty/unmerged worktree. If a standard is pending publication, mention it as pending or use a durable external URL.
- Do **not** claim full docs-suite green from a focused OKF verifier. Call it ad hoc targeted verification.
- Do **not** make a private bundle link a relative path unless that bundle actually exists inside the hub repo at that path.
- Do **not** stage unrelated pre-existing dirty files when committing OKF closeouts.
- Do **not** leave future agents without a breadcrumb when the app/project repo lacks an `okf/` tree. Add a repo-local OKF map that points to the canonical hub record and link it from the README.
- Do **not** verify hub OKF existence solely from a dirty local checkout. Prefer remote readback (`git show origin/main:<path>`) for the specific indexed records.
- Do **not** promote hidden docs directly from branch counts. First create an explicit source-selection manifest, then synthesize current records from selected provenance.
- Do **not** publish raw historical branch dumps after canonical project records land. Batch archival material as curated rollups, keep unsafe/private candidates redacted/quarantined, and keep cleanup blocked until a final cleanup manifest plus explicit approval.
- Do **not** turn the cleanup gate into cleanup execution. The cleanup-gate deliverable is an approval manifest with `cleanup_executed: false`; every branch/ref/worktree/local-dir/duplicate/unsafe-private candidate still requires manual approval.
- Do **not** bulk-clean OKF branches/worktrees after one family is canonical. First land the named family to `origin/main`, verify remote readback, remove only temp artifacts created for that family, and manifest all remaining refs as source candidates.
- Do **not** include raw unsafe/private paths or titles in cleanup manifests. Use redacted markers such as `[REDACTED_PATH_001]` and keep unsafe/private candidates `manual-review-only`.
- Do **not** let a broad `path_hint` accidentally look like a path. Avoid `/` and `\\\\` entirely in unsafe/private review hints; use wording like `category only: redacted sensitive OKF candidate; raw location intentionally withheld`.
- Do **not** continue sensitive cleanup inline after packaging unsafe/private candidates. Create a paused Linear task with the review package paths and exit criteria, then move back to the primary operational work.
- Do **not** treat stale-guard paths under `/tmp` as artifacts to recreate after cleanup. Verify the durable replacement on the target remote branch and explicitly state that the temp worktree/script was intentionally removed.
- Do **not** omit provenance/verification boundary from a canonical project index just because it is an index; Batch 2 verifiers should require provenance tables and exact boundary language on the index too.
- If Hermes auto-checkpoints a WIP commit during documentation work, squash/reset it into the required clean commit message before opening the PR.
- Do **not** ship a project with a HANDOFF.md that lacks a `## 1. What is this?` section naming the **verbatim parent exit criterion**. Without it, the cold-start reader cannot tell when their work is done.

## Verification language template

```text
Ad hoc targeted OKF verification: PASS
- /tmp/hermes-verify-xxxx.py created with tempfile and cleaned up
- required frontmatter present
- local Markdown links resolve
- new docs reachable from indexes
- evidence markers present: <markers>
Scope: ad hoc targeted OKF verification only — not full docs-suite green.
```

16. **Plan-mode flow for OKF + Linear handoff.** When Michael asks for a comprehensive plan that should later be loaded into Linear as an epic + child tasks, treat the OKF docs as the canonical plan and Linear as the downstream execution surface. The right flow is: (a) write the OKF artifacts (standard, project index, decisions with Owner + Acceptance Test IDs, risk with named owners + observable signals, discovery, **HANDOFF.md**); (b) verify; (c) **make exactly one approval pause**; (d) create the full Linear tree (parent epic + child epics + child tasks with the **seven-field description shape** + the **Distributed-Execution Header** as field 8) in a single batched mutation; (e) read back to confirm the structure, then report. Do **not** pause between OKF docs and Linear mutation, do **not** pause to re-confirm scope after each phase, and do **not** ask "approve?" twice — one approval covers both the plan shape and the Linear handoff. The OKF docs ARE the plan; if you wrote them, the plan was already approved at write time. The seven-field description shape and the Distributed-Execution Header are defined in `linear-handoff-build-out` — defer to that skill for the exact wording and the cold-start fitness gate. See `references/okf-linear-handoff-2026-07-26.md`.

17. **For the OKF `git_path` frontmatter field, use the repo-relative path, not the OKF-relative path.** `git_path: okf/projects/<slug>/index.md`, not `git_path: projects/<slug>/index.md`. `resource` should end with the same repo-relative path. A frontmatter verifier that checks `git_path == rel` against an OKF-relative `rel` will spuriously fail; check against `f"okf/{rel}\"` instead. See `references/okf-git-path-repo-relative-2026-07-26.md`.

18. **For ephemeral verifiers, prefer `execute_code` over `/tmp/hermes-verify-*.py` when the goal is post-write verification on a fresh artifact.** A `tempfile.mkstemp` verifier under `/tmp` leaves a deleted-but-still-named file and is sometimes flagged as an additional changed path by post-turn verification guards. Running the same Python checks inline via `execute_code` (no file artifact) avoids the cleanup step and avoids making the verifier itself part of the diff. Reserve `/tmp/hermes-verify-*` for cases where the artifact is large enough that the harness cap forces a real file, or where the user explicitly asks for a reusable script under the skill.

19. **Treat "is this enough?" / "would 3-5 agents know how to do this?" as audit triggers, not as defensive questions.** When Michael asks those questions, the right move is to **re-audit the bundle**, not to defend it. A common failure pattern is to claim completeness on a plan that looks done (parent epic, child epics, child tasks with seven-field descriptions, labels) and miss the real gaps: no `depends_on_siblings`, no branch_slug, no swarm_locks, no pytest command, no `agent:peer-review-blocked`, no claim protocol, no handoff protocol. See `linear-handoff-build-out/references/distributed-execution-header.md` for the Distributed-Execution Header spec that closes these gaps. The lesson generalizes: any time the user asks "is X enough?", treat it as a request to enumerate the missing pieces by category, then patch.

20. **For multi-agent pickup, the project's `index.md` Routing Convention section must name the Distributed-Execution Header and link the canonical reference.** Without that pointer, agents picking up tasks may stop at the seven-field body and never see the header. The canonical reference is `okf/standards/references/distributed-execution-multi-agent-task-pickup.md`.

21. **"What gaps do you see?" is an audit trigger, not an opinion prompt.** When Michael asks what gaps exist in a platform or feature, the right move is an **active audit** against the live filesystem/Linear state — not a brainstorm, not a memory recall, not a claim. The audit must produce a tiered inventory (genuinely broken / operationally fragile / missing product surface / meta cross-cutting) with file-path evidence and severity signals. A common failure pattern is to answer from memory and miss real issues that are obvious in the source. Read the relevant modules, list every category (cron / scheduler, dispatch / routing, agent harness, Linear integration, gateway / IPC, storage / state dbs, plugin / skill, quality / gates, sandbox / security, observability / telemetry, API / web, CLI / admin), and tag each item exists / partial / absent / has-spec-but-no-impl. The output of the audit is the input to the next plan-mode iteration.

22. **For plans addressing multiple stakeholders, split OKF docs by audience, not by topic.** When a comprehensive plan needs different reviewers (e.g., foundational primitives go to a stability reviewer like George; cross-cutting + blocked tasks go to the operator; meta work goes to nobody yet), the right structural move is **two separate OKF docs**, not one doc with sections per audience. The audit doc (full inventory + tiered findings) goes in `okf/reports/<date>-<slug>-audit.md`. The foundational-only subset goes in `okf/reports/<date>-<slug>-foundational.md` with explicit "decisions needed from <reviewer>" questions at the end. The cross-cutting + blocked subset goes in `okf/reports/<date>-<slug>-cross-cutting.md` with explicit "blocked on first-wave Epic 3" markers. Each doc carries its own routing pointer; the audit doc is the index of record. The mistake to avoid is one giant doc — different stakeholders won't read past their section, and the doc gets approved in pieces without anyone seeing the whole.

23. **For the Telegram-downloadable .md pattern, copy from the OKF source to `~/.hermes/profiles/fred/cron/output/`.** When Michael asks for a `.md` doc to forward to a stakeholder (George, a contractor, an external reviewer), the path is `cp okf/<path> ~/.hermes/profiles/fred/cron/output/<basename>-YYYY-MM-DD.md` then attach via `MEDIA:` in the reply. Do NOT inline the entire doc into a Telegram message — Telegram renders Markdown but truncates aggressively past ~4k chars. Do NOT zip or compress; the user wants a single readable file. The `<basename>-YYYY-MM-DD.md` naming convention makes the file easy to find later in the cron output dir.

24. **For per-task owner labels, do not copy the parent epic's owner to every child.** The PE dispatcher keys off Linear labels, not title or description content. If the parent epic is `agent:ned` but a specific task is owned by `agent:fred` (e.g., for an audit, sign-off, or configuration), the child task MUST carry `agent:fred`, not `agent:ned`. A bulk label copy that uses the parent's owner for every task silently misroutes work. Verify each child's label set against the per-task owner map before declaring the build-out done.

25. **For OKFs consumed by AI build agents (Antigravity 2.0, AGY), add a Context Pack section near the end.** Human readers can `git grep` for missing context, ask in chat, and tolerate "TBD" placeholders. AI build agents on a single laptop can't — they get a prompt, then start building. The Context Pack is a 12-sub-section structure (canonical file paths, live API endpoints, live git SHAs, live Linear state, live environment + fresh-clone command, build conventions, 10 anti-patterns, spec-freeze destinations, acceptance-marker verification commands, debugging tips, "did I miss anything?" checklist, quick-reference card). Every referenced path must pass `os.path.exists` before the OKF is signed off. The full pattern is in `references/okf-context-pack-for-ai-build-agents-2026-07-31.md`. Worked example: the Review/Merge Factory V1 OKF at `/home/ubuntu/.hermes/profiles/orchestrator/state/okf-review-factory-v1.md` §16 (12 subsections, 25 verified paths, 7 acceptance-marker commands). A second worked example (docs/workspace/deploy OKF, 2026-08-01) and the patterns it surfaced (wrap-don't-replace, sibling frontmatter, verify-paths-before-citing, anti-pattern count scaling) are in `references/okf-context-pack-for-ai-build-agents-2026-08-01.md`. Read both references when designing a new AI-build-agent OKF.

26. **When the ask is "update any OKF/skill/memory references for X," it is a multi-surface value-propagation task, not a one-doc edit.** A single canonical value (URL, endpoint, path, label) is often prescribed from many emitters at once — and the one you're looking at is rarely the one that actually emits it. The 2026-08-20 case: the correct workspace-tree URL had to be propagated through **11 profile `SOUL.md` files** (the system-prompt sources that emit the link), a peer's live skill, and the OKF skill mirror — while the live contract docs and memory were already correct. Procedure: (a) sweep ALL surfaces — OKF hub **and** its `okf/skills/hermes/` mirror, **all** profiles' `~/.hermes/profiles/*/skills/`, and **all** `SOUL.md`/`AGENTS.md` system-prompt sources, plus memory; (b) triage every hit as **prescriptive** (instructs future behavior → update), **historical** (dated incident record → leave), or **internal** (localhost route test / API param / "keep the legacy route working" → leave); (c) update only prescriptive surfaces; (d) re-sync the OKF skill mirror from the live skills (byte-identical `diff -rq`) and remove any superseded reference doc; (e) verify with a final grep that **zero prescriptive stale refs remain** (with historical/internal patterns excluded); (f) memory is a last check — if the correct value is already there, don't re-edit it. The failure mode is editing the visible doc and declaring done while the real emitter keeps producing the stale value. See `references/reference-value-propagation-multi-surface-2026-08-20.md`.

## References

- `references/okf-context-pack-for-ai-build-agents-2026-07-31.md` — the Context Pack section shape for OKFs consumed by AI build agents (Antigravity, AGY) rather than human readers. 12 sub-sections, 25-path verification gate, anti-patterns + checklist + quick-reference card. Use whenever the OKF handoff target is an AI agent on a single laptop, not a multi-agent chat room. Companion to the human-oriented OKF project-hub structure below.
- `references/okf-context-pack-for-ai-build-agents-2026-08-01.md` — second worked example (docs/workspace/deploy OKF) and the patterns surfaced by applying the Context Pack template twice: wrap-don't-replace, sibling OKF frontmatter, verify-paths-before-citing, two-OKF continuity, anti-pattern count scaling. Read alongside the 2026-07-31 reference when designing a new AI-build-agent OKF.
- `references/okf-project-hub-structure-2026-07-26.md` — the canonical OKF project-hub shape (standard + project index + HANDOFF + decisions + risk + discovery + indexes) with required content per file.
- `references/okf-verifier-design-pitfalls-2026-07-26.md` — verifier bugs that have already shipped (git_path repo-relative vs OKF-relative, literal forbidden-marker strings, section-heading patterns, sequence vs parallel in depends_on_siblings, runtime-signal labels need a claim protocol).
- `references/plan-reconciliation-after-peer-review.md` — companion reference: when a peer reviewer (George-style) hands you a structured correction packet, how to verify the corrections, write the revised plan, and hold the no-mutation boundary. See the `plan-reconciliation-after-peer-review` skill for the full workflow.
- `references/codex-cli-integration.md` — companion reference: when an OKF doc or Linear task needs to invoke the standalone Codex CLI (not a Hermes profile), what argv/auth-boundary/cap-1 contract applies. See the `codex-cli-integration` skill.
- `references/okf-closeout-clean-pr-and-verifier-2026-07.md` — session-specific pattern from HDE/MCP/cron OKF closeouts: polluted PR replacement, clean branch from origin/main, frontmatter/link/index verifier, and post-merge fresh-clone check.
- `references/okf-clean-worktree-closeout-prismatic-ingestion-queue-2026-07.md` — clean temporary OKF worktree pattern for documenting operational repairs when the primary knowledge hub checkout is dirty; includes stale-verification-guard handling.
- `references/prismatic-okf-treasure-hunt-reconciliation-2026-07.md` — class-level pattern for full OKF/doc source inventory, hidden-branch extraction, dedupe, classification, canonical structure proposal, cleanup safety, and stale-verification guard handling when project docs are stranded across backup branches/worktrees.
- `references/okf-treasure-hunt-reconciliation-2026-07.md` — class-level pattern for discovering, manifesting, deduplicating, classifying, and landing stranded OKF/docs from hidden branches, backup refs, and archived worktrees before cleanup.
- `references/prismatic-okf-next-batches-archive-standards-map-2026-07.md` — follow-on pattern after canonical project records land: Batch 3 archive/quarantine rollups, Batch 3.5 standards/decision extraction, Batch 4 repo-local map finalization, and stale-guard verification for intentionally cleaned temp worktrees/scripts.
- `references/prismatic-okf-cleanup-gate-manifest-2026-07.md` — final cleanup-gate pattern: generate an approval-only manifest with every candidate requiring manual approval, unsafe/private redacted/manual-review-only, durable remote evidence checks, and no cleanup execution.
- `references/prismatic-okf-unsafe-private-manual-review-2026-07.md` — redacted unsafe/private review package pattern: local-only JSON/Markdown artifacts, strict no raw content/path fields, exact seven-column Markdown table, fresh verifier, and paused Linear parking task.
- `references/okf-ssot-agent-memory-reconciliation-2026-07.md` — SSOT pattern for landing one canonical OKF family on `origin/main`, verifying by remote readback, removing only temp artifacts created for the merged family, and manifesting remaining dirty branches/worktrees before cleanup.
- `references/okf-ssot-dirty-worktree-cleanup-2026-07.md` — dirty hub worktree cleanup pattern: manifest source candidates, promote only selected current records through a clean `origin/main` worktree, quarantine raw/private/archive dumps, remove duplicate-superseded untracked files only after canonical readback, and return the active hub checkout to clean `main`.
- `references/okf-selective-safe-promotion-review-reduction-2026-07.md` — review-reduction pattern for stale OKF PRs: promote safe/repaired docs, exclude credential-adjacent/private/noisy material, then present only genuine human-review leftovers.
- `references/okf-linear-handoff-2026-07-26.md` — session-specific OKF + Linear handoff flow used during the journal-pe-integration build.
- `references/okf-git-path-repo-relative-2026-07-26.md` — the git_path frontmatter convention with verifier anti-pattern.
- `references/okf-staging-promotion-workflow-2026-07-28.md` — companion to `okf-linear-handoff-2026-07-26.md`: covers the `prismatic-staging-governance` pre-push-hook promotion flow (`feature/<agent>` → `deploy-fresh`, **never** `main` → `deploy-fresh`), with three flow failures documented and the verbatim hook error messages. Worked example: mbgulden/growthwebdev-knowledge standard promotion 2026-07-28.
- `references/platform-gap-audit-pattern-2026-07-26.md` — what to do when Michael asks "what gaps do you see?" The 5-phase audit pattern: surface inventory → tiered classification → stakeholder split → verify-before-claiming → decision-pause discipline. Pairs with §21, §22, §23.
- `references/reference-value-propagation-multi-surface-2026-08-20.md` — when the ask is "update any references for X," the multi-surface value-propagation pattern: sweep OKF hub + skill mirror + all profiles' skills + all SOUL.md system-prompt sources + memory, triage each hit prescriptive/historical/internal, update only prescriptive, re-sync the mirror, verify zero prescriptive stale remain. Pairs with §26.
- `references/shared-hub-concurrent-writer-landing-2026-08-20.md` — landing OKF changes in a hub with a concurrent background auto-regen writer: rebuild from fresh origin/main, verify superset, `--force-with-lease` on your own feature branch only, read back from origin. Pairs with the git-hygiene pitfall.