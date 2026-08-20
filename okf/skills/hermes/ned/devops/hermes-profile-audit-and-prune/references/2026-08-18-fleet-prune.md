# 2026-08-18 Fleet prune: 26 → 7 profiles

Context: orchestrator was rotated to a new BotFather token (8929563456:AAG…) after OpenClaw on lightbringer-windows (100.93.104.46, SSH firewalled, needs RDP) kept contending the old bot (865347…) via `getUpdates`. Michael then asked: "Fred IS orchestrator — can we just delete the Fred profile? And all the other unused profiles?" Approved as four numbered decisions; all executed in one session.

## Outcome
Survivors: autobot, george, kai, ned, next-step, orchestrator + `fred` (symlink → orchestrator, KEPT as identity).
Deleted 20 dirs: active-oahu, agy, ai-consulting, archived, beyondsaas-leads, codex-5-4, codex-5-5, deepseekv4, google-ai-toolkit, hdengine, hermeslocal, home, jules, kai-content, kai-css, kai-js, profiles (nested migration artifact), qwenlocal, testprof, v.
Units removed: hermes-gateway-fred.service + hermes-fred-gateway.service (both dead; the latter had stop-start-limit-hit + gateway.lock PermissionError + 94k+ restarts).
Backup: /var/tmp/profiles-cleanup-20260818.tgz (1.4M), restore with `tar xzf ... -C /home/ubuntu/.hermes/profiles/`. Flag for deletion ~2 weeks later.

## Reference hits that blocked naive deletion (audit evidence)
- `prismatic-agent-bus-fred.service`: `worker --agent fred` — the bus worker is the real Fred runtime (static unit + enabled timer). Kept.
- `/home/ubuntu/.prismatic/repos/prismatic-engine-control/config/agents.yaml`: `fred:` agent "Hermes orchestrator, local" (file signal /tmp/prismatic + http fred.internal:9001 + dead_letter telegram) and `agy:` agent. **agy profile deleted after Michael's explicit "delete all" — agents.yaml `agy` signal config now points at a dead profile; if AGY bus signals break, this is why.**
- `honeybadger_infra_readiness.py` (copied into ~10 work repos) reads `/home/ubuntu/.hermes/profiles/fred/.env` — resolves through the symlink, still works.
- `home` profile: no units/processes/scripts referencing it → deleted (had 2 memory files).
- Old token 865347 was in exactly 4 profiles: active-oahu, ai-consulting, google-ai-toolkit, hdengine — all deleted, so token eradicated. Verified zero hits across remaining profiles' .env/config.yaml.

## Live-state confirmations
- Orchestrator gateway on new token, stable; conflict delta 0 over 45s (log is one continuous file — 1238 historical conflicts must NOT be read as live).
- Local standalone bots (Sam/Becca/BeyondSaaS, `python .../bot.py` in ~/work/next-step-*) each carry their OWN tokens (86786/89664/84319 prefixes) — verified via /proc/<pid>/environ, ruled out as local rogues.
- OpenClaw still polling the orphaned old bot — harmless, needs RDP + `openclaw pairing approve telegram <code>` / stop on lightbringer-windows to kill at source.

## Sandbox-HOME evidence (why absolute paths matter)
`echo $HOME` in Ned's terminal = `/home/ubuntu/.hermes/profiles/ned/home`; `ls ~/.hermes/profiles/` showed only `orchestrator` (a sandbox copy with one subdir) and `~/.hermes/profiles/fred` readlink'd to the nested path. Real tree is /home/ubuntu/.hermes/profiles/ (26 entries). Every audit command in this skill uses absolute paths.
