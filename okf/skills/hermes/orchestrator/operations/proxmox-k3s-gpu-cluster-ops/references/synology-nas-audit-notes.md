# Synology_NAS Audit Notes (2026-08-24)

This document summarizes the findings from a read-only audit of the Synology_NAS, accessed via Proxmox node `pve1` at IP `192.168.1.201`. The primary goal was to identify "low hanging fruit" 100% duplicate files to reduce disk usage.

## Current Disk Usage

- **Filesystem**: `192.168.1.40:/volume1/proxmox_backups`
- **Size**: `27T`
- **Used**: `24T`
- **Available**: `2.6T`
- **Use%**: `91%`
- **Mounted on**: `/mnt/pve/Synology_NAS`

## Discovered Directory Structure

The root of `/mnt/pve/Synology_NAS/` contains the following directories:
- `dump/`: Primarily contains Proxmox backup files (`.vma.zst`).
- `hub/`: Contains Hugging Face model caches (`models--mbley--NousResearch-Hermes-3-Llama-3.1-70B-AWQ`).
- `#recycle/`: Likely a trash bin or recycle bin.
- `template/`: Likely contains unique templates.
- `vllm-weights/`: Found to be empty or contain no regular files during this audit.

## Duplicate File Audit Findings

### In `/mnt/pve/Synology_NAS/dump/`
No 100% duplicate files found (based on identical size and SHA256 checksum) among the `.vma.zst` Proxmox backup files.

### In `/mnt/pve/Synology_NAS/hub/`
No 100% duplicate files found (based on identical size and SHA256 checksum) among the Hugging Face model cache files.

### In `/mnt/pve/Synology_NAS/vllm-weights/`
No files to audit as the directory was empty.

## Recommendations for Reducing Disk Usage (from 91% to 80-85%)

Since no exact duplicates were found in the audited directories, other strategies must be considered to reduce the Synology_NAS disk usage:

1.  **Review Proxmox Backup Retention Policies**: The `dump/` directory is the largest contributor to disk usage. Adjusting Proxmox's backup retention settings for VMs and CTs can significantly free up space.
2.  **Archive Older Backups**: Identify and move older, less critical backup files from `dump/` to a colder storage solution or external drive.
3.  **Manual Inspection for Non-Essential Files**: Manually review all directories on the NAS for large, non-essential files or datasets that are no longer actively used and can be safely removed or offloaded. This would require broader access to the NAS filesystem beyond the current Proxmox mount.
4.  **Investigate `#recycle/` and `template/`**: While not audited for duplicates, these directories could contain old or unused data that can be safely cleaned up.

---