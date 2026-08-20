# Distribution Readiness / First-User Gate Pattern — 2026-07-08

## When this applies

Use this when a Golden Thread / Proof Loop task asks for a public/private-demo readiness gate, first-user install path, package metadata audit, or `Done means exit-criterion evidence` for a distribution/publishing decision.

## Proven workflow

1. **Confirm the explicit exit criterion first**
   - If Linear is unavailable/rate-limited, use the offline task bundle or previously saved issue description.
   - Do not claim Linear evidence posting if cooldown/rate-limit is active; write a Linear-ready evidence comment locally.

2. **Lock before editing Prismatic repo files**
   - Use the swarm lock protocol for every repo file touched.
   - Work on a `feature/` branch.
   - Commit with `[Fred] ... (#ISSUE)`.

3. **Build a single readiness gate script**
   - Put it in `scripts/distribution_readiness_smoke.py` or equivalent.
   - Required checks:
     - pyproject package name/readme/license consistency.
     - LICENSE file matches declared license.
     - README has a first-user path and no Michael-only `/home/ubuntu` assumptions.
     - package-data includes shipped `skills`, `templates`, and `config` directories when present.
     - every `[project.scripts]` entrypoint imports.
     - Dockerfile license/COPY sources/entrypoint are coherent.
     - systemd/operator docs are clearly optional, not first-user requirements.
   - Add `--fresh-install` mode that copies the repo to a temp checkout, creates a venv, runs `pip install .`, verifies each console script `--help`, and imports the package.

4. **Let the gate expose real P0s and fix low-risk contradictions**
   - In the session this pattern came from, the gate caught:
     - README used `/home/ubuntu` and internal/TBD license language.
     - Dockerfile copied missing `config/`.
     - `pyproject.toml` omitted `prismatic/config/**/*` package data.
     - `prismatic-engine-skills --help` failed because `cli_skills()` required an arg despite console-script invocation passing none.
   - Fix these if low-risk, then rerun the gate.

5. **Separate targeted gate green from full-suite green**
   - Readiness gate PASS is an ad hoc targeted verification unless the canonical suite also passes.
   - If canonical tests fail on unrelated/stale collection errors, report that bluntly as a separate blocker and do not call the whole repo green.

6. **Save or post evidence, then close only the exact proven child**
   - Save root/fresh smoke outputs under `artifacts/distribution-readiness/`.
   - Save a `linear-evidence-comment.md` that can be posted later if Linear is unavailable.
   - Include: commands, exit codes, files changed, scope label, cleanup status, blockers.
   - When Linear is available, post evidence to the parent epic and the exact child issue whose exit criterion was satisfied.
   - Resolve the child list from Linear before moving state; do not assume the top child ID from memory.
   - Move only that child to a completed state after evidence posts. Do **not** move the parent epic until each sibling child has explicit evidence/closeout.

7. **Use schema-correct Linear closeout if helpers fail**
   - If helper functions fail with HTTP 400 resolving `GRO-*`, do one direct GraphQL lookup using `issue(id: "GRO-####") { id identifier title state { name } team { states { nodes { id name type } } } }`.
   - Pick the completed workflow state by `type == "completed"` (or the closest Done-named completed state, e.g. `Done - Doc Pending`).
   - Post the comment by internal `issueId`, then update `issueUpdate(id: <uuid>, input: {stateId: <completed-state-id>})`.
   - Verify once with `issue(id: "GRO-####") { identifier title state { name type } }` and stop; do not keep hammering Linear if this schema-correct path fails.

## Verification language

Use language like:

```text
Ad hoc targeted verification: PASS — not canonical/full-suite green.
- python3 scripts/distribution_readiness_smoke.py -> PUBLISHABLE
- python3 scripts/distribution_readiness_smoke.py --fresh-install -> PUBLISHABLE
- /tmp/hermes-verify-* wrapper cleaned up
Canonical suite: <pass/fail separately with exact blocker>
```

## Pitfalls

- Do not rely on README claims. The gate should run actual console scripts from a fresh install.
- **Do not mark Done from a successful commit alone.** Done requires the exit criterion and evidence. For proof-loop epics, post evidence to Linear, resolve the exact child issue from Linear, move only that evidenced child, and leave the parent epic open until sibling tasks have their own closeout.
- Do not burn Linear API during cooldown just to post evidence; save the comment locally.

- If push fails due remote unpack/transfer, report it as a delivery blocker after retrying a safe alternative such as `git push --no-thin`.
