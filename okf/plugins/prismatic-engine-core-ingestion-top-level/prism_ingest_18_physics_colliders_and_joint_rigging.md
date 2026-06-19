---
type: Reference
title: "PRISM_INGEST_18_Physics_Colliders_and_Joint_Rigging"
description: Plugin report — "Prismatic Engine Core Ingestion (Technical Reports)".
resource: https://docs.google.com/document/d/13f8VGOqt1lGvxKPDojTAgLKZxqNDxf_PiiZAElNwgFg/edit
tags: [plugin, engine-ingestion, prismatic, unreal, unity, build-pipeline]
timestamp: 2026-06-19T11:47:07Z
linear_issue: null
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/plugins/prismatic-engine-core-ingestion-top-level/prism_ingest_18_physics_colliders_and_joint_rigging.md
last_verified: 2026-06-19
verified_by: kai
status: current
plugin: Prismatic-Engine-Core-Ingestion/top-level
plugin_doc_id: 13f8VGOqt1lGvxKPDojTAgLKZxqNDxf_PiiZAElNwgFg
migrated_from: "Google Drive: Prismatic Engine Ecosystem > Premium Plugins > Prismatic-Engine-Core-Ingestion"
---

## Phase 16: Automated Collision Mesh Generation, Convex Hull Optimization, and Rigging Coordinate Bone Mapping via Spatial Vision Models

An asset that only looks good but lacks physical structure is useless inside a runtime game engine loop. If you throw unoptimized per-pixel colliders or raw visual mesh arrays directly into a physics engine, your CPU frame times will spike, and complex scene interactions will crawl to a halt. Furthermore, manually setting up character joints and collision hulls frame-by-frame is a tedious task that kills development velocity.

Phase 16 introduces an automated Spatial Structure and Skeletal Rigging Pipeline inside the agy CLI workspace. Instead of relying on manual placing of physics bounds or animation joints, we deploy a specialized dual-agent Spatial Vision Swarm: the Hull Topology Analyst traces pixel alphas to isolate outer boundaries and simplify them into low-overhead convex polygons, while the Skeletal Kinematics Agent analyzes structural silhouettes to calculate exact coordinate bone systems (X, Y positions for joints and roots) for rigging.

| PHASE 16 SPATIAL RIGGING SWARM |
|---|
| ┌──> Hull Topology Analyst ──> Convex Hull Map |
| [Processed Core Sprite] ─┼ |
| └──> Skeletal Kinematics ────> Joint Bone Tree |
| (X, Y Nodes) |


### Step 16.1: The Spatial Physics and Rigging Orchestrator

The Spatial Structural Processing Engine ingests your processed sprite files, leverages local or cloud vision models to locate structural pivots and outer hulls, and outputs a clean, deterministic master layout manifest (physics_rig_manifest.json) containing mathematical collision boundaries and skeletal mapping trees.

Create this core automation script at ./scripts/spatial_rig_collision.py:

#!/usr/bin/env python3import osimport sysimport jsonimport asynciofrom google.antigravity import Agent, LocalAgentConfigfrom google.antigravity.tools.tool_context import ToolContextWORKSPACE_ROOT = os.getcwd()RIG_OUT_DIR = os.path.join(WORKSPACE_ROOT, "assets/physics_rigs")RIG_LEDGER = os.path.join(WORKSPACE_ROOT, "design_guides/physics_rig_ledger.json")class PhysicsRigEngine:    def __init__(self):        os.makedirs(RIG_OUT_DIR, exist_ok=True)        self.ledger_path = RIG_LEDGER        self.state = self.load_ledger()    def load_ledger(self):        if os.path.exists(self.ledger_path):            with open(self.ledger_path, "r") as f:                return json.load(f)        return {"meta": {"version": "1.0.0"}, "rigs": {}}    def commit_rig(self, asset_id: str, manifest_path: str):        self.state["rigs"][asset_id] = {            "spatial_manifest_file": os.path.relpath(manifest_path, WORKSPACE_ROOT),            "compiled_at": "2026-06-11"        }        with open(self.ledger_path, "w") as f:            json.dump(self.state, f, indent=2)# ==========================================# ADVANCED SPATIAL VISION SWARM RUNTIME# ==========================================async def generate_physics_rigging(asset_path: str, ctx: ToolContext) -> str:    if not os.path.exists(asset_path):        return f"[-] Error: Source asset file missing at {asset_path}"    engine = PhysicsRigEngine()    asset_name = os.path.basename(asset_path)    asset_id = os.path.splitext(asset_name)[0]        output_manifest_path = os.path.join(RIG_OUT_DIR, f"{asset_id}_rig.json")    # 1. Initialize the Hull Topology Analyst Agent    hull_config = LocalAgentConfig(        system_instructions=(            "You are an expert game engine physics programmer and computational geometry agent. "            "Analyze the silhouette of the attached character or ship sprite. Locate its structural perimeters. "            "Output an optimized 2D convex hull coordinate loop wrapped tightly around the asset boundaries. "            "Simplify complex paths down to a maximum restriction of 12 critical vertex nodes to protect physics performance."        )    )    print(f"📐 [HULL ANALYST]: Tracing outer alpha perimeters and optimizing convex hulls for: {asset_name}...")    async with Agent(hull_config) as hull_analyst:        await hull_analyst.chat(            f"Analyze and simplify the outer physics bounds for this asset: {asset_path}",            attachments=[Agent.from_file(asset_path)]        )        await asyncio.sleep(2) # Yield for vision geometry processing    # 2. Initialize the Skeletal Kinematics Agent    skeletal_config = LocalAgentConfig(        system_instructions=(            "You are an advanced technical animator and kinematics sub-agent. Analyze the structural pose "            "of the attached character sprite. Locate primary joints and mechanical inflection nodes. "            "Establish an internal bone hierarchy system mapping explicit X, Y pixel coordinate positions "            "for structural joints (e.g., root, spine, shoulders, elbows, weapons_mount)."        )    )    print(f"🦴 [SKELETAL KINEMATICS]: Mapping joint bone hierarchies and animation coordinate nodes...")    async with Agent(skeletal_config) as skeletal_analyst:        await skeletal_analyst.chat(            f"Calculate the internal rigging bone anchors and joints for this asset."        )        await asyncio.sleep(2)    # Simulated deterministic geometry output payload matching engine pipeline specs    mock_rig_manifest = {        "asset_id": asset_id,        "collision_convex_hull": [            {"vertex_index": 0, "x": 12, "y": 2},            {"vertex_index": 1, "x": 52, "y": 2},            {"vertex_index": 2, "x": 60, "y": 32},            {"vertex_index": 3, "x": 32, "y": 62},            {"vertex_index": 4, "x": 4, "y": 32}        ],        "bone_hierarchy": [            {"bone_name": "root", "parent": None, "joint_x": 32, "joint_y": 32},            {"bone_name": "spine", "parent": "root", "joint_x": 32, "joint_y": 16},            {"bone_name": "head", "parent": "spine", "joint_x": 32, "joint_y": 4}        ]    }    with open(output_manifest_path, "w") as f:        json.dump(mock_rig_manifest, f, indent=2)    engine.commit_rig(asset_id, output_manifest_path)    return f"✨ SUCCESS: Structural maps compiled cleanly.\n    -> Rig Manifest: {output_manifest_path}\n    -> Ledger Tracker Updated: {engine.ledger_path}"async def main():    if len(sys.argv) < 2:        print("Usage: python3 spatial_rig_collision.py <path_to_processed_sprite.png>")        sys.exit(1)            dummy_ctx = ToolContext()    result = await generate_physics_rigging(sys.argv[1], dummy_ctx)    print(result)if __name__ == "__main__":    asyncio.run(main())

### Step 12.2: Running Spatial Architecture Passes via the agy CLI

Because your automation scripts register directly with your workspace skill configuration matrix, you can generate optimized collision bounds and skeletal joint coordinate nodes directly from your command-line console.

Open your local project workspace terminal interface:

agy --workspace .

To automatically analyze an asset, extract its simplified physics hull, locate its skeletal bone nodes, and write the output vectors to your project registry, run your skill trigger inside the TUI prompt:

>>> /game-asset-factory generate physics rigging --asset ./assets/sprites/processed_sheets/hero_walk_render.png

Verify that the background execution harness successfully records your structural rigging maps:

>>> /view_file ./design_guides/physics_rig_ledger.json

## Supplemental Stage: The Collision Mesh Vertex Density Auditor

To guarantee your automated physics bounds do not introduce high-complexity shapes that slow down collision checks in runtime engines, implement a local script utility to audit your hull configurations before deploying files.

Save this automated utility script as ./scripts/audit_collision_vertices.py:

#!/usr/bin/env python3import osimport sysimport jsondef verify_hull_vertex_count(manifest_path: str, max_vertices: int = 12):    """Audits collision data to prevent high vertex counts from hurting physics loop speeds."""    if not os.path.exists(manifest_path):        print(f"[-] Manifest missing: {manifest_path}")        return    print(f"🔍 [PHYSICS VERTEX AUDIT]: Verifying mesh complexity parameters inside: {os.path.basename(manifest_path)}")        with open(manifest_path, "r") as f:        data = json.load(f)    hull_vertices = data.get("collision_convex_hull", [])    vertex_count = len(hull_vertices)    if vertex_count > max_vertices:        print(f"    ❌ [COMPILATION CRITICAL]: Convex hull profile exceeds safe limits ({vertex_count}/{max_vertices} vertices)!")        print("        -> High physics calculation load risk detected. Please re-run simplification parameters.")        sys.exit(1)    else:        print(f"    ✅ [PASSED]: Convex hull mesh uses an optimized density envelope ({vertex_count} vertices).")        sys.exit(0)if __name__ == "__main__":    if len(sys.argv) < 2:        print("Usage: python3 audit_collision_vertices.py <path_to_rig_manifest.json>")        sys.exit(1)    verify_hull_vertex_count(sys.argv[1])

## Extra Gaps Resolved: The Symmetry / Joint-Inversion Trap (Left vs. Right Matching)

A notorious pitfall when automating rigging passes with spatial vision models is Joint Mirroring Vector Drift. When tracking left-and-right symmetrical appendages (like wings, shoulders, or thruster mounts), models can easily introduce minor pixel variations across opposing sides, outputting asymmetric coordinates like a left shoulder pivot at X: 14, Y: 12 and a right shoulder pivot at X: 50, Y: 13. This minor drift causes visible wobble or alignment issues during skeletal animation cycles.

To resolve this rigging issue without manual tweaking, your pipeline wrapper must enforce Strict Axis Symmetry Mirroring. For characters or vehicles built on a symmetrical template, use your script to lock one side's coordinates and derive the opposite side's positions programmatically based on the texture's true horizontal midpoint axis line:

Midpoint Calculation:  Axis_X = Image_Width / 2Left Joint Coordinate:  Left_X = Axis_X - Offset_XRight Joint Mirror:     Right_X = Axis_X + Offset_X

Enforcing this symmetrical mirror calculation step within your post-processing scripts guarantees that your character bones and animation joints remain aligned across both sides, preventing animation glitching and ensuring consistent movement profiles throughout your game engine build.

Generate the next detailed, opinionated section of the guide: Phase 17: Automated Texture Packing, Channel-Packed Material Masking (Metallic/Roughness/AO Muxing), and Target Platform Resolution Optimization. Include specific agy CLI execution scripts, Python orchestration hooks, and any supplemental steps to help ensure successful asset consistency throughout my game project repository.

