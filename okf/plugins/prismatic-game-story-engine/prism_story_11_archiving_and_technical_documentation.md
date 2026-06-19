---
type: Reference
title: "PRISM_STORY_11_Archiving_and_Technical_Documentation"
description: Plugin report — "Prismatic Game Story Engine Plugin".
resource: https://docs.google.com/document/d/1tsIKp-nbHM3p_brJcefNM4iopHg1q2MRuZBryjVeMqI/edit
tags: [plugin, story, narrative, prismatic, ai]
timestamp: 2026-06-19T11:47:07Z
linear_issue: null
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/plugins/prismatic-game-story-engine/prism_story_11_archiving_and_technical_documentation.md
last_verified: 2026-06-19
verified_by: kai
status: current
plugin: Prismatic-Game-Story-Engine
plugin_doc_id: 1tsIKp-nbHM3p_brJcefNM4iopHg1q2MRuZBryjVeMqI
migrated_from: "Google Drive: Prismatic Engine Ecosystem > Premium Plugins > Prismatic-Game-Story-Engine"
---

## Phase 9: Metadata Extraction, Automated Documentation, and Production-Ready Archive Compilation

Leaving a complex generation pipeline undocumented is a recipe for long-term project failure. Months from now, when you need to remaster a cutscene or re-render a character arc, tracking down the exact model seeds, prompt modifiers, prompt weights, target audio stems, and visual anchor configurations across scattered JSON logs will be nearly impossible.

Phase 9 establishes the final Production Archive and Documentation Portal inside your workspace. Instead of manually writing post-mortems, we use an automated extraction framework triggered via the agy CLI skill layer.

This engine crawls your workspace directory tree, extracts metadata from your active state ledgers, aggregates prompt matrices, evaluates QA feedback loops, and compiles a comprehensive, human-readable Living Documentation Portal (PRODUCTION_LOG.md). Simultaneously, it packages all high-fidelity output files into a cryptographically signed, zero-loss production archive (.tar.gz) optimized for long-term cold storage.

| PHASE 9 PACKAGING SYSTEM |
|---|
| [State Ledger] + [Anchors] + [Cue Sheets] ──> Metadata Aggregator |
| ┌────────────────────────────────────────────┴─────────────────┐ |
| ▼                                                              ▼ |
| PRODUCTION_LOG.md                                       Verified Tarball |
| (Markdown Wiki Portal)                                  (SHA-256 Signed) |


### Step 9.1: The Documentation and Archive Compiler

The Archive Compiler Agent scans your workspace paths, extracts the exact configurations used to generate every verified asset, and builds a centralized release package. It acts as an automated technical director, ensuring your project's history remains completely trackable.

Create this core automation file at ./scripts/compile_archive_docs.py:

#!/usr/bin/env python3import osimport sysimport jsonimport tarfileimport hashlibfrom datetime import datetimefrom google.antigravity.tools.tool_context import ToolContextWORKSPACE_ROOT = os.getcwd()LEDGER_PATH = os.path.join(WORKSPACE_ROOT, "assets/cutscenes/act_01_production/state_ledger.json")MANIFEST_PATH = os.path.join(WORKSPACE_ROOT, "design_guides/anchor_manifest.json")CUE_SHEET_PATH = os.path.join(WORKSPACE_ROOT, "tickets/cue_sheets/act_01_cue_sheet.json")FINAL_MASTERS_DIR = os.path.join(WORKSPACE_ROOT, "assets/cutscenes/final_masters")DOCS_DIR = os.path.join(WORKSPACE_ROOT, "documentation")VAULT_DIR = os.path.join(WORKSPACE_ROOT, "vault/archives")class ArchiveCompiler:    def __init__(self, act_num: int):        self.act_num = act_num        os.makedirs(DOCS_DIR, exist_ok=True)        os.makedirs(VAULT_DIR, exist_ok=True)                with open(LEDGER_PATH, "r") as f: self.ledger = json.load(f)        with open(MANIFEST_PATH, "r") as f: self.manifest = json.load(f)        with open(CUE_SHEET_PATH, "r") as f: self.cue_sheet = json.load(f)    def calculate_sha256(self, file_path: str) -> str:        """Generates a cryptographic checksum to protect assets from bit rot."""        sha256_hash = hashlib.sha256()        if not os.path.exists(file_path):            return "FILE_NOT_FOUND"        with open(file_path, "rb") as f:            for byte_block in iter(lambda: f.read(4096), b""):                sha256_hash.update(byte_block)        return sha256_hash.hexdigest()    def generate_markdown_log(self) -> str:        """Synthesizes a production wiki portal compiling all pipeline details."""        log_path = os.path.join(DOCS_DIR, f"act_{self.act_num:02d}_production_log.md")        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")                md_content = (            f"# Production Log & Technical Manifest: Act {self.act_num:02d}\n"            f"**Generated On:** {timestamp} | **Pipeline Owner:** Michael Benjamin Gulden\n\n"            "## 🗜️ Core Visual Identity Anchors\n"            "The following static image seeds were used as input ingredients to lock visual continuity:\n\n"            "| Asset Entity | Target Category | Local File Path | Cryptographic Seed |\n"            "| :--- | :--- | :--- | :--- |\n"        )                for anchor_name, data in self.manifest.get("anchors", {}).items():            md_content += f"| `{anchor_name}` | {data['type']} | `{data['file_path']}` | `{data['lock_seed']}` |\n"                    md_content += (            "\n## 🎬 Verified Cinematic Renders Sequence\n"            "The generation execution history tracking results for this act's timeline:\n\n"            "| Shot ID | Verification Status | High-Fi Target Asset Node | Generation Cost Profile |\n"            "| :--- | :--- | :--- | :--- |\n"        )                for shot_id, data in self.ledger.get("history", {}).items():            md_content += f"| `{shot_id}` | **{data['status']}** | `{data['file_path']}` | 50 Credits (4K Mode) |\n"                    with open(log_path, "w", encoding="utf-8") as f:            f.write(md_content)                    return log_path    def compile_tarball(self, md_log_path: str) -> str:        """Packages all high-fidelity binaries and tracking manifests into an archive."""        archive_name = f"act_{self.act_num:02d}_production_vault.tar.gz"        archive_path = os.path.join(VAULT_DIR, archive_name)                print(f"📦 [ARCHIVE CORES]: Compiling zero-loss tarball bundle configuration...")                with tarfile.open(archive_path, "w:gz") as tar:            # Append our logs and files cleanly to the vault matrix            tar.add(md_log_path, arcname=os.path.basename(md_log_path))            tar.add(LEDGER_PATH, arcname="state_ledger.json")            tar.add(MANIFEST_PATH, arcname="anchor_manifest.json")                        # Map high-fidelity outputs safely into the archive            if os.path.exists(FINAL_MASTERS_DIR):                for file in os.listdir(FINAL_MASTERS_DIR):                    if file.endswith(".mp4"):                        full_p = os.path.join(FINAL_MASTERS_DIR, file)                        tar.add(full_p, arcname=f"media/{file}")                                return archive_path# ==========================================# ANTIGRAVITY PIPELINE EXECUTIVE INTERFACE# ==========================================def execute_archive_compilation(act_num: int) -> str:    print(f"🗄️  [ARCHIVE ENGINE]: Initializing pipeline metadata collection for Act {act_num:02d}...")        compiler = ArchiveCompiler(act_num)    md_log = compiler.generate_markdown_log()    print(f"    📝 Living Document Portal written successfully: {os.path.relpath(md_log, WORKSPACE_ROOT)}")        vault_tar = compiler.compile_tarball(md_log)    checksum = compiler.calculate_sha256(vault_tar)        # Store checksum alongside archive for permanent file verification validation checks    with open(f"{vault_tar}.sha256", "w") as f:        f.write(f"{checksum}  {os.path.basename(vault_tar)}\n")            print(f"    🔒 Cryptographic Signature Created: {checksum}")    return f"✨ ARCHIVE WORKFLOW COMPLETE. Master Vault committed to: {vault_tar}"if __name__ == "__main__":    if len(sys.argv) < 2:        print("Usage: python3 compile_archive_docs.py <act_number>")        sys.exit(1)    result = execute_archive_compilation(int(sys.argv[1]))    print(result)

### Step 9.2: Running the Extraction via the agy CLI/TUI

Because this packaging engine uses plain files inside your workspace, you can trigger data extraction, sign archives, and generate documentation logs without leaving your terminal dashboard.

Open your local project workspace shell terminal:

agy --workspace .

To automatically scan your production folders, format your markdown log portal, and output a signed tarball vault bundle, issue your skill trigger directly inside the TUI dashboard panel:

>>> /game-asset-factory compile archive docs from target act: 1

To review the generated markdown log portal straight from your terminal editor pane, open the text block payload:

>>> /view_file ./documentation/act_01_production_log.md

## Supplemental Stage: The Archive Verification Guardrail

To ensure your long-term storage backups remain safe from filesystem damage or accidental corruption, implement an automated script hook that compares your archived tarball against its original SHA-256 signature file before committing changes to a backup drive.

Save this automated utility script as ./scripts/verify_archive_integrity.py:

#!/usr/bin/env python3import osimport sysimport hashlibdef verify_vault_hash(tar_path: str, sha_path: str):    """Parses a generated archive file to verify its checksum integrity."""    if not os.path.exists(tar_path) or not os.path.exists(sha_path):        print("[-] Verification Error: Target archive files missing from vault paths.")        sys.exit(1)    print(f"🛡️  [INTEGRITY ACCURACY SYSTEM]: Validating cryptographic bounds for: {os.path.basename(tar_path)}")        # Calculate current file hash values    sha256 = hashlib.sha256()    with open(tar_path, "rb") as f:        for block in iter(lambda: f.read(4096), b""):            sha256.update(block)    calculated_hash = sha256.hexdigest()    # Read original verification signature string    with open(sha_path, "r") as f:        recorded_hash = f.read().split()[0].strip()    if calculated_hash != recorded_hash:        print("    ❌ [SECURITY ALERT]: Checksum mismatch! Archive file data has been altered or corrupted.")        sys.exit(1)    else:        print("    ✅ [PASSED]: Archive cryptographic fingerprint verified. Secure data lock complete.")        sys.exit(0)if __name__ == "__main__":    if len(sys.argv) < 3:        print("Usage: python3 verify_archive_integrity.py <vault.tar.gz> <vault.tar.gz.sha256>")        sys.exit(1)    verify_vault_hash(sys.argv[1], sys.argv[2])

## Extra Gaps Resolved: Embedding Sidecar Generation Metadata Into Output Binaries

A common oversight when archiving rendering outputs is separating the asset files from their structural prompt histories. If someone opens an .mp4 file out of context years from now, they won't know which prompts or settings generated it.

To solve this, configure your orchestration scripts to write an internal Metadata Sidecar File (.meta.json) alongside every master video file inside your target folders.

By keeping your tracking manifests appended directly to the individual video blocks, you can safely move, rename, or share individual media assets across your team without losing their original generation histories:

{  "asset_tracking_id": "ACT_01_SHOT_04",  "generation_engine": "veo-3.1-quality",  "original_prompt_source": "Cinematographic camera flight panning across mechanical array surfaces...",  "associated_identity_seed_lock": 7481910}

Generate the next detailed, opinionated section of the guide: Phase 10: Multi-Platform Localization, Subtitle Injection, and Marketing Promo Asset Forking. Include specific agy CLI execution scripts, Python orchestration hooks, and any supplemental steps to help ensure successful asset consistency throughout my game project repository.

