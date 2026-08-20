# Sentinel ITAD Manual Resale Proof Pattern — 2026-07-22

## Context

Daily Golden Thread selected Sentinel IT Asset Logistics because its registry `last_action_at` was the stalest among projects with live non-done Linear issues. The active issue cluster was `GRO-1602` manual eBay listing, `GRO-1603` inventory-to-eBay converter, `GRO-1604` order dashboard, plus `GRO-469` wipe/certificate tooling.

The key strategic correction was to avoid letting resale become a software build before a single manual sale is proven.

## Durable Pattern

For hardware resale / ITAD projects where the stalled action mixes manual selling and automation:

1. **Live-check Linear first.** Confirm current non-done issues and states for the project before trusting the registry.
2. **Challenge automation-first assumptions.** If converter/dashboard work is active before one manual sale/listing exists, treat this as a likely premature-engineering risk.
3. **Pick manual proof as the first execution slice when inventory is already on hand.** Create a publish-ready listing packet, not a live listing.
4. **Do not publish or mark sold without Michael.** Include a Michael-only publish checklist and leave it unchecked by design.
5. **Ground the packet in canonical inventory/valuation artifacts.** Do not create a duplicate source of truth for assets, serials, prices, or locations.
6. **Require revenue math.** Include target price, fees, shipping/insurance assumptions, minimum acceptable net, and time-to-cash hypothesis.
7. **Create a manual-before-software gate.** Automation tickets should remain paused/backlog until a small manual sprint proves recurring pain and measurable time savings.
8. **Verify the artifact deterministically.** A tiny checker should assert required fields, no placeholders, canonical citations, revenue math, and the assumption test.

## Good Linear Task Shape

Top task title pattern:

`GT YYYY-MM-DD — Sentinel first-item eBay listing packet`

Required rubric:

- **Unit:** packet has all fields for one named item and no TODO/TBD placeholders.
- **Integration:** cites/extends existing Sentinel inventory or valuation artifacts rather than creating duplicate source of truth.
- **Revenue:** includes expected gross, fees/shipping assumptions, minimum acceptable net, and time-to-cash hypothesis.
- **Assumption:** tests whether manual listing beats building converter/dashboard code first.

Exit criterion:

`A 3-item manual resale sprint produces one publish-ready listing packet, channel-specific prices/fees/shipping math, and a sell/no-sell decision log without requiring new dashboard/converter code. Done only when evidence paths and revenue assumptions are attached.`

## Evidence Example

The successful execution produced:

- `docs/resale/sentinel_first_item_ebay_listing_packet.md`
- `ops/verify_listing_packet.py`

Verification command:

```bash
python3 /home/ubuntu/work/sentinel-it-asset-logistics/ops/verify_listing_packet.py
```

Expected result categories:

- Unit PASS
- Integration PASS
- Revenue PASS
- Assumption PASS
- Exit criterion PASS

## Pitfalls

- Do not publish to eBay, Facebook Marketplace, or any live sales channel from the cron pipeline.
- Do not mark inventory sold/contacted/sent without Michael's explicit confirmation.
- Do not let an AGY PASS stand alone; rerun or inspect the deterministic artifact verifier directly.
- Do not accept static wipe/certificate gaps as blockers to manual sale of non-storage assets, but do keep MSP/data-bearing-media offers gated behind wipe/certificate proof.
- Do not create a fresh inventory table if `homelab/inventory.json`, Sentinel resale inventory docs, or valuation scripts already exist.