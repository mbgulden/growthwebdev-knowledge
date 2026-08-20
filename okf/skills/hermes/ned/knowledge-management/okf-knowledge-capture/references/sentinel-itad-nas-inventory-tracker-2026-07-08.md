# Sentinel ITAD NAS Inventory Tracker Pattern — 2026-07-08

## When this applies

Use this pattern when Michael is converting loose Sentinel ITAD stock into tracked inventory and asks whether to use NAS, Google Drive, spreadsheets, or folders.

## Durable lesson

For Sentinel ITAD inventory, the best source-of-truth shape is:

> NAS = canonical archive / truth
> Google Drive = client-facing exports and convenience copies only

Do not make Google Drive the canonical home for hundreds or thousands of intake/listing/serial photos. It becomes a scattered photo dump. Use the NAS for bulk evidence and folder stability, then export/share selected files through Drive as needed.

## Recommended canonical NAS structure

```text
Sentinel-ITAD/
  00_Admin/
    templates/
    insurance/
    vendor-docs/
  01_Intake-Lots/
    YYYY-MM-DD-lot-name/
      photos/
      serials/
      manifest.csv
      notes.md
  02_Inventory/
    sentinel-inventory-master.csv
    sentinel-inventory-master.xlsx
    exports/
  03_Data-Destruction/
    wipe-reports/
    drive-destroy-logs/
    certificates/
  04_Resale/
    ready-to-list/
    listed/
    sold/
    listing-photos/
  05_Recycle-Disposition/
    recycler-receipts/
    disposition-certificates/
  06_Client-Deliverables/
```

## Spreadsheet fields that worked

Seed `sentinel-inventory-master.csv` with columns:

```text
Lot ID,Asset ID,Quantity,Type,Make,Model,CPU,RAM,Storage,GPU,Networking,Serial/Service Tag,Data Bearing Media,Wipe Status,Test Status,Disposition,Location,Photo Folder,Listed Where,Listing URL,Asking Price,Sold Price,COGS/Acquisition Cost,Fees/Shipping,Net Recovery,Priority,Notes
```

## Workflow correction / pitfall

If the user says “I have 10 of these” and sends a photo, do not stop at a prose answer. Convert it into an inventory row immediately when enough facts are known, and mark unknowns as `TBD` instead of blocking the tracker.

Example row from the session:

- Quantity: 10
- Make/model: HP ProLiant DL380 Gen10
- CPU: 2x Intel Xeon Gold exact model TBD
- Storage: U.2 NVMe cage
- Networking: 40G networking card + 40G DAC cables
- Listed where: Facebook Marketplace
- Listing URL: source Marketplace URL
- Status: listed/verify
- Priority: high

## Capture rule

For batch hardware, ask for or capture:

1. whole-item photo
2. model/spec label photo
3. serial/service tag photo
4. BIOS/iLO/spec screen if it boots
5. whether every unit has identical config

Then update the master CSV and intake lot notes. Storage devices stay `pending`/not listable until wipe/test status is known.

## Tone/shape preference embedded by the work

Michael needs this work to become operational infrastructure, not a decorative report. Prefer concrete folders, CSV rows, and next physical capture actions over strategic narrative once the inventory system exists.
