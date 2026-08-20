# OKF Operations Closeout Documentation Pattern

Use this reference when Michael asks to document a broad work session, operational sweep, or “all the other work you did today” in OKF.

## Goal

Turn ephemeral Telegram/session work into a durable OKF operations record that future agents can use without replaying the whole session.

## When to use

- Michael asks to document today’s work in OKF.
- A session covered multiple systems: dashboard, Linear, cron, AGY, credentials, verification, or remediation routing.
- Work produced durable artifacts such as Linear issues, CLI commands, API endpoints, verification scripts, skill references, or OKF entries.

## Target location

Prefer:

```text
/home/ubuntu/work/okf/operations/YYYY-MM-DD-<topic>-closeout.md
```

Then add a pointer to:

```text
/home/ubuntu/work/okf/operations/INDEX.md
```

Do not rely on Hermes session history as the durable artifact.

## Report shape

Include:

1. Frontmatter:
   - `title`
   - `type: operations-closeout`
   - `status`
   - `created`
   - `owner`
   - `systems`
   - `verification_scope`
2. Executive summary.
3. Workstream sections, each with:
   - outcome
   - changed/verified paths
   - commands/API endpoints
   - Linear issue links/IDs when relevant
   - source evidence paths
   - verification evidence
   - cleanup status
   - blockers/warnings
4. Explicit verification posture:
   - “ad hoc targeted verification” vs “full suite-green”
   - public/live checks skipped reason when applicable
5. Follow-up queue.

## Verification pattern

After writing or patching OKF markdown, run a fresh temporary verifier under `/tmp` using `tempfile.mkstemp(prefix="hermes-verify-", suffix=".py", dir="/tmp")`.

The verifier should check:

- changed markdown files exist and are non-empty
- frontmatter/title shape is present
- required sections/keywords are present
- index links to the new report
- index date or relevant pointer changed
- fenced code blocks are balanced
- known typo/corruption markers are absent
- the temp verifier deletes itself

Report as:

```text
AD_HOC_VERIFICATION: PASS
Scope: OKF documentation verification only — not suite-green.
cleanup=PASS removed /tmp/hermes-verify-...
```

## Pitfalls

- Do not bury broad operational closeout in a chat response only.
- Do not call markdown verification “suite green.”
- Do not overstate live/public proof when only local/ad hoc checks ran.
- Do not print secrets in OKF; use `set/missing` or masked prefixes.
- If the system asks for fresh verification after a markdown edit, rerun a new `/tmp/hermes-verify-*` script instead of citing the previous run.
