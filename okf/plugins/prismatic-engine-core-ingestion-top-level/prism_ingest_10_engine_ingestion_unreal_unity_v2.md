---
type: Reference
title: "PRISM_INGEST_10_Engine_Ingestion_Unreal_Unity_v2"
description: Plugin report — "Prismatic Engine Core Ingestion (Technical Reports)".
resource: https://docs.google.com/document/d/1Ec6q3mdlgIWMjVxPParLlmKonaGuuE6IAnqd1-utA34/edit
tags: [plugin, engine-ingestion, prismatic, unreal, unity, build-pipeline]
timestamp: 2026-06-19T11:47:07Z
linear_issue: null
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/plugins/prismatic-engine-core-ingestion-top-level/prism_ingest_10_engine_ingestion_unreal_unity_v2.md
last_verified: 2026-06-25
verified_by: kai
status: current
plugin: Prismatic-Engine-Core-Ingestion/top-level
plugin_doc_id: 1Ec6q3mdlgIWMjVxPParLlmKonaGuuE6IAnqd1-utA34
migrated_from: "Google Drive: Prismatic Engine Ecosystem > Premium Plugins > Prismatic-Engine-Core-Ingestion"
---

## Phase 8: Game Engine Ingestion and Automated Asset Packaging (Unity/Unreal Pipeline Integration)

The ultimate failure point of any asset pipeline is the manual import bottleneck. Forcing an artist or developer to manually drag a 4K master cinematic file, a sprite sheet, or a .wav sound cue into Unity or Unreal Engine opens the door to human error. A single misplaced file, an unoptimized texture compression setting, or an unassigned audio mixer group can completely break your target runtime build.

Phase 8 establishes an automated, production-grade Engine Ingestion Bridge inside your workspace. Instead of treating your game engine folder as a separate world, we write an automated ingestion script triggered by the agy CLI skill framework. This script hot-loads newly generated assets straight into the correct engine sub-directories, updates engine-specific asset manifests, and forces optimization overrides (like disabling texture streaming for pixel-art sprites or building streaming media blueprints for 4K video clips) on the fly.

### Step 8.1: The Automated Engine Ingestion Linker

The Asset Packaging Engine targets your actual game repository directory structure. It reads the output artifacts from Phase 7 (.mp4 masters), Phase 3 (static sprites), and Phase 6 (audio stems). Based on your project configuration, it copies or symlinks the files into Unity's Assets/ or Unreal Engine's Content/ directories while automatically structuring the directory tree and writing out necessary engine configuration meta tags.

Create this core automation script at ./scripts/engine_pipeline_linker.py:

#!/usr/bin/env python3import osimport sysimport jsonimport shutilimport argparsefrom google.antigravity.tools.tool_context import ToolContextWORKSPACE_ROOT = os.getcwd()CONFIG_PATH = os.path.join(WORKSPACE_ROOT, "design_guides/engine_pipeline_config.json")class EngineIngestionBridge:    def __init__(self, target_engine: str, project_path: str):        self.engine = target_engine.lower()        self.project_path = os.path.abspath(project_path)        self.verify_directories()    def verify_directories(self):        if not os.path.exists(self.project_path):            print(f"[-] Critical Error: Target game project path does not exist: {self.project_path}")            sys.exit(1)    def get_destination_folder(self, asset_type: str) -> str:        """Determines folder paths based on game engine conventions."""        base_content_dir = "Content" if self.engine == "unreal" else "Assets"                type_mapping = {            "cutscene": os.path.join(self.project_path, base_content_dir, "Cinematics/Cutscenes"),            "sprite": os.path.join(self.project_path, base_content_dir, "Textures/Sprites"),            "audio": os.path.join(self.project_path, base_content_dir, "Audio/SFX_Tunnels")        }        return type_mapping.get(asset_type, os.path.join(self.project_path, base_content_dir, "ImportStaging"))    def generate_unity_meta(self, dest_path: str, asset_type: str):        """Generates predictable texture and media settings for Unity."""        meta_path = f"{dest_path}.meta"        if os.path.exists(meta_path):            return        print(f"    ⚙️  [META GENERATOR] Creating preset Unity reference meta configurations for {asset_type}...")                # Build strict texture/media import parameter overrides        if asset_type == "sprite":            meta_content = (                "fileFormatVersion: 2\n"                "guid: deadbeef10014001a001fffffffff001\n"                "TextureImporter:\n"                "  textureType: 8\n" # Sprite (2D and UI) type identifier                "  spritePixelsToUnits: 100\n"                "  filterMode: 0\n" # Point filtering (Locked for crisp pixel art symmetry)                "  textureCompression: 1\n"            )        else:            meta_content = "fileFormatVersion: 2\nguid: deadbeef000000000000000000000002\n"        with open(meta_path, "w") as f:            f.write(meta_content)    def ingest_asset(self, source_path: str, asset_type: str) -> str:        if not os.path.exists(source_path):            return f"[-] Error: Source asset file missing at {source_path}"        dest_dir = self.get_destination_folder(asset_type)        os.makedirs(dest_dir, exist_ok=True)                filename = os.path.basename(source_path)        dest_path = os.path.join(dest_dir, filename)        # Copy binary streams safely over to the active environment        shutil.copy2(source_path, dest_path)        print(f"    📦 Ingested asset committed: {os.path.relpath(dest_path, self.project_path)}")        if self.engine == "unity":            self.generate_unity_meta(dest_path, asset_type)        return dest_path# ==========================================# ANTIGRAVITY AUTOMATION SYSTEM BINDINGS# ==========================================def run_ingestion_sync(args) -> str:    # Safe loading wrapper for our target engine pathways    if not os.path.exists(CONFIG_PATH):        default_config = {            "target_engine": "unreal",            "project_path": "./local_game_repo_mock"        }        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)        with open(CONFIG_PATH, "w") as f:            json.dump(default_config, f, indent=2)    with open(CONFIG_PATH, "r") as f:        config = json.load(f)    bridge = EngineIngestionBridge(        target_engine=config.get("target_engine", "unreal"),        project_path=config.get("project_path", "./local_game_repo_mock")    )    print(f"🎮 [ENGINE INGESTION ROUTER]: Commencing packaging pass for asset type: '{args.type}'...")    final_path = bridge.ingest_asset(args.source, args.type)        return f"🚀 Sync Operations Complete. Asset successfully deployed into active game build: {final_path}"if __name__ == "__main__":    parser = argparse.ArgumentParser(description="Antigravity Automated Engine Linker Core")    parser.add_argument("--source", required=True, help="Path to compiled source asset file")    parser.add_argument("--type", required=True, choices=["cutscene", "sprite", "audio"])        args = parser.parse_args()    result = run_ingestion_sync(args)    print(result)

### Step 8.2: Invoking the Linker via the agy CLI/TUI

Because your local tool registry is fully automated inside the game-asset-factory workspace setup, running an asset ingestion sync doesn't require jumping through separate file-moving loops. The agy tool handles path variables automatically.

Open your local project workspace shell terminal:

agy --workspace .

To automatically move and configure a finished 4K master cutscene file directly into your game project repository, pass the tracking properties down into your TUI prompt line:

>>> /game-asset-factory ingest asset from file: ./assets/cutscenes/final_masters/act_01_master_4K.mp4 --type cutscene

To confirm the newly added file structure and meta files are tracking properly inside your engine asset tree, list the target engine repository directory nodes:

>>> /read_dir ./local_game_repo_mock/Content/Cinematics/Cutscenes

## Supplemental Stage: The Git LFS Tracking Validation Guardrail

When pushing large binary media structures (like 30-second 4K .mp4 video files or heavy .wav spatial sound beds) into a project repository, forgetting to track them under Git LFS (Large File Storage) can cause the remote repository to balloon in size and ruin git action runner sync times. Before finalizing an ingestion loop, use a script hook to confirm that your large extensions are correctly mapped to your LFS rules list.

Save this automated validation hook script as ./scripts/verify_git_lfs.sh:

#!/usr/bin/env bash# Git LFS Binary Structure Validation CheckATTRIBUTES_FILE="./.gitattributes"echo "💾 [GIT LFS INTEGRITY CHECK]: Auditing asset type registration rules..."if [ ! -f "$ATTRIBUTES_FILE" ]; then    echo "    ⚠️  [WARNING]: .gitattributes file is missing from project workspace root!"    echo "        -> Large media files might be committed as raw text deltas. Git bloat risk high."    exit 1fi# Check if required binary containers are properly tracked under LFSLFS_MP4=$(grep -c "*.mp4 filter=lfs" "$ATTRIBUTES_FILE")LFS_WAV=$(grep -c "*.wav filter=lfs" "$ATTRIBUTES_FILE")if [ "$LFS_MP4" -eq 0 ] || [ "$LFS_WAV" -eq 0 ]; then    echo "    ❌ [REGISTRATION ERROR]: Media extensions (*.mp4 / *.wav) are missing LFS parameters."    echo "        -> Please add appropriate tracker blocks to your .gitattributes setup."    exit 1else    echo "    ✅ [PASSED]: Large binary structures are correctly registered under Git LFS bounds."    exit 0fi

## Extra Gaps Resolved: Automating Unreal Engine Media Player Blueprints

A common issue when working with Unreal Engine 5 is that importing a flat .mp4 file into your Content/ directory doesn't automatically expose it as a playable texture asset. Unreal requires you to manually instantiate a File Media Source, a Media Player Asset, and a target Media Texture Canvas to display the output frame tracks inside a level blueprint.

To automate this setup without manual clicking, configure your engine_pipeline_linker.py script wrapper to write a basic JSON manifest directly into your engine's Developer/Autoload/ workspace directory when importing a cutscene asset:

{  "automation_task": "GENERATE_MEDIA_PLAYER_TRIPLET",  "source_file_target": "Content/Cinematics/Cutscenes/act_01_master_4K.mp4",  "output_package_path": "Content/Movies/Blueprints/BP_Act_01_Player"}

When you open the Unreal Editor engine console, an internal editor python utility script reads this manifest hook on startup. It automatically builds the media assets and maps the file variables programmatically, cutting down on setup time and ensuring seamless playback in your test builds.

Generate the next detailed, opinionated section of the guide: Phase 9: Metadata Extraction, Automated Documentation, and Production-Ready Archive Compilation. Include specific agy CLI execution scripts, Python orchestration hooks, and any supplemental steps to help ensure successful asset consistency throughout my game project repository.

