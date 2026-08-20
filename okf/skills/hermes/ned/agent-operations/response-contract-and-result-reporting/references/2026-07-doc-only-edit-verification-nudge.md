---
type: Reference
title: Verification nudge handling for documentation-only edits
description: When a verification nudge lists Markdown / docs / packet paths with no source, the canonical build command is not actually verifying the changed path. Use a focused artifact verifier instead.
tags: [verification, nudge, documentation, hermes-agent, ad-hoc]
timestamp: 2026-07-27T22:46:00Z
source_session: HDE reconciliation packet patch (2026-07-27)
related_skills: [response-contract-and-result-reporting, multi-source-reconciliation-packet]
---

# Verification nudge handling for documentation-only edits

## Symptom

After patching a Markdown / docs / packet artefact in a repo, the platform issues the standard "Run the relevant verification command now (`npm run build`)" nudge, listing the changed Markdown path.

## Why the standard nudge is wrong here

`npm run build` exercises the source/JS/JSON/Astro pipeline. It will pass for unrelated reasons (the source is unchanged) while silently failing to verify that the patched Markdown is actually present, intact, sane, or safe. Reporting "build passed" after a Markdown-only edit is honest-but-misleading: it conflates two different verification scopes.

## Honest response shape

1. Run the canonical command once if it is cheap and the repo expects it. Report its result, but explicitly state it does not verify the changed path.
2. Write a focused `/tmp/hermes-verify-<topic>.py` script that asserts:
   - the new Markdown markers / sections / tables are present (`assert "<required string>" in content`),
   - ASCII-only if the file is meant for Telegram delivery (for each `c` in content, `ord(c) < 128`),
   - no credential-shaped strings (`ghp_`, `github_pat_`, `sk-`, `xox[ab]-`, `AKIA`, `postgres://...@`, `mysql://...@`, `redis://...@`) leak into the file,
   - the file appears as expected in `git status --porcelain` (untracked vs tracked).
3. Run it. Report `PASS` with the verifier's printed line.
4. Delete the verifier.
5. State the verification scope clearly: the verifier confirms the artefact is intact, sane, and free of leaked secrets — it does not prove the documentation is correct in a business sense.

## Worked example (HDE reconciliation packet, 2026-07-27)

- Patched: `hd-platform/docs/operations/_reconciliation/hde-reconciliation-packet-2026-07-27.md` (collapsed four sign-off items to one decision).
- Companion created: `...-telegram.md` (ASCII-safe export).
- Canonical build: `npm run build` -> PASS (10 pages built, postbuild 244 legacy files preserved, 170 sitemap routes, 5 directory collisions skipped).
- Artifact verifier (`/tmp/hermes-verify-hde-reconciliation-2026-07-27.py`): required markers present, telegram ASCII-only, no credential-shaped strings, both files untracked -> PASS.
- Verifier deleted. Final report: build + artifact verifier both PASS; changes are documentation-only.

## Pitfalls

- Do not respond by re-running the build and reporting "still passing" without the artifact verifier. That is the path that produces plausible-looking but unverifiable results.
- Do not turn the verifier into a permanent fixture. Delete it; keep the script body in this reference for re-use.
- Do not invent a build command for a pure-Markdown repo just to satisfy the nudge. If the repo has no build, state "no canonical build applies; artifact verifier is the only check" and run that.
- If the artifact is a Telegram export, ASCII safety is non-negotiable. Smart quotes, em-dashes, and arrows mojibake in pasted Telegram output (see `references/2026-07-telegram-markdown-mojibake-safe-export.md`).