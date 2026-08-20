# Workspace-tree deep-link contract + workspace_id typo false alarm (2026-08-20)

Session detail from the HFG guest-fleet review-packet handoff.
**CORRECTION of the predecessor version of this file (titled "…review-link-400-and-gateway-sot…"):
the "strict registry flake / gateway regression" story was a false alarm. The 400s were a
hand-typed `workspace_id` with the wrong zero-count. The gateway and its strict registry
were healthy the entire time.** This file keeps the still-valid lessons (runtime SOT,
verify-the-link, link+tarball complements) and records the corrected root cause and the
canonical deep-link contract.

## What happened (corrected timeline)

1. Packet written to `hd-platform-staging/review-packets/hfg-guest-fleet-2026-08-20/`.
2. First probe used the API shape from a STALE worktree copy of the gateway (`?file=`
   param) → 400. Correct signal: the deployed build's preview API takes
   `workspace_id`+`path`.
3. Deployed gateway identified properly: pid on `:9000` → `ls -l /proc/<pid>/cwd`
   = `/home/ubuntu/work/prismatic-engine`; env
   `PRISMATIC_WORKSPACE_REGISTRY_FILE=~/.prismatic/config/workspace-registry.json`.
   Registry holds 4 workspaces; IDs are `ws-` + 32 hex chars (e.g. Work Repositories
   = `ws-0000000000000000000000000002`, length 35 total), validated by
   `WORKSPACE_ID_RE = ^ws-[0-9a-f]{32}$` in `prismatic/gateway/workspace_tree.py`.
4. **The mistake:** test commands hand-typed the ID with a wrong zero-count (28-hex
   body). Every subsequent `400 invalid workspace identifier` — local AND public,
   "for minutes", on what were believed to be "valid" inputs — came from reusing that
   bad literal. `/api/workspaces` kept listing the 4 real IDs, which read like
   "list vs resolve disagree = registry flake". It was not.
5. **Decisive unit-level repro** (gateway venv, gateway's env vars):
   `WORKSPACE_ID_RE.fullmatch` = True for all 4 IDs read from the registry file;
   `load_registry()` + `reg.resolve(id)` succeeds for all 4; only the hand-typed
   33-char literal fails. And the one API run that **fetched the ID from
   `/api/workspaces` and fed it back programmatically** returned 200 with exact
   packet bytes — 6/6, public + local.
6. **The correct surface (Michael supplied):**
   `https://prismatic.growthwebdev.com/workspaces?file=<workspace-relative-path>`
   → `307` → `/dashboard?file=…#workspaces`. The SPA detects `?file=` on load,
   switches to the Workspaces tab, and calls `/api/workspace-tree/resolve?file=…`
   where the **server** picks the owning workspace (no hand-typed ID at all), then
   auto-opens the preview. Verified end-to-end: 307 chain, resolve 200 + correct
   relative path, preview 200 + exact byte-match — local and public, 2× each,
   folded into the 23/23 ad-hoc verifier.
7. The earlier "offer a separate infra fix" decision was retracted in writing
   (Linear correction comment on GRO-4797). No gateway/registry change was needed.

## Rules

- **Never hand-type a `workspace_id`.** The strict regex
  `^ws-[0-9a-f]{32}$` rejects a one-zero typo with the exact same message as a real
  registry failure. Always either (a) fetch the ID from `/api/workspaces` and feed
  it back programmatically, or (b) use the canonical `?file=` deep link and let
  `/api/workspace-tree/resolve` pick the workspace.
- **A 400 on hand-typed input is your typo until proven otherwise.** Before
  suspecting the registry, repro at the unit level in the gateway venv with the
  gateway's env vars: `load_registry()` (no path arg — it reads
  `PRISMATIC_WORKSPACE_REGISTRY_FILE` from the env) then `reg.resolve(id)`. If the
  sourced IDs resolve, the "API bug" was your literal.
- **The canonical review-file deep link is `/workspaces?file=<workspace-relative-path>`.**
  The relative path is relative to the OWNING workspace root (for
  `hd-platform-staging/…` files that's `/home/ubuntu/work`). This is the same link
  the server itself emits (307) and the SPA consumes on load — use it, don't
  re-invent `?workspace_id&path` URLs by hand.
- **Verify the link the reviewer will actually fetch:** public domain, the exact
  redirect chain, the resolve API ok, and sha256(preview content) == sha256(disk
  file). "The route exists" or a localhost 200 is not handoff-grade proof.
- **Source of truth for the deployed gateway is the runtime checkout, not the
  worktree:** `pid=$(ss -tlnp | grep ':9000 ' | grep -oP 'pid=\K[0-9]+' | head -1)`
  → `tr '\0' ' ' < /proc/$pid/cmdline`, `ls -l /proc/$pid/cwd`,
  `tr '\0' '\n' < /proc/$pid/environ | grep -iE 'registry|workspace'`. Reading any
  `work/prismatic-<feature>/` copy for deployed behavior is a stale-read trap (it
  produced the wrong first probe here).
- **Handoff link + tarball are complements, not alternatives:** post BOTH. The
  tarball comment carries SHA256 + contents + "verify SHA first, then run §3". When
  the packet changes, rebuild, re-verify, and post ONE authoritative SHA comment
  that names the earlier values stale.
- **When you've misdiagnosed publicly, retract in writing** — a Linear correction
  comment AND the skill/reference update in the same pass. A misdiagnosed
  "production incident" that was actually your own input error wastes user trust
  and can spawn an unneeded infra-fix task.

## Final state (HFG guest-fleet packet)

- Link: `https://prismatic.growthwebdev.com/workspaces?file=hd-platform-staging/review-packets/hfg-guest-fleet-2026-08-20/REVIEW_PACKET.md`
  — verified 23/23 ad-hoc (incl. 6 deep-link checks, local + public).
- Tarball: `/home/ubuntu/hfg-guest-fleet-2026-08-20-for-review.tar.gz`,
  SHA256 `432fcb76788b446b1e83163239dda7fc8cb38f9c74c47c87e2d0d4c7ac13e485`
  (the single authoritative value on GRO-4797; earlier values superseded).
