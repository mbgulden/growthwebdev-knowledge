# Frozen prefill: diagnosis + all-profiles repair (2026-09-07, GRO-4930)

Symptom: the cold-start greeting is days/weeks **older than `current.json`** — e.g.
the session opens with a "KPI dashboard" greeting from 11 days ago while
`state/current.json` says "vLLM keying complete". The hot handoff is fresh; the
thing the LLM is *injected* is not.

## The two-file model (why this confuses)

```
state/current.json            # HOT handoff — written every substantive turn (handoff.py)
state/prefill_messages.json   # what the LLM is actually injected at cold start
                              #   derived from current.json's one_line by wire_cold_start.py
                              #   config key: prefill_messages_file
```

`handoff.py write` updates ONLY `current.json`. The prefill is a *derived
artifact* — it only refreshes when a rewire runs. If the rewire is broken or
never invoked, the two files silently drift. **The file that matters for
"what does the LLM see" is the prefill, not current.json** — verify the one
that actually got injected (the greeting text the session opened with).

## Detection recipe

1. `stat -c %y` both files (or `written_at_utc` in current.json vs prefill mtime).
   Prefill mtime << current.json write time = frozen.
2. `wire_cold_start.py status --all` (read-only) — shows each profile's prefill
   preview + message roles. A stale preview confirms the content divergence.
3. Run the rewire directly and READ the output:
   `wire_cold_start.py wire --profile <p>`. A broken rewire throws — do not let
   a `| tail` pipe hide it.

## 2026-09-07 root cause (the one to check first)

`wire_cold_start.py` called `subprocess.run` **without `import subprocess`** →
every rewire `NameError`-d silently. `handoff.py` (no subprocess) worked fine,
so the hot file stayed fresh and the defect looked like a *runtime/loader*
problem. It was a **script bug, not a runtime gap** — the loader IS live
(proven by the stale greeting reaching the model at cold start). Distinguish the
two before concluding "the mechanism is dormant": an old-but-real greeting
arriving at cold start *proves* the inject path works; it only proves the
*content* is stale.

Fix = add `import subprocess` to the **canonical** copy.

## Scope: it's ONE canonical file, symlinked by all profiles

In this swarm the shared skill is adopted across profiles — every profile's
`skills/agent-operations/session-state-handoff` is a **symlink to the
orchestrator's canonical copy** (same inode). Confirm with
`stat -c %i <paths>` before assuming per-profile copies. Consequences:

- The bug froze **every** profile's prefill, not just one.
- The fix belongs in the canonical (orchestrator) file — a cross-profile write,
  needs explicit user authorization.
- After the fix, rewire **all** profiles:
  `wire_cold_start.py wire --profile <p>` for each → expect `"status": "wired"`.
  (`status --all` stays read-only; `wire --all` if you want one shot.)

## Verify after rewire

- `"status": "wired"`, prefill mtime bumped, `messages_count: 2`.
- Roles MUST be `user`/`user` — a `system` role triggers the vLLM
  dual-system 400 (see the `role: user` pitfall in SKILL.md).
- Embedded one_line matches `current.json` (not a stale value).

## Standing rule (prevents recurrence)

Write handoffs via **`write_and_wire.py`** (atomic write + rewire) — or, if you
use bare `handoff.py write`, run `wire_cold_start.py wire --profile <p>`
immediately after. Never assume a bare `handoff.py write` keeps the prefill in
sync; it does not.

## 2026-09-07: the running-process leg ("wired on disk" ≠ "what the model sees")

After the import fix + fleet rewire (all 6 profiles `wired`, prefills current as of 02:59 UTC), the cold-start greeting on ned
STILL showed the 11-day-old pre-freeze text. The file was right; the process was not.

**Root cause:** the gateway reads `prefill_messages_file` **once at GatewayRunner init** (same fact as the role:system restart note,
applied to content freshness). Ned's gateway (PID 981635, unit `hermes-gateway-ned.service`) had been up since **2026-08-27 08:04** —
11 days older than the rewire. It serves the pre-freeze prefill it loaded at boot, forever, until restarted.

**Detection (run after any fleet-wide rewire):**

```bash
# gateway start times
ps -eo pid,lstart,cmd | grep -E "hermes.*(gateway|--profile)" | grep -v grep
# or per profile: state/gateway.heartbeat → "start_time" (epoch)
cat /home/ubuntu/.hermes/profiles/<p>/state/gateway.heartbeat
# compare against prefill mtime
stat -c %y /home/ubuntu/.hermes/profiles/<p>/state/prefill_messages.json
```

Process start **older** than prefill mtime ⇒ the rewire is invisible to that process. This swarm's gateways are long-lived systemd
units (`hermes-gateway-ned.service`, `hermes-gateway-george.service`, `hermes-gateway-kai.service`, `autobot.service`,
`jeff.service` = next-step, `hermes-orchestrator-gateway.service`), so a one-shot `wire --all` can easily outlive every running
process by days. **Check the whole fleet after any rewire, not just the profile that triggered it** — the 02:58–02:59 batch rewired
6 profiles whose 5–6 gateways all predated it.

**Resolution:** restart each affected gateway (seconds of message-interruption per bot). This is a gateway-lifecycle change ⇒
explicit human approval required (Ned's edge-case rule: never make infrastructure changes without approval). Roll one at a time,
verify the unit is `active` and the heartbeat `pid` changed. Until the restart, greet from the on-disk `current.json` and label the
greeting you were injected as stale — that is exactly the 2026-09-07 session that surfaced this leg.
