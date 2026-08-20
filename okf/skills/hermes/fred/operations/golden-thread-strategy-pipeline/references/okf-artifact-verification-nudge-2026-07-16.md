# OKF Artifact Verification Nudge Pattern — 2026-07-16

## Context
A post-turn verifier repeatedly flagged a changed OKF Markdown artifact as `unverified` even after the main pipeline had already verified the operational artifacts. The changed path was the durable OKF report itself:

`/home/ubuntu/work/okf/operations/2026-07-16-ai-consulting-security-posture-golden-thread.md`

## Durable Lesson
When the nudge names an OKF/report artifact, verify the **artifact contract**, not the final chat-delivery shape.

A first verifier failed because it expected final-response wording and mobile workspace links that were not required inside the OKF artifact. The corrected verifier checked the actual OKF report requirements:

- Required OKF sections are present.
- Selected project and registry slug are present.
- Research artifact paths are present.
- Assumption and strategy tables are present.
- Linear issue IDs are present.
- Rubric entries include Unit/Integration/Revenue/Assumption PASS evidence.
- No-send/manual-send guardrail is present for outreach work.
- Verification command references are present.
- Placeholder/silent markers are absent.
- Temporary verifier removes itself.

## Pattern
Use `tempfile.mkstemp(prefix="hermes-verify-", suffix=".py", dir="/tmp")`, write a tiny focused checker, run it, delete it in the same terminal call, and report the output explicitly as **ad-hoc targeted verification, not suite green**.

## Pitfall
Do not make the verifier stricter than the artifact's intended contract. For example, durable OKF artifacts do not necessarily need the same markdown headings, mobile links, or final-response wording used in the delivered summary.
