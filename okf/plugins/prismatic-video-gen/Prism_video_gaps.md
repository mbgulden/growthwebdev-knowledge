---
type: Reference
title: "Prism video gaps"
description: "Mirrored from Google Drive on 2026-06-25. Source: Drive file 1JzsOTALQQBg83MVCXleFZVTgCLxobaIfdOFFEQmtZRY (modified 2026-06-14). Originally part of the Prismatic source plugin plans and AGY architecture reports."
resource: https://docs.google.com/document/d/1JzsOTALQQBg83MVCXleFZVTgCLxobaIfdOFFEQmtZRY/edit?usp=drivesdk
tags: [drive-mirror, prismatic, gemini-evaluation, agy-report, source-plugin-plans]
timestamp: 2026-06-25T04:04:13.221Z
git_repo: mbgulden/growthwebdev-knowledge
linear_issue: TBD
last_verified: 2026-06-25
verified_by: fred
status: current
drive_file_id: "1JzsOTALQQBg83MVCXleFZVTgCLxobaIfdOFFEQmtZRY"
drive_modified: "2026-06-14T06:49:37.196Z"
---

The video features across the **PRISM\_VID** series are technically cohesive in their "factory-floor" automation, but foundational gaps exist for a production-ready plugin. While the pipeline manages everything from screenplay serialization to 4K mastering, it lacks the interactive and real-time oversight required for a professional "Prismatic Engine" experience.

### **Cohesion of Existing Video Features**

The current workflow follows a logical, state-managed progression:

* **Serialized Pre-production**: Narrative prose is deterministically converted into JSON shot lists with explicit camera movement and visual prompts.  
* **Low-Cost Prototyping**: Uses Veo 3.1 Lite to generate 16:9 low-fi animatics, ensuring blocking and pacing are locked before high-credit renders.  
* **QA-Guarded Rendering**: A stateful rollback system intercepts renders, evaluates them for artifacts or subject mutation, and executes "git-style" rollbacks if defects are found.  
* **High-Fi Mastering**: Verified clips are upscaled to 4K, frame-interpolated for fluid motion (60fps+), and remapped to HDR10 Rec.2020 color spaces.

### **Foundational Gaps & Missing "Plugin" Essentials**

To move from a series of Python scripts to a comprehensive plugin, these foundational elements must be addressed:

* **Real-time Editor Feedback**:  
  * **Current State**: Scripts are "headless" and run in CLI/TUI environments.  
  * **Gap**: A plugin requires an in-engine (UE5/Unity) GUI for visual debugging, such as a "Shot List Editor" or "Visual QA Dashboard" to review rollbacks without leaving the workspace.  
* **Dynamic Resource & VRAM Budgeting**:  
  * **Current State**: Pipelines assume a local 8x RTX 3090 cluster for parallel tasks like ray-traced denoising and 4K mastering.  
  * **Gap**: A foundational "Sentry" is needed to warn developers if their asset stack exceeds the VRAM or disk I/O limits of target consumer hardware (e.g., PS5, Steam Deck).  
* **Temporal Stability & Inter-frame Logic**:  
  * **Current State**: QA loops evaluate individual clips.  
  * **Gap**: The system lacks "Inter-Shot Cohesion" checks. There is no automated auditor to ensure character positions or lighting vectors remain consistent *between* separate rendered segments, which can lead to jarring "jump cuts" in the final master.  
* **Interactive "Human-in-the-Loop" Hooks**:  
  * **Current State**: Automation is highly deterministic; if a render fails 3 times, the pipeline halts.  
  * **Gap**: A plugin needs "Creative Override" handles. Designers should be able to manually "seed-lock" specific frames or adjust AI prompt weights mid-loop via engine Blueprints or C\# scripts.  
* **Content Safety & Watermarking**:  
  * **Current State**: Focus is on physical artifact detection (macro-blocking, subject mutation).  
  * **Gap**: To be a real product, it needs automated content moderation (SFW filters) and digital watermarking to track the provenance of AI-generated cinematic assets.

### **Summary of Foundational Requirements**

| Feature Category | Foundational Need | Purpose |
| ----- | ----- | ----- |
| **UX/UI** | **Live Viewport Scrubbing** | Audit AI-generated blocking directly in the 3D scene. |
| **Performance** | **Hardware-Agnostic Scaling** | Profiles for non-3090 rigs (e.g., Cloud-only execution). |
| **QA** | **Cross-Shot Continuity Auditor** | Prevent lighting or asset "drift" across a sequence. |
| **Compliance** | **Metadata Attribution Registry** | Automatically bake licensing and AI-origin tags into .mp4 masters. |

