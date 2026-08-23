# Local LLM watchdog "flapping" — false-positive diagnosis recipe

Session-derived (2026-08-22, VM232/kai `llama-kai.service` + `llm_server_watchdog.py`). Use when Michael reports "your and Kai's setup keeps going on and off" or a watchdog alert like `🔴 VMxxx down — keyed completion probe failed (no output)`.

## Working hypothesis (confirmed on 232)

"No output" probe failures during load are NOT server outages. The watchdog wrapper runs the probe over SSH with a hard `subprocess` timeout (20s in this deployment) while the on-host probe's own `urllib` timeout is 120–180s — the wrapper always wins. When a multi-slot llama.cpp server (`--parallel 2`) is saturated with long agent turns (tasks generating 27k–43k tokens + 12k–18k-token prefills), a fresh `max_tokens:1` probe request queues and first-token latency blows past the wrapper's budget → `TimeoutExpired` → empty stdout → "no output" alert. Next tick, a slot frees → "✅ back up (was down)". Pattern: every DOWN self-resolves in 1–2 ticks; server uptime/restart counters never move.

## Diagnosis sequence

1. **Classify the flap from watchdog run history first.** Cron `no_agent` jobs write per-run markdown to `<profile>/cron/output/<job_id>/*.md`: `🔴` = DOWN alert, `✅` = recovery line, `silent (empty output)` = healthy tick. A loop over the day's files gives the exact flap timeline (down windows, self-recovery interval).
2. **Prove the server never went down.** On the model host:
   `systemctl show <unit> -p ActiveEnterTimestamp -p NRestarts` — if ActiveEnter predates the entire flap window and NRestarts=0, no real outage.
   `dmesg | grep -iE "out of memory|killed process"` — rule out OOM kills.
   `ss -tln | grep <port>` — port still LISTEN.
3. **Prove the window was load, not failure.** `journalctl -u <unit> --since <window> --until <window>` — high `print_timing`/task volume with long `n_gen` counts on all slots = saturated queue. That's the cause.
4. **Reproduce the probe live, timed.** Run the exact watchdog probe command (same host, script, model, port, key file) with `time ssh ...`. A 3s `HTTP:200` right after a DOWN alert confirms the timeout-under-load mode, not a persistent fault.
5. **Explain "why both agents move together".** Multiple profiles pointing at the same `custom_providers` local backend correlate by construction — contention, not two independent failures. Check `model:`/`provider:` per profile config to confirm shared backend; check each profile's `fallback_chain` so a real outage has a route (here: gemini-2.5-flash fallback covers genuine down, not load stalls).

## Applied fix (2026-08-22, Michael-authorized, verified)

`/home/ubuntu/.hermes/profiles/autobot/scripts/llm_server_watchdog.py` now ships the recommended shape — treat this as the current deployed baseline when touching the watchdog again:

- **Split timeouts:** `SSH_TIMEOUT = 20` for `systemctl is-active`; `PROBE_TIMEOUT = 180` for the completion round-trip (matches the on-host probe's urllib cap). `ssh()` takes a per-call timeout; `TimeoutExpired` returns `rc=None` with `ssh timeout after Ns` text.
- **Distinguished failure text:** `rc is None` → `probe timed out (no response within 180s) — <err>`; `rc==2` → key-file problem; non-2xx → `keyed completion probe failed (<out or err or 'no output'>)`. A load stall can no longer read as "no output".
- **MIN_STRIKES = 2:** a single failed tick records `strikes` in the state file but prints nothing; two consecutive failed ticks declare down (first alert includes `(2 consecutive failed probes)`); ongoing outage re-alerts hourly as `still down (N strikes)`; recovery prints `✅ back up (was down)`.
- **State file schema:** `{down, strikes, last_alert}` per target — backward compatible: old `{down, last_alert}` files load fine (`strikes` defaults to 0 via `.get`). The healthy path and the "already alerted, within dedup window" branch must both write the full 3-key shape AND advance `strikes` — this is where two real bugs lived (see verification below).

## Verification recipe: unit-test the watchdog state machine

`no_agent` cron watchdogs are deterministic state machines on a file — test them without waiting for live cron ticks:

1. Load the module by path: `importlib.util.spec_from_file_location("wd", path)` + `module_from_spec` + `exec_module`.
2. **Redirect `STATE_FILE` to a temp path** (`/tmp/wdtest/state.json`, `rm -f` first) so the real state file is untouched.
3. **Fake the clock inside the module:** the script does `import time` and calls `time.time()`, so patch `wd.time.time = lambda: fake["t"]` and advance `fake["t"]` per scenario (dedup-window tests need +300s and +3601s steps). Note: this mutates the process-global `time` module — run the harness in a disposable process, never inside a long-lived one.
4. **Monkeypatch `wd.check_target`** to return `[]` (healthy) or a canned problems list, and capture `wd.main()`'s stdout with `contextlib.redirect_stdout(io.StringIO())` — that captured string is exactly what cron would deliver to Telegram.
5. **Assert BOTH the stdout string AND the exact state dict** after every tick. The three-scenario minimum set: (a) single failed tick → empty stdout + `strikes:1, down:false`; (b) recovery from sub-threshold stall → empty stdout, no false "back up"; (c) two consecutive failures → one alert with strike count; then dedup silence, hourly re-alert with updated count, and recovery "back up".
6. Finish with one **live run of the real script** (`python3 llm_server_watchdog.py`), asserting empty stdout on health, exit 0, and the state file now carrying the new schema — this is the deployment-shaped proof the unit tests can't give.

Label the whole thing `AD_HOC_OR_CANONICAL=ad-hoc targeted` (unit tests + one live health tick, not a production soak).

## State-machine bug patterns caught by the tests

- **State key drop on healthy path:** writing `{"down": False, "strikes": 0}` without `last_alert` silently resets the dedup anchor on the next recovery — assert the exact full dict, not just the `down`/`strikes` fields.
- **Counter frozen in dedup branch:** the "already alerted, within 1h" branch must still advance `strikes` while preserving `last_alert`; copying `prev` verbatim freezes the counter and breaks the "still down (N strikes)" re-alert text.
- **Fake-clock miss:** patching a local `now` variable in the test does nothing — `main()` calls `time.time()` directly, so `wd.time.time` must be the thing you control. The symptom is a dedup-window assertion that fails only at the +3601s step.

## Pitfalls

- A watchdog probe that is a real chat completion inherits the model's latency profile — it is a load test, not a health ping. `/health`-style checks don't queue the same way.
- The probe's own long timeout is dead config when a shorter wrapper subprocess timeout kills it first — read the wrapper, not the probe.
- Do not conclude "stale memory note about wrong port" from a config excerpt that didn't show `base_url`; verify the listener before claiming which host/port a profile actually uses.
