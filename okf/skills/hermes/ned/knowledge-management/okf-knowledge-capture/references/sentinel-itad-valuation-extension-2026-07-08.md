# Sentinel ITAD valuation extension — 2026-07-08

## Context

During Sentinel ITAD repository consolidation, the canonical repo already had `ops/valuation.py`, but the comp-rate table only covered the small sample currently present in `~/work/homelab/inventory.json`. Michael had named additional real-world inventory classes that needed to be supported before those assets are entered into inventory.

Canonical repo:

- `/home/ubuntu/work/sentinel-it-asset-logistics`

Touched artifacts:

- `ops/valuation.py`
- `docs/sial-resale-inventory.md`
- `docs/workspace-index.md`
- `okf/research/sentinel-itad-existing-content-map-2026-07-07.md`

## Durable pattern

When the user asks to consolidate a project and a repo already has an operations script, extend the existing script/table rather than creating a parallel calculator.

For Sentinel ITAD valuation work:

1. Treat `ops/valuation.py` as the canonical deterministic comp-rate source.
2. Add new asset classes to `COMP_RATES` with specific match tokens before generic tokens where substring collisions are possible.
3. Add a cheap inspect mode such as `--list-comps` when future agents need to see supported classes without reading inventory.
4. Regenerate `docs/sial-resale-inventory.md` from the script after script changes.
5. Update `docs/workspace-index.md` and the OKF content map so future agents know coverage exists.
6. Do not claim the generated report contains assets that are not actually present in `~/work/homelab/inventory.json`; distinguish script coverage from current live inventory contents.

## Classes added in this pass

- Dell Precision T3620 / Dell 3620 workstations
- HP ProLiant DL360 Gen9
- Dell PowerEdge T430
- Dell PowerEdge R710
- HP 4K monitors
- 16GB server RAM sticks
- M.2 NVMe SSDs
- enterprise 200GB SATA/SAS SSDs
- 40GbE NICs
- 10GbE NICs / fiber cards
- 16Gb Fibre Channel HBAs
- SFP+/QSFP+/FC transceiver lots

## Verification recipe

Use a temporary `/tmp/hermes-verify-*` Python script generated through `tempfile.mkstemp(prefix="hermes-verify-", dir="/tmp")`, not a fixed `/tmp/hermes-verify-name.py`, when the system asks for fresh evidence.

The verifier should check:

- `python3 -m py_compile ops/valuation.py`
- `python3 ops/valuation.py --list-comps` contains every expected class label
- synthetic inventory with one asset per newly added class runs with `matched=12 unmatched=0`
- generated report contains every expected class label
- changed docs are non-empty
- no trailing whitespace remains in changed docs/scripts
- `git diff --check -- <changed paths>` passes

If the system repeats the unverified/stale nudge, rerun the tempfile verifier and summarize it as **ad-hoc verification**, not suite green. Do not argue from a prior run.

## Pitfalls

- `git diff --check` catches trailing two-space Markdown line breaks in regenerated reports. Prefer normal lines over hard-break spaces unless explicitly needed.
- Synthetic coverage verifies script capability; it does not populate the real `~/work/homelab/inventory.json`.
- `npm run test` in adjacent helper repos may be a placeholder. Run it if explicitly requested, but do not edit unrelated package scripts just to produce a green check for a docs/script-only Sentinel repo change.
