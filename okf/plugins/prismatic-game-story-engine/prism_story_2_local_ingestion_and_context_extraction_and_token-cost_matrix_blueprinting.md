---
type: Reference
title: "PRISM_STORY_2_Local_Ingestion_and_Context_Extraction_and_Token-Cost_Matrix_Blueprinting"
description: Plugin report — "Prismatic Game Story Engine Plugin".
resource: https://docs.google.com/document/d/1QdSXaDPCpUld0eztWnaVhV7eBnpJk5lBe592X6XUN1Y/edit
tags: [plugin, story, narrative, prismatic, ai]
timestamp: 2026-06-19T11:47:07Z
linear_issue: null
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/plugins/prismatic-game-story-engine/prism_story_2_local_ingestion_and_context_extraction_and_token-cost_matrix_blueprinting.md
last_verified: 2026-06-25
verified_by: kai
status: current
plugin: Prismatic-Game-Story-Engine
plugin_doc_id: 1QdSXaDPCpUld0eztWnaVhV7eBnpJk5lBe592X6XUN1Y
migrated_from: "Google Drive: Prismatic Engine Ecosystem > Premium Plugins > Prismatic-Game-Story-Engine"
---

Welcome to the master reference guide for your multimedia production engine. We are breaking this sprawling production down into a disciplined, multi-stage pipeline, utilizing local compute to do the heavy text lifting for $0 overhead, and leveraging the Antigravity CLI (agy) to orchestrate the heavy cloud rendering engines using your 25,000 monthly Ultra Premium credits.

Here is the master roadmap of our deep-dive series:

Phase 1: Local Ingestion, Context Extraction, and Token-Cost Matrix Blueprinting (Current Section)

Phase 2: Screenplay Serialization and Multi-Agent Shot List Generation

Phase 3: Visual Identity Anchor Generation and Asset Seed-Locking

Phase 4: Low-Fi Animatics and Storyboard Execution via Veo 3.1 Lite

Phase 5: Automated Multimodal Visual QA Loops and Fallback/Rollback Recovery

Phase 6: Audio Tunnel Ingestion and Acoustic Rhythm Synchronization via Gemini Omni

Phase 7: High-Fidelity Master Rendering, 4K Upscaling, and Automated Concat Compilation

## Phase 1: Local Ingestion, Context Extraction, and Token-Cost Matrix Blueprinting

Trying to dump a raw 60,000-word lore bible directly into a cloud agent's context window for every minor generation turn is a rookie mistake. It induces token bloat, increases execution latency, and causes the agent to lose its grip on tight character details by burying the signal in noise.

Phase 1 establishes a Hybrid Architecture: we offload massive text parsing to local hardware models to chunk and structure the data into high-density JSON states, which are then fed into the agy workspace environment using clean context commands.

| LOCAL WORKSPACE |
|---|
| ANTIGRAVITY CLI (agy) |


### Step 1.1: Local Semantic Chunking and Entity Mapping

Instead of relying on cloud endpoints to memorize your lore, you run a local script utilizing an offline inference engine (like an Ollama or vLLM instance running an open-weight model) to split your text files into explicit Entities, Locations, and Lore Rules.

Run this localized extraction script (./scripts/extract_lore_matrix.py) to systematically parse your narrative asset maps:

#!/usr/bin/env python3import osimport jsonimport requestsLORE_FILE = "./design_guides/canon_lore.txt"OUTPUT_MAP = "./design_guides/structured_lore_matrix.json"OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"def chunk_text(text, max_words=2000):    words = text.split()    for i in range(0, len(words), max_words):        yield " ".join(words[i:i + max_words])def extract_entities(text_chunk):    system_prompt = (        "You are an advanced text parser. Analyze the input lore text and extract an explicit JSON block containing: "        "1. 'ships': Array of ship entities with descriptions, physical traits, and tech constraints. "        "2. 'biomes': Array of environments with atmospheric properties and lighting signatures. "        "3. 'banter_tones': Key character interactions and speaking styles.\n"        "Output ONLY raw, well-formatted JSON. Do not include markdown code block syntax."    )        payload = {        "model": "llama3.1:8b-instruct-q8_0", # Running locally at maximum quantization density        "prompt": f"{system_prompt}\n\nTEXT CHUNK:\n{text_chunk}",        "stream": False,        "format": "json"    }        try:        response = requests.post(OLLAMA_ENDPOINT, json=payload)        return json.loads(response.json()['response'])    except Exception as e:        print(f"Error during extraction: {e}")        return {"ships": [], "biomes": [], "banter_tones": []}def main():    if not os.path.exists(LORE_FILE):        print(f"[-] Missing source lore text file at {LORE_FILE}")        return    print("[*] Ingesting 60,000-word canon text via local model engine...")    with open(LORE_FILE, 'r', encoding='utf-8') as f:        full_text = f.read()    compiled_matrix = {"ships": {}, "biomes": {}, "banter_tones": {}}        for idx, chunk in enumerate(chunk_text(full_text)):        print(f"    -> Parsing segment block {idx + 1}...")        data = extract_entities(chunk)                # Merge arrays dynamically into indexed dictionaries        for ship in data.get("ships", []):            compiled_matrix["ships"][ship["name"].lower().replace(" ", "_")] = ship        for biome in data.get("biomes", []):            compiled_matrix["biomes"][biome["name"].lower().replace(" ", "_")] = biome    with open(OUTPUT_MAP, 'w') as f:        json.dump(compiled_matrix, f, indent=2)    print(f"[+] Lore Matrix successfully compiled to: {OUTPUT_MAP}")if __name__ == "__main__":    main()

### Step 1.2: Mounting Context into the agy TUI Environment

Once your text metadata is flattened into a high-density JSON matrix file, load it into your active terminal workspace session. The Antigravity Go-engine will parse the file structure cleanly, making it available as an underlying context piece without wasting massive text-token bandwidth.

Initialize your project workspace inside your shell terminal:

# Navigate to your structured workspace rootcd ~/my-game-project# Fire up the interactive Antigravity TUI environment agy --workspace .

Inside the active agy prompt line, use context utility hooks to append your newly compiled semantic maps directly into the background runner state:

>>> /context add ./design_guides/structured_lore_matrix.json>>> /context add ./design_guides/brand_palette.json

To verify that the workspace configuration is parsed and successfully tracking your design assets, query the active token manager:

>>> /context

This prints out a clean visualization tree of all verified file bindings, checking off your active references before any generation work begins.

## Supplemental Stage: The Local Pre-Flight Token Cost Estimator

To avoid surprises inside your active cloud sessions, you should run a local pre-flight token check before letting any sub-agent loops talk to the backend. This python script acts as an inline metric evaluator, looking at the structural state definitions inside your project folder and warning you of potential token inflation before you hit the cloud engines.

Save this script as ./scripts/preflight_token_check.py:

#!/usr/bin/env python3import osimport jsondef estimate_tokens(text: str) -> int:    # Conservative baseline multiplier for standard structural text tokens    return int(len(text.split()) * 1.35)def run_telemetry():    print("📈 [PRE-FLIGHT TELEMETRY SYSTEM] Checking context profile sizes...")    matrix_path = "./design_guides/structured_lore_matrix.json"        if not os.path.exists(matrix_path):        print("[-] Context matrix files missing. Run local extraction loops first.")        return            with open(matrix_path, 'r') as f:        raw_data = f.read()            token_count = estimate_tokens(raw_data)    print(f"    -> Baseline Lore Matrix Size: ~{token_count} Workspace Tokens")        if token_count > 15000:        print("    ⚠️  [WARNING]: Context file exceeds 15k tokens. Recommend selective extraction filters.")    else:        print("    ✅ [OPTIMAL]: Context footprint within safe high-speed boundary tolerances.")if __name__ == "__main__":    run_telemetry()

## Extra Gaps Resolved: Setting Up Global System Preferences

Before launching any massive generation pipelines, ensure that your global configuration file (~/.gemini/antigravity-cli/settings.json) is properly customized. This ensures the agy CLI won't constantly prompt you with noisy logs or confirmation warnings every time a local automation pipeline script makes an adjustment to a project file.

Make sure your configuration matches these parameters:

{  "verbosity": "low",  "auto_approve_tools": [    "view_file",    "read_dir",    "write_file"  ],  "editor": "nvim",  "max_sub_agents": 4,  "keyring_sync": true}

By setting "auto_approve_tools" to include local file actions, your background scripts can cleanly read design guides and log production changes smoothly without interrupting your terminal workspace session.

Copy and run the prompt below to generate the next deep dive guide in this multi-part production setup.

Generate the next detailed, opinionated section of the guide: Phase 2: Screenplay Serialization and Multi-Agent Shot List Generation. Include specific agy CLI execution scripts, Python orchestration hooks, and any supplemental steps to help ensure successful asset consistency throughout my game project repository.

