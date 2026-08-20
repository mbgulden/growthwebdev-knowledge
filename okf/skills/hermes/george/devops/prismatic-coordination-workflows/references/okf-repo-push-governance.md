# OKF Repo Push Governance — growthwebdev-knowledge

Class: pushing commits to the `mbgulden/growthwebdev-knowledge` OKF hub
(local `/home/ubuntu/work/growthwebdev-knowledge`) under Prismatic lane governance.
Verified working path 2026-08-19 (PR #27 via `feature/`, PR #28 via `george/`).
George is a registered agent as of 2026-08-19 (Michael authorized George, Fred,
Kai, Ned to commit+push to the OKF; decision record:
`okf/decisions/okf-agent-commit-authorization.md`).

## Hard rules (repo-local pre-push hook, Fred / GRO-2217)

- Hook: `.git/hooks/pre-push` → `scripts/prismatic-pre-push-hook.py`; config in
  `PRISMATIC_ENGINE.yaml` at repo root.
- **Never pushes directly to `main`** — "Production deployments are manual-only.
  Use deploy-fresh for staging, then merge manually." (Rule 5)
- `deploy-fresh` (staging) pushable only by governor `fred`.
- Branch prefix → agent mapping in the hook:
  | prefix | agent | owned lanes |
  |---|---|---|
  | `feature/` | fred | `*` (everything) |
  | `content/` | kai | okf/hubs, okf/standards, okf/projects/*/index.md, okf/audits |
  | `research/` | agy | okf/audits, okf/reports |
  | `jules/` | jules | okf/integrations, README.md |
  | `ned/` | ned | okf/integrations, okf/standards |
  | `george/` | george | `*` (cross-lane review role; registered 2026-08-19) |
- Also checks file locks (`$PRISMATIC_HOME/.antigravity/swarm_locks.json`, 5-min stale TTL).

## Working push flow for George (verified)

1. Commit on local `main` — local commits are fine; the hook only gates push.
2. `git checkout -b george/<topic>-<date>` — George is a registered agent
   (prefix `george/`, `owner: ["*"]`); the hook reports
   `Pre-push OK: george → george/...` with correct agent attribution (PR #28).
   Pre-2026-08-19 fallback: `feature/george-<topic>-<date>` (maps to fred,
   `owner: ["*"]`, files pass but push is attributed to fred).
3. Check out the branch — REQUIRED: the hook resolves the pushing agent
   from the **currently checked-out branch**, not the pushed ref. Pushing a
   branch ref while checked out on `main` fails with "Branch 'main' doesn't
   match any agent prefix."
4. `git push origin george/...` → `✅ [Prismatic Engine] Pre-push OK`.
5. `gh pr create --base main --head george/...` (gh is authed as `mbgulden`
   via GITHUB_TOKEN in this profile).
6. Human merges the PR — "manual-only" means Michael/Fred merges; an agent must
   not self-merge to main without explicit instruction.

### Pre-push verification (before opening the PR)

Run the hook's own functions against the changed files, from the repo checkout:

```python
import importlib.util, sys
from pathlib import Path
sys.path.insert(0, "scripts")
spec = importlib.util.spec_from_file_location("hook", "scripts/prismatic-pre-push-hook.py")
hook = importlib.util.module_from_spec(spec); spec.loader.exec_module(hook)
config = hook._read_yaml_config(Path("."))
agent = hook._determine_agent("<branch-name>", config)          # expect 'george'
owned, violations = hook._check_lane_ownership(files, agent, config)
assert not violations
```

When the YAML itself changes, also assert all 5 pre-existing agents still
resolve (regression) and that `staging.governor` is still `fred`.

### Changing the governance config itself

Adding an agent to `PRISMATIC_ENGINE.yaml` needs **no hook code change** —
the hook is config-driven (`_determine_agent` + `_check_lane_ownership` read
the YAML at push time). Ship together: the YAML block, an OKF decision record
in `okf/decisions/`, and both index updates (`okf/decisions/index.md` + root
`okf/index.md`) — all on a `george/` branch. The live push resolving to the
new agent id is the registration proof.

## Pitfalls

- Never bypass with `--no-verify` — the hook encodes Michael's lane
  governance, bypassing it is a process violation, not a shortcut.
- `main` can be several commits ahead of `origin/main` (observed: Fred's
  deploy-fresh merge + George docs, both unpushed). A feature branch cut from
  main carries them into the PR — flag this in the PR body.
- For a new branch the hook's lane diff is `local~1..local` only; for
  multi-commit branches check `git log origin/main..HEAD` before opening the PR.
- On checkouts lacking `scripts/prismatic-pre-push-hook.py` the hook prints a
  warning and allows the push (convention mode) — silent pass, not a pass.
- Committing uncommitted-but-reviewed batch work: verify frontmatter, relative
  links (`./x.md` resolves against the index file's own directory), and no
  secrets before committing; `verified_by` in frontmatter is the author's
  attestation, not George's — say so in reports.
