---
name: hermes-profile-audit-and-prune
description: Audit and safely prune dormant Hermes profiles in a multi-agent fleet. Classify live / identity-symlink / dormant-empty / dormant-data / dormant-secrets, find every reference before deleting (systemd, prismatic agents.yaml, ops scripts, cron), tar-backup, delete units then profiles, and verify. Use when Michael asks "can we delete profile X", "which profiles are unused", "clean up the fleet", or after a bot-token rotation leaves orphaned profile state.
category: devops
tags: [hermes, profiles, cleanup, systemd, fleet-hygiene]
related_skills: [telegram-bot-onboarding-operations, worktree-hygiene-and-cleanup-safety]
---

# Hermes Profile Audit & Prune

Fleet sprawl is the norm: a real 26-profile fleet contained only 6 running gateways. "Delete the unused ones" is a recurring ask that looks simple and has three ways to go wrong: deleting an identity symlink, deleting a profile an ops script references, or deleting data Michael still wants. Audit first, back up everything, delete units before profiles.

## When to use
- Michael asks to delete a profile or "all the unused profiles".
- A token rotation (see `telegram-bot-onboarding-operations` rogue-poller section) left orphaned profiles carrying the old token.
- The profiles dir has grown past ~10 entries and nobody can say what's alive.

## Classification axes — run ALL five before classifying anything

```bash
PROFILES=/home/ubuntu/.hermes/profiles
# 1. Running processes
ps aux | grep -E "gateway run|hermes --profile" | grep -v grep | grep -oE "\-\-profile [a-z0-9_-]+" | sort -u
# 2. systemd units
grep -l "profile" /etc/systemd/system/*.service | while read f; do
  refs=$(grep -ohE "\-\-profile [a-z0-9_-]+" "$f" | sort -u | tr '\n' ' ')
  [ -n "$refs" ] && echo "$f: $refs"; done
# 3. Hermes cron jobs per profile
for d in $PROFILES/*/; do [ -f "$d/cron/jobs.json" ] && echo "$(basename $d): $(python3 -c "import json;print(len(json.load(open('$d/cron/jobs.json'))))") jobs"; done
# 4. Prismatic bus agents (the one that surprises people)
grep -n -A4 "^[a-z-]*:" /home/ubuntu/.prismatic/repos/prismatic-engine-control/config/agents.yaml
# 5. Ops scripts hardcoding profile paths (scoped — see pitfall on grep timeouts)
grep -rl "profiles/<name>" /home/ubuntu/work --include="*.py" --include="*.sh" | head
```

Plus per-profile data value: `ls -ld` (symlink detection), `du -sh`, presence of `state.db`/messages DBs, `memories/` count.

## Buckets
| Bucket | Rule |
|---|---|
| LIVE | running process or active unit → never delete |
| IDENTITY-SYMLINK | profile dir is a symlink to another profile (e.g. `fred -> orchestrator`). The link is often the agent's *entire* identity — prismatic bus workers and ops scripts resolve through it. Delete the **dead units that make it dangerous**, not the link |
| DORMANT-EMPTY | no DBs/memories, no references → delete |
| DORMANT-DATA | has state DBs or memories → present to Michael for per-profile call, never auto-delete |
| DORMANT-SECRETS | still carries a rotated/shared token → scrub the token from its `.env` even if the profile is kept — starting any of those gateways re-ignites the polling conflict |

## Fleet health audit — "is anything broke in the profiles/configs?"

Distinct recurring ask from deletion. Config layer is cheap: loop `hermes --profile <p> config check` over every profile; unset optional env vars (e.g. `DINGTALK_*`) are informational, not errors — grep for `error|invalid|fail|✗`, not every `○` line. The real findings live in process/systemd mismatches:

```bash
# 1. Every running gateway PID and its unit ownership
for pid in $(pgrep -f "hermes_cli|gateway run"); do
  cmd=$(tr '\0' ' ' < /proc/$pid/cmdline); echo "$cmd" | grep -q "gateway" || continue
  ppid=$(awk '{print $4}' /proc/$pid/stat 2>/dev/null)
  unit=$(grep -oE "system.slice/[^ ]+" /proc/$pid/cgroup 2>/dev/null | head -1)
  prof=$(echo "$cmd" | grep -oE "\-\-profile [a-z0-9-]+"); echo "$pid $prof ppid=$ppid unit=${unit:-NONE}"
done
```

- **Orphaned gateway:** `hermes profile list` "running" is process-level truth — it shows running even when the owning unit died. A gateway PID with `ppid=1` and no `system.slice/<unit>` cgroup has NO auto-restart and NO journald logs: it was started by hand after its unit died and will silently die on the next crash. Fix: start the correct unit, verify its gateway is up, then signal the orphan PID (never `systemctl restart` from inside a running gateway — see restart-safety rules in the `hermes-agent` skill).
- **Stale failed unit stubs:** `systemctl list-units --state=failed` can list units with `Loaded: not-found` — deleted/renamed unit files with stale state. Harmless; clean with `sudo systemctl reset-failed <unit>`.
- **Failed timers adjacent to profiles** (curator digests, telemetry pollers) surface in the same `--state=failed` sweep — report them separately; they're not profile defects but Michael asks "anything broke?" and expects the whole board.

## Safe deletion procedure
1. **Back up first, always** — even the "empty" ones:
   `tar czf /var/tmp/profiles-cleanup-$(date +%Y%m%d).tgz -C $PROFILES <list of names>`
   Confirm non-empty size.
2. **Units before profiles.** Non-root `systemctl stop/disable` fails with "Interactive authentication required" — use sudo (Ned has passwordless sudo; check with `sudo -n true`):
   `sudo rm -f /etc/systemd/system/<unit>.service && sudo systemctl daemon-reload`
   (Skip `systemctl stop` if the unit is already `inactive (dead)`.)
3. **Profiles:** `rm -rf` each directory individually (never `rm -rf $PROFILES/*`). Keep LIVE + IDENTITY-SYMLINK.
4. **Verify:** `ls $PROFILES/` shows only expected entries; `systemctl list-unit-files | grep <name>` shows nothing for deleted units; running gateway process list unchanged; if this followed a token rotation, old-token grep across remaining profiles' `.env`/`config.yaml` returns zero hits and conflict delta over a 45-60s window is 0.
5. **Report** the backup path and a suggested expiry (e.g. "I'll flag it for deletion in 2 weeks").

## Pitfalls
- **Cgroup unit ≠ `--profile` flag is a red flag, not proof either way.** A gateway process can carry a cgroup naming a different profile's unit (e.g. `--profile orchestrator` living under `hermes-gateway-kai.service`) — usually forked from another gateway's context before daemonizing. Don't report "orphaned" or "owned by X" off either signal alone; cross-check `ppid`, the unit's `MainPID` (`systemctl show -p MainPID`), and `ps -o ppid,pgid` before stating ownership.
- **Unit names don't follow a pattern.** `next-step` profile runs under `jeff.service`; `orchestrator` under `hermes-orchestrator-gateway.service`. Never guess `<unit> = hermes-<profile>.service` — enumerate with `systemctl list-units --type=service | grep -iE 'hermes|gateway|bot'` and match on the unit file's `--profile` arg or description.
- **Sandbox HOME (Ned):** `~/.hermes/profiles/` resolves into the nested sandbox (`/home/ubuntu/.hermes/profiles/ned/home/.hermes/profiles/`) and shows a truncated, misleading tree (e.g. "only orchestrator exists"). Always use absolute `/home/ubuntu/.hermes/profiles/...`.
- **grep timeouts:** `grep -rl <token> $PROFILES/` over multi-GB profiles (with node_modules) can hang past any timeout. Scope to each profile's `.env` + `config.yaml` explicitly in a loop.
- **Terminal guard blocks gateway stops from inside a gateway process:** `systemctl stop hermes-gateway-*` issued from a running gateway's shell gets SIGTERM'd/blocked. If the unit is already dead, just `sudo rm` the file and `daemon-reload` — no stop needed.
- **Stale log lines ≠ live problem:** gateway logs are one continuous file; `tail | grep -c` counts history. Only a count delta over a real window (baseline → sleep 45-60s → recount) proves live or clean.
- **`prismatic-agent-bus-<name>.service`/`.timer` is different from `hermes-gateway-<name>.service`:** the bus worker is the *real* agent runtime (static unit + timer); the gateway unit is the dangerous duplicate. Delete the gateway unit, keep the bus worker.
- **Frame it honestly:** dormant profiles are usually ~MBs total while live ones are multi-GB. This is hygiene, not space reclamation — say so before Michael expects disk to free up.
- **Never delete on bucket label alone** when the bucket is DORMANT-DATA, even if Michael says "delete all" — "delete all" has been given in a context where the assistant's own bucket table (🟡/🔴) still gated the decision; restate what's in each bucket in the report so the approval is informed.
- **Operator layer ≠ product layer — map the data before declaring "safe to delete."** A Hermes profile can be the *operator* assistant for a live product whose customer data lives in entirely separate layers (Docker containers, data dirs, systemd units) that a profile deletion never touches. HDE is the canonical case: the `hdengine` profile was the operator assistant, but the customer "containers" were Docker `guest-hermes-{id}`, journals lived in `/home/ubuntu/users/guest_*`, per-customer config in `/home/ubuntu/guest_hermes_bot_*`, and the customer-facing bot ran from the `hde_router` systemd unit with its token in `hd-platform-staging/.env`. Michael will conflate "you deleted the profile" with "you deleted my bot" until you prove the data layer is intact. Before reporting safe-to-delete for any operator profile: (1) `docker ps -a --format '{{.Names}}\t{{.Status}}' | grep guest` for per-user containers, (2) `docker inspect <container> --format '{{range .Mounts}}{{.Source}} -> {{.Destination}}{{"\n"}}{{end}}'` to see where journals/data mount from, (3) `grep -rl <profile-name> ~/work/<product>/scripts/ /etc/systemd/system/` to prove the live stack does (or doesn't) resolve the profile. Full map + walkback: `references/2026-08-18-hde-walkback.md`.

## Walkback (restore after a deletion scare)

When Michael says "we deleted the whole X setup — walk it back":
1. **Prove what actually died.** The product data layer (containers / data dirs / services) is usually untouched — show it alive first; the deletion almost always hit only the operator-profile layer.
2. **Inventory the FULL sweep before restoring anything:** `tar tzf <tarball> | cut -d/ -f1 | sort -u` — a "cleanup" tarball often holds far more than the profiles Michael is asking about (the 2026-08-18 HDE case: Michael thought 4 profiles died; the tarball held 19 top-level entries including a 5th HDE-referenced profile, `jules`, that was only found by this sweep). For every entry, decide restore-vs-leave with the same reference check used before deletion: `grep -rl <profile> ~/work/<product>/scripts/ /etc/systemd/system/`. Restoring only the profile Michael named while a sibling referenced by live code stays deleted is a silent pipeline degradation.
3. Extract: `tar xzf <tarball> -C /home/ubuntu/.hermes/profiles <name>` — one name at a time, never a blanket extract. Pre-flight: assert the target dir does not already exist (protects against clobbering a profile recreated since the tarball). Verify completeness afterward: per-profile live file count vs `tar tzf | grep -c '^<name>/.*[^/]$'`, and `yaml.safe_load` each restored `config.yaml`. Note: a profile without `config.yaml` is not necessarily broken (bus-lane profiles like `jules` only have `SOUL.md` + `lane_config.yaml`).
4. **Scrub the rotated token before the profile is live again:** a restored profile's `.env`/`config.yaml` almost certainly still carries the old token. Replace or blank it, then scoped grep: old-token prefix returns zero hits. Residue in logs, `.env.bak*`, `credentials.json` is common and usually inert — prove it with one `getMe` on the old token: if Telegram returns HTTP 401 the token is dead and log residue cannot poll; scrubbing logs is then optional hygiene, not a safety requirement.
5. **Verify identity continuity without printing the secret:** read the token from the product's `.env` in Python (assemble the env-var name by string concatenation — see the name-scrubbing pitfall in `api-key-handling-for-ned`), hit `https://api.telegram.org/bot<token>/getMe`, assert the token never appears in stdout and the username matches the known bot.
6. **Do NOT recreate a gateway unit unless the profile had one.** Operator profiles are usually bus/on-demand driven; a missing unit is not a defect.
7. **Audit the product's maintenance crons while you're in the blast radius.** Deletion scares are the moment to check whether the product's own crons (backups, pruning, hibernation) are actually running — `tail /var/log/...`-style logs and the crontab. Class-level gotcha: a cron entry pointing at a script that was deleted (often never git-committed, so unrecoverable from repo) fails silently every run and can sit for weeks — the 2026-08-18 HDE case found guest-data backup dead for 32 days this way. Distinguish the layers: postgres dumps may be current while the file-level journal backup is stale. Report the gap and propose a git-committed replacement script rather than silently re-adding a dead cron entry.

## Verification checklist
- [ ] tarball exists and is non-empty
- [ ] `ls $PROFILES/` = expected survivors only
- [ ] no deleted unit in `systemctl list-unit-files`
- [ ] running gateway profiles unchanged
- [ ] (post-rotation) old token absent from all remaining profiles; conflict delta 0 over ≥45s

See `references/2026-08-18-fleet-prune.md` for the 26→7 fleet prune session: exact reference hits that blocked deletion (prismatic agents.yaml, honeybadger ops scripts), the two dead Fred gateway units, and the backup location.

See `references/2026-08-18-hde-walkback.md` for the HDE case: operator profile vs product data layer (Docker guest containers, `/home/ubuntu/users/` journals, `hde_router` bot, token locations) and the token-scrubbed restore recipe.
