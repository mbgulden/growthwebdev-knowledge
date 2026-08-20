# Sentinel ITAD OKF Sync — 2026-07-07 Example

## Situation

User asked to record a Sentinel IT Asset Disposal / Sentinel IT Asset Logistics planning conversation in the OKF and explicitly warned that a mature lead research net with contact info already existed. The important workflow lesson was not the specific business plan; it was the knowledge-capture pattern:

1. Find existing OKF/project artifacts first.
2. Sync new facts into the project structure.
3. Cross-link from indexes.
4. Add explicit anti-duplication instructions so future agents do not recreate lead research.
5. If challenged about whether all prior work was found, do a second content-map pass rather than defensively claiming completeness.
6. Verify doc changes with a targeted temporary script when no canonical suite exists.

## Existing artifacts found

Relevant existing Sentinel/SIAL artifacts included:

- `sentinel-it-asset-logistics/README.md`
- `sentinel-it-asset-logistics/okf/index.md`
- `sentinel-it-asset-logistics/okf/research/index.md`
- `sentinel-it-asset-logistics/docs/separation-from-sovereign-sentinel.md`
- `sentinel-it-asset-logistics/docs/sial-resale-inventory.md`
- `sentinel-it-asset-logistics/docs/google-drive-extraction-todo.md`
- `sentinel-it-asset-logistics/ops/valuation.py`
- `sentinel-itad/docs/msp_outreach_kit.md`
- `sentinel-itad/docs/subcontract_loop_workflow.md`
- `sentinel-itad/docs/downstream_partners_research.md`
- `sentinel-itad/docs/sentinel_bin_placement_terms.md`
- `sentinel-itad/docs/facebook_marketplace_listing_guide.md`
- `sentinel-itad/docs/dl380_liquidation_kit.md`
- `sentinel-itad/docs/ebay_setup_checklist.md`
- `sentinel-itad/ops/ebay_test_listing.py`
- `sentinel-itad/ops/ship.py`

The correct action was to reference these, not duplicate them.

## Google Drive content-map pass

The second pass found Google Drive source documents through the local Drive MCP scripts. Useful local script names included:

- `local-gdrive-mcp/list_sentinel_files.js`
- `local-gdrive-mcp/read_docs_local.js`
- `local-gdrive-mcp/read_sial_by_id.js`
- `local-gdrive-mcp/read_all_relevant.js`
- `local-gdrive-mcp/find_sial_docs.js`

High-signal Drive docs found:

- `Sentinel IT Asset Logistics: Plan` — main business plan / Blue Collar Cyber / service tiers.
- `Sentinel IT: ITAD Data Sanitization & Hardware Disposal Protocol...` — NIST/data sanitization, chain of custody, certificates.
- `HP DL380 Gen10 Logistics Strategy - March 2026` — server logistics / Hawaii-to-Idaho movement.
- `AI-Driven Business Transformation Plan` and `Alignment 1: Resource Orchestration Report` — large strategy reports; summarize relevant ITAD sections rather than copying raw.

When reading Drive docs, save temporary exports under `/tmp`, summarize into OKF, and clean the temp files. Do not commit raw Drive exports unless the user explicitly asks and the content is safe.

## Lead/contact net found

The mature lead net was not in the SIAL repo; it was in adjacent AI consulting/research paths. Reuse contact facts but rewrite the angle for ITAD.

- `/home/ubuntu/work/ai-consulting/leads.json`
- `/home/ubuntu/work/ai-consulting/outreach/lead-*.txt`
- `/home/ubuntu/work/research/ai-consulting/idaho-msp-contacts-leads1-3.md`
- `/home/ubuntu/work/research/treasure_valley_contacts_resolved.json`
- `/home/ubuntu/work/research/ai-consulting/idaho-contacts-benconnected-hawleytroxell.md`
- `/home/ubuntu/work/research/benconnected_hawley_troxell_contacts.md`

## Durable user facts captured

The user-provided facts were written as operating context, including:

- Meridian, Idaho operating base.
- Growth Web Development LLC DBA Sentinel IT Asset Disposal.
- Domain: `sentinelitad.com`.
- Public phone for now: `808-498-1125`.
- Vehicle/capacity: minivan, Tesla Model Y, 4x6 trailer, 1 rack / ~1,500 lb trailer load, Tesla ~3,500 lb tow rating, truck rental possible.
- Storage: garage with roughly 1.5 car ports usable.
- Drive wiping: hardware exists, tooling/process not installed yet.
- Desired brand: small, exclusive, professional, security-first, respectful.
- Avoid positioning as junk picking; frame as secure data disposal plus responsible gear recovery.
- Current bottleneck: listing throughput / freeze around posting inventory.
- First listing priorities: Dell 3620 workstations, HP DL360 Gen9, Dell T430, Dell R710, 4K HP monitors, server RAM, NVMe/enterprise SSDs, 40G/10G/16G networking cards/transceivers.

## Anti-duplication clause used

A useful clause to include when the user warns of existing research:

> Michael explicitly stated that a mature lead research net with contact info already exists. Any future agent assigned to lead generation must first locate that artifact and summarize its contents before doing new research. Do not create a duplicate MSP/datacenter/company list until the existing net has been found and deduped.

## Verification pattern and pitfall

When no canonical Markdown/docs verification exists, create a temporary script under `/tmp` using a `hermes-verify-` prefix. Check:

- changed files exist and are non-empty
- frontmatter delimiters exist where expected
- required user facts are present
- anti-duplication warning is present
- relative Markdown links resolve
- temporary helper files from Drive extraction are absent after cleanup

Then run it, delete it, and report as ad-hoc verification only.

If an external system demands a canonical command such as `npm run test`, run it in the relevant workspace and quote the result. If it is only a placeholder like `echo "Error: no test specified" && exit 1`, say canonical verification is blocked by the placeholder test script and report the ad-hoc verifier separately. Do not claim suite green.

## Commit hygiene

If unrelated dirty files exist, leave them alone. Stage and commit only intentional OKF paths. Use lane/lock protocol where applicable before editing project files.
