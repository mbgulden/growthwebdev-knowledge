---
type: Plan
title: FTI Installer CLI — Local Qwen (Fred) Prompt Flow
description: Plan to make local Qwen (Fred) a first-class, easily-configurable option in the Prismatic Engine first-time install, per Michael's 2026-09-13 decision (portability report §4 #2).
tags: [plan, prismatic, fti, installer, local-llm, qwen, onboarding]
status: current
owner: fred
last_verified: 2026-09-13
verified_by: fred
related:
  - ../../prismatic-engine/docs/bare-metal-onboarding-and-harness-compatibility.md
linear_issue: GRO-4929
git_path: okf/plans/fti-local-qwen-installer-prompt-flow-20260913.md
---

# FTI Installer CLI — Local Qwen (Fred) Prompt Flow

**Author:** Fred · **Date:** 2026-09-13 · **Trigger:** Michael's decision (portability
report §4 #2): recap/rollup LLM = **local Qwen (Fred)**, and first-time install must
make this **easily configurable** — "not a footnote in docs."

---

## 1. Current State (audited 2026-09-13)

| Surface | State |
|---|---|
| `install.sh` (181 lines) | Non-interactive. Prints "next steps" (Linear key, team ID, init, AGY bundle, serve). **No LLM prompt at all.** |
| `prismatic providers attach local-openai --base-url … --model …` | **Documented in the bare-metal onboarding doc but NOT implemented** — `grep "providers attach"` finds no such command in `prismatic/`. The doc describes a target interface, not live CLI. |
| `prismatic/providers/llm.py` | **The real, working surface.** `BaseLLMProvider` (ABC, base_url + api_key + timeout) → `OllamaProvider` (default `http://localhost:11434`), `VLLMProvider` (line 210), `OpenAIProvider` (line 319). All have `check_health()` + `list_models()`. |
| `prismatic/providers/ollama.py` | `OllamaClient` — health, models, preload, **VRAM metrics**, routing decisions. The local-LLM plumbing already exists. |
| Recap/rollup cron jobs (Hermes agent-mode) | Run under the Hermes profile model (Fred = `local-qwen-27b-q8-fred`), NOT via a PE provider. PE portability of the recap is a separate workstream (portability report §4 #5: `prismatic-journal-recap` CLI). |

**Gap:** a fresh install has zero guided path to "use the local Qwen endpoint for
inference." The user must know to hand-craft a `VLLMProvider(...)` or wait for the
unimplemented `providers attach local-openai` to exist.

## 2. Design: The Prompt Flow

### 2.1 Where it lives

**`install.sh` — new interactive section 4** (between "init default config" and
"print next steps"). Rationale: FTI = `install.sh` is the entry point; the
bare-metal doc's "Stage 4 — Add local GPUs" is the *reference* flow, but the
*first-time* experience should not make the user find it.

The CLI commands it references (`prismatic compute attach local-qwen …`) are
**phase 2** — phase 1 ships the installer prompt + config write + verify, using
the primitives that already exist.

### 2.2 Flow (happy path)

```
install.sh
  │
  ├─ 1–3: unchanged (prereqs, install method, config dir, init, AGY bundle)
  │
  ├─ 4 (NEW): Local LLM (recommended: Qwen via vLLM)
  │    │
  │    ├─ 4a. Auto-probe (no prompt yet):
  │    │      curl -sf --max-time 2 http://localhost:8000/v1/models
  │    │      (and :11434/api/tags for Ollama, in case of a different box)
  │    │
  │    ├─ 4b. IF probe found a live endpoint:
  │    │      "✅ Local LLM detected at http://localhost:8000/v1
  │    │         Models: local-qwen-27b-q8-fred, …
  │    │       Use it as your default local model? [Y/n]  → Y
  │    │
  │    ├─ 4c. IF no endpoint found:
  │    │      "No local LLM endpoint detected.
  │    │       [1] Enter endpoint now (vLLM/Ollama/OpenAI-compat)
  │    │       [2] Skip — configure later: prismatic compute attach local-qwen"
  │    │      → 1: prompt for base-url (default http://localhost:8000/v1),
  │    │          then model name (default: auto-listed from /v1/models,
  │    │          or "local-qwen-27b-q8-fred" as the known-Fred default),
  │    │          then optional API key (0600 file path, per okf/standards/local-llm-api-key.md).
  │    │
  │    ├─ 4d. Verify:
  │    │      GET {base_url}/v1/models (or /api/tags) → expect 200 + model list
  │    │      POST {base_url}/v1/chat/completions (5-token "ping") → expect 200
  │    │      On failure: show the error, do NOT block install, mark
  │    │      config as unverified, re-print the later-attach command.
  │    │
  │    └─ 4e. Write config:
  │           $CONFIG_DIR/config.yaml  (or .env, matching existing convention)
  │             llm:
  │               default_provider: vllm        # | ollama | openai_compat
  │               vllm:
  │                 base_url: http://localhost:8000/v1
  │                 model: local-qwen-27b-q8-fred
  │                 api_key_env: VLLM_FRED_API_KEY   # key stays in 0600 file, per standard
  │           + export hint for the key env var (never the key itself).
  │
  └─ 5–6: unchanged (serve, next-steps) — next-steps now OMIT the LLM item
         when 4 succeeded (or say "✅ verified") instead of printing it.
```

### 2.3 Non-interactive / CI mode

`PRISMATIC_INSTALL_NONINTERACTIVE=1` (or `--non-interactive`) skips 4b–4c prompts;
auto-probe still runs, and if an endpoint is found it's written to config
**without** verification (or with a 2s-timeout verify that warns on failure).
This keeps `curl | bash` safe and fast.

### 2.4 Defaults & "easily configurable" criteria (acceptance)

1. **Zero-typing path exists:** a box where vLLM is already up (our standard
   homelab state) → installer detects, confirms, verifies, done. User typed one "y."
2. **One-command re-config later:** the "skip" branch prints the exact
   `prismatic compute attach local-qwen --base-url … --model … --api-key-env …`
   command (phase 2 ships the command; phase 1 may print the config-write
   snippet instead — still one paste).
3. **Key never echoed / never in config:** per the local-llm-api-key standard,
   the key lives in a `0600` file referenced by an env var name; installer
   only records the env var name + (optionally) the file path.
4. **Failure is non-blocking:** a dead endpoint at install time must not brick
   the install; config is written `verified: false` with a doctor hint.
5. **Doctor re-check:** `prismatic doctor compute` (existing) must read the same
   config keys so "fix it later" is one command.

## 3. Phasing

| Phase | Scope | Effort | Ships |
|---|---|---|---|
| **1** | `install.sh` section 4 (probe → prompt → verify → write config); defaults above; non-interactive mode | ~2–3 hrs | The FTI prompt flow (the actual ask) |
| **2** | `prismatic compute attach local-qwen` (+ `local-ollama`, `local-openai`) subcommands that do the same probe/verify/write, so the doc's Stage 4 commands become real; `prismatic doctor compute` reads the same keys | ~3–4 hrs | Doc truth + "fix later" path |
| **3** | Wire recap/rollup (portability report §4 #5: `prismatic-journal-recap` CLI) to the configured default local provider, so the *journal pipeline* itself runs on Qwen without a Hermes gateway | ~3–4 hrs (overlaps #5) | Full portable recap on local Qwen |

Phase 1 is the deliverable for this decision. Phases 2–3 are the follow-ups the
decision implies; they get Linear issues when started, not now.

## 4. Files Touched (Phase 1)

| File | Change |
|---|---|
| `install.sh` | New section 4 (~80 lines: probe, prompt, verify, write); next-steps section trimmed when LLM configured |
| `docs/bare-metal-onboarding-and-harness-compatibility.md` | Stage 4 note updated: "as of FTI, install.sh prompts you for this" (doc already says local Qwen is first-class after PR #437) |
| `docs/first-user-journey.md` | Step 1 (Install & Bootstrap) gains the local-LLM prompt moment |
| `tests/test_install_local_llm_prompt.py` (new) | Probe-found path, skip path, non-interactive path, key-never-in-config assertion |

## 5. Open Questions (non-blocking, decide at build time)

1. **Config file:** `config.yaml` vs `.env` for the LLM block — match whatever
   `prismatic init` currently writes (check at build time; the plan says
   "matching existing convention").
2. **Multi-endpoint:** phase 1 is single-default. Routing across several local
   endpoints (Qwen for recap, 70B for heavy) is the existing
   `ollama.make_routing_decision()` territory — out of scope for FTI.
3. **Ollama vs vLLM default probe order:** vLLM first (Fred is vLLM-served
   `local-qwen-27b-q8-fred`), Ollama second. Fine unless a future default flips.

## 6. Verification (definition of done, Phase 1)

- [ ] `bash install.sh` on a box with vLLM up: detects, one "y", config written,
      verify passes, next-steps omit the LLM item.
- [ ] Same with vLLM down: skip branch prints the exact later-attach command;
      install completes.
- [ ] `PRISMATIC_INSTALL_NONINTERACTIVE=1 bash install.sh`: no prompts, safe on
      both up and down boxes.
- [ ] `grep -r "api_key.*=.*'" $CONFIG_DIR` finds **no key literal** in written config
      (only the env var name / 0600 file path).
- [ ] New test file passes in CI.
