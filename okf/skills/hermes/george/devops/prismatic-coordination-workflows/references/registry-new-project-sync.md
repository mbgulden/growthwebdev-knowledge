# New-project registry sync (Linear record + project-registry.json)

Pattern proven 2026-08-20 on the OKF MCP Phase 2 record (project `80433cf7-8080-4324-9e78-b471b3bbb428`, GRO-4818..4821). Use whenever the **first** Linear record for a project is created and the canonical registry has no entry for it yet.

## Why the stock helpers are not enough

`/home/ubuntu/.hermes/profiles/orchestrator/scripts/registry_writer.py` is still the single point of registry write, but its public functions (`update_next_action`, `sync_project_from_issue`) only **update** entries already present under `ventures`, `standalone_projects`, or `prismatic-engine`. For a brand-new project key they return `False` and write nothing. Do not "fix" this by editing the JSON with echo/heredoc or chat prose.

## Steps

1. Create the Linear record first (fail-closed writer: dry-run → apply → independent readback → durable receipt at a stable path, e.g. `/home/ubuntu/.prismatic/deployments/<slug>/<date>/receipts/...json`).
2. Build the registry entry from the **durable receipt** — never re-fetch Linear to get IDs (receipt is the correlated source of truth for what this writer just created).
3. Model the entry on a sibling in the same section (for MCP servers: `openhumandesignmcp`). Core fields: `name`, `project_type`, `linear_project_id`, `linear_project_name`, `linear_issue_ids` (list of UUIDs), `repos`, `public_endpoint` if applicable, `next_action` (must reference an issue that exists in Linear — the "what's next" must be real work, usually the open item like an Inspector/cloud-call closer), `last_action_at`, `_last_updated`, `completed[]` (dated, issue-keyed, evidence-labeled entries).
4. Merge into the section dict, preserving any pre-existing `completed[]` entries (dedupe on issue+date), then persist via `registry_writer._write_registry_atomically(reg)` (temp-file + rename). Import the module rather than re-implementing the atomic write.
5. Independent readback: reload the registry from disk and assert the project ID, sorted issue-ID list, and `next_action` prefix.
6. Report: mode (create/update), key, IDs, next_action, and that sibling entries were untouched.

## Guardrails

- **Do not clobber lane state files.** `/home/ubuntu/.hermes/profiles/<agent>/state/current.json` belongs to that lane's dispatcher handoff (AGY/Prismatic lanes are actively managed). A registry sync is not a handoff write; if a lane state file is stale, say so — do not overwrite it.
- **Label verification evidence correctly.** Registry `completed[].evidence` must carry the same ad-hoc vs canonical distinction used in the report; never let an ad-hoc pass read as canonical-suite green.
- **No GitHub remote is not a gap to fix** — local-only repos are a valid registry value; record the path and state "local only".
- The weekly `registry_reconciler.py` cron only reconciles existing entries; a missing key is invisible to it until one of these syncs creates it.

## Proof shape

```text
COMMAND=python3 <profile>/scripts/registry_sync_<slug>.py
RESULT=PASS (mode=create|update, atomic write, readback asserted)
TARGET=/home/ubuntu/work/project-registry.json → <section>["<key>"]
LINKS=linear_project_id + N issue IDs (from receipt)
NEXT_ACTION=<identifier>: <short>
OTHERS_INTACT=<sibling keys untouched>
LANE_STATE_TOUCHED=false
```
