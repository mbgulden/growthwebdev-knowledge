# Reconciliation worked example — pe-foundational-gaps vs George (2026-07-27)

This is the session that produced the `plan-reconciliation-after-peer-review` skill. Concrete evidence and corrections live here; the skill is the abstraction.

## Inputs

| Input | Path / SHA |
|---|---|
| Original draft | `pe-foundational-gaps-for-george-2026-07-26.md` — 496 lines, 31,028 bytes, SHA-256 `1c51012d2013423b2741e72fd58a980ab13a9fa7baf26ee344b580b8cd02bd9d` |
| Reviewer packet | `PE_FOUNDATIONAL_GAPS_RECONCILIATION_PLAN_2026-07-27.md` — 248 lines, SHA-256 `55dfccc25ff64ee18115de5a42dce577594a93263ede756cb93e201a6e823265` |
| Reconciled doc | same path as original draft, replaced in place — 24,199 bytes, 2026-07-27 |

## Reviewer corrections and how each was verified

| Reviewer claim | Verification command run | Outcome | Honored in reconciled doc? |
|---|---|---|---|
| `locking.py` is real (fcntl, owner release, stale pruning) | `git -C /home/ubuntu/work/prismatic-engine show origin/main:prismatic/core/locking.py` | Confirmed: real fcntl-guarded mutex | F1 reframed as "authority convergence" |
| `_parse_dt()` doesn't handle epoch milliseconds | `git show origin/main:prismatic/linear_rate_limit.py` | Confirmed: `fromisoformat` + `parsedate_to_datetime` only | F4 reduced to one bounded audit/repair slice (PE-LINEAR-CIRCUIT-REPAIR-01); no sleep-until-future test |
| `dispatcher.launch_codex` builds unsupported `--issue/--task` argv | `grep -n "def launch_codex\|--issue\|--task" prismatic/dispatcher.py` | Confirmed at `dispatcher.py:2496` | F2 plan includes "Replace/remove unsupported `launch_codex --issue/--task`" |
| Lane contracts has `agy`, no `codex` | `grep -n "codex\|agy" prismatic/lane_contracts.py` | Confirmed: `agy` at line 85, no `codex` | F2 plan requires new `codex` contract entry |
| Harness registry has `codex-cli disabled`, module missing | `cat prismatic/harnesses/registry.json` | Confirmed: 4 entries; `codex-cli` enabled=false, `agy-cli` enabled=true | F2 plan includes codex harness implementation |
| Profile state contains config + backups + .env (not empty) | `ls -la /home/ubuntu/.hermes/profiles/{agy,codex-5-4,codex-5-5}/` | Confirmed: 8–17 files per profile, including `.env`, `SOUL.md`, `cron/`, `logs/` | F0 plan replaced destructive wipe with inventory → export → archive → approved deletion |
| Cron checkout is dirty on `design/GRO-3837` | `git -C /home/ubuntu/work/prismatic-pe-native-crons status --porcelain \| wc -l` | Confirmed: 89 porcelain entries | F3 plan calls for "reconcile to one trigger authority into one canonical PE runner" |
| Live crontab has 10 generated commands | `crontab -l \| grep -c "^[^#]"` inside the PRISMATIC_NATIVE_CRONS block | Confirmed: 10 command lines | F3 plan does NOT add a second tick scheduler |
| `event_router.db` is 102,219,776 bytes | `stat -c '%s' /home/ubuntu/.prismatic/db/event_router.db` | Confirmed: 102,219,776 bytes | F6-2 plan refuses to rotate the whole DB; per-table authority + dry-run + restore proof |
| Codex auth resolves under service HOME, not universal `~/.codex` | `codex doctor --json` | Confirmed: `auth file: /home/ubuntu/.hermes/profiles/fred/home/.codex/auth.json` | F2 plan states "Explicit runtime service HOME"; canonical argv in doc |
| Codex CLI 0.132.0 rejects `--ask-for-approval after exec` | `codex exec --help` argv parsing | Confirmed (reviewer-tested) | F2 corrected argv: `/usr/bin/codex -a never exec ...` |

## Compression result

| Bucket | Original draft | Reconciled |
|---|---|---|
| Total tasks | ~29 across 7 new epics | 18 bounded slices under existing PE parents + 2 profile-hygiene slices in a separate operator packet |
| New epics | 7 (F0/F1/F2/F3/F4/F5/F6) | 0 (all use existing GRO-4261/4262/4263/4264) |
| Already-implemented areas | 0 | 1 (F4 rate-limit) — converted to audit/repair slice |
| Destructive cleanup language | yes ("wipe from history") | no (inventory → export → archive → approved deletion) |
| Profile-state assumption | "empty placeholder" | "contains config + backups + .env — NOT empty" |
| Cron assumption | "12 crons show last_run_at=None" → "decorative" | "live crontab has 10 commands bypassing registry runner" → split-brain |
| Codex argv | `codex exec --ask-for-approval never ...` | `/usr/bin/codex -a never exec ...` |

## What stayed

- Codex CLI vs Hermes-profile separation (Michael's 2026-07-26 decision holds).
- AGY CLI vs Hermes-profile separation (Michael's 2026-07-26 decision holds).
- Cap 1 parallel Codex CLI invocation; expand only after measured rate-limit/sandbox evidence.
- Existing PE parents: GRO-4261 / GRO-4262 / GRO-4263 / GRO-4264.

## Decisions surfaced to Michael (in reconciled doc)

1. Approve the reconciliation direction.
2. Approve a read-only child-description dedupe pass for existing GRO-4262/4263/4264.
3. Choose profile-retirement policy: supported `hermes profile delete` (recommended) vs. leave in place + mark retired.
4. Confirm Codex auth ownership: operator runs `codex login` for the dedicated PE service HOME; no credential copy.
5. Confirm system cron as the thin trigger into one canonical PE runner, not a second tick scheduler.

## Non-claims held

- No Linear issue or relation created/edited/moved/labeled/assigned/closed.
- No source, profile, alias, credential, crontab, process, service, database, or runtime checkout changed.
- No Codex or AGY inference invoked (Codex not logged in).
- No cron manually run.
- No merge, release, deployment, restart, or writer-cap increase.
- No history rewrite, no manual `rm -rf`, no credential copy.
- Focused source checks are ad-hoc targeted evidence, not canonical suite green.

## What the reconciled doc enabled next

The reconciled doc is a **plan**, not a build-out. The next step (when Michael approves the 5 decisions) is to invoke `linear-handoff-build-out` to:

1. Read existing child descriptions under GRO-4262/4263/4264 against the 18 slices (dedupe/update matrix).
2. Build the OKF bundle under `okf/projects/pe-foundational-gaps/` (index, HANDOFF, decisions with Owner + Acceptance Test IDs, risk register with named owners + observable signals).
3. Mutate Linear: parent + child epics + child tasks, all with seven-field descriptions and the Distributed-Execution Header.

Until Michael approves, the reconciled doc lives only at `~/.hermes/profiles/fred/cache/documents/` and `~/.hermes/profiles/orchestrator/cache/documents/` (same inode on this host). No MERGE, no PUSH.

## Anti-pattern notes from this session

1. **First draft proposed `codex exec --ask-for-approval never ...` — the parser rejects it on 0.132.0.** Build argv from the actual `codex --help` output, not from memory of an older version. The reviewer caught this; my original draft did not.
2. **First draft said "wipe from history" for profile cleanup.** The retired profiles contain `cron/`, `logs/`, sessions databases, and `.env` files. A safe replacement is the inventory → supported export → archive → explicit destructive approval → supported deletion sequence. The reviewer required this; my original wording would have nuked evidence.
3. **First draft proposed a 3-task `PE-LINEAR-GUARD` epic.** The reviewer proved the rate-limit circuit is already wired into dispatcher.gql, webhook draining, and dashboard. A new epic would have duplicated work. The reconciled doc keeps only one bounded audit/repair slice.
4. **First draft proposed `pe crons tick` daemon alongside per-job system cron.** The reviewer proved the live crontab already has 10 commands that bypass the registry runner, and adding a daemon would create a second scheduler authority. The reconciled doc reconciles to one canonical PE runner, no daemon.
5. **First draft described `event_router.db` as 17 MB.** It's actually 102 MB and growing. The reviewer-corrected number forced per-table retention planning instead of a blanket rotation.
6. **First draft's verification packet had `CODEX_AUTH_STATUS=***`** when patching because I noticed the wrong string at write time and patched, but the proof-of-this-session artifact shows the same care goes into the verification packet as into the doc body.

---

## v2 addendum (2026-07-27, same day, post-approval)

Michael approved decisions 1, 2, 3(a), 4 and re-framed decision 5. The reconciled doc grew to **427 lines / 32,343 bytes** to fit the new trigger-authority section.

### Decision 5 lesson: system cron is the wrong default for a multi-device product

The reconciled v1 doc proposed "system cron as the preferred thin trigger" into one canonical PE runner. Michael rejected that framing on the spot:

> "prismatic engine will be accessible on multiple devices and may or may not be on a server that's 'always on'. You may be accessing it from your phone. Is system cron as the preferred thin trigger the way to go?"

**Why this matters:** system cron only fires when the host process is running. If PE is mobile/laptop/phone-first, the host is not always on. An always-on PE daemon contradicts the deployment model. The reconciliation's job was to translate the user correction into a workable trigger architecture without losing the George's "one canonical scheduler/trigger authority" invariant.

### v2 trigger model: opportunistic wakeup into one canonical runner

| Trigger surface | Fires when | Role |
|---|---|---|
| System cron lines (existing `PRISMATIC_NATIVE_CRONS` block) | Host is on AND minute matches | Thin opportunistic hook into canonical PE runner. If PE asleep → marker + exit. No direct script execution from cron. |
| PE startup / device wake / dashboard open | Any operator opens the gateway | Catch-up sweep over `(now - last_session_end)`, bounded backfill window (TBD: 24h/72h/7d), missed-after-window recorded as `missed_during_offline`. |
| Manual operator action | Operator clicks "Run now" | Ad-hoc fire through same canonical runner. |
| External event | Webhook / push / registered upstream | Forwarded into same runner. Not a separate scheduler. |

**Invariant preserved:** exactly one canonical PE runner. No second scheduler authority. Receipt authority `(cron_id, schedule_bucket, trigger_kind)` keeps every fire observable.

### Concrete crontab change (re-framed)

```cron
# Before (v1 crontab): direct script execution
0 3 * * * cd /home/ubuntu/work/prismatic-pe-native-crons && python3 scripts/pwp credentials refresh ubersuggest

# After (v2 target): thin pointer into canonical runner
0 3 * * * /usr/bin/env python3 -m prismatic.native_crons run --trigger=system-cron --session="$(date +%Y%m%d%H%M)" --cron-id=pwp_credentials_refresh_ubersuggest
```

The runner decides whether to actually fire the underlying command. If PE is asleep, the runner records a "trigger while asleep" marker (visible on next dashboard open) and exits.

### v2 four sub-decisions still pending George's confirmation

1. **`trigger_kind` taxonomy**: `system-cron | pe-startup | manual | external-event` sufficient? Or do we also need `mobile-wake | background-fetch | deferred-push`?
2. **Backfill window default**: 24h, 72h, or 7 days?
3. **Hook binary**: `python3 -m prismatic.native_crons` vs standalone `pe-cron-tick` shim? (Recommended: standalone shim.)
4. **Catch-up sweep gating**: auto-run on every dashboard open vs opt-in first time per session? (Recommended: opt-in.)

### Anti-pattern note from v2

The v1 doc assumed a stable, always-on deployment model. The v2 lesson is: when a plan names an authority ("the trigger authority"), check whether the *deployment model* can support it. If the user corrects the deployment model, the authority choice must change too. In this case, "system cron as thin trigger" was right for a server, wrong for a mobile product; the correct invariant was "one canonical runner" all along.

### Non-claims held in v2

Same as v1, plus: no crontab mutation, no PE daemon started, no `codex login` attempted, no profile `delete` executed. The doc is a planning artifact awaiting George's four sub-decisions on the trigger model.
