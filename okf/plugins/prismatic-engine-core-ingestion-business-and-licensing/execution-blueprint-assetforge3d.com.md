---
type: Reference
title: "Execution Blueprint: AssetForge3D.com"
description: Plugin report — "Prismatic Engine Business & Licensing".
resource: https://docs.google.com/document/d/1YwuC2XS7CtgLApImgxoh9USBYYfztMOd5tlCKkQjogU/edit
tags: [plugin, business, licensing, prismatic, tokenomics]
timestamp: 2026-06-19T11:47:07Z
linear_issue: null
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/plugins/prismatic-engine-core-ingestion-business-and-licensing/execution-blueprint-assetforge3d.com.md
last_verified: 2026-06-25
verified_by: kai
status: current
plugin: Prismatic-Engine-Core-Ingestion/business-and-licensing
plugin_doc_id: 1YwuC2XS7CtgLApImgxoh9USBYYfztMOd5tlCKkQjogU
migrated_from: "Google Drive: Prismatic Engine Ecosystem > Premium Plugins > Prismatic-Engine-Core-Ingestion > Business_and_Licensing"
---

# Execution Blueprint: AssetForge3D Pipeline

## Phase 1: Solving the "Lumpy" Geometry (The Template Strategy)

Instead of using a pure "Prompt-to-3D" pipeline (which hallucinates geometry from thin air), your pipeline needs to be Mesh Conditioned.

The Base Vault: Create a library of perfect, low-poly, pre-rigged base meshes (A generic human male, human female, dwarf, quadruped/cat, etc.). These are your "perfect examples/templates."

The New Pipeline: * User prompts: "A cyborg cat with metal plating."

Your AI selects the pre-rigged "Cat" template.

Instead of generating a new 3D model, the AI generates Displacement Maps (to push the geometry out where the metal plates are) and Texture/PBR Maps (to paint it).

The Result: The cat's face is mathematically guaranteed to be perfectly symmetrical and shaped like a cat, but it looks like a cyborg. Because the base template was already rigged, the model is instantly ready to be posed on your site.

## Phase 2: The Google AI Synthetic Data Factory

You are leveraging state-of-the-art generative tools to build the dataset that will train your local 3090s. Here is how to structure that data extraction:

### 1. Google AI Ultra (Image Generation) for Turnarounds

The Goal: Generate the datasets for your LoRAs.

The Technique: You need absolute consistency. When prompting for your character sheets, force the AI to use flat, shadowless lighting (e.g., "Albedo render, flat lighting, purely white background, orthographic projection"). If the AI generates shadows on the 2D image, your 3D model will have shadows permanently baked into the skin, which looks terrible when the user rotates the model in the Three.js viewer.

### 2. Google Veo for PBR (Physically Based Rendering) Extraction

The Goal: Teach your local AI how surfaces "behave" (metal shines, cloth diffuses light, leather absorbs it).

The Technique: Generate short Veo videos of characters rotating under a moving light source. By feeding these videos into a local photometric stereo script on your k3s cluster, you can extract perfect Normal Maps (micro-details), Roughness Maps (how shiny it is), and Metallic Maps.

The Outcome: When a user generates a Warhammer knight, the armor will actually reflect the lighting in your Three.js viewer, rather than just being painted grey.

## Phase 3: SaaS Architecture (Serving the Public from a 42U Rack)

This is the most critical part of your execution. Hosting a public SaaS with Stripe integrations directly from a home k3s cluster is incredibly dangerous if not architected correctly. If a TikTok about AssetForge3D goes viral, your 3090s will get DDoS'd by legitimate users, and your home internet will crash.

### 1. The Asynchronous Queue (Never make the user wait)

3D generation takes time. If a user clicks "Generate" and their browser just spins, the HTTP request will time out after 60 seconds.

The Flow:

User pays/uses a credit on the Vercel/Next.js frontend.

Frontend writes a new row to your Supabase generations table with the status "pending".

Your k3s cluster (via OpenClaw or a custom worker) is constantly listening to Supabase. It grabs the pending job, changes status to "processing", and fires up the GPUs.

When the 3090s finish, the k3s cluster uploads the .glb or .stl file to Supabase Storage, and updates the database row to "complete".

The frontend (listening via Supabase Realtime) sees the "complete" status and displays the model to the user.

### 2. Protecting the Home Network (Cloudflare Tunnels)

Do not open ports on your home router. * Install cloudflared (Cloudflare Tunnels) as a DaemonSet or Deployment in your k3s cluster.

This creates a secure, outbound-only tunnel to Cloudflare's edge network. Your APIs are securely exposed to the internet, but your home IP address is completely hidden, and Cloudflare will absorb any malicious DDoS attacks before they ever reach your 42U rack.

## Phase 4: The Bazar & Printful Swag

Once the core pipeline is generating rigged, template-based models, the ecosystem comes alive:

The Bazar: Users can sell their generated, posed configurations. (Supabase makes revenue splitting easy here).

Printful API: Because your AI generated flat textures (thanks to the Google AI Ultra flat-lighting prompts), you can take the UV map of the character's face/chest, flatten it, and send it directly to the Printful API to put the custom character's face on a t-shirt or mug.

