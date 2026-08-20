---
name: prismatic-core-skill-distribution-ops
description: "Operate Prismatic Engine Core skill/profile/workflow distribution as real API-backed tooling: bundled skills, installed skill stores, dashboard Skills tab wiring, sync/export/import, and ad-hoc verification."
triggers:
  - Prismatic skills tab is mock data
  - wire skills dashboard to real API
  - distribute skills across profiles or computers
  - make skill/workflow sync production ready
  - Prismatic Core skill registry API
  - universal skill distribution
---

# Prismatic Core Skill Distribution Ops

Use this when Michael asks whether skill/profile/workflow distribution is real Core tooling or just local metadata, dashboard mock data, copied Hermes profile files, or instructions.

## Core principle

A skill distribution system is not real until it has all three layers:

1. **Packaged source of truth** — bundled skill packages under the Prismatic Engine distribution, plus user-installed skill stores.
2. **API/tool surface** — gateway endpoints and/or CLI commands that list, inspect, install, uninstall, export, import, and sync skills.
3. **Dashboard truth** — the governance UI fetches live Core APIs; it must not render hardcoded `mockSkills` or stale local assumptions.

Local Hermes profile copies are operator convenience only. They are not the production distribution artifact.

## Current known Core primitives

- `prismatic.skills` manages bundled and installed skill packages.
- Bundled skills live under the engine distribution, typically `prismatic/skills/<skill>/`.
- Installed skills live under `~/.prismatic/skills/<skill>/`.
- CLI shape:

```bash
prismatic-engine skills list
prismatic-engine skills list --installed
prismatic-engine skills info <name>
prismatic-engine skills install <name>
prismatic-engine skills uninstall <name>
```

## Gateway API contract

The Skills dashboard should be backed by real API endpoints:

```text
GET  /api/skills
GET  /api/skills/{name}
POST /api/skills/{name}/install
POST /api/skills/{name}/uninstall
```

Expected behaviors:

- `GET /api/skills` returns `source: "prismatic.skills"`, bundled count, installed count, and skill cards with `installed` and `status`.
- install succeeds for bundled skills and returns `409` when already installed.
- uninstall removes from the user skill store and returns `404` for missing installed skills.
- unknown skill info/install/uninstall returns `404`.

## Dashboard wiring rules

- Search dashboard templates for `mockSkills`, hardcoded capability cards, and non-awaited `renderSkillsView()` calls.
- Replace mock rendering with `fetch("/api/skills")`.
- Install/uninstall buttons should call `/api/skills/${encodeURIComponent(skillId)}/${action}` with `POST`.
- The UI should render loading, empty, and API error states so operators can distinguish “no skills” from “registry API broken.”

## Verification contract

When changing this class of functionality, create a focused `/tmp/hermes-verify-*.py` script and report it as **ad-hoc targeted verification**, not suite green.

The verifier should:

1. Check changed paths exist.
2. Run `py_compile` on gateway/API modules and tests.
3. Run focused tests for the Skills API.
4. Inspect dashboard HTML to prove mock data is gone and live API fetch/action routes exist.
5. Use `tempfile.TemporaryDirectory(prefix="hermes-verify-core-skills-home-")` and set `HOME` to it before API install/uninstall tests, so real `~/.prismatic/skills` is not mutated.
6. Exercise list/info/install/duplicate-install/uninstall/unknown-404 paths through `fastapi.testclient.TestClient`.
7. Remove the verifier script in a `finally` block and mention cleanup.

## Agent-neutral discovery layer

When Michael asks whether skills/workflows should work across Hermes, AGY CLI, OpenClaw, or future high-agency runtimes, do **not** solve it by hand-editing one `soul.md` or copying profile files. Prefer a packaged Core discovery layer:

```text
packaged manifest → Python module → CLI/API → generated AGENTS.md/soul.md managed block
```

Recommended contract:

```text
prismatic/agent_context/manifest.yaml
prismatic.agent_context::{load_manifest,list_context_cards,render_context_lines,install_context_doc}
prismatic-agent-context line --agent agy|hermes|openclaw
prismatic-agent-context install-doc AGENTS.md --agent hermes
GET /api/agent-context?agent=agy
GET /api/agent-context/line?agent=hermes
```

The generated markdown block should preserve human-authored content and replace only the managed `PRISMATIC_AGENT_CONTEXT` block. This gives every agent a compact capability pointer without creating drift between Hermes skills, AGY workflows, OpenClaw prompts, and future standards.

See `references/agent-context-discovery-layer.md` for the worked pattern and verifier contract.

## Reference index

- `references/agent-context-discovery-layer.md` — agent-neutral discovery layer pattern + verifier
- `references/skills-tab-live-api-wiring.md` — dashboard mock-data audit + live API wiring
- `references/agent-completed-work-skill-packs.md` — portable completed-work skill-pack contract
- `references/skills-agent-context-timeline-audit.md` — timeline audit verification
- `references/cross-profile-skill-adoption-symlink-loop.md` — case study: the source-profile trap in `os.symlink` adoption loops. **Load before writing any script that distributes one source to N target profiles.**
- `references/agy-scratch-packet-review-recipe.md` — 6-step recipe for reviewing AGY-authored scratch packets (verify scratch matches on-disk; fixture-harness + schema-validate + bidirectional mutation suite; dual-tree sync; registry discovery; mode-bit check). **Load whenever a worker announces a skill is deployed to `scratch/`.**

## Audit-first workflow for skill system changes

Before modifying the Skills system, audit existing skill setup and recent agent-owned changes instead of overwriting them:

```bash
git branch -a --list '*kai*' '*skill*' '*agent-context*'
git log --all --oneline --author='Kai' --since='90 days ago' -- prismatic/skills.py prismatic/gateway/server.py prismatic/gateway/templates/dashboard.html prismatic/agent_context.py tests
git log --all --oneline --grep='kai.*skill\|skill.*kai\|agent-context\|agent context\|skills tab' --regexp-ignore-case --since='90 days ago'
```

If no relevant Kai/agent changes exist in the checkout, preserve the existing `prismatic.skills` primitives and wire around them. If relevant changes do exist, integrate them first, then add Fred-owned API/dashboard/timeline wiring.

## Audit timeline requirement

Skill capability changes are not done until they are auditable:

```text
POST /api/skills/{name}/install      → source=SkillRegistry, title=Skill installed
POST /api/skills/{name}/uninstall    → source=SkillRegistry, title=Skill uninstalled
POST /api/agent-context/install-doc  → source=AgentContext, title=Agent context doc installed
```

Verification must prove the timeline filters show those events:

```text
/api/timeline?source=SkillRegistry
/api/timeline?source=AgentContext
```

Keep tests isolated with both `HOME` and `PRISMATIC_STATE_DIR` temp dirs so real `~/.prismatic/skills` and real timeline state are never mutated.

See `references/skills-agent-context-timeline-audit.md` for the worked verification contract.

## Agent completed-work skill-pack contracts

When Michael asks to wire shared/agent-specific completed-work skill packs, prefer a repo-level contract/docs/static-verifier slice unless he explicitly asks to mutate live Hermes profiles. This documents the portable packet contract without claiming agents are retrained or skills are installed everywhere.

Recommended artifacts:

```text
docs/agent-skill-packs/completed-work-skill-packs.md
tests/test_agent_skill_packs_static.py
```

The static verifier should prove:

```text
shared_contract_exists=true
agy_packet_example_has_source_path=true
proof_packet_example_has_command_result_log_scope_nonclaims_marker=true
non_claims_example_present=true
agent_specific_skill_matrix_present=true
no_secrets_in_docs=true
```

Keep non-claims explicit: no live profile installation, no agent retraining, no overnight/automerge/production claims. See `references/agent-completed-work-skill-packs.md`.

## Next production slices

After local list/install/uninstall, agent-context discovery, timeline audit, and repo-level completed-work skill-pack contracts are real, the next universal distribution layer should add:

```text
GET  /api/skills/status
POST /api/skills/sync
POST /api/skills/export
POST /api/skills/import
GET  /api/skills/conflicts
```

Those future sync/export/import/conflict endpoints must also emit timeline events so governance history shows who changed capability state and when.

## Pitfalls

- Do not claim the Skills tab is wired because a tab exists in the dashboard. Inspect whether it uses live API data.
- Do not mutate real user skill stores during tests; isolate `HOME`.
- Do not call copied Hermes profile skills “universal distribution.” Package data + Core API/CLI is the portable layer.
- Do not blur ad-hoc verifier output into full suite-green.

### Manifest contract: `manifest.yaml` ≠ SKILL.md frontmatter

**The bug.** A worker (e.g. Antigravity, the closeout-contract skill) authors a new skill under `prismatic/skills/<name>/` with `SKILL.md` carrying YAML frontmatter (`name`, `version`, `description`, `category`). It looks complete. But the engine's `/api/gateway/skills` endpoint calls `prismatic.skills.list_skills()` → `_load_manifest(skill_dir)` which requires `<skill_dir>/manifest.yaml` to exist and parse. **A skill without `manifest.yaml` is invisible to the registry**, regardless of how polished its `SKILL.md` is.

**The reference shape** is `prismatic/skills/code-review/manifest.yaml`:

```yaml
name: <skill-name>
version: <semver>
description: <one-line>
author: Prismatic Engine
category: <existing-category>
labels: [agent:<target>]
config:
  <skill-specific keys>
```

`SKILL.md` is the operator-facing readme; `manifest.yaml` is the registry-facing identity. Both are required for activation. A skill with only one of them is half-built.

**Live transcript (2026-08-04, fred profile, closeout-contract v0.2 review).** Antigravity shipped SKILL.md + schema + validator + examples under `prismatic/skills/prismatic-agent-closeout-contract/`. `/api/gateway/skills` returned only the 3 originals (code-review, docs-generator, research-synthesizer). The skill was on disk, fully validated, fully fixture-tested — and the engine had no idea it existed. The blocker was caught in step 5 of the scratch-packet review recipe; the fix was to author `manifest.yaml` matching the code-review shape, plus `README.md` for the operator-facing card, and re-run the sync.

**The corollary.** Whenever a worker reports a new skill "deployed" or "live," the activation gate is not satisfied until `/api/gateway/skills` lists it. If you cannot find the skill there, the skill is not activated. Look at `_load_manifest()` in `prismatic/skills.py` to confirm what the registry actually expects before authoring a manifest by guess.

### Mode bits on `scratch/` files

Files written to `/home/ubuntu/work/prismatic-engine-stable/scratch/` land with the calling process's umask. On hermes-webtop that is `0600`, not `0644`. Antigravity's stated convention is `0644` files / `0755` dirs. **If a file Fred is expected to read is not world-readable, it is invisible.** Every verifier for a scratch-packet review must check `stat.S_IMODE(st.st_mode) == 0o644` (or `0o755` for directories), not just file existence.

### Cross-profile skill adoption: the source-profile trap

**The bug.** When adopting shared skills onto multiple profiles via `os.symlink`, the most natural target list is "all running profiles." The most natural source is the orchestrator's `skills/<category>/<skill>/` directory. If the orchestrator appears in the running-profiles list, the adoption loop will:

1. Read `dst = profiles/orchestrator/skills/<category>/<skill>/` (existing real directory).
2. Call `dst.unlink()` to "clean" before creating the symlink. **The unlink fails with `IsADirectoryError` because it's a real directory, not a symlink.** Naïve code does `shutil.rmtree(dst)` instead — which succeeds and **deletes the canonical source**.
3. Create `os.symlink(<source>, dst)` where `<source>` is the path just deleted. The symlink now points to itself, producing `Too many levels of symbolic links` and breaking every other profile's symlink that referenced the same canonical source.

**Live transcript (2026-07-27, fred profile, while trying to adopt session-state-handoff + proactive-execution-discipline across running profiles).** The orchestrator appeared in `hermes profile list` filtered for `running` gateways. The adoption loop iterated over it. The result: 6 profile adoption symlinks broken, the canonical SKILL.md files destroyed, and a 6-turn rebuild required.

**The fix (always).** When the source list and the target list overlap, **explicitly exclude the source profile from the target set**. The canonical rule is:

```text
source = "<a single profile whose skill dir is the source of truth>"
target = "every other profile, NOT including source"
```

Equivalently, if a skill lives at `profiles/<source>/skills/<category>/<skill>/`, the target list must be `{p for p in profiles if p != source}`. Never let the source be a target of itself. The cleanest way to enforce this is at script construction time, not in a runtime check.

**The deeper lesson.** `os.symlink(src, dst)` is a destructive operation when `dst` is a real directory: the deletion of `dst` is implicit in "replace existing." Any adoption/dedup/copy script that uses symlinks MUST treat "destination is a real directory" as a hard-stop error before unlinking, not as a cue to delete and replace. The check is `if dst.is_dir() and not dst.is_symlink(): raise SystemExit("refusing to delete a non-symlink directory")`.

**The recovery pattern when the bug has already fired.** Stop the script. Inspect the symlink graph with `find <profile>/skills -type l -exec ls -la {} \;` to identify the cycle. Do NOT delete the symlink blindly — that destroys the only copy of the source. Instead, restore the canonical source from the conversation transcript (the original `write_file` content), then re-run the adoption with the source profile excluded. The 2026-07-27 case study is at `references/cross-profile-skill-adoption-symlink-loop.md` for the full transcript and the corrected adoption helper.

**Why this belongs here, not in `hermes-agent`.** `hermes-agent` covers operational diagnosis (gateway lockouts, profile discovery, model routes). Cross-profile skill adoption is a packaging concern that lives with the distribution layer. The umbrella is where future-self looks when shipping a skill to multiple profiles.
