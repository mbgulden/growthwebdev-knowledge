# PWP portable tooling bundle lesson — 2026-07-12

## Trigger

During the HDE PWP Visual QA install, Michael corrected the implementation direction: Visual QA could not remain a repo-local harness, OKF standard, Hermes profile skill, or metadata-only pattern. It needed to be part of the actual PWP plugin and portable for any website/webapp install.

## Durable lesson

When building PWP capabilities, ask: **is this only a standard/fixture/doc, or can a new repo install and verify it from the PWP plugin?** If it is important to PWP delivery, prefer a plugin-owned installer and verifier.

## Pattern that worked

1. Put production distribution under `plugins.pwp`, not only in Hermes skills.
2. Add a manifest function that describes the capability and commands.
3. Add an installer function that copies templates/assets into a target repo.
4. Merge `package.json` scripts/dependencies where applicable.
5. Register plugin tools on `PWPDesignTokenPlugin` so supervisors/agents can call it.
6. Add bundled Prismatic skill docs for operator guidance on another machine.
7. Update `pyproject.toml` package data so plugin templates/docs/fixtures ship in wheels.
8. Verify with:
   - targeted pytest,
   - `py_compile`,
   - install into a clean fake repo,
   - build wheel and inspect required members,
   - install wheel into fresh venv and call installer from installed package,
   - run generated verifier scripts from the target repo.

## Built from the lesson

- `plugins.pwp.visual_qa.install_visual_qa(target_dir)` installs Visual QA.
- `plugins.pwp.tooling.install_contract_tooling(target_dir)` installs schemas, fixtures, docs, and `scripts/pwp-contracts-verify.py`.
- `plugins.pwp.tooling.install_theme_starter(target_dir)` installs the `trust-light` starter.
- `plugins.pwp.tooling.install_pwp_tooling(target_dir)` installs contracts + Visual QA + starter theme.
- Plugin tools include `pwp_install_tooling`, `pwp_tooling_manifest`, and validation helpers.

## Metadata clusters that should become installable tooling

Already converted to installable bundle:

- module contract schemas and fixture gallery,
- theme package/registry schemas,
- theme agent prompt packs,
- community theme review checklist,
- SmartMedia semantic slot registry,
- EmDash guard contract documentation,
- PWP Visual QA standard,
- `trust-light` theme starter.

Still good candidates for future tooling:

- Astro component generator from module contracts,
- TypeScript type generator from schemas,
- SmartMedia asset recommender/runtime resolver,
- EmDash editable-map generator from module contracts,
- SEO/schema preview CLI for arbitrary page manifests.

## Pitfalls

- Do not report a PWP capability as portable unless wheel package data includes the relevant templates/docs/fixtures and a fresh-venv smoke can import and run the installer.
- Do not treat Hermes profile skill copies as distribution. They are local operator guidance only.
- Keep portable docs under consistent target paths like `docs/pwp/*`; inconsistent doc paths cause install/verifier drift.
- When a supervisor asks for ad-hoc verification, create `/tmp/hermes-verify-*.py`, run it, and clean it up; label the result as ad-hoc targeted verification, not suite-green.
