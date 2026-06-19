---
type: Reference
title: "PRISM_VID_3_Cinematic_Pre-production_Screenplay_and_Shot_List"
description: Plugin report — "Prismatic Video Gen Plugin".
resource: https://docs.google.com/document/d/1MF0IwFrtiPzpuuSk-DxGWOC-onMkPaszrdLs26HYpg0/edit
tags: [plugin, video-gen, prismatic, cinematic, ai]
timestamp: 2026-06-19T11:47:07Z
linear_issue: null
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/plugins/prismatic-video-gen/prism_vid_3_cinematic_pre-production_screenplay_and_shot_list.md
last_verified: 2026-06-19
verified_by: kai
status: current
plugin: Prismatic-Video-Gen
plugin_doc_id: 1MF0IwFrtiPzpuuSk-DxGWOC-onMkPaszrdLs26HYpg0
migrated_from: "Google Drive: Prismatic Engine Ecosystem > Premium Plugins > Prismatic-Video-Gen"
---

## Phase 2: Screenplay Serialization and Multi-Agent Shot List Generation

Dumping a raw story outline into a video generation engine will yield chaotic, unstructured visual noise. To maintain perfect continuity across 10+ cutscenes, you must separate creative composition from technical execution.

Phase 2 establishes an opinionated, multi-agent pipeline inside the agy workspace. We take your 60,000-word canon core (structured into the structured_lore_matrix.json from Phase 1) and run it through a dual-agent compilation loop: the Screenplay Writer Agent transforms narrative concepts into strict screenplays, and the Cinematographer Agent strips those scripts down into a frame-accurate, multi-axis JSON Shot List.

| PHASE 2 DUAL-AGENT PIPELINE OVERVIEW |
|---|
| [Lore Matrix + Raw Notes] ---> Screenplay Writer Agent ---> [Markdown] |
| [Deterministic JSON]     <---  Cinematographer Agent  <───────────┘ |


### Step 2.1: Screenplay Serialization

The Screenplay Writer Agent's sole purpose is to convert prose, lore nodes, and character banter sheets into structured, standard screenplay layouts. It cross-references your character arc profiles to ensure that dialogue matches their technical traits and personal backgrounds.

To execute this headlessly inside the agy CLI, create an automation orchestration file at ./scripts/serialize_screenplay.py. This script spins up the parent writer agent, mounts your Phase 1 local context, and outputs serialized markdown acts.

#!/usr/bin/env python3import osimport sysimport asynciofrom google.antigravity import Agent, LocalAgentConfig# Ensure workspace paths are lockedWORKSPACE_ROOT = os.getcwd()LORE_MATRIX = os.path.join(WORKSPACE_ROOT, "design_guides/structured_lore_matrix.json")OUTPUT_DIR = os.path.join(WORKSPACE_ROOT, "tickets/serialized_acts")async def run_serialization(raw_notes_path: str, act_num: int):    if not os.path.exists(LORE_MATRIX):        print(f"[-] Critical Error: Lore matrix missing at {LORE_MATRIX}. Run Phase 1 first.")        sys.exit(1)            with open(raw_notes_path, "r", encoding="utf-8") as f:        raw_notes = f.read()    os.makedirs(OUTPUT_DIR, exist_ok=True)    output_file = os.path.join(OUTPUT_DIR, f"act_{act_num:02d}_screenplay.md")    # Define strict structural boundaries for the Writer Agent    writer_config = LocalAgentConfig(        system_instructions=(            "You are a master screenplay encoder specializing in hard science-fiction cinematography. "            "Your task is to serialize raw narrative notes into a strict, production-ready markdown screenplay.\n\n"            "FORMATTING RULES:\n"            "1. Use classic screenplay sluglines: INT/EXT. LOCATION - TIME\n"            "2. Character action blocks must accompany all technical descriptions.\n"            "3. Dialogue formatting must be explicitly separated by line breaks.\n"            "4. Infuse spatial coordinates into descriptions (e.g., Foreground, Background, Frame Right).\n\n"            "CRITICAL: Adhere to character behavioral traits and ship tech parameters defined in the lore matrix context file."        )    )    print(f"🎭 [WRITER SWARM]: Compiling Act {act_num} into a standardized screenplay format...")        async with Agent(writer_config) as writer:        # Load the lore matrix into memory via the runtime attachment layer        response = await writer.chat(            f"Contextualize using the loaded lore matrix. Now, serialize this raw narrative outline into Act {act_num}:\n\n{raw_notes}",            attachments=[Agent.from_file(LORE_MATRIX)]        )                screenplay_content = ""        async for token in response:            screenplay_content += token            # Stream live tracking to stderr to keep the main output pipeline clean            sys.stderr.write(token)            sys.stderr.flush()    with open(output_file, "w", encoding="utf-8") as f:        f.write(screenplay_content)            print(f"\n[+] Act {act_num} successfully written to: {output_file}")if __name__ == "__main__":    if len(sys.argv) < 3:        print("Usage: python3 serialize_screenplay.py <path_to_raw_notes.txt> <act_number>")        sys.exit(1)    asyncio.run(run_serialization(sys.argv[1], int(sys.argv[2])))

### Step 2.2: Multi-Agent Shot List Generation

Once your script is saved as clean markdown, the Cinematographer Agent parses the file. This agent converts creative prose into an explicit, multi-axis JSON format that specifies aspect ratios, focal lengths, camera motion paths, and identity keys for Veo 3.1.

Create the generation script at ./scripts/generate_shot_list.py:

#!/usr/bin/env python3import osimport sysimport jsonimport asynciofrom google.antigravity import Agent, LocalAgentConfigWORKSPACE_ROOT = os.getcwd()INPUT_DIR = os.path.join(WORKSPACE_ROOT, "tickets/serialized_acts")OUTPUT_DIR = os.path.join(WORKSPACE_ROOT, "tickets/shot_lists")async def compile_shot_list(act_num: int):    screenplay_path = os.path.join(INPUT_DIR, f"act_{act_num:02d}_screenplay.md")    if not os.path.exists(screenplay_path):        print(f"[-] Screenplay file missing: {screenplay_path}")        sys.exit(1)    with open(screenplay_path, "r", encoding="utf-8") as f:        screenplay_text = f.read()    os.makedirs(OUTPUT_DIR, exist_ok=True)    output_json_path = os.path.join(OUTPUT_DIR, f"act_{act_num:02d}_shot_list.json")    cinematographer_config = LocalAgentConfig(        system_instructions=(            "You are an automated Cinematographer and Shot-List Director. Your objective is to parse a markdown screenplay "            "and output a completely deterministic, well-structured JSON array of shots tailored for Veo 3.1 video generation.\n\n"            "JSON SCHEMA EXPECTED:\n"            "[\n"            "  {\n"            "    \"shot_id\": \"ACT_XX_SHOT_XX\",\n"            "    \"duration_seconds\": 8,\n"            "    \"camera_movement\": \"Dolly in, slow tracking pan left, 35mm low-angle wide\",\n"            "    \"visual_prompt\": \"Detailed description of elements matching style anchors\",\n"            "    \"identity_anchors\": {\n"            "      \"primary_subject\": \"ship_dreadnought_alpha\",\n"            "      \"environment_biome\": \"plasma_reef\"\n"            "    }\n"            "  }\n"            "]\n\n"            "CRITICAL RULES:\n"            "1. Output ONLY the raw JSON block. No markdown markers, no wrap code fences, no preamble text.\n"            "2. Split long screenplay beats into separate shots of 4, 6, or 8 seconds each.\n"            "3. Assign strict reference names to identity_anchors keys matching our style protocols."        )    )    print(f"🎬 [CINEMATOGRAPHER SWARM]: Translating Act {act_num} script into a structural JSON sequence...")        async with Agent(cinematographer_config) as director:        response = await director.chat(f"Parse this screenplay text into our production JSON schema layout:\n\n{screenplay_text}")                raw_json = ""        async for token in response:            raw_json += token    # Sanitize any unexpected wrap strings introduced by model formatting variations    sanitized_json = raw_json.strip()    if sanitized_json.startswith("```json"):        sanitized_json = sanitized_json[7:]    if sanitized_json.endswith("```"):        sanitized_json = sanitized_json[:-3]    sanitized_json = sanitized_json.strip()    try:        # Validate JSON formatting structure before committing data to disk        parsed_validation = json.loads(sanitized_json)        with open(output_json_path, "w", encoding="utf-8") as f:            json.dump(parsed_validation, f, indent=2)        print(f"[+] Successfully structured shot list verified and saved: {output_json_path}")    except Exception as e:        print(f"❌ Structural Validation Failed. Error parsing response string: {e}")        print("Raw trace recorded to error log.")        with open("./logs/failed_shotlist_payload.txt", "w") as log:            log.write(raw_json)if __name__ == "__main__":    if len(sys.argv) < 2:        print("Usage: python3 generate_shot_list.py <act_number>")        sys.exit(1)    asyncio.run(compile_shot_list(int(sys.argv[1])))

### Step 2.3: Invoking Phase 2 Natively via the agy CLI/TUI

With your orchestration hooks in place, you don't need to manually interact with raw python inputs during production. Map these automation tasks directly to your game-asset-factory skill dashboard to run them using your active session keyring credentials.

Open your project workspace inside your terminal interface:

agy --workspace .

To sequentially parse, compile, and structure a scene file from your project backlog, pass the execution target strings straight into your active prompt line:

>>> /game-asset-factory serialize screenplay from raw input: ./tickets/raw_notes/act_01_outline.txt --act 1>>> /game-asset-factory compile shot list sequence from target act: 1

To confirm the newly minted data structures are accurately verified and tracked across your directory logs, run a quick status check:

>>> /view_file ./tickets/shot_lists/act_01_shot_list.json

## Supplemental Stage: The Motion Vector Cohesion Audit

A major point of failure when chaining multiple video generation cuts is camera vector whiplash (e.g., Shot 1 abruptly tracks fast left, while Shot 2 instantly pulls fast right, disorienting the viewer). To fix this, implement a local python pre-flight validator to analyze your shot lists and ensure camera paths flow smoothly before sending them to the rendering engines.

Save this script file as ./scripts/audit_motion_vectors.py:

#!/usr/bin/env python3import jsonimport osimport sysdef audit_vectors(json_path: str):    if not os.path.exists(json_path):        print(f"[-] Target shot list missing: {json_path}")        return    with open(json_path, "r") as f:        shots = json.load(f)    print(f"🔍 [MOTION VECTOR AUDIT] Inspecting tracking profiles for: {os.path.basename(json_path)}")    previous_dir = None        for idx, shot in enumerate(shots):        movement = shot.get("camera_movement", "").lower()        current_dir = None                if "pan left" in movement or "track left" in movement:            current_dir = "LEFT"        elif "pan right" in movement or "track right" in movement:            current_dir = "RIGHT"                    if previous_dir and current_dir and previous_dir != current_dir:            print(f"    ⚠️  [ALERT]: Directional Whiplash Detected at Shot {idx + 1} ({shot['shot_id']})!")            print(f"        -> Previous camera motion vector was bound: {previous_dir}")            print(f"        -> Current camera motion vector shifts to: {current_dir}")            print("        -> Recommended fix: Insert a static bridging cut or align tracking vectors.")        else:            print(f"    ✅ Shot {idx + 1} ({shot['shot_id']}): Motion profile clear.")                    if current_dir:            previous_dir = current_dirif __name__ == "__main__":    if len(sys.argv) < 2:        print("Usage: python3 audit_motion_vectors.py <path_to_shot_list.json>")        sys.exit(1)    audit_vectors(sys.argv[1])

## Extra Gaps Resolved: Context Limit Protections

When running your scripts, you can keep sub-agent memory overhead low by configuring a strict limit on your JSON text payloads. If your raw screenplays grow too large, use an input slicing flag inside your LocalAgentConfig setup to process the file block-by-block. This keeps generation speeds fast and ensures consistent outputs from the cloud models:

# Insert directly into your setup profiles to handle massive files smoothlyconfig.max_token_slice = 8192  # Limits agent memory buffers to processing crisp scene chunks

Copy and run the prompt below to generate the next deep dive guide in this multi-part production setup.

Generate the next detailed, opinionated section of the guide: Phase 3: Visual Identity Anchor Generation and Asset Seed-Locking. Include specific agy CLI execution scripts, Python orchestration hooks, and any supplemental steps to help ensure successful asset consistency throughout my game project repository.

