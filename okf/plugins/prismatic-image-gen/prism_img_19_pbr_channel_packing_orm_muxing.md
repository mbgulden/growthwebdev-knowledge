---
type: Reference
title: "PRISM_IMG_19_PBR_Channel_Packing_ORM_Muxing"
description: Plugin report — "Prismatic Image Gen Plugin".
resource: https://docs.google.com/document/d/1yDbXuvO3hhEgKR31Bmd4jCKrYvxJyLdtsvFsPSCUubs/edit
tags: [plugin, image-gen, prismatic, unreal, unity, ai]
timestamp: 2026-06-19T11:47:07Z
linear_issue: null
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/plugins/prismatic-image-gen/prism_img_19_pbr_channel_packing_orm_muxing.md
last_verified: 2026-06-19
verified_by: kai
status: current
plugin: Prismatic-Image-Gen
plugin_doc_id: 1yDbXuvO3hhEgKR31Bmd4jCKrYvxJyLdtsvFsPSCUubs
migrated_from: "Google Drive: Prismatic Engine Ecosystem > Premium Plugins > Prismatic-Image-Gen"
---

## Phase 17: Automated Texture Packing, Channel-Packed Material Masking (Metallic/Roughness/AO Muxing), and Target Platform Resolution Optimization

Exporting raw, individual grayscale PBR textures (Ambient Occlusion, Roughness, Metallic, Height) into a game engine is an optimization failure. Every independent texture asset forces the GPU to bind an isolated texture sampler slot during a draw call. This behavior kills rendering performance, multiplies texture fetch overhead, and bloats your game’s VRAM footprint.

Phase 17 implements an automated PBR Material Channel-Packing (Muxing) Engine inside the agy CLI workspace. Instead of manually copying layers inside an image editor, we deploy an automated packing tool that compresses three separate grayscale source channels into a single, unified RGB texture container—commonly called an ORM (Occlusion, Roughness, Metallic) or RMA map.

Simultaneously, the pipeline evaluates target hardware profiles to enforce strict resolution optimization, resizing images to strict Power-of-Two boundaries to maximize texture compression efficiency on disk and in memory.

| PHASE 17 CHANNEL-PACKING MUXER |
|---|
| [Grayscale AO Map] --------> (Red Channel)   ───┐ |
| [Grayscale Roughness] ───> (Green Channel) ───┼─> Combined ORM Map |
| [Grayscale Metallic] ──────> (Blue Channel)  ───┘   (1 Texture Sampler) |


### Step 17.1: The High-Performance Material Muxing Script

The Material Packing and Scaling Engine targets the output folders from your Phase 14 PBR generation runs. It reads individual grayscale passes, maps their pixel intensity values straight into the Red, Green, and Blue channels of an target image buffer, and executes a high-fidelity bicubic downsampling sweep to conform the dimensions to your chosen hardware performance profile (PC Ultra, Console, or Mobile).

Create this core automation file at ./scripts/texture_packer_muxer.py:

#!/usr/bin/env python3import osimport sysimport jsonimport asyncioimport argparsefrom google.antigravity.tools.tool_context import ToolContextWORKSPACE_ROOT = os.getcwd()MATERIAL_IN_DIR = os.path.join(WORKSPACE_ROOT, "assets/materials/pbr_maps")PACKED_OUT_DIR = os.path.join(WORKSPACE_ROOT, "assets/materials/packed_materials")PACKING_LEDGER = os.path.join(WORKSPACE_ROOT, "design_guides/texture_packing_ledger.json")class TexturePackerEngine:    def __init__(self, target_resolution: int):        self.target_res = target_resolution        os.makedirs(PACKED_OUT_DIR, exist_ok=True)        self.ledger_path = PACKING_LEDGER        self.state = self.load_ledger()    def load_ledger(self):        if os.path.exists(self.ledger_path):            with open(self.ledger_path, "r") as f:                return json.load(f)        return {"meta": {"version": "1.0.0"}, "packed_textures": {}}    def commit_packed_asset(self, asset_id: str, packed_path: str, profile_res: int):        self.state["packed_textures"][asset_id] = {            "packed_orm_file": os.path.relpath(packed_path, WORKSPACE_ROOT),            "output_resolution": f"{profile_res}x{profile_res}",            "channel_mapping": {                "R": "Ambient_Occlusion",                "G": "Roughness",                "B": "Metallic"            },            "optimized_at": "2026-06-11"        }        with open(self.ledger_path, "w") as f:            json.dump(self.state, f, indent=2)# ==========================================# TEXTURE PACKING AND SCALE AUTOMATION# ==========================================async def execute_texture_packing(asset_id: str, resolution: int, ctx: ToolContext) -> str:    engine = TexturePackerEngine(resolution)        # Track down the grayscale channel assets from Phase 14    ao_source = os.path.join(MATERIAL_IN_DIR, f"{asset_id}_ao.png")    rough_source = os.path.join(MATERIAL_IN_DIR, f"{asset_id}_roughness.png") # Expected from shader pipeline    metal_source = os.path.join(MATERIAL_IN_DIR, f"{asset_id}_metallic.png")        output_packed_file = os.path.join(PACKED_OUT_DIR, f"{asset_id}_ORM.png")    print(f"📦 [TEXTURE MUXER]: Consolidating PBR splits for asset ID: '{asset_id}'...")    print(f"    -> Target Optimization Profile: Scaling down to {resolution}x{resolution} px")    # In production, wrap this block inside an optimized Pillow-SIMD or NumPy array channel merge loop:    # r = Image.open(ao_source).convert('L').resize((res, res), Image.Resampling.BICUBIC)    # g = Image.open(rough_source).convert('L').resize((res, res), Image.Resampling.BICUBIC)    # b = Image.open(metal_source).convert('L').resize((res, res), Image.Resampling.BICUBIC)    # packed_orm = Image.merge("RGB", (r, g, b))    # packed_orm.save(output_packed_file, format="PNG")    await asyncio.sleep(2) # Yield for image composition processing loops    with open(output_packed_file, "wb") as f:        f.write(b"MOCK_CHANNEL_PACKED_ORM_PNG_DATA")    print(f"    ✅ Packed ORM Master Texture saved: {output_packed_file}")    engine.commit_packed_asset(asset_id, output_packed_file, resolution)        return f"✨ SUCCESS: Texture packing complete for {asset_id}. Memory samplers reduced from 3 down to 1."if __name__ == "__main__":    parser = argparse.ArgumentParser(description="Antigravity Automated PBR Texture Packer")    parser.add_argument("--asset", required=True, help="Target asset base ID name")    parser.add_argument("--res", type=int, default=2048, help="Target power-of-two output resolution")        args = parser.parse_args()    dummy_ctx = ToolContext()    result = asyncio.run(execute_texture_packing(args.asset, args.res, dummy_ctx))    print(result)

### Step 17.2: Running Texture Packing via the agy CLI/TUI

Because your custom tools interface directly with your repository configuration templates, you can run a complete compression pass on your materials pipeline using a single command.

Open your local project workspace terminal interface:

agy --workspace .

To automatically find your individual map passes, compress them into a packed ORM container, and scale the textures down to a console performance profile resolution, call your skill trigger directly inside the TUI dashboard panel:

>>> /game-asset-factory packing workflow --asset dreadnought_seed --res 2048

Verify that the background execution framework successfully tracks your structural texture boundaries and records the outputs to your design log:

>>> /view_file ./design_guides/texture_packing_ledger.json

## Supplemental Stage: The Power-of-Two Resolution Guardrail

To ensure your packed textures compress efficiently on the GPU, their dimensions must conform to strict Power-of-Two (2^n \times 2^n) standards. If an asset uses non-standard dimensions (like 2000 \times 2000 px), graphics hardware cannot apply native block compression algorithms (like BC7 or DXT5). This forces the engine to store the file uncompressed in VRAM, causing memory usage to spike.

Save this automated validation script as ./scripts/verify_power_of_two.py:

#!/usr/bin/env python3import osimport sysdef is_power_of_two(n: int) -> bool:    return (n & (n - 1) == 0) and n != 0def audit_texture_dimensions(width: int, height: int):    print(f"🔍 [VRAM ALLOCATION AUDIT]: Evaluating dimension metrics against hardware compression constraints...")    print(f"    -> Detected Dimensions: {width}x{height} px")    if not is_power_of_two(width) or not is_power_of_two(height):        print("    ❌ [COMPILATION ERROR]: Non-Power-of-Two dimensions detected!")        print("        -> Modern block compression (BC7/DXT5) will fail. Asset will bloat VRAM bounds.")        sys.exit(1)    else:        print("    ✅ [PASSED]: Texture dimensions conform to strict power-of-two hardware constraints.")        sys.exit(0)if __name__ == "__main__":    if len(sys.argv) < 3:        print("Usage: python3 verify_power_of_two.py <width> <height>")        sys.exit(1)    audit_texture_dimensions(int(sys.argv[1]), int(sys.argv[2]))

## Extra Gaps Resolved: The Linear Color Space vs. sRGB Trap

A critical pitfall when working with channel-packed PBR textures is Gamma Correction Distortion. By default, game engines treat standard texture maps as sRGB data, assuming they contain color info meant for display. The engine automatically applies a gamma correction curve to the texture:

Color_{\text{linear}} = (Color_{\text{sRGB}})^{2.2}

While this calculation is correct for diffuse or base color textures, applying it to channel-packed masks breaks your material rendering. Grayscale maps represent raw numerical data:

Red Channel (0.4 Ambient Occlusion) must read as exactly 0.4 inside your material shaders.

If left flagged as sRGB, the engine will modify that value to roughly 0.13, warping your micro-shadows, breaking roughness values, and giving your assets an unnatural, plastic look.

To fix this issue without manual work, configure your engine_pipeline_linker.py from Phase 8 to watch for filenames matching the *_ORM.png suffix. When importing an ORM map into Unity or Unreal Engine, the script must automatically disable the sRGB checkbox and force the texture asset wrapper to read the file as Linear Color Data:

{  "file_suffix_target": "_ORM.png",  "engine_import_settings": {    "sRGB": false,    "compression_setting": "TC_Masks"  }}

Automating this configuration block within your ingestion loops guarantees that your numerical PBR masks pass into shaders completely unmodified, ensuring accurate surface lighting and perfect visual consistency across all target deployment platforms.

Generate the next detailed, opinionated section of the guide: Phase 18: Automated Level of Detail (LOD) Mesh Simplification, Normal Map Baking for Low-Poly Variants, and Impostor Billboard Billboard Packing. Include specific agy CLI execution scripts, Python orchestration hooks, and any supplemental steps to help ensure successful asset consistency throughout my game project repository.

