---
type: Standard
title: Kai Architecture — The Recipe (regression-tested 2026-06-23)
description: The complete, tested, working architecture for the Kai agent. Content writing, CSS, JS, AOT-specific work. Lane governance, dispatcher pattern, workdir conventions.
resource: okf/standards/kai-architecture-recipe.md
tags: [standard, kai, architecture, recipe, regression-test, dispatcher, content, css, active-oahu]
timestamp: 2026-06-23T17:00:00Z
linear_issue: GRO-2239
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/standards/kai-architecture-recipe.md
last_verified: 2026-06-25
verified_by: fred
status: current
---

# Kai Architecture — The Recipe (regression-tested 2026-06-23)

> **STOP.** If you are about to change anything Kai-related, READ THIS FIRST.

## TL;DR

Kai handles **content + frontend** tasks. Four labels: `agent:kai`, `agent:kai-content`, `agent:kai-css`, `agent:kai-js`. One dispatcher. Special: Kai's `.gemini` directory was a real dir (now a symlink — see Anti-pattern).

## What Kai owns

| Label | Scope |
|---|---|
| `agent:kai` | General content tasks (blog posts, landing pages, copy) |
| `agent:kai-content` | Content writing specifically (text, copy, structure) |
| `agent:kai-css` | CSS / design system / Tailwind / styling |
| `agent:kai-js` | JavaScript / interactivity / widgets |

## What Kai does NOT own

- Infrastructure (→ Ned)
- Visual assets / image generation (→ AGY)
- Architecture / research (→ AGY)

## The Recipe

### Component 1: Kai dispatcher

**Location:** `~/.hermes/profiles/orchestrator/scripts/kai_delta_dispatcher.py`
**Cron:** `5fe7de2a1d9a` (every 15 min)

Same pattern as Ned (write to /tmp/issue-batches/) but with Kai-specific WORKDIR:

```python
workdir = "active-oahu-tours" if any(l.startswith("agent:kai") for l in labels) else "prismatic"
```

Kai's primary workdir is `active-oahu-tours` (the AOT site), not `prismatic`. The AOT site is Kai's home territory.

### Component 2: Kai agent identity

| Property | Value |
|---|---|
| Agent UUID | `12f0bea3-c9b6-4321-9a8d-5b48b0e8d3a3` (incorrect in earlier docs) → real one in config |
| Default workdir | `active-oahu-tours` |
| Branch prefix | `content/` |
| Linear label | `agent:kai` (or sub-labels above) |

**IMPORTANT: Kai's `.gemini` was a real directory (not a symlink).** When OAuth tokens refresh on the other profiles, Kai wouldn't see the update. **Fix:** `ln -sfn /home/ubuntu/.gemini /home/ubuntu/.hermes/profiles/kai/home/.gemini`. Idempotent script at `~/.hermes/profiles/orchestrator/scripts/fix_kai_gemini_symlink.sh`. **This is documented in GRO-2220.**

### Component 3: Lane governance

Kai respects the same lane governance as Ned. In the AOT repo (Kai's primary workdir), Kai can write to:
- `content/`, `active-oahu/`
- `okf/`
- `README.md`

And read-only:
- `src/`, `infra/`, `deploy/`

## Regression log — every Kai breakage

| Date | What broke | Why | Fix |
|---|---|---|---|
| 2026-06-23 (AM) | Kai dispatcher timing out on 5-min batch invoke | Subprocess.run(timeout=300) for 7+ issues | Write to /tmp/issue-batches/ (commit e0b3b8a) |
| 2026-06-23 (AM) | Kai's `.gemini` was a real dir, OAuth drift | Originally created as a directory, never symlinked | `ln -sfn /home/ubuntu/.gemini .../kai/home/.gemini` (GRO-2220) |
| 2026-06-23 (PM) | Kai content scope creep in PR #8 | 100 files for "add llms.txt" PR | Filed GRO-2225 review, asked for split |

## Recipe for fixing Kai when it breaks

**Step 1: Diagnose.** Check the dispatcher log + check if `.gemini` is a symlink:
```bash
ls -la ~/.hermes/profiles/kai/home/.gemini
# Should be: ... -> /home/ubuntu/.gemini
```

**Step 2: Match symptom to regression log.**

**Step 3: Apply the fix. NEVER re-implement.**

## Change log

- 2026-06-23 17:00 UTC: Initial doc. Kai architecture regression-tested + documented.
