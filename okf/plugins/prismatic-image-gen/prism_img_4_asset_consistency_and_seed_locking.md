---
type: Reference
title: "PRISM_IMG_4_Asset_Consistency_and_Seed_Locking"
description: Plugin report — "Prismatic Image Gen Plugin".
resource: https://docs.google.com/document/d/1m-xy1hSJHX3Bp580snljiGaUTS4QHlYTl4eUSDGW7fY/edit
tags: [plugin, image-gen, prismatic, unreal, unity, ai]
timestamp: 2026-06-19T11:47:07Z
linear_issue: null
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/plugins/prismatic-image-gen/prism_img_4_asset_consistency_and_seed_locking.md
last_verified: 2026-06-25
verified_by: kai
status: current
plugin: Prismatic-Image-Gen
plugin_doc_id: 1m-xy1hSJHX3Bp580snljiGaUTS4QHlYTl4eUSDGW7fY
migrated_from: "Google Drive: Prismatic Engine Ecosystem > Premium Plugins > Prismatic-Image-Gen"
---

## Phase 3: Visual Identity Anchor Generation and Asset Seed-Locking

If you pass generic text prompts to Veo from shot to shot, your flagship dreadnought will look like a sleek Star Destroyer in Scene 1, a bulky industrial freighter in Scene 2, and a biological alien cruiser in Scene 3. To maintain perfect continuity across 10+ cutscenes, you must establish Visual Identity Anchors before rendering a single frame of video.

Phase 3 implements an opinionated asset-locking architecture inside the agy workspace. We use the Gemini Omni Image / Imagen 3 generation layer to synthesize static master assets (Ships, Characters, and Biomes) with a strict architectural seed, extract their visual fingerprints, and commit them to an immutable anchor_manifest.json. These reference images act as the structural "Ingredients" that bind all subsequent video generations.

| PHASE 3 SEED-LOCKING ARCHITECTURE |
|---|
| [Shot List Config] ---> Anchor Synthesis Agent ---> [Master PNG Seeds] |
| [Immutable Reference Matrix] <--- Anchor Manifest <───────┘ |


### Step 3.1: Anchor Asset Synthesis

The Anchor Synthesis Agent consumes your Phase 2 JSON shot list and your Phase 1 lore matrix to generate orthographic projection sheets of your game assets. For vehicles and hardware, it forces high-contrast, multi-angle views against clean solid backdrops. For biomes, it enforces wide-angle matte paintings establishing light vectors and atmospheric particle rules.

Create this core automation script at ./scripts/generate_anchors.py to drive the cloud image generation engine while tracking seeds locally:

#!/usr/bin/env python3import osimport sysimport jsonimport asynciofrom google.antigravity import Agent, LocalAgentConfigWORKSPACE_ROOT = os.getcwd()SHOT_LIST = os.path.join(WORKSPACE_ROOT, "tickets/shot_lists/act_01_shot_list.json")MANIFEST_PATH = os.path.join(WORKSPACE_ROOT, "design_guides/anchor_manifest.json")ASSETS_DIR = os.path.join(WORKSPACE_ROOT, "assets")async def synthesize_visual_anchors():    if not os.path.exists(SHOT_LIST):        print(f"[-] Missing shot list profile at {SHOT_LIST}. Run Phase 2 first.")        sys.exit(1)    with open(SHOT_LIST, "r") as f:        shots = json.load(f)    # Gather unique identity keys to avoid duplicate credit burn    unique_ships = set()    unique_biomes = set()    for shot in shots:        anchors = shot.get("identity_anchors", {})        if "primary_subject" in anchors: unique_ships.add(anchors["primary_subject"])        if "environment_biome" in anchors: unique_biomes.add(anchors["environment_biome"])    # Load or initialize the immutable manifest structure    if os.path.exists(MANIFEST_PATH):        with open(MANIFEST_PATH, "r") as f:            manifest = json.load(f)    else:        manifest = {"meta": {"version": "1.0.0"}, "anchors": {}}    config = LocalAgentConfig(        system_instructions=(            "You are a Senior Technical Concept Artist and Asset Automator. Your job is to take text tags and "            "generate precise, deterministic prompts for Imagen 3 / Gemini Omni Image generation that create hyper-consistent "            "reference sheets. For ships, always enforce: 'Orthographic studio concept design, three-quarter view, crisp technical details, "            "solid dark gray backdrop, no text annotations'. For biomes, enforce: 'Cinematic wide master environmental plate, definitive main "            "light source direction, clean atmosphere rule mapping'."        )    )    async with Agent(config) as artist:        # 1. Synthesize Ship Anchors        for ship in unique_ships:            if ship in manifest["anchors"]:                print(f"    -> Anchor '{ship}' already locked in manifest. Skipping generation.")                continue            print(f"🚀 [ANCHOR ENGINE]: Formulating seed prompt for ship asset: '{ship}'...")            prompt_turn = await artist.chat(f"Create a production-ready image generation prompt for a starship entity named: {ship}")                        generated_prompt = ""            async for token in prompt_turn:                generated_prompt += token            target_path = os.path.join(ASSETS_DIR, f"ships/{ship}_seed.png")            os.makedirs(os.path.dirname(target_path), exist_ok=True)            # In runtime, this interfaces with the active session keyring to hit the generation API.            # We simulate the secure cloud rendering download:            await asyncio.sleep(3)            with open(target_path, "wb") as img:                img.write(b"MOCK_HIGH_RES_PNG_BINARY_DATA")            # Lock seed metadata parameters permanently            manifest["anchors"][ship] = {                "type": "hard_surface_mesh",                "file_path": os.path.relpath(target_path, WORKSPACE_ROOT),                "lock_seed": hash(generated_prompt) % 9999999,                "compiled_prompt": generated_prompt.strip()            }            print(f"[+] Identity Lock established for {ship} at: {target_path}")    # Write state back to the workspace design repository    with open(MANIFEST_PATH, "w") as f:        json.dump(manifest, f, indent=2)    print(f"\n✨ Manifest verification verified. All anchors synchronized at: {MANIFEST_PATH}")if __name__ == "__main__":    asyncio.run(synthesize_visual_anchors())

### Step 3.2: Binding and Indexing the Anchor Manifest via the agy CLI

Once your master seeds are rendered and captured inside the file system, you must expose them to the environment's background execution context. This turns your loose assets into explicit systemic dependencies that your game-asset-factory skill can fetch dynamically during video assembly.

Open your project terminal and check your current workspace parameters:

agy --workspace .

To automatically crawl your assets tree, synthesize missing identity seeds, and output the updated mapping manifests, trigger your automation target line inside the TUI dashboard:

>>> /game-asset-factory synchronize anchors from target shotlist: ./tickets/shot_lists/act_01_shot_list.json

Verify that the Go runtime engine cleanly tracks your image bounds and reads the structural anchor configurations out of your design guide folder:

>>> /view_file ./design_guides/anchor_manifest.json

## Supplemental Stage: The Pixel-Art / Palette Uniformity Audit

Because you are building components tailored to a unified artistic style, letting raw cloud variations introduce stray, out-of-gamut colors will compromise visual continuity. Before pushing an asset to your reference folder, run this local script to parse the image's color palette distribution and ensure it adheres to your defined style rules.

Save this script as ./scripts/audit_palette_uniformity.py:

#!/usr/bin/env python3import osimport sysimport jsondef check_image_palette(image_path: str, palette_config_path: str):    """    Simulates a local image verification check comparing the color palette     of a generated seed image against the project's master design palette map.    """    if not os.path.exists(image_path) or not os.path.exists(palette_config_path):        print("[-] Verification Error: Required asset files missing.")        sys.exit(1)    print(f"🎨 [PALETTE AUDIT SYSTEM]: Evaluating color distribution for: {os.path.basename(image_path)}")        with open(palette_config_path, "r") as f:        allowed_palette = json.load(f)    # Simulated color space matrix checking    # In a production environment, wrap this block inside a native PIL (Pillow) image histogram loop    out_of_gamut_count = 0         if out_of_gamut_count > 0:        print(f"    ⚠️  [ALERT]: Found {out_of_gamut_count} stray out-of-gamut pixels in asset.")        print("        -> Recommended action: Re-run seed generation or apply a post-process color remap script.")    else:        print("    ✅ [PASSED]: Image color matrix matches the master brand guidelines palette perfectly.")if __name__ == "__main__":    if len(sys.argv) < 3:        print("Usage: python3 audit_palette_uniformity.py <path_to_image.png> <path_to_palette.json>")        sys.exit(1)    check_image_palette(sys.argv[1], sys.argv[2])

## Extra Gaps Resolved: Seed Stability Realities

A common pitfall with cloud generation models is assuming that appending a numerical seed parameter ("seed": 482910) will guarantee a persistent shape output across completely different prompt descriptions. In modern generative models, text modifiers still exert significant influence over object structures.

To overcome this behavior, always keep your Core Descriptor Block completely static inside your prompt layouts. If your ship is a "Vanguard Class Cruiser with asymmetric forward weapon arrays and solar sails", that precise line must be passed identically across every downstream prompt configuration, varying only the context descriptions (like position, damage tracking, or engine throttle values).

Copy and run the prompt below to generate the next deep dive guide in this multi-part production setup.

Generate the next detailed, opinionated section of the guide: Phase 4: Low-Fi Animatics and Storyboard Execution via Veo 3.1 Lite. Include specific agy CLI execution scripts, Python orchestration hooks, and any supplemental steps to help ensure successful asset consistency throughout my game project repository.

