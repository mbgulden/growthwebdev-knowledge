# Gap closures from 2026-07-29 — worked examples

This is the concrete record of 8 gap closures in one session. Future-self: read this when closing a new gap to see the canonical shape; the discipline is in SKILL.md, the worked examples are here.

## The 8 gaps closed

| # | Gap title | Skill shipped | OKF doc | Verifier | First-run bugs |
|---|---|---|---|---|---|
| 1 | Live state vs. memory drift | session-state-handoff | hermes-session-handoff-discipline.md | handoff.py round-trip | None on first run (verifier was reused from handoff.py itself) |
| 2 | Proactive execution is too gentle | proactive-execution-discipline | hermes-proactive-execution-discipline.md | proactive_count.py + daily_briefing.py | argparse `--profile` shadowed by subparser; fixed by stripping pre-subcommand flags |
| 3 | Projector awareness slipped into generic tone | projector-aware-communication-discipline | hermes-projector-aware-communication-discipline.md | verify_reply_shape.py | None on first run; 4 representative cases all passed |
| 4 | Linear work too machine-dependent | (RUNTIME_REQUIREMENTS.md, no skill) | hermes-runtime-requirements.md | assert_runtime.sh | awk extraction can match fallback_providers before model block; live verdict PASS today, fragility pinned |
| 5 | OKF/evidence verification sometimes lazy | verifier-as-deliverable-discipline | hermes-verifier-as-deliverable-discipline.md | okf-section-check/verify.py + evidence-no-secret-marker/verify.py | Triple-quote syntax error in skill.md; broken-symlink FileNotFoundError; over-broad regex |
| 6 | Skills vs. memory boundary leak | (6 micro-skills) | hermes-memory-skills-boundary-discipline.md | (no separate verifier) | Adopter is hardcoded to agent-operations/, doesn't see skills/micro/; workaround: direct symlink loop |
| 7 | Telegram is too chatty on digests | telegram-cron-output-contract (micro) | (updated existing cron-alert-output-contract.md) | telegram-cron-output-check/verify.py | 10 forbidden-pattern violations across 12 scripts; 16-pattern regex set with stubs for self-references |
| 8 | "What ships next" gate is manual | next-action-truth-source (micro) | hermes-next-action-truth-source-discipline.md | (reconciler dry-run + live test) | prismatic.linear.budget module is a .pyc orphan; bypassed with direct GraphQL. TimelessDateOrDateTime filter 400; switched to state.type filter |

## The recurring bug patterns

These showed up in **every gap closure** that involved a new verifier:

1. **`py_compile` first, always.** A 2-line test: `subprocess.run(["python3", "-c", f"import py_compile; py_compile.compile({path!r}, doraise=True)"])`. Catches syntax errors that would otherwise only surface when the system nudges for verification.

2. **Regex escapes get mangled by `write_file`.** When writing a verifier via Python's `write_file` with a triple-quoted string containing regexes, the backslashes get interpreted. Use raw strings (`r"..."`) and avoid embedding regexes inside triple-quoted strings when possible. If you must, escape with `\\` at the Python level.

3. **Subprocess, not bash, when running shell commands from Python.** `subprocess.run(["python3", script, "arg1"], capture_output=True, text=True)` avoids bash-quoting issues with `$`, `*`, `***`, `&`, etc. The bash shell will eat or mangle these characters; subprocess passes them through verbatim.

4. **The first verifier run is for discovering bugs, not for "this should pass."** Plan for 1-2 rounds of bug-fix-and-re-verify. The bug class you find in round 1 (regex escapes, syntax, false positives) is the same bug class you'll find in round 2 (mode precedence, edge cases). The discipline is to expect bugs and ship the fix; it's NOT to be surprised.

## The pattern for "what shipped"

Each gap-closure turn shipped:
- 1 SKILL.md (or 1 micro-skill, or updated an existing one)
- 1 verify.py (or updated existing)
- 1 OKF doc (or updated existing)
- Adoption to N profiles (via symlink or _adopt_shared_skills.py)
- 1 focus verifier run (PASS-count reported honestly)
- 1 handoff update (gaps_closed list, follow-ups pinned)

The size of each "bounded slice" ranged from 3 bounded moves (gap 1, gap 4) to 12 (gap 7). The discipline scales; the shape doesn't.
