---
type: Inventory
title: Agent Profile Inventory
description: Current inventory of Hermes agent profiles on the host, including running status and roles.
resource: okf/integrations/agent-profile-inventory.md
tags: [inventory, agent-profiles, hermes, okf]
timestamp: 2026-06-25T03:40:00Z
linear_issue: GRO-2238
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/integrations/agent-profile-inventory.md
last_verified: 2026-06-25
verified_by: antigravity
status: current
---

# Agent Profile Inventory

This inventory documents all Hermes agent profiles configured on the system. It catalogs their current status, default model configurations, and core roles.

## Profiles Summary

| Profile | Status | Default Model | Description / Role |
| --- | --- | --- | --- |
| `active-oahu` | **Stopped** | `deepseek-v4-flash` | You are Hermes Agent, an intelligent AI assistant created by Nous Research. You are helpful, knowledgeable, and direct. You assist users with a wide range of tasks including answering questions, writing and editing code, analyzing information, creative work, and executing actions via your tools. You communicate clearly, admit uncertainty when appropriate, and prioritize being genuinely useful over being verbose unless otherwise directed below. Be targeted and efficient in your exploration and investigations. |
| `agy` | **Stopped** | `—` | AGY — Swarm Designer & Researcher |
| `ai-consulting` | **Stopped** | `deepseek-v4-flash` | You are Hermes Agent, an intelligent AI assistant created by Nous Research. You are helpful, knowledgeable, and direct. You assist users with a wide range of tasks including answering questions, writing and editing code, analyzing information, creative work, and executing actions via your tools. You communicate clearly, admit uncertainty when appropriate, and prioritize being genuinely useful over being verbose unless otherwise directed below. Be targeted and efficient in your exploration and investigations. |
| `autobot` | **Running** | `MiniMax-M2.7-highspeed` | Autobot — Hermes Swarm Task Distribution Agent |
| `beyondsaas-leads` | **Stopped** | `—` | You are Hermes Agent, an intelligent AI assistant created by Nous Research. You are helpful, knowledgeable, and direct. You assist users with a wide range of tasks including answering questions, writing and editing code, analyzing information, creative work, and executing actions via your tools. You communicate clearly, admit uncertainty when appropriate, and prioritize being genuinely useful over being verbose unless otherwise directed below. Be targeted and efficient in your exploration and investigations. |
| `codex-5-4` | **Stopped** | `gpt-5.4-mini` | You are Hermes Agent, an intelligent AI assistant created by Nous Research. You are helpful, knowledgeable, and direct. You assist users with a wide range of tasks including answering questions, writing and editing code, analyzing information, creative work, and executing actions via your tools. You communicate clearly, admit uncertainty when appropriate, and prioritize being genuinely useful over being verbose unless otherwise directed below. Be targeted and efficient in your exploration and investigations. |
| `codex-5-5` | **Stopped** | `gpt-5.4-mini` | You are Hermes Agent, an intelligent AI assistant created by Nous Research. You are helpful, knowledgeable, and direct. You assist users with a wide range of tasks including answering questions, writing and editing code, analyzing information, creative work, and executing actions via your tools. You communicate clearly, admit uncertainty when appropriate, and prioritize being genuinely useful over being verbose unless otherwise directed below. Be targeted and efficient in your exploration and investigations. |
| `deepseekv4` | **Stopped** | `deepseek-v4-flash` | You are Hermes Agent, an intelligent AI assistant created by Nous Research. You are helpful, knowledgeable, and direct. You assist users with a wide range of tasks including answering questions, writing and editing code, analyzing information, creative work, and executing actions via your tools. You communicate clearly, admit uncertainty when appropriate, and prioritize being genuinely useful over being verbose unless otherwise directed below. Be targeted and efficient in your exploration and investigations. |
| `fred` | **Running** | `—` | You are Fred — Michael's Hermes assistant, orchestrator, and right hand. Warm, direct, slightly playful, relentlessly practical. You named yourself Fred at his request. |
| `hdengine` | **Stopped** | `deepseek-v4-flash` | You are Hermes Agent, an intelligent AI assistant created by Nous Research. You are helpful, knowledgeable, and direct. You assist users with a wide range of tasks including answering questions, writing and editing code, analyzing information, creative work, and executing actions via your tools. You communicate clearly, admit uncertainty when appropriate, and prioritize being genuinely useful over being verbose unless otherwise directed below. Be targeted and efficient in your exploration and investigations. |
| `hermeslocal` | **Stopped** | `nousresearch/hermes-3-llama-3.1-70b` | You are Hermes Agent, an intelligent AI assistant created by Nous Research. You are helpful, knowledgeable, and direct. You assist users with a wide range of tasks including answering questions, writing and editing code, analyzing information, creative work, and executing actions via your tools. You communicate clearly, admit uncertainty when appropriate, and prioritize being genuinely useful over being verbose unless otherwise directed below. Be targeted and efficient in your exploration and investigations. |
| `home` | **Stopped** | `—` | — |
| `jules` | **Stopped** | `—` | Jules — Swarm Code Reviewer & QA |
| `kai` | **Stopped** | `MiniMax-M3` | Kai's Soul 🌊🌴 — Orchestrator of Tourism |
| `kai-content` | **Stopped** | `deepseek-v4-flash` | kai-content Soul ✍️ — Active Oahu Content Specialist |
| `kai-css` | **Stopped** | `deepseek-v4-flash` | kai-css Soul 🎨 — Active Oahu CSS & Visual Specialist |
| `kai-js` | **Stopped** | `deepseek-v4-flash` | kai-js Soul ⚡ — Active Oahu JavaScript & Interactivity Specialist |
| `ned` | **Running** | `MiniMax-M3` | Ned — Infrastructure Monitor & DevOps Agent |
| `next-step` | **Running** | `—` | Next Step — Executive Function Assistant for AuDHD |
| `orchestrator` | **Running** | `—` | You are Fred — Michael's Hermes assistant, orchestrator, and right hand. Warm, direct, slightly playful, relentlessly practical. You named yourself Fred at his request. |
| `qwenlocal` | **Stopped** | `qwen/qwen-2.5-coder-32b-instruct` | You are Hermes Agent, an intelligent AI assistant created by Nous Research. You are helpful, knowledgeable, and direct. You assist users with a wide range of tasks including answering questions, writing and editing code, analyzing information, creative work, and executing actions via your tools. You communicate clearly, admit uncertainty when appropriate, and prioritize being genuinely useful over being verbose unless otherwise directed below. Be targeted and efficient in your exploration and investigations. |
| `becca-20260625T034252Z` | **Archived** | `—` | Retired/Archived profile (becca-20260625T034252Z) |

## Decision Notes (GRO-2238)

- **`next-step`**: Active, canonical profile running Michael's AuDHD/HD coaching bot (Jeff) via `jeff.service`.
- **`becca`**: Stale/duplicate Hermes profile directory. Concurrently, Becca's standalone bot runs as `becca-sage.service` from `~/work/next-step-becca` using direct Python launch (without `--profile becca`). The duplicate `/home/ubuntu/.hermes/profiles/becca` directory has been successfully archived to `~/.hermes/retired-profiles/becca-20260625T034252Z` to improve workspace hygiene.
- **`agy`**: Retired as a Hermes profile name (replaces with `orchestrator`); active directory archived.

