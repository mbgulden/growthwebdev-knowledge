# Lane-replacement supersession verification

Session-derived pattern (2026-09-05, F2/F3 re-verification on prismatic-engine). Use when a
stale spec item (foundational-gaps epic, older review finding, handoff `next_action`) names a
mechanism that a later workstream may have **replaced entirely** — e.g. the August "Gold Master"
introduced the Hermes-profiles fleet harness and deleted the codex CLI lane. The correct output
is a *classification* (superseded / partial / still-valid), not "build it" or "fix it".

## Why this class exists

Spec docs and handoffs go stale. Re-deriving an old item without checking the current tree
produces two failure modes: (1) rebuilding a lane that already has a live replacement, and
(2) misreading a dead registry entry as a crash risk (or a live lane as dead). Both were
encountered: `registry.json` still listed `codex-cli -> prismatic.harnesses.codex_cli` after the
module was deleted — that is dead config, not an import crash.

## Recipe (verified 2026-09-05 against `origin/main`)

Run everything against `origin/main` after `git fetch origin`, never the local worktree (it can
be dirty/stale; in this session the local checkout had modified artifacts/ screenshots).

1. **Mechanism tree diff.** `git ls-tree -r origin/main --name-only <dir>/` — list what actually
   exists (e.g. `prismatic/harnesses/` = `base.py`, `agy_cli.py`, `hermes/`, `registry.json`).
   The *deleted* module is the supersession signal (`codex_cli.py` gone).
2. **Registry/config enabled flags.** `git show origin/main:<path>/registry.json` — check
   `enabled: true/false` per entry. Disabled entry pointing at a deleted module = **dead config**.
3. **Caller count for the old entrypoint.** `git grep -n "<old_fn>" origin/main -- <pkg>/`
   excluding the def line. Zero real callers (only the def + a static map entry like
   `AGENT_LAUNCHERS["codex"]`) = **vestigial**, not a live lane.
4. **Dynamic-import check.** Confirm whether the registry's `module` string is imported at
   runtime anywhere. In PE it is NOT: gateway `/api/harnesses` returns raw JSON
   (`server.py` ~line 647); `harnesses/__init__.py` imports only the active harnesses. So a
   dangling `module` string cannot crash imports — classify it as dead config, report it as a
   small cleanup item, and do not treat it as a defect.
5. **Self-containment of vestigial code.** Read the def body / `ast.parse` the file. If it only
   uses `subprocess` and never references the deleted module, it is inert — safe to leave or
   clean up in a small PR (which still needs Michael's go-ahead).
6. **Live importability smoke.** Prove main is importable in production:
   `systemctl is-active <gateway unit>; ss -ltnp | grep :<port>; curl -s -o /dev/null -w '%{http_code}' <prod>/{,dashboard,health}`.
   200s = production build imports fine; no import risk to claim.
7. **Stale premise for "canonical runner" items.** If the spec assumed a module/runner that does
   not exist on main (`prismatic/native_crons/` absent), find where the live equivalent actually
   runs (e.g. the `PRISMATIC_NATIVE_CRONS` crontab block executing from a sibling repo
   `prismatic-pe-native-crons`) and classify that checkout's hygiene — branch, `ahead 1`,
   `git status --porcelain | wc -l` (89 dirty files) — as a **durability watch item**, not an
   F-series code gap.
8. **Fleet identity check** for replacement claims: `git show origin/main:<pkg>/agents/registry.py`
   — `CORE_FLEET` listing (fred, agy, kai, george, ned, autobot, swarmproof + dynamic node
   discovery) is the evidence the Hermes-profiles fleet is the dispatch path.

## Reporting shape

- Lead with the classification per item: `SUPERSEDED (replacement live)`, `DEAD CONFIG (no crash
  risk)`, `VESTIGIAL (zero callers)`, `STILL VALID (needs work)`.
- Name the exact residual cleanup items (file + line) and ask for a small-PR go-ahead — do not
  open the PR without it.
- Label the proof class: `ad-hoc targeted verification on post-fetch origin/main + live prod
  smoke`, **not** canonical suite green.

## Pitfalls

- Do not rebuild a replaced lane because a spec doc still names it; check the tree first.
- Do not present a dangling `module` string in a non-imported registry as a crash risk (verified
  inert 2026-09-05) — but do record it as dead config for cleanup.
- Counts in the report (caller count, dirty-file count) come from the exact grep/`wc -l`
  command, not log-view estimation (see session-state-handoff count pitfall).
