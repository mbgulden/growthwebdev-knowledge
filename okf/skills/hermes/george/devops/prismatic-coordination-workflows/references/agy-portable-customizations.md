# AGY / Antigravity portable customizations coordination note

Use this when Michael asks to audit, standardize, productize, or verify AGY/Antigravity CLI skills, rules, `.agents`, `.gemini`, or related Prismatic operator customization assets.

## Durable pattern

Treat AGY customization work as a productized Prismatic install slice, not a home-directory cleanup.

1. Inventory live AGY roots secret-safely:
   - portable candidates: rules/skills/docs intended for a workspace;
   - non-portable runtime state: OAuth tokens, conversations, transcripts, caches, logs, binaries, MCP results, project registries, local DBs;
   - unsafe patterns: absolute user paths, raw launch wrappers, permission-bypass instructions, unrestricted execution, account/model bindings, global token mutation, detached runtime procedures.
2. Convert only portable behavior into a repository-native workspace bundle:
   - `.agents/rules/*.md`
   - `.agents/skills.json`
   - `.agents/skills/<name>/SKILL.md`
   - optional installed package resources mirroring the bundle.
3. Ship a managed lifecycle instead of copy-paste instructions:
   - `audit`, `validate`, `install`, `status`, `uninstall`;
   - dry-run first;
   - whole-plan conflict detection before any write;
   - atomic same-directory writes;
   - symlink and non-regular path refusal;
   - managed manifest as exact shipped-bundle inventory/status, not user-controlled overwrite/delete authorization;
   - no-follow, collision-resistant backup-before-force;
   - uninstall only files that still match the current shipped bundle, not merely mutable manifest digests;
   - preserve user drift by default;
   - fail closed on tampered manifests or destination escape.
4. Verify source and installed-distribution behavior separately:
   - source/resource parity;
   - wheel and sdist archive inspection;
   - non-editable clean-room wheel install from an empty CWD with source tree removed from `PYTHONPATH`;
   - CLI namespace parsing, dry-run, install/status/idempotent reinstall/uninstall;
   - focused tests for symlinks, non-regular files, conflict atomicity, tampered manifests, and drift preservation.
5. Bind proof to exact head/tree and separate claims:
   - focused tests are not canonical suite green;
   - GitHub canonical `python -m pytest tests/` can differ from raw repository-root `pytest` collection;
   - raw-root collection failures outside the workflow boundary must be reported as non-claims/baseline defects, not hidden or relabeled.
6. Draft PR first when independent review is still pending. Do not merge/deploy/restart/global-migrate AGY config until exact-head independent review and Michael's authorization policy are satisfied.

## Security-review repair reference

If an independent review finds installer/audit/manifest vulnerabilities, switch from productization mode to the fail-closed repair workflow in `references/agy-customization-security-review-repair.md`. Treat stale-by-hash reports as blockers when their reproduced behavior still exists in the current candidate, then require fresh exact-head independent re-review before merge/readiness.

For the PR #398 atomic-mutation/audit-root repair and closeout pattern, including provider-filtered review fallback, exact-tree merge binding, and late checkpoint readback verification, use `references/pr398-agy-atomic-closeout.md`.

## Packaging pitfall

Hidden resource directories such as `.agents` may be excluded by Python packaging defaults. If a hidden workspace bundle must ship in wheels, mirror it under a non-hidden package resource path such as `prismatic/resources/antigravity/workspace/agents/`, then map that resource tree to destination `.agents/` at install time. Verify with wheel/sdist archive inspection and a non-editable installed-wheel lifecycle test.

## Reporting boundary

Use explicit non-claims for AGY customization work:

```text
NOT_CLAIMING=AGY authentication; global AGY config migration; hooks/plugins/MCP install; production/deployment; service restart; Linear writes; merge; raw-root pytest green unless actually proven
```

## Keep out of portable bundles

Do not package or copy:

- OAuth tokens, API keys, cookies, credential helpers;
- conversations, transcripts, brain/runtime databases, logs, caches;
- binaries/wrappers coupled to one host;
- project registry state;
- account-specific model/provider choices;
- AOT/HDE/SEO/email/Cloudflare persona-specific skills unless the task explicitly asks for a separate named pack;
- instructions that bypass permissions or encourage unrestricted execution outside Prismatic admission/supervision.
