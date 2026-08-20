# Ned Cron — Hermes VM Disk Cleanup Decision Tree

When the disk-fill-rate alarm fires (crosses 85% absolute, or rate anomaly >20× baseline), here's the triage playbook for finding the culprit fast. Adapted from the 2026-06-26 06:29Z tick when disk jumped 82→86% in 37 min (~50× baseline).

## Step 1: Confirm the alarm

```bash
df -h /home/ubuntu
```

Cross-check against the last probe value (delta matters more than absolute — see `verify_gpu_node.sh` Section 5).

## Step 2: Top-level `du` sweep

```bash
sudo du -sh /home/ubuntu/* 2>/dev/null | sort -hr | head -15
```

Look for: anything >5G that's not a known repo (`darius-star` = 8.7G is the highest known workload dir; `mounts` at 28G is suspicious because NAS mounts should not occupy local disk unless the mount is broken).

## Step 3: Drill into the work dir

```bash
sudo du -sh /home/ubuntu/work/* 2>/dev/null | sort -hr | head -15
```

**Red flags:**
- Multiple `darius-star-gro-NNNN/` clones (old PR branches) — can usually be removed after verifying the issue is Done
- Multiple `active-oahu-{static,tours}-mirror-NNNN/` directories — same pattern (build branch snapshots)
- `agy_warm_cache/` > 1G — AGY model cache, trimmable via `agy cache prune` if supported
- `Hermes-Research.archived/` — explicitly archived, but if it grew, check for new subdirs

## Step 4: Cache dirs

```bash
sudo du -sh /home/ubuntu/.cache /home/ubuntu/.local /home/ubuntu/.npm /home/ubuntu/.wrangler /home/ubuntu/.antigravity 2>/dev/null
```

- `.cache` > 2G → likely pip wheels, npm cache, AGY warm cache — safe to trim selectively
- `.npm` > 1G → `npm cache clean --force` is the sledgehammer
- `.wrangler` > 100M is unusual (it's small by design) — investigate

## Step 5: Suspicious mounts

```bash
mount | grep -E "(mounts|synology)"
ls -la /home/ubuntu/mounts/
```

**The biggest suspect in the 06:29Z incident: `/home/ubuntu/mounts` = 28G.** That's larger than the entire local work tree. Possible causes:
- NAS mount became stale, kernel started buffering writes to local disk
- A previous test wrote junk to a mount path that no longer resolves
- Snapshot expansion on a bind-mounted directory

**Always check `mount` output first** — if the expected NAS mount is missing but the directory still has files, you have a stale-mount data leak that can fill disk silently.

## Step 6: Report

In the cron reply (even on SUPPRESS ticks), include:
- Top 5 largest directories with sizes
- Rate anomaly callout vs. baseline
- ETA to 90% and 100% at current rate
- Specific cleanup targets ordered by safety (safe-to-rm → needs-Michael-confirmation)

**Cleanup safety tiers:**

| Tier | Items | Action |
|---|---|---|
| 1 — Safe to prune unattended | `.cache`, `.npm`, `.wrangler`, `agy_warm_cache` | Standard cache eviction; reversible by reinstall |
| 2 — Safe after issue verification | `darius-star-gro-NNNN/`, `active-oahu-{static,tours}-mirror-NNNN/` | Verify the related Linear issue is Done, then `rm -rf` |
| 3 — Needs Michael's call | `/home/ubuntu/mounts` contents, `recovery/` (4.6G), source-tree `node_modules/` | Could lose data; surface in reply, don't auto-delete |

**Per the system prompt rule:** "If disk exceeds 90%, don't just report — suggest specific cleanup targets." Apply the same rule at >85% with rate anomaly — the combination is the alarm.

## Step 7: Rate anomaly recovery — the "resolved" tick pattern

When a prior tick escalated a rate anomaly (e.g. +4%/37min at 06:29Z, ~50× baseline), the next tick's job is to **explicitly confirm the anomaly resolved or escalate that it didn't.** Do NOT silently drop the rate-anomaly callout from the delta table just because the absolute value hasn't changed.

**Canonical 07:38Z example** (follow-up to the 06:29Z escalation): disk still at 86%, but rate has stabilized back to baseline. The cron reply's delta table row was:

```
| Hermes VM disk (`/`) | 86% | 86% | 86% | **stable** (rate anomaly from 06:29Z fully resolved) |
```

Three things to nail in the "resolved" row:
1. **All three readings same value** — proves the rate anomaly stopped, not just paused
2. **Explicit "resolved" label** — makes the change-from-alarm-state obvious to anyone scanning
3. **No new cleanup recommendation** — disk is still 86% absolute, but rate-baseline + absolute < 90% = no action needed this tick

**If the third reading is STILL climbing** (e.g. 86% → 86% → 87%), the reply must escalate again with a new ETA, not just note "still climbing." The 50× baseline tier requires the same critical-infra-finding treatment as the original alarm — recovery isn't assumed from one stable interval.

## Baseline values for delta detection (June 2026)

These are the historical baselines established across multiple cron ticks. Use for rate comparison:

- **Normal fill rate:** ~1% per 8h (~0.125%/h)
- **5× baseline:** ~0.625%/h (one-time spike from a build, usually transient)
- **20× baseline:** ~2.5%/h (something is leaking — investigate within the same tick)
- **50× baseline:** ~6.25%/h (active leak — escalate in cron reply)

## Reproduction recipe for the 06:29Z tick

```bash
# 1. Probe disk
df -h /home/ubuntu

# 2. Top-level du
sudo du -sh /home/ubuntu/* 2>/dev/null | sort -hr | head -15

# 3. Work-dir du (likely culprit zone)
sudo du -sh /home/ubuntu/work/* 2>/dev/null | sort -hr | head -15

# 4. Cache audit
sudo du -sh /home/ubuntu/.cache /home/ubuntu/.npm 2>/dev/null

# 5. Mount audit (always run this — silent mounts are the scariest leak)
mount | grep -E "mounts|synology"
```

Output of the actual 06:29Z run for cross-reference:
- `/home/ubuntu/mounts` = 28G ← **primary suspect, needs Michael**
- `/home/ubuntu/work/darius-star` = 8.7G ← expected (game assets)
- `/home/ubuntu/work/darius-star-gro-2166` = 1.6G ← tier-2 cleanup
- `/home/ubuntu/work/darius-star-gro-2165` = 1.4G ← tier-2 cleanup
- `/home/ubuntu/work/agy_warm_cache` = 1.5G ← tier-1 cleanup
- `/home/ubuntu/.cache` = 3.1G ← tier-1 cleanup
- `/home/ubuntu/.npm` = 2.3G ← tier-1 cleanup

Total reclaimable (tier 1+2) ≈ 9.8G. Enough to bring disk from 86% back below 80%.