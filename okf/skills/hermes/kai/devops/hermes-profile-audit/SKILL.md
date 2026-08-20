---
name: hermes-profile-audit
description: "Audit a Hermes profile's config, toolsets, env keys, cron jobs, caches, and disk — and distinguish display-only config keys from runtime-effective ones by reading the installed hermes_cli source. Use when asked to verify what model/vision/provider a profile actually uses, audit a profile's health, prune profile disk bloat, or confirm whether a config key will take effect on next gateway boot."
tags: [hermes, profile, audit, toolsets, disk, config]
related_skills: [hermes-agent, local-llm-inference-ops, tailscale-lan-access]
---

# Hermes Profile Audit

Class of work: verifying the *actual* state of a Hermes profile (model, vision, tools, keys, cron, disk) rather than trusting memory notes, and safely pruning bloat. Always verify claims empirically — memory notes go stale (this session's "Qwen is blind" note was wrong; the server had been restarted with mmproj).

## Audit inventory (run in this order)
0. **Identity check (do this FIRST):** profiles on this box can be **hardlink twins**. Verified 2026-08-18: `profiles/fred` and `profiles/orchestrator` share the same inode for `config.yaml`, `SOUL.md`, `memories/` (every memory file), and fred's runtime dirs (`logs/`, `state.db`, `sessions/`, `gateway_state.json`, `channel_directory.json`) are **symlinks into the orchestrator profile**. There is no separate `--profile fred` gateway — one process serves both names. Before auditing "profile X", prove what X actually is:
   ```bash
   stat -c '%i' profiles/X/config.yaml profiles/Y/config.yaml   # same inode = twin
   readlink -f profiles/X/logs profiles/X/state.db profiles/X/gateway_state.json
   ```
   If twins, the audit of X is an audit of Y: report both names, one brain, one DB.
1. **Live gateway process (don't trust `gateway_state.json`'s pid):** the recorded pid can be stale or belong to a *different* profile's process (this is how the fred/orchestrator confusion hid for a full session). Verify ownership of the log file, not the pid file:
   ```bash
   fuser -v profiles/X/logs/gateway.log        # which pid actually holds the log open
   pgrep -af 'gateway run'                     # list all live gateways + their --profile flag
   tail -3 profiles/X/logs/gateway.log         # fresh timestamps = live; then correlate to the fuser pid
   ```
   For telegram, confirm which bot is really live: `TOK=$(grep -oP 'TELEGRAM_BOT_TOKEN=*** .env); curl -s https://api.telegram.org/bot$TOK/getMe` — compare `first_name`/`username` to what the user thinks "that profile" is.
2. **Model + vision:** `curl http://<host>:<port>/v1/models`, then the live process: `ssh root@<host> "for p in \$(pgrep -f llama); do tr '\0' ' ' </proc/\$p/cmdline; echo; done"`. The `--mmproj` flag in cmdline is necessary but NOT sufficient — prove vision with a live image round-trip (see `local-llm-inference-ops` for the 2×2 red/blue PNG recipe). The server's "multimodal" capability flag in API metadata is not proof either.
3. **Config parse:** `python3 -c "import yaml; c=yaml.safe_load(open('config.yaml')); ..."` for providers, fallback_providers, auxiliary, image_gen, tts, toolsets, platform_toolsets, mcp_servers.
4. **Env keys:** `grep -oE '^[A-Za-z0-9_]+=' .env | tr -d '='` for names; then `printenv` each to see which are actually resolvable in the shell. Report SET vs empty WITHOUT printing values.
5. **Cron:** parse `cron/jobs.json` (it's `{"jobs": [...]}`; `schedule` may be a dict — read `.get('value')`). Count enabled vs paused; Michael dislikes paused legacy duplicate noise.
6. **Disk:** `du -sh */` on the profile root; drill into the biggest dirs. Note: profile `home/` sandbox may be **LIVE** — check `tr '\0' '\n' < /proc/<pid>/environ | grep '^HOME='` for running gateway children before pruning. Safe to remove: `.npm/_cacache`, `.npm/_npx`, `.cache/uv`, `.cache/pip`. NEVER remove `.cache/ms-playwright` (browser tool re-download is painful).
7. **Stale config backups:** `ls config.yaml.bak*` — clutter, but don't delete without approval.
8. **Skill-tree symlink hygiene (2026-08-20):** profiles' `skills/` trees are symlink-heavy (shared skills cross-linked), and **a self-referential symlink inside a skill dir makes the skill lister follow it into a phantom loop** — the `<available_skills>` block then lists one skill 14+ times (observed: `projector-aware-communication-discipline` nested to depth 14, ~500 tokens/turn of garbage injected into every prompt of every profile that symlinks into the broken tree). The loop is invisible to `ls -la` of the skill dir until you check the *children*. Detection (all profiles in one pass):
   ```bash
   find /home/ubuntu/.hermes/profiles/*/skills -type l | while read l; do
     r=$(readlink -f "$l" 2>/dev/null); d=$(dirname "$l")
     case "$r" in "$d"|"$l"|"$d"/*) echo "CYCLE: $l";; esac
   done
   ```
   **False-positive caveat:** a symlink whose *target path merely contains the link's own path as a prefix* (e.g. `_adopt_shared_skills -> _adopt_shared_skills.py`) triggers the `$d/*` branch but is harmless if the target is a file with no SKILL.md — check `find -L <link> -name SKILL.md` before flagging. Fix: back up (`cp -P` to /tmp), `rm` the link, verify the real skill's SKILL.md is intact, then re-run the scan + the profile's `skills_list` to confirm the phantom copies are gone. The real skill's own dir is untouched — only the self-link inside it is the bug.

## Config-key semantics: display-only vs runtime-effective
**Pitfall:** a top-level `toolsets:` list in config.yaml looks like it gates which tools load — in Hermes v0.17.0 it is **display-only** (consumed by `dump.py` for the `features:` summary and listed as a valid root key in `config.py` `_KNOWN_ROOT_KEYS`; nothing in agent/gateway reads it to load tools). Runtime tool gating uses **`platform_toolsets`** (per-platform, e.g. `telegram:`), falling back to the platform default toolset (`hermes-telegram` for telegram, `hermes-cli` for cli) when the key is absent.

How to verify for any config key (don't trust this skill's version claim — Hermes updates):
```bash
SP=$(dirname $(dirname $(readlink -f $(which hermes))))/lib/python3.12/site-packages
grep -rn 'get("toolsets")' $SP --include='*.py'   # find all consumers
```
Then classify each consumer: display (dump.py) vs validation (config.py allowlist) vs runtime (agent/, gateway). Cross-check empirically: a fresh telegram gateway session with full tools while a restrictive `toolsets:` key exists is proof of inertness.
- `hermes_cli/tools_config.py:_get_platform_tools` is the runtime gate; `PLATFORMS` there maps platform → `default_toolset`.
- One-shot `hermes -z --toolsets` reads the flag, then platform tools — also not the top-level key.

## Report shape (Michael's preference)
- Solid table (area → status), then 🚩 gaps table (#, gap, why it matters, fix), then hygiene list.
- End with numbered next-step options; default-recommend the zero-risk ones.
- Concise proof + next blank to fill, not a narrative.

## Session detail
- 2026-08-18: verified kai profile — mmproj live, toolsets key display-only (4-check ad-hoc probe, ALL PASS), pruned 2.5G regenerable caches in live profile home sandbox (3.7G→1.2G), cron clean (1 active), gaps: no FAL key for image_gen, tts/voice unconfigured.
- 2026-08-18 (second pass): end-to-end audit of "Fred's VLLM → Hermes → Telegram" exposed the fred/orchestrator hardlink twin (new step 0). `gateway_state.json` pid pointed at the orchestrator gateway process; `fuser` on the log file proved single-process ownership. Telegram bot confirmed live via getMe (@FredTheFredBot, id 8929563456). Findings: vLLM :8000 serving INT8 27B (model id `local-qwen-27b-q8-fred`) answering in ~1s; 3× empty-response retries in errors.log 19:20-19:22 (recovered via fallback); stale systemd unit `hermes-orchestrator-gateway.service` TimeoutStopSec=90s < drain 180s (fix: `hermes gateway service install --replace`); `prismatic-agent-bus-fred.service` stuck in `activating (start)`.
- 2026-08-20: skill-inventory audit across all 12 profiles found the self-referential symlink loop in the orchestrator's `projector-aware-communication-discipline` skill dir (new step 8). Fixed by removing the one link (backed up to /tmp/skill-loop-backup-2026-08-20/); re-scan clean, live `skills_list` confirmed phantom copies gone. Full fleet census: 159 unique canonical skills (symlink-resolved) / 283 physical SKILL.md / 176 unique names, 12 divergent — now versioned in `okf/skills/` (PR #33, see `okf-mcp-hub` → `references/skill-hub-phasea-2026-08-20.md`).
