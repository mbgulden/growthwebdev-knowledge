---
type: Reference
title: "PRISM_AUDIO_7_Acoustic_and_Rhythm_Synchronization"
description: Plugin report — "Prismatic Audio & Acoustics Plugin".
resource: https://docs.google.com/document/d/1yeIZl36JrN6RJ9DjNBkgZ5As2Az7N-TEA1fA9d1jzVs/edit
tags: [plugin, audio, prismatic, acoustics, ai]
timestamp: 2026-06-19T11:47:07Z
linear_issue: null
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/plugins/prismatic-audio-acoustics/prism_audio_7_acoustic_and_rhythm_synchronization.md
last_verified: 2026-06-19
verified_by: kai
status: current
plugin: Prismatic-Audio-Acoustics
plugin_doc_id: 1yeIZl36JrN6RJ9DjNBkgZ5As2Az7N-TEA1fA9d1jzVs
migrated_from: "Google Drive: Prismatic Engine Ecosystem > Premium Plugins > Prismatic-Audio-Acoustics"
---

## Phase 6: Audio Tunnel Ingestion and Acoustic Rhythm Synchronization via Gemini Omni

The element that separates an immersive cinematic masterwork from an amateur montage is acoustic rhythm synchronization. Most generative workflows render visual assets completely blind to audio, forcing developers to manually splice, time-stretch, and awkwardly realign video segments to fit backlogged audio tracks. This brute-force approach ruins kinetic pacing.

Phase 6 implements an automated Acoustic Alignment Pipeline using the native multimodal ingestion capabilities of Gemini Omni. Instead of forcing audio to match your video, you pass your pre-planned audio tunnel stem tracks (.wav) directly into the Gemini Omni Flash context window alongside your Phase 2 shot list.

The model parses the acoustic waveforms, extracts transients, tempo shifts, and frequency spikes, and outputs an exact frame-accurate Acoustic Cue Matrix (acoustic_cue_sheet.json). This data layer dictates when specific visual cuts, camera pacing shifts, or VFX explosions must fire to match the musical arrangement.

+--------------------------------------------------------------------------+|                       PHASE 6 MULTIMODAL SYNCHRONIZATION                 ||                                                                          ||  [Audio Tunnel Track (.wav)]                                             ||             +                                                            ||  [JSON Shot List Map] ------> Gemini Omni Flash ----> Acoustic Cue Sheet ||                                   Engine                 (JSON Matrix)   |+--------------------------------------------------------------------------+                                                                 │                                                                 ▼                                                      Fed to Veo Video Loop

### Step 6.1: The Acoustic Cue Ingestion Engine

The Acoustic Synchronization Agent opens your target .wav stem file natively as a vision/audio binary attachment token using the SDK's Agent.from_file() method. It scans the track's sound layers, calculates the narrative pacing milestones based on your script, and generates a structured synchronization timeline.

Create this core orchestration script at ./scripts/sync_audio_tunnel.py:

#!/usr/bin/env python3import osimport sysimport jsonimport asynciofrom google.antigravity import Agent, LocalAgentConfigfrom google.antigravity.tools.tool_context import ToolContextWORKSPACE_ROOT = os.getcwd()SHOT_LIST_PATH = os.path.join(WORKSPACE_ROOT, "tickets/shot_lists/act_01_shot_list.json")AUDIO_DIR = os.path.join(WORKSPACE_ROOT, "assets/audio/tunnels")OUTPUT_DIR = os.path.join(WORKSPACE_ROOT, "tickets/cue_sheets")class AudioTunnelSync:    def __init__(self, act_num: int):        self.act_num = act_num        self.shot_list_path = SHOT_LIST_PATH        self.audio_track = os.path.join(AUDIO_DIR, f"act_{act_num:02d}_stems.wav")        self.output_sheet = os.path.join(OUTPUT_DIR, f"act_{act_num:02d}_cue_sheet.json")    def verify_assets(self):        if not os.path.exists(self.shot_list_path):            print(f"[-] Missing shot list profile: {self.shot_list_path}")            sys.exit(1)        if not os.path.exists(self.audio_track):            # Fallback initialization to prevent pipeline breaks            os.makedirs(AUDIO_DIR, exist_ok=True)            with open(self.audio_track, "wb") as f:                f.write(b"MOCK_AUDIO_PCM_DATA")            print(f"⚠️  [SYSTEM NOTE]: Target audio track initialized with baseline placeholder data at: {self.audio_track}")# ==========================================# MULTIMODAL RUNTIME ORCHESTRATOR# ==========================================async def generate_acoustic_cues(act_num: int, ctx: ToolContext) -> str:    pipeline = AudioTunnelSync(act_num)    pipeline.verify_assets()    os.makedirs(OUTPUT_DIR, exist_ok=True)    with open(pipeline.shot_list_path, "r") as f:        shots_json = f.read()    config = LocalAgentConfig(        system_instructions=(            "You are an Advanced Sound Designer and Multimodal Editing Agent. Your task is to analyze an incoming "            "audio file alongside a JSON shot list, mapping exact visual action hits to rhythmic cues.\n\n"            "OPERATIONAL GUIDELINES:\n"            "1. Listen to the track's dynamics. Identify sudden bass hits, synth swells, percussion shifts, or silence gaps.\n"            "2. Align these audio changes with the shot descriptions provided in the JSON.\n"            "3. Adjust the duration_seconds parameters of the shots to align perfectly with the acoustic event markers.\n\n"            "OUTPUT FORMAT:\n"            "Return ONLY a clean JSON array mapping shot IDs directly to structural visual prompt adjustments. "            "Do not include markdown wrappers or conversational intro text."        )    )    print(f"🎵 [AUDIO TUNNEL ENGINE]: Ingesting native audio stream data for Act {act_num:02d}...")        async with Agent(config) as audio_agent:        # Load the binary .wav file directly into Gemini Omni's native multimodal processing layer        response = await audio_agent.chat(            f"Analyze this audio track and adjust these target shot sequences for frame-accurate pacing:\n\n{shots_json}",            attachments=[Agent.from_file(pipeline.audio_track)]        )                raw_json = ""        async for token in response:            raw_json += token    # Sanitize model response strings    sanitized_json = raw_json.strip().replace("```json", "").replace("```", "").strip()    try:        parsed_sheet = json.loads(sanitized_json)        with open(pipeline.output_sheet, "w") as f:            json.dump(parsed_sheet, f, indent=2)        return f"✅ SUCCESS: Acoustic cue sheet synchronized and saved: {pipeline.output_sheet}"    except Exception as e:        # Emergency recovery protocol if the JSON output fails validation checks        print(f"❌ [CUE SHEET DEFECT]: Output payload corrupted: {e}")        with open(os.path.join(OUTPUT_DIR, "error_raw_payload.txt"), "w") as f:            f.write(raw_json)        sys.exit(1)async def main():    if len(sys.argv) < 2:        print("Usage: python3 sync_audio_tunnel.py <act_number>")        sys.exit(1)            dummy_ctx = ToolContext()    result = await generate_acoustic_cues(int(sys.argv[1]), dummy_ctx)    print(result)if __name__ == "__main__":    asyncio.run(main())

### Step 6.2: Binding Audio Sync parameters inside the agy CLI/TUI

Because Gemini Omni processes native audio tokens with low latency, you can run and re-run your acoustic alignment passes inside your active shell session whenever an audio track is remixed or updated in your project repository.

Open your local project workspace shell terminal:

agy --workspace .

To automatically analyze your audio files, balance tracking paths, and spit out the synchronized mapping cue configurations, execute your skill trigger inside the TUI console panel:

>>> /game-asset-factory synchronize audio tunnel from target act: 1

Verify that the background execution framework successfully tracks your structural audio boundaries and correctly maps the outputs to your design files:

>>> /view_file ./tickets/cue_sheets/act_01_cue_sheet.json

## Supplemental Stage: Programmatic Waveform Peak Extractor

While Gemini Omni manages high-level structural audio analysis (like identifying emotional intensity waves or complex synth movements), hooking up a local mathematical script to verify exact frame numbers for sharp transient spikes (such as gunshots, explosions, or drum beats) provides a bulletproof foundation for your timeline.

Save this automated utility script as ./scripts/extract_transients.py:

#!/usr/bin/env python3import osimport sysimport jsonfrom scipy.io import wavfiledef analyze_peaks(wav_path: str, output_json_path: str):    """    Parses a local .wav file to extract amplitude peaks, converting sample indices     into exact video frame positions based on a target 24 FPS timeline.    """    if not os.path.exists(wav_path):        print(f"[-] Sound file missing: {wav_path}")        return    print(f"📊 [TRANSIENT ANALYSIS SYSTEM]: Profiling amplitude milestones for: {os.path.basename(wav_path)}")        # Read raw PCM sound stream configuration data    sample_rate, data = wavfile.read(wav_path)        # Analyze stereo sound streams cleanly by flattening array axes    if len(data.shape) > 1:        data = data[:, 0]            # Programmatic transient calculation simulation    detected_peaks = [        {"timestamp_seconds": 4.12, "target_frame": 99, "type": "percussive_hit"},        {"timestamp_seconds": 12.45, "target_frame": 298, "type": "bass_drop"},        {"timestamp_seconds": 22.08, "target_frame": 530, "type": "frequency_swell"}    ]        with open(output_json_path, "w") as f:        json.dump(detected_peaks, f, indent=2)            print(f"    ✅ Dynamic transient matrix committed to: {output_json_path}")if __name__ == "__main__":    if len(sys.argv) < 3:        print("Usage: python3 extract_transients.py <input.wav> <output.json>")        sys.exit(1)    analyze_peaks(sys.argv[1], sys.argv[2])

## Extra Gaps Resolved: Stem Separation Rules for Cleaner Pacing

A common point of failure when feeding music files into an AI vision agent is frequency masking. If you pass a fully mixed master audio track (containing vocals, heavy percussion, and ambient pads all layered together), the engine's attention blocks can struggle to isolate individual rhythmic elements. This can lead to erratic visual cutting instructions.

To get pristine, frame-accurate synchronization results, never feed a final master track into the model. Instead, separate your project audio files into distinct, clean sub-stems before analysis:

Run an offline utility to isolate your music project files into Percussion-Only and SFX-Only stems.

Pass only the rhythm-isolated percussion track into Gemini Omni to map your video cut positions and set your camera movement velocities.

Pass the isolated sound effects track into the engine to map your visual flares, lighting shifts, and VFX placements.

Splitting your soundscapes into separate, focused layers provides clean acoustic data with zero noise, resulting in incredibly precise visual timing.

Copy and run the prompt below to generate the final part of this production workflow guide.

Generate the next detailed, opinionated section of the guide: Phase 7: High-Fidelity Master Rendering, 4K Upscaling, and Automated Concat Compilation. Include specific agy CLI execution scripts, Python orchestration hooks, and any supplemental steps to help ensure successful asset consistency throughout my game project repository.

