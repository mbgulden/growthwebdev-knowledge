# Skill-hub daily regen cron + sandboxed script verification (2026-08-20)

Session record: post-PR-#33 work — daily regen cron, PR #34 churn fixes, and
the pattern for safely verifying a repo-writing cron script.

## The cron (live)

- Job `okf-skill-hub-regen` (no-agent, `0 7 * * *` UTC, deliver=origin,
  silent-when-clean → empty stdout = nothing sent to Michael).
- Script: `~/.hermes/profiles/kai/scripts/skill-hub-regen.sh`.
- Contract: fetch → ensure clean main at origin/main (stash/restore unrelated
  local edits) → run `scripts/skill-hub-snapshot.py` → **only if `git diff --
  okf/skills/` is non-empty**: commit + push. Push runs WITHOUT `--no-verify`;
  if a push guard blocks, the commit is held LOCAL and the script reports
  "open a PR from <sha>" instead of bypassing. Never add a `--no-verify`
  fallback to a script — it masks guard decisions (hit live: the OKF repo
  accepts direct main pushes, but prismatic-engine's hook blocks; a silent
  fallback made it impossible to tell which guard fired).

## PR #34 churn fixes (why the first version was wrong)

1. **Wall-clock `generated_at` broke no-op stability** — every regen rewrote
   index.md/index.json even with zero skill changes → daily noise commits.
   Fix: derive `generated_at` from `git log -1 --format=%cd --date=short`
   over skill files, EXCLUDING the index files
   (`-- ":(glob)okf/skills/**" ":(exclude)okf/skills/index.json" ":(exclude)okf/skills/index.md"`).
   No-op runs are now byte-identical; the index diff only reflects real
   skill changes.
2. **`.usage.json` is runtime telemetry, not skill content** — it changes on
   every skill use; mirroring it guaranteed daily churn. Excluded via
   `SKIP_FILES` in the generator.
3. **Per-profile marker scheme leaked stale trees** — with a marker per
   profile subdir, a new generator run left removed/renamed profile dirs
   behind (and a top-level `hermes/` wipe didn't fire). Fix: ONE marker per
   source root (`hermes/`, `agy/`, `prismatic/`); the hermes wipe removes ALL
   profile subdirs under the marked root.
4. **`SKILL_HUB_ROOT` env override** on the generator's hub path — required
   for sandboxed verification AND for Phase B portability (engine sync on
   other machines).

## Sandbox verification recipe (for ANY repo-writing script)

Testing a script that commits+pushes to a real repo requires a full git
sandbox — never point it at the real remote:

```python
bare  = SANDBOX / "remote.git";  sh(f"git init -q --bare {bare}")
clone = SANDBOX / "repo";       sh(f"git clone -q <real-hub> {clone}")
sh("git remote set-url origin " + str(bare), cwd=clone)        # redirect origin
sh("git config user.email v@l && git config user.name v", cwd=clone)  # PITFALL A
# give the bare a main: push the branch, then check it out in the clone
sh("git push -q origin <branch>:main && git switch -q main && git pull -q --ff-only origin main", cwd=clone)
# create a REAL diff (no-op scripts exit silently — you need a change to test the commit+push path):
# scratch-edit a mirrored file, commit "sandbox: scratch diff"
# sed the script: replace the real repo path with the clone path;
# if the script calls a generator with a hardcoded hub path, inject
# `export SKILL_HUB_ROOT="$HUB"` AFTER the `HUB=...` line (PITFALL B)
```

Assertions:
- **run 1 (diff present)**: exit 0, HEAD moved, stdout reports the commit,
  AND the scratch edit was reverted (proves the script re-imports live
  content — the registry can't drift from the live stores).
- **run 2 (no changes)**: exit 0, **empty stdout** (silent contract), HEAD
  unchanged.
- **real remote untouched**: capture `git ls-remote origin main` on the REAL
  repo BEFORE the test, assert identical AFTER. **Never assert a static SHA**
  (PITFALL C) — main may have moved legitimately earlier in the session.
- Cleanup: `shutil.rmtree(SANDBOX)`; `git checkout -- <generated dirs>` in the
  real repo if the test ran the generator there.

## Sandbox pitfalls hit (2026-08-20)

- **A**: clone has no git identity → `git commit` fails with "unable to
  auto-detect email address". Set repo-local user.email/user.name.
- **B**: injecting `export SKILL_HUB_ROOT="$HUB"` at the top of a
  `set -u` script → `HUB: unbound variable`. Export AFTER `HUB=` is defined.
- **C**: stale static-SHA expectation for "remote untouched" failed because
  an earlier live test push had legitimately moved main. Use before/after.
- **D**: deleting the sandbox dir that the shell is `cd`-ed into →
  `getcwd: cannot access parent directories` on the next command. cd to a
  stable path before/after cleanup.

## Verification receipts

- Phase A suite: 12/12 (exit, idempotence, json↔disk, per-source 1:1,
  markers, index sections, secrets scan).
- Fixed generator + regen script: **19/19** including the sandboxed run-1 /
  run-2 / remote-untouched checks above.

## Post-merge closeout (2026-08-20, PR #34 merged)

- `pkill` on the per-profile MCP server severs **your own** gateway's stdio
  pool: `mcp_okf_*` → `ClosedResourceError`, then ~15-60s "unreachable"
  cooldown. **The pool auto-heals**: the gateway respawns a fresh server child
  and reconnects — verified live, first MCP call after ~3-4 min succeeded at
  the new head with no gateway restart and no manual action. Do not kill your
  own gateway to fix it (rule 6); just don't block on MCP calls in the
  meantime — on-disk git state is the source of truth for verification.
- Closeout checklist after a skill-hub merge: (1) `git reset --hard
  origin/main` (squash-merge → local main diverges; verify content-identical
  with `git diff --stat <pr-head> origin/main` first), (2) post-merge regen
  on main (expect genuine drift if agents edited skills concurrently — see
  above; restore clean with `git checkout -- okf/skills/ && git clean -fdq
  okf/skills/`), (3) MCP reindex check via `mcp_okf_status` head == merge
  sha, (4) cron job present in `hermes cron list`.
