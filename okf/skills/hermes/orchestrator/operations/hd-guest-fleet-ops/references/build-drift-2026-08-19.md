# 2026-08-19 fleet unification — session detail

## The incident
"Chart filed under the wrong name" (Michael's test name) on guest HD sessions.
Root cause was NOT the naming code in the template — it was fleet drift.

## Build matrix found
| Build (lines) | Guests | Notes |
|---|---|---|
| 2286 | 2, 3, 23, 29 | oldest; the misfiled charts came from this tier |
| 2594 | 30, 31, 32, 38, 39 | prompt-text drift only |
| 2593 | 40 | wording variants of the 2594 tier |
| 2656 | 42, 43 | matches template (md5 3a4fcc34c1d7327013e8f2c15960cebc) |

10 of 12 had live containers; guests 40 and 42 had workspaces but NO running container.

## Key findings
1. `grep -n "Gulden"` on the template: exactly ONE hit, `Becca Gulden` in the
   Becca-naming branch (~line 1363). `Michael Gulden` was already removed from
   the template in an earlier fix — but 10 workspaces still ran pre-fix copies,
   so the bug stayed live fleet-wide. **Template-clean ≠ fleet-clean.**
2. Feature-level diff (classes/defs/`@app.*` routes) was EMPTY across all four
   build tiers — no container was missing any endpoint. All 370 lines of the
   2286-vs-template gap were prompt text + small logic. Only 6–7 lines per old
   build were unique-to-old, zero guest-specific identifiers → blanket overwrite safe.
3. Some images ship a decoy `/app/guest_agent_server.py` (2281 lines in the
   Jul-16 image); the served file is the `/workspace` mount. Auditing `/app`
   gave a misleading number.
4. Naming fallback in current build: `explicit_name or default_profile.get("name")
   or os.getenv("GUEST_USER_NAME") or "Sanctuary Guest"` — 8 occurrences per file.

## Rollout that worked
- Backups: `guest_agent_server.py.bak-20260819T2100Z` in each updated workspace (10 files).
- Copy template → workspace, `chown 1000:1000`, restart container, verify in-container
  `wc -l` + `/docs` after ~20s (healthcheck start_period 15s).
- All 10 live guests healthy at 2656 lines post-restart.

## Open items (Michael's call)
- Guests 40/42: start containers or leave decommissioned (host files already current).
- Prune the 10 `.bak-20260819T2100Z` files after ~1 week clean, with approval.
