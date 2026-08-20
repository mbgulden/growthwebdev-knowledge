# HDE North Star OKF + Operational Consolidation — 2026-07-18

Use this reference when a project vision/gap audit must become durable repo knowledge and not just chat memory.

## Durable capture pattern

1. Write a canonical North Star document in the project repo, not only in a Linear comment or chat summary.
2. Add a green-state rubric that defines what “done” means by category.
3. Add a source map for future agents: repo path, staging/production URLs, verification commands, Linear epics, and proof artifact locations.
4. For stray operational files, write an inventory script and a summarized inventory doc before moving/deleting anything.
5. Copy reusable operational source into the canonical repo first; do not delete active Hermes profile cron scripts or runtime backups until cron/systemd references are repointed and verified.
6. Keep raw `/tmp` logs and cron outputs out of git; summarize durable findings into `docs/operations/`.

## HDE North Star formulation

Human Design Engine helps people understand their design, regulate their nervous system through embodied daily action, and keep becoming the highest-integrity version of themselves — together.

Reports are maps. Sanctuary, daily transit work, reflection, coaching, relationship practice, and community are where the work happens.

## Verification pattern

- Compile copied Python scripts.
- Run the inventory script on a bounded root.
- Run doc assertions for key North Star/rubric/source-map strings.
- Secret-scan changed docs/scripts for obvious credential literals.
- Run the repo build when docs/scripts live in a frontend repo with postbuild normalization.
- Use `git diff --check` for Markdown/doc additions.
