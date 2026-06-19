---
type: Index
title: Prismatic Engine Plugins
description: AGY-authored plugin research reports for the Prismatic Engine ecosystem — image gen, video gen, audio/acoustics, game story engine, core engine ingestion, and business/licensing.
resource: okf/plugins/index.md
tags: [index, plugins, prismatic, agy]
timestamp: 2026-06-19T11:50:00Z
linear_issue: null
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/plugins/index.md
last_verified: 2026-06-19
verified_by: kai
status: current
source_drive_folder: "Prismatic Engine Ecosystem > Premium Plugins"
---

# Prismatic Engine Plugins

AGY (Antigravity CLI) authored 81+ technical reports covering six plugin
domains for the Prismatic Engine ecosystem. All reports were originally
created in Google Drive on 2026-06-14 and mirrored to this OKF bundle
on 2026-06-19.

## Source

- **Google Drive folder:** `Prismatic Engine Ecosystem > Premium Plugins`
- **Authoring agent:** AGY (Antigravity CLI)
- **Created:** 2026-06-14
- **Mirrored to OKF:** 2026-06-19 (Kai)

## Plugin sections

| Section | Reports | Description |
|---|---|---|
| [Prismatic Image Gen](./prismatic-image-gen/index.md) | 14 | AI image gen for game engines — sprite sheets, normal maps, PBR packing, seed locking |
| [Prismatic Video Gen](./prismatic-video-gen/index.md) | 8 | Cinematic video gen — shot lists, animatics, super-resolution, denoising |
| [Prismatic Audio & Acoustics](./prismatic-audio-acoustics/index.md) | 8 | Game audio — spatial SFX, lip-sync, flow music, acoustic occlusion |
| [Prismatic Game Story Engine](./prismatic-game-story-engine/index.md) | 11 | Narrative systems — localization, VR/AR UI, UGC workshop, sprite animation |
| [Prismatic Engine Core Ingestion](./prismatic-engine-core-ingestion-top-level/index.md) | 30 | Unreal/Unity ingestion — physics, networking, shaders, telemetry, build orchestration |
| [Prismatic Engine Business & Licensing](./prismatic-engine-core-ingestion-business-and-licensing/index.md) | 10 | AssetForge3D — tokenomics, execution blueprint, business plan |
| **TOTAL** | **81** | |

## What these reports cover

These reports collectively describe a comprehensive plugin suite that
AI-augments Unreal Engine and Unity workflows:

- **Asset pipelines** — automated ingestion from AI generation (image,
  video, audio) into engine-ready assets with proper LODs, atlases, and
  metadata.
- **Build orchestration** — multi-platform compilation pipelines with
  hardware-targeted asset profiling.
- **Real-time rendering** — neural super-resolution, denoising, RTGI,
  volumetric lighting.
- **Audio integration** — distributed audio architecture, phoneme
  extraction for lip-sync, physics-driven occlusion.
- **Story & content** — prompt engineering, swarm analysis, UGC
  validation, localization.
- **Business model** — AssetForge3D tokenomics, low-latency 3D generation
  architecture, execution blueprint.

The plugins target **darius-star**, **whatanadventure-games**, and any
other game project in the prismatic ecosystem.

## Conventions

Each individual report file:

- Lives at `okf/plugins/<section>/<slugified-name>.md`
- Frontmatter carries `plugin_doc_id` (Google Doc ID) for round-trip lookup
- Frontmatter carries `migrated_from` with the original Drive path
- `resource:` points back to the live Google Doc
- `type: Reference` (these are dense reference docs, not decisions or
  audits)

## What counts as a "plugin report"

A plugin report is a dense technical reference document covering one
specific implementation, architecture, or workflow inside a Prismatic
Engine plugin. Distinguished from:

- **Standards** (`okf/standards/`) — cross-project invariants
- **Decisions** (`okf/decisions/`) — ADRs with context + choice + consequences
- **Audits** (`okf/audits/`) — gap analyses with findings + recommendations
- **Reports** (`okf/reports/`) — time-stamped operational snapshots
- **Research** (`okf/research/`) — reusable reference research

Plugin reports are reference docs you read end-to-end when implementing
or extending a specific feature.
