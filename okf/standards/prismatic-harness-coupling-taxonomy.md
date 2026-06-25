---
type: Standard
title: Prismatic Harness Coupling Taxonomy
description: 5-bucket taxonomy distinguishing engine-kernel concerns from harness plumbing — the canonical model for classifying journal-setup work.
resource: /home/ubuntu/work/Hermes-Research/reports/journal-continuity-audit/prismatic-coupling-taxonomy.md
tags: [standard, prismatic-engine, architecture, taxonomy]
timestamp: 2026-06-19T10:52:02Z
linear_issue: null
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/standards/prismatic-harness-coupling-taxonomy.md
last_verified: 2026-06-25
verified_by: kai
status: current
migrated_from: /home/ubuntu/work/Hermes-Research/reports/journal-continuity-audit/prismatic-coupling-taxonomy.md
---

# Prismatic Engine — Harness-Coupling Taxonomy

The Prismatic Engine ships two distinct kinds of feature: **engine-kernel** (lives at `$PRISMATIC_HOME`, harness-agnostic) and **harness-only plumbing** (lives wherever the harness lives, configurable per deployment). The taxonomy below defines the five buckets and their acceptance tests. It is referenced by `prismatic-independence-map.md` and any other Prismatic Engine migration.

## The five buckets

### (1) Pure engine-kernel

- **What it is:** the feature runs as a Prismatic Engine CLI/script with zero harness imports. Pure stdlib or engine-blessed third-party deps only.
- **Target location:** `$PRISMATIC_HOME/bin/`, `$PRISMATIC_HOME/specs/`, `$PRISMATIC_HOME/portable-skills/`, or `~/.local/bin/` for the CLI binary.
- **Acceptance test:** after `pip install prismatic-engine` (or `git clone prismatic-engine && make install`) on a fresh VM with no Hermes, OpenClaw, or any other harness installed, the feature works.
- **Examples:** `prismatic-publish`, `prismatic-reply`, the file-reference-resolution spec, the sequenced-agent-workflow schema.

### (2) Engine + thin harness shim

- **What it is:** the engine has a canonical CLI; the harness exposes a ≤ 3-line shim under a harness-specific name for ergonomic reasons.
- **Acceptance test:** the shim is `exec prismatic-X "$@"` (or equivalent 1-liner). It does not re-implement the engine's logic. Removing the shim is safe; the canonical CLI still works.
- **Examples:** `hermes-publish` → `prismatic-publish`, `hermes-reply` → `prismatic-reply`. (Don't add more shims unless they're needed.)

### (3) Harness-only plumbing

- **What it is:** cron, dashboard widgets, profile isolation, OAuth refresh, alert routing, agent identity, plugin registries.
- **Acceptance test:** removing the harness's plumbing stops the harness's scheduling / UI / auth from working, but the engine's feature itself is unaffected. The user wires their own equivalent.
- **Examples:** Hermes dashboard plugin, AGY OAuth auto-refresh, AGY resource monitor, the Unified Agent Dispatcher cron, profile-level PATH symlinks, agent label routing.

### (4) Shared / deferred

- **What it is:** a feature that has both engine-kernel and harness-plumbing aspects, and the boundary isn't clear yet. Listed with rationale.
- **Acceptance test:** a one-paragraph rationale explains the decision. The decision is revisable; the report includes "migrate when" criteria.
- **Examples:** the **contract** for a tunnel + DNS + Access deployment (the engine documents it; the harness deploys it), the **structure** of a project-registry (the engine defines it; the harness fills it).

### (5) Leaves as is

- **What it is:** explicitly out of scope for the engine. The engine has nothing to say about it.
- **Acceptance test:** a one-sentence "why" is required. If we can't write "why" in one sentence, it's not in this bucket.
- **Examples:** user API keys for Linear / Telegram / Slack / Google / GitHub / DeepSeek / OpenRouter (they belong to whatever deployment wires them); agent identity (Fred, Kai, Ned, AGY, Jules CLI — these are Hermes's identity, not the engine's).

## Why this taxonomy exists

Without a clear bucket boundary, every Prismatic Engine feature starts coupled to the harness that wrote it. The taxonomy is the boundary. It exists so a contributor can ask "what bucket is this in?" before they start coding, and so a future maintainer can ask "why is this here?" without guessing.

## How to use this document

1. **Before adding a new feature:** classify it. The classification goes in the Linear issue's acceptance criteria.
2. **Before migrating an existing feature:** check which bucket it belongs in. If bucket 1, migrate. If bucket 3, leave. If bucket 4, decide.
3. **Before reviewing a PR:** verify the changes match the bucket. A bucket-1 PR that adds `os.environ.get('TELEGRAM_BOT_TOKEN')` is wrong. A bucket-3 PR that moves cron scripts to `$PRISMATIC_HOME/bin/` is wrong.
4. **When in doubt:** bucket 4 first. Get a decision. Then move to bucket 1 or 3.

## Reference

- The first concrete application of this taxonomy is in `prismatic-independence-map.md` (GRO-1954), which classifies every component of the journal setup.
- The first bucket-1 migration done with this taxonomy is the file-reference-resolution feature (`prismatic-publish`, `prismatic-reply`, `portable-skills/prismatic-artifact-publisher/`).
