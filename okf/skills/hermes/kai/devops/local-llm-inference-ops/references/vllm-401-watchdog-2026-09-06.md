# vLLM watchdog 401 — 2026-09-06 (session detail)

Incident: cron job `280f505e055a` ("Kai LLM engine watchdog", `no_agent: true`, script `profiles/kai/scripts/llm-engine-watchdog.py`) failed at `2026-09-06T06:30:11` — HTTP 401 on `192.168.1.230:8000` (fred-vllm) and `:8003` (ned-vllm); `192.168.1.232:8080` (kai-llama) OK. Telegram alert said "provider authentication error" (scheduler's generic wrapper, not a provider-config issue).

## Timeline (UTC)
- 2026-09-05 ~19:40 — kai `profiles/kai/.env` edited (VLLM_FRED_API_KEY len 58, VLLM_NED_API_KEY len 57; backups `.env.bak-vllmkey*`).
- 2026-09-05 20:06 / 20:29 — `.230` fred key file written / `vllm-fred.service` restarted (live key len 58, prefix `vllm-fred`).
- 2026-09-05 23:25 / 09-06 00:24 — `.230` ned key file written / `vllm-ned.service` restarted (live key len 57, prefix `vllm-ned-`).
- 2026-09-06 06:30 — watchdog 401s both vLLM endpoints. Its output file is **MISSING** from `cron/output/280f505e055a/` (previous night's 06:30 file present) → died before writing the report.
- 2026-09-06 later — all live probes pass: `.env` keys hash-match live service keys from `/proc/<pid>/cmdline`; 200 on both ports; sanitized-env run exits 0.

## Evidence that ruled things out
- vLLM services up continuously (Jul 31 base; only the two rotation restarts above) — no crash loop around 06:30.
- Key files on `.230` unchanged since the rotation; consumer `.env` existed before the failure.
- Manual runs pass under every tested `HOME` (gateway, redirected profile home, bogus path).

## Diagnosis
Stale/mismatched key window: the rotation night (fred 20:29, ned 00:24 restarts) vs consumer `.env` mirroring left a 401 window at the 06:30 run. Residual uncertainty: `.env` mtime (19:40) predates the `.230` key-file mtimes, so the 06:30 trigger may also have been a transient env-resolution miss inside the sanitized subprocess. Functional state verified fixed by live 200s regardless.

## Durable lessons
- `no_agent` cron = gateway-env subprocess with secret env vars stripped; scripts must read keys from the profile `.env`. `~`/`Path.home()` inside such scripts is a latent bug (agent-shell HOME redirected; gateway HOME `/home/ubuntu`).
- Missing cron output file is itself a signal: crash before the report-write step.
- Key extraction from `/proc/<pid>/cmdline`: compare length/prefix only; pipe into `curl` in one step — a combined `extract && rm` + `scp` pipeline races (scp reads after the remote `rm` → "No such file or directory").
## Hardening APPLIED + verified (2026-09-06, same day)

Rewrote `profiles/kai/scripts/llm-engine-watchdog.py` (240 lines) with:
1. **HOME-proof `.env` resolution** — `_ENV_FILE_CANDIDATES` tries the script-adjacent absolute path (`…/profiles/kai/.env`) then the legacy `~`-based path; survives hostile `HOME=/nonexistent`.
2. **Key-source labeling** — each probe records `key_source` = `env` | `env-file:<path>` | `none`; `VLLM_WATCHDOG_DEBUG=1` prints it + a `KEY SOURCE MISSING` warning.
3. **Failure detail in `error`, not `running`** — 401s now read `DOWN: authentication failed (401) — check API key` instead of `DOWN: None`.
4. **Single alert** — removed a duplicated `print(msg)` that double-posted.

Verification matrix (all real runs, `env -i` = cron-equivalent): compile OK; clean env + normal HOME → exit 0 silent; hostile HOME → exit 0 silent (script-adjacent `.env` rescues); debug → `key_source=env-file:…/.env alive=True`; stale-key sim → exit 1 + single alert + 401 detail. Live: `.env` keys → 200 on `:8000`/`:8003`.

Self-inflicted bugs found DURING the hardening (both are the real lesson of this session):
- **Lookup-key mismatch in my own rewrite:** `_KEY_ENV` keyed `"fred"`/`"ned"` while `main()` passed `"fred-vllm"`/`"ned-vllm"` → debug printed `key_source=None` on healthy endpoints. I chased this as an env mystery (gateway `/proc/<pid>/environ`, PID archaeology) before reading my dict. See SKILL.md pitfall "Diagnostic-label trap".
- **Two consecutive fuzzy patches mangled the file** (dropped the debug block, then the `__main__` tail) → full `write_file` rewrite was the fix. See SKILL.md pitfall "Patch-mangle discipline".
