# HDE Guest Fleet — Verified State (2026-08-20)

Snapshot from the LOCK-IN session. Verify live before relying on it (`python3 fleet_audit.py` is the source of truth — this file is a baseline, not the truth).

## Canonical build
- Template: `/home/ubuntu/work/hd-platform-staging/scripts/guest_hermes_template/guest_agent_server.py`
- md5 `baf3887bf391357d61294b369b12bed7` (2725 lines) — includes drift canary + naming guard
- Prior baselines: `3a4fcc34c1d7327013e8f2c15960cebc` (2656 lines, 08-19), `5652256ae2153e2f756d0b7db7c14c98` (2693 lines, canary-only)

## Fleet matrix (post-rollout)
| Guest | Status | Notes |
|---|---|---|
| 2, 3, 23, 29, 30, 31, 32, 38, 39, 43 | live (10 containers) | all on `baf3887b`, `.build` markers present |
| 40, 42 | decommissioned | no containers, host files frozen per owner decision 2026-08-19 |

## Rollback backups (prune after ~1 week clean)
- `.bak-20260819T2100Z` — original 12-way sync (2286/2593/2594 builds)
- `.bak-20260820T0402xxZ` — canary rollout (10 guests)
- `.bak-20260820T0451xxZ` — naming-guard rollout (10 guests)
- Per-test backups from canary/sync negative proofs on guest_3 (T041308Z, T040326Z)

## Naming-guard sweep results (read-only, zero deletions)
- 10 of 12 workspaces clean
- **guest_2**: `people/index.json` + `charts/personal/michael_gulden/` (chart_data.json, coach_manifest.json) — `michael gulden`
- **guest_23**: `people/index.json` + `charts/personal/michael_gulden/` + `charts/personal/becca_gulden/` (4 chart files) — `michael gulden`, `becca gulden`
- Deletion decision: Michael's (both are his test guests). Full report was at `/tmp/hfg_naming_sweep.json` (ephemeral — re-run the sweep if needed).

## Environment facts (verified)
- Router: `hde_router.service` (systemd), 1000-chat/5000-queue caps, re-resolves container IPs per request
- Inference: `192.168.1.230:8000` (vLLM `local-qwen-27b-q8-fred`, INT8) + `:8002` (llama.cpp Q4_K_M, multimodal). No SSH from webtop to `.230` (publickey denied) — probe GPU baseline there via `nvidia-smi` + `:8000/metrics`.
- Guest containers: non-root UID 1000:1000, cap_drop ALL, no-new-privileges, 2GB/CPU caps, egress blocked
- pytest: only `/usr/bin/python3` (9.0.3) — platform venv lacks it
