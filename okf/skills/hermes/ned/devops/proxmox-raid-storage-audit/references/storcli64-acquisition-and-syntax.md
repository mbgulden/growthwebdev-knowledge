# storcli64 — acquisition, working syntax, POH decode

Captured from a live PVE1 audit (Lenovo 930-8i / LSI SAS3508, 8 physical drives in one enclosure, EID 134).

## Getting the binary (vendor mirrors are blocked)
From a headless PVE host, these all returned 403/404 (as of 2026-08):
- `https://downloadmirror.intel.com/848223797/storcli-1.17.16_30.bin` → 243B XML AccessDenied
- Intel MR7.29 standalone page (`/download/17809`) → only **EFI** build (`StorCLI_...efi.zip`), no Linux binary for this Broadcom card
- `https://www.microchip.com/en-us/software/downloads/007.2705.0000.0000_Unified_StorCLI.zip` → 403
- `https://download.broadcom.com/download/10037/...` → connection failed

**Working path — GitHub-hosted mirror repo `wachira90/lern-storcli64`:**
```
# Lite (1.6MB, single static binary) — enough for topology + basic PD state:
curl -sL -o /tmp/lite.zip https://raw.githubusercontent.com/wachira90/lern-storcli64/HEAD/Linux_Lite/storcli64.zip
# Full RPM (recommended — supports prescan + per-drive show smart):
curl -sL -o /tmp/full.rpm https://raw.githubusercontent.com/wachira90/lern-storcli64/HEAD/Linux/storcli-007.3405.0000.0000-1.noarch.rpm
```
Extract on a host without `unzip` (PVE often lacks it):
- zip: `python3 -c "import zipfile; zipfile.ZipFile('lite.zip').extractall('lite_x')"`
- rpm: `apt-get install -y rpm2cpio cpio && rpm2cpio full.rpm | cpio -idm` → binary lands at `opt/MegaRAID/storcli/storcli64`

`chmod +x` then run as root. Both are statically linked x86-64 ELF; no deps.

## Working vs failing command forms (v007.3405 "SAS Customization Utility")
| Purpose | WORKS | FAILS (with error) |
|---|---|---|
| Controller + topology + PD LIST | `storcli64 /c0 show all` | — |
| PD LIST only | `storcli64 /c0 show` (includes `PD LIST` section) | `storcli64 /c0 show physdisk` → `TOKEN_UNKNOWN` |
| Per-drive state + attributes | `storcli64 /c0/e134/s0 show all` | `storcli64 /c0 e134 p0` → `TOKEN_OBJ_ENCLOSURE`; `/c0/e134/p0` → `TOKEN_OBJ_PHY` |
| Per-drive SMART | `storcli64 /c0/e134/s0 show smart` (after `prescan`) | — |
| Refresh SMART | `storcli64 /c0/e134/s0 prescan` | `storcli64 /c0 e134 p0 prescan` → `TOKEN_OBJ_ENCLOSURE` |
| VD table (cache policy) | `storcli64 /c0 show` → `DG/VD ... Cache` row | `storcli64 /c0/v0 show` → `TOKEN_OBJ_VD` |
| Event log | NOT supported in this build — `show eventlog` → `TOKEN_UNKNOWN` | — |

Syntax rule: **slash-form with enclosure before slot**: `/c0/e<EID>/s<slot>`. Space-form `/c0 e... p...` and `/p` (phy) addressing are rejected by this build. `/c0/s0` (no enclosure) parses but returns `Drive not found`.

EID is not always 134 — read it from the PD LIST header (`EID:Slot` column) or the topology table.

## What to extract per drive
From `show all` (State section):
- `Media Error Count`, `Other Error Count`, `Predictive Failure Count`, `S.M.A.R.T alert flagged by drive`
- `Drive Temperature` (°C)
- Model / SN / Firmware / WWN (for the audit table)
- `State` line from PD LIST: `Onln`/`Dgrd`/`Offln`/`Rbld`, `DG` membership

## POH decode (verified)
`show smart` dumps the raw 512-byte ATA SMART page as hex with **no attribute names**. Each attribute is 10 bytes: `ID ST TH VA WO [raw 6 bytes]`.

Find the row where `ID = 09` (Power_On_Hours). The 6 bytes after `09 32 00 <VA> <WO>` are the raw 48-bit **little-endian** counter. Decode:
```python
raw = bytes.fromhex("97 ad 00 00 00 00")   # 6 raw bytes
poh = int.from_bytes(raw, "little")        # = 0x00AD97 = 44,439
```
Verified against the live PVE1 dump:
- s0 Toshiba: `09 32 00 01 01 97 ad 00 00 00` → raw `97 ad 00 00 00 00` → **44,439h** (~5.05y)
- s1 Toshiba: `... 9e ad 00 00 00` → raw `9e ad 00 00 00 00` → **44,446h**
- s2 Seagate: `09 32 00 37 37 3b 9b 00 00 00` → raw `3b 9b 00 00 00 00` → **39,739h** (~4.5y)

⚠️ The `01 01` after the threshold are `value` + `worst` (normalized), **not** part of the counter. Only the 6 bytes after those are raw. If you accidentally include the `01 01` you get an absurd 2.9M-hour result — a clear mis-order. Sanity-check: a drive in service ~4–5 years should read 35k–50k hours; anything in the millions is a decode bug. Label the figure "est." and report the raw hex alongside.

## Audit report shape (what Michael accepted)
1. TL;DR with status emojis (🟢/🟡/🔴) — drives first, then the *real* risk (usually backups).
2. Topology table (LUN → VD → RAID level → members → use).
3. Per-drive SMART table (slot, model, array, temp, media/other err, PFC, alert, est. POH).
4. Pool usage + "what's actually important" (VM list, orphans flagged).
5. Backup status (last vzdump date, cron state, log count after cutoff).
6. Ranked recommendations. Method/reproducibility footer.
