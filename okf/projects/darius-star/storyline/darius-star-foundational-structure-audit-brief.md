---
type: Reference
title: "Darius Star — Foundational Structure Audit Brief"
description: "AGY research brief — dependency graph audit of darius-star to identify missing modules, files, and structural gaps."
resource: okf/projects/darius-star/storyline/darius-star-foundational-structure-audit-brief.md
tags: [darius-star, storyline, game-design, narrative, world-building]
timestamp: 2026-06-19T12:10:56Z
linear_issue: null
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/storyline/darius-star-foundational-structure-audit-brief.md
last_verified: 2026-08-19
verified_by: kai
status: current
migrated_from: "/tmp/darius-star-audit-brief.md"
migrated_from_repo: mbgulden/darius-star
---
# AGY Research Brief: Darius Star Foundational Structure Audit

## Goal
Map the COMPLETE dependency graph of darius-star and identify all missing modules, files, and structural gaps. Produce a prioritized build plan.

## Context
- darius-star is an 8000-line canvas shoot-'em-up in a single index.html
- index.html references 8 external .js files — but only 3 exist on disk (upgrade_system.js, combo.js, banter_engine.js)
- 5 are MISSING: save_system.js, economy.js, multiplayer.js, ngplus.js, leaderboard.js
- The AGENTS.md claims these are "already extracted" — they're not
- Jules is currently extracting 7 MORE modules from index.html (player, enemies, combat, renderer, sprites, audio, UI)
- The game needs EVERY referenced file to exist before those extractions can work

## Files to Read
1. `/home/ubuntu/work/darius-star/index.html` — grep for ALL function calls and class references to the missing modules
2. `/home/ubuntu/work/darius-star/AGENTS.md` — the project rules
3. Any existing .js files in `/home/ubuntu/work/darius-star/` to understand patterns

## Questions to Answer
1. What functions/classes does index.html expect from each missing module? Search for all references like `saveSystem.`, `Economy.`, `Multiplayer.`, `NGPlus.`, `Leaderboard.`
2. Are there inline fallbacks in index.html when these modules fail to load?
3. What's the dependency order? (e.g., does economy.js need combo.js?)
4. What globals does each missing module need access to?
5. What directory scaffolding is missing? (js/, tools/, tests/)

## Output
Write `/home/ubuntu/work/darius-star/docs/foundational-structure-audit.md` with:

### Section 1: What Exists
- Every file on disk (type, size, purpose)
- Every script tag in index.html with EXISTS/MISSING status

### Section 2: Missing Module Specifications
For each of the 5 missing modules:
- Exact function/class signatures needed
- Globals it depends on
- Globals it must expose
- Priority (Critical/High/Medium)

### Section 3: Dependency Graph
- Load order diagram
- Which modules depend on which

### Section 4: Build Plan
- Prioritized list of what to create, in what order
- Estimated effort per item
- Which agent should build each (Jules for code, AGY for design/docs)

### Section 5: Directory Scaffolding Needed
- Exact mkdir commands
- File placement map

CONSTRAINT: Do NOT write code. Do not modify any existing files. This is a PURE RESEARCH task. Only write the one output file.
