# OKF Context Pack for AI Build Agents (2026-07-31)

A class-level methodology that emerged from the Review/Merge Factory V1 build (2026-07-31): when the OKF is consumed by an AI build agent (e.g., Antigravity 2.0, AGY) rather than a human reader, the OKF needs a structured **Context Pack** section that the agent can verify-against-state without inventing context.

## Why this is a new pattern

Human-oriented OKF docs assume the reader can `git grep` for missing context, ask in chat, or browse. AI build agents can't reliably do that — they get a prompt, then start building. If the OKF doesn't hand them verified file paths, live API endpoints, exact git SHAs, and concrete anti-patterns, the agent *will* invent context, find stale local checkouts, or skip the verification step.

The Review/Merge Factory V1 OKF shipped with a 12-sub-section Context Pack (§16) and the build went from "Michael worried AGY would miss things" to "OKF is Antigravity-ready with zero ambiguity on file paths, APIs, SHAs, and acceptance markers."

## The Context Pack sub-sections (proven shape)

1. **Canonical file paths** — orchestrator profile paths (7) and target-repo paths (17). Group by purpose. Mark which paths are the OKF itself, which are sibling OKFs, and which are target-repo source files.

2. **Live API endpoints** — group by surface (intake, plugins, agents, health). Show the exact path strings. Note which ones RF-N will reuse as a pattern (e.g., "RF-1 ingestion reuses the `/api/plugins/jobs` shape").

3. **Live git SHAs** — every SHA the agent might need (PR merge commit, base SHA, branch tip, related PRs, lane-owner review-fix commits). Include a note when a SHA is "verify against `origin/main`" vs "fixed value as of OKF write."

4. **Live Linear state** — project ID, parent epic ID, current task states, owner user IDs (with displayName for `@mention`). Note which IDs are entry-point-only vs lane-owner-authoritative.

5. **Live environment** — working dir, profile dir, state dir, default DB paths, Python version, test framework, lint version, CI workflow. **Include the fresh-clone command** if the local checkout is stale (this caught me — `/home/ubuntu/work/prismatic-engine/` was on `ned/GRO-4195` and missing files that existed on `origin/main`).

6. **Build conventions** — commit message format, branch naming, pre-commit hook, test isolation, immutability rules, lane scope. One row per convention + where it's enforced.

7. **Anti-patterns (10 numbered)** — concrete "do NOT do this" list. Each item names a specific failure mode that the agent is likely to repeat. Anti-patterns are more durable than conventions because they capture the *failure shape* not the *correct shape*.

8. **Spec-freeze deliverables with exact file destinations** — a literal directory tree showing where the spec docs land. Include the acceptance marker command for the freeze itself.

9. **Acceptance marker verification commands** — for each RF slice, the exact command pattern that proves the marker (`PE_REVIEW_FACTORY_*_OK`). Run from the canonical working dir.

10. **Debugging tips** — symptom → first-check table. 7 rows minimum. Each row is a "stuck at X, do Y first" mapping.

11. **"Did I miss anything?" checklist** — 11-item checklist the agent must run before declaring any RF slice done. The checklist is the gate.

12. **Quick-reference card** — a printable ASCII box summarizing build owner, source repo, base branch, ownership table, do-not list, verification commands, and current state. Agents read this last as a refresher.

## Verification step (the agent must do this before signing off)

Before declaring the OKF Context Pack complete, the agent (or the author) runs:

```python
import os
referenced = [list of every path in the Context Pack section]
for p in referenced:
    assert os.path.exists(p), f"missing: {p}"
print(f"all {len(referenced)} referenced paths resolve")
```

If any path is missing, **the OKF is wrong**, not the path. Fix the OKF to point at the real location. The failure modes that hide here:
- Stale local checkout (path exists on `origin/main` but not in local working tree)
- Documented path is the dir, file is one level deeper (use `os.path.exists` on the exact string)
- Case sensitivity on macOS vs Linux (the OKF server is Linux; write Linux paths)

## Why this works for AI build agents specifically

| Human OKF reader | AI build agent |
|---|---|
| Can `git grep`, ask in chat, browse | Has the prompt + tools, no chat |
| Will notice when a path looks stale | Will write code against the stale path |
| Will forgive "see the dashboard tab" without a route | Will silently build the wrong route |
| Reads conventions as reminders | Reads them as the source of truth |
| Tolerant of "TBD" placeholders | Will invent content for "TBD" |

## Companion: OKF Linear-handoff shape

After the Context Pack is verified, the agent (or author) creates the Linear epic tree per `linear-handoff-build-out`. The Context Pack does NOT duplicate the Linear tree — they're different surfaces:
- Context Pack = "what the agent needs to know to build" (in the OKF, read by agent before coding)
- Linear tree = "what tasks get dispatched and reviewed" (in Linear, read by reviewer before approving)

Both surfaces need the **same** acceptance markers + ownership + verification commands, but they serve different audiences.

## Worked example

`/home/ubuntu/.hermes/profiles/orchestrator/state/okf-review-factory-v1.md` §16 (the Review/Merge Factory V1 OKF) is the canonical instance. 12 subsections, 25 verified file paths, 12 API endpoints, 6 git SHAs, 10 anti-patterns, 11-item checklist, 7 acceptance-marker commands. The OKF author verified every referenced path with `os.path.exists` before signing off.

## Pitfalls

- **Don't trust "I'll fix that path later"** — every path in the Context Pack must exist at OKF write time. If a path doesn't exist, either wait for the upstream to land or remove the reference.
- **Don't add sections the agent won't use** — if the agent won't run a CLI, don't include CLI commands in the verification table. Match the Context Pack to the agent's actual capabilities.
- **Don't include "TBD" placeholders** — every entry must be concrete. If you don't know the value, look it up before writing the OKF.
- **Don't duplicate the Linear tree in the Context Pack** — they're different surfaces with different audiences. The Context Pack is for the builder; the Linear tree is for the reviewer.
- **Don't skip the verification step** — `os.path.exists` on every referenced path is the gate. Without it, the OKF is a wish list, not a spec.

## Related references

- `references/okf-linear-handoff-2026-07-26.md` — companion for the Linear half of the handoff
- `linear-handoff-build-out` — the skill that defines the Linear tree shape
- `okf-documentation-ops` §16 — the OKF + Linear handoff flow