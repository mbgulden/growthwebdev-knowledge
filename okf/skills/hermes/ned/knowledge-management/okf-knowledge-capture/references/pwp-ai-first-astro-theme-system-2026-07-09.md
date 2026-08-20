# PWP AI-First Astro Theme System — 2026-07-09

## Context

Michael asked for a master plan for an AI-first, human-facing Astro template/theme system robust enough to become part of the Prismatic Web Plugin (PWP). The planning work needed to avoid reinventing the wheel and use proven open standards/community-compatible patterns.

## Canonical artifact

The plan was written under the Prismatic Engine repo in Ned's writable lane:

- `/home/ubuntu/work/prismatic-engine/plugins/pwp/docs/pwp-ai-theme-system-master-plan.md`
- Remote branch: `ned/pwp-ai-theme-master-plan`
- Remote file: `https://github.com/mbgulden/prismatic-engine/blob/ned/pwp-ai-theme-master-plan/plugins/pwp/docs/pwp-ai-theme-system-master-plan.md`

Important lane correction: the initially natural doc path `docs/pwp-ai-theme-system-master-plan.md` is outside Ned's lane in Prismatic Engine. For PWP-specific docs, use `plugins/pwp/docs/` unless a Linear issue or owner explicitly routes doc edits elsewhere.

## Durable planning pattern

When asked to design a reusable PWP/Astro theme system, include these layers:

1. **Principles**
   - AI-first development, human-first frontend.
   - Theme packages, not page dumps.
   - Open standards first.
   - Redesigns update tokens/components/manifests once, not page-by-page CSS.

2. **Open standards / proven strategies**
   - W3C Design Tokens Community Group format.
   - Style Dictionary-compatible transforms.
   - CSS custom properties.
   - Astro layouts/components/content collections.
   - JSON Schema + Zod + TypeScript contracts.
   - EmDash structured editable content / Portable Text-style fields.
   - Playwright, axe-core, Lighthouse CI, visual regression.

3. **Core PWP artifacts**
   - `theme.json` manifest.
   - W3C-style `tokens.json` with PWP CSS variable compilation.
   - module manifests with props schema, variants, accessibility rules, and editable fields.
   - EmDash edit maps with locked compliance/system fields.
   - theme registry and compatibility metadata.
   - deployment provenance: theme hash, token hash, content hash, module hash.

4. **Phased roadmap**
   - Phase 0: contracts/schemas.
   - Phase 1: token foundation.
   - Phase 2: Astro module library.
   - Phase 3: EmDash editing integration.
   - Phase 4: theme registry.
   - Phase 5: page synthesis pipeline.
   - Phase 6: visual/a11y/performance regression.
   - Phase 7: deploy/rollback/provenance.
   - Phase 8: SDK/community contributor model.
   - Phase 9: agent specialization/autopilot.

5. **Verification**
   - For doc-only master plans without a canonical suite, use a `/tmp/hermes-verify-*` script checking required sections, all phases, code-fence balance, lane-correct path, diff hygiene, and remote raw content if GitHub API was used.

## GitHub push fallback observed

Normal `git push` from `prismatic-engine` repeatedly failed with a remote unpack/index-pack error for this branch. Workaround used successfully:

1. Create/update remote branch with `gh api repos/<owner>/<repo>/git/refs` if needed.
2. Base64-encode the file content locally.
3. Use GitHub Contents API `PUT /repos/{owner}/{repo}/contents/{path}` with `message`, `content`, `branch`, and optional `sha`.
4. Verify with the raw GitHub URL.

Capture the workaround as a fallback only after normal push and `--no-thin` push fail. Do not treat this as a global rule that git push is broken.
