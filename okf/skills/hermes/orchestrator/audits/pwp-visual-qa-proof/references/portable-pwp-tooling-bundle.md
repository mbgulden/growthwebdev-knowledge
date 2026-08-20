# Portable PWP Tooling Bundle Pattern

Use this when a PWP standard starts as docs/fixtures/checklists/prompt packs but needs to be reusable across website/webapp repos.

## Durable lesson

A PWP capability is not production-portable until it has all of these:

1. A plugin-owned Python API, e.g. `plugins.pwp.tooling.install_pwp_tooling(target_repo)`.
2. Template/schema/docs/fixtures included as package data in the Python distribution.
3. Target-repo installer behavior that copies files into predictable paths and updates `package.json` scripts when appropriate.
4. Plugin tool registration so dashboard/supervisor/MCP-style callers can discover and invoke it.
5. A bundled skill or operator guide that points to the plugin API, not local Hermes profile paths.
6. Fresh verification with:
   - source-tree install into a clean temp repo,
   - wheel build member inspection,
   - fresh virtualenv install from the wheel,
   - install from the installed wheel into another clean temp repo.

## Example split

- `plugins.pwp.visual_qa` owns Visual QA-only installation.
- `plugins.pwp.tooling` owns the broader portable bundle: contracts, schemas, fixtures, docs, theme starter, and Visual QA.

## Pitfall

Do not report “portable” just because a template folder exists in the repo or a Hermes skill was copied across profiles. Profile skill copies are local operator guidance; the production artifact is the plugin/package API plus package data.