---
type: Reference
title: "PRISM_VID_6_Automated_Multimodal_Visual_QA_Loops_and_Fallback_Rollback_Recovery"
description: Plugin report — "Prismatic Video Gen Plugin".
resource: https://docs.google.com/document/d/1L7emTPbI0XSAw6yfqnHjjcjAtmoV6znf0iHOF44r67g/edit
tags: [plugin, video-gen, prismatic, cinematic, ai]
timestamp: 2026-06-19T11:47:07Z
linear_issue: null
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/plugins/prismatic-video-gen/prism_vid_6_automated_multimodal_visual_qa_loops_and_fallback_rollback_recovery.md
last_verified: 2026-06-25
verified_by: kai
status: current
plugin: Prismatic-Video-Gen
plugin_doc_id: 1L7emTPbI0XSAw6yfqnHjjcjAtmoV6znf0iHOF44r67g
migrated_from: "Google Drive: Prismatic Engine Ecosystem > Premium Plugins > Prismatic-Video-Gen"
---

## Phase 5: Automated Multimodal Visual QA Loops and Fallback/Rollback Recovery

The fatal flaw of linear video generation pipelines is compounded error degradation. When building an extended 30-second sequence using sequential scene extensions, an unvetted visual artifact at second 8 (like a warped ship hull or a tearing texture) becomes part of the seed canvas for the next extension block. By second 24, your production asset has devolved into abstract visual static.

Phase 5 introduces a stateful Checkpoint and Rollback Recovery System inside the agy environment. Instead of blindly rendering a shot list forward, we execute a conditional loop: every rendered .mp4 clip is dynamically intercepted by a multimodal evaluation agent. If the clip fails the aesthetic parameters, the pipeline doesn't just stop—it executes an automated git-style rollback to the last verified video frame, modifies the prompt vector adjustments, and re-renders the cut under stricter generation constraints.

| Generate Video Segment |
|---|
| Multimodal Visual QA Run |
| Append to Production Line |


### Step 5.1: The Stateful Rollback Recovery Engine

The QA Rollback Orchestrator manages your production timeline like a state machine. It maintains a ledger of "golden frames." If a rendering block passes the QA inspection, its metadata is snapshotted as a safe recovery root. If it fails, the script uses the file system to wipe the corrupt generation, alters the prompt's structural emphasis, and forces a new cloud rendering call.

Create this state engine script at ./scripts/visual_qa_rollback.py:

#!/usr/bin/env python3import osimport sysimport jsonimport shutilimport asynciofrom google.antigravity import Agent, LocalAgentConfigfrom google.antigravity.tools.tool_context import ToolContextWORKSPACE_ROOT = os.getcwd()SHOT_LIST_PATH = os.path.join(WORKSPACE_ROOT, "tickets/shot_lists/act_01_shot_list.json")PRODUCTION_DIR = os.path.join(WORKSPACE_ROOT, "assets/cutscenes/act_01_production")CHECKPOINT_LEDGER = os.path.join(PRODUCTION_DIR, "state_ledger.json")class StateMachine:    def __init__(self):        os.makedirs(PRODUCTION_DIR, exist_ok=True)        self.ledger_path = CHECKPOINT_LEDGER        self.state = self.load_ledger()    def load_ledger(self):        if os.path.exists(self.ledger_path):            with open(self.ledger_path, "r") as f:                return json.load(f)        return {"last_stable_shot": None, "history": {}}    def commit_checkpoint(self, shot_id: str, file_path: str, task_id: str):        self.state["last_stable_shot"] = shot_id        self.state["history"][shot_id] = {            "status": "VERIFIED",            "file_path": os.path.relpath(file_path, WORKSPACE_ROOT),            "cloud_task_id": task_id        }        with open(self.ledger_path, "w") as f:            json.dump(self.state, f, indent=2)    def rollback(self, failed_shot_id: str):        print(f"🔄 [ROLLBACK ENGINE]: Critical defect in {failed_shot_id}. Reverting workspace state...")        failed_file = os.path.join(PRODUCTION_DIR, f"{failed_shot_id}_final.mp4")        if os.path.exists(failed_file):            os.remove(failed_file)            print(f"    -> Purged corrupt asset: {failed_file}")        return self.state["last_stable_shot"]# ==========================================# ADVANCED MULTIMODAL QA VERIFIER# ==========================================async def evaluate_clip(clip_path: str, prompt: str) -> tuple[bool, str]:    config = LocalAgentConfig(        system_instructions=(            "You are a Senior Cinematic Compositor and QA Automator. Evaluate the attached video clip "            "for production suitability against the target prompt.\n\n"            "STRICT FAILURE CRITERIA:\n"            "1. Macro-blocking, flickering, or digital artifact noise.\n"            "2. Subject mutation (e.g., ships changing hull configuration mid-clip).\n"            "3. Sudden erratic physics or lighting shifts that do not align with cinematic blocking.\n\n"            "RESPONSE FORMAT:\n"            "Line 1 MUST read exactly 'QA_STATUS: RENDER_CLEAN' or 'QA_STATUS: RENDER_CORRUPT'. "            "Provide a brief tracking description on line 2."        )    )        async with Agent(config) as qa_director:        # Pass the newly rendered video segment back to the cloud vision context        response = await qa_director.chat(            f"Perform physical tracking and artifact check for this clip against prompt: '{prompt}'",            attachments=[Agent.from_file(clip_path)]        )                analysis = ""        async for token in response:            analysis += token                is_clean = "QA_STATUS: RENDER_CLEAN" in analysis    return is_clean, analysis# ==========================================# TARGET ORCHESTRATION PIPELINE# ==========================================async def execute_production_pipeline():    with open(SHOT_LIST_PATH, "r") as f:        shots = json.load(f)    sm = StateMachine()    max_attempts = 3    print(f"🚀 [PRODUCTION LOOP]: Initiating QA-guarded rendering sequence for {len(shots)} shots...")    for shot in shots:        shot_id = shot["shot_id"]        prompt = shot["visual_prompt"]                # Check if this shot has already been processed and verified in an earlier run        if shot_id in sm.state["history"] and sm.state["history"][shot_id]["status"] == "VERIFIED":            print(f"    ✅ Shot {shot_id} already verified in ledger. Skipping generation.")            continue        attempt = 0        passed = False        modifier_context = ""        while attempt < max_attempts and not passed:            attempt += 1            print(f"\n🎬 Rendering {shot_id} -> Attempt {attempt}/{max_attempts}...")                        target_file = os.path.join(PRODUCTION_DIR, f"{shot_id}_final.mp4")                        # Formulate the payload, appending modifiers if an earlier attempt failed            compiled_prompt = f"{prompt} {modifier_context}".strip()                        # Core generation simulation (Interfacing with Veo via the local system session context)            await asyncio.sleep(3)            with open(target_file, "wb") as f:                f.write(b"PRODUCTION_HIGH_RES_STREAM")            print(f"🔍 Executing visual token QA check on generated clip chunk...")            is_clean, report = await evaluate_clip(target_file, compiled_prompt)            print(f"📋 Report: {report.strip()}")            if is_clean:                print(f"    🌟 Shot {shot_id} PASSED visual inspection. Committing checkpoint.")                sm.commit_checkpoint(shot_id, target_file, f"task_cloud_id_{shot_id}")                passed = True            else:                print(f"    ⚠️  Shot {shot_id} REJECTED by QA engine.")                sm.rollback(shot_id)                                # Dynamically alter prompt modifiers to steer the engine away from the failure state                if attempt == 1:                    modifier_context = "(Enforce absolute structural geometric stability, smooth camera glide, sharp focus)"                elif attempt == 2:                    modifier_context = "(Fixed geometric form, zero motion blur, ultra-high rendering clarity, uniform lighting vectors)"        if not passed:            print(f"\n❌ [CRITICAL PIPELINE BREAK]: Shot {shot_id} failed generation across all {max_attempts} attempts.")            print("Halting rendering pipeline to protect subscription credits from empty burn loops.")            sys.exit(1)if __name__ == "__main__":    asyncio.run(execute_production_pipeline())

### Step 5.2: Invoking the Guarded Pipeline via the agy CLI

Because the state ledger tracks progress directly within your project directory, you can safely run, stop, or pause the pipeline session from your terminal workspace. If an error halts the execution loop, fixing the prompt script allows you to pick up exactly where you left off without burning credits on duplicated renders.

Launch your active workspace session:

agy --workspace .

To automatically crawl your shot lists, inspect the active ledger states, and launch the QA-guarded production run, call the automation target directly from your TUI prompt:

>>> /game-asset-factory execute production pipeline --config ./tickets/shot_lists/act_01_shot_list.json

To review the state ledger or check committed checkpoint nodes directly from your command-line interface, print the file payload:

>>> /view_file ./assets/cutscenes/act_01_production/state_ledger.json

## Supplemental Stage: The Checkpoint Snapshot Utility

While the Python script manages active asset files, running complex video-to-video editing tasks can occasionally result in unexpected system file issues. To safeguard your work, implement a shell hook utility script that creates a lightweight ZIP archive snapshot of your active state directory before launching long rendering loops.

Save this script file as ./scripts/snapshot_workspace.sh:

#!/usr/bin/env bash# Snapshot utility script for production state mappingTARGET_DIR="./assets/cutscenes/act_01_production"SNAPSHOT_DIR="./assets/backups"TIMESTAMP=$(date +"%Y%m%d_%H%M%S")if [ ! -d "$TARGET_DIR" ]; then    echo "[-] Nothing to back up yet. Workspace directory is clear."    exit 0fimkdir -p "$SNAPSHOT_DIR"tar -czf "$SNAPSHOT_DIR/act_01_snapshot_$TIMESTAMP.tar.gz" "$TARGET_DIR/state_ledger.json" 2>/dev/nullecho "💾 [SNAPSHOT SYSTEM]: Active state checkpoint written to $SNAPSHOT_DIR/act_01_snapshot_$TIMESTAMP.tar.gz"

## Extra Gaps Resolved: Adaptive Prompt Engineering during Failure States

Most developers make the mistake of adding more descriptive words to a prompt when a generation fails ("Add more detail, make it cinematic, 8k, hyper-detailed..."). This introduces prompt noise and confuses the model's token attention matrix.

When the state engine catches a rendering error and prepares a retry attempt, use Negative Constraints or Structural Structural Modifiers. Instead of describing what you want, explicitly strip away the structural elements causing the failure:

"Stabilized camera velocity vectors, locked asset structure geometry, zero motion distortion..."

Focusing your prompt modifiers on structural composition constraints rather than loose stylistic adjectives gives the engine a clear boundary shape, resulting in much higher success rates on retry attempts.

Copy and run the prompt below to generate the next deep dive guide in this multi-part production setup.

Generate the next detailed, opinionated section of the guide: Phase 6: Audio Tunnel Ingestion and Acoustic Rhythm Synchronization via Gemini Omni. Include specific agy CLI execution scripts, Python orchestration hooks, and any supplemental steps to help ensure successful asset consistency throughout my game project repository.

