# Golden Thread digest deterministic cron repair

Use this when a Golden Thread / daily digest cron produces vague LLM error summaries such as:

- registry file not found at `$PRISMATIC_HOME/work/project-registry.json`
- `Skill 'golden-thread' not found`
- `fatal: not a git repository` from `gh pr list` / git commands

## Durable lesson

Do not keep tuning a fragile LLM-only digest prompt when the job has a stable reporting contract. Convert it to a deterministic profile-local no-agent script when the output can be generated from durable sources.

## Repair pattern

1. Inspect the live cron job record and the latest real error lines.
2. Identify the broken contracts separately:
   - unresolved/wrong env-var path (`$PRISMATIC_HOME/work/...` vs canonical `/home/ubuntu/work/...`)
   - missing skill dependency in the active profile
   - shell/GitHub commands assuming cwd is a git repo
3. Create a profile-local script under the active profile `scripts/` directory.
4. Use absolute canonical paths for durable sources, especially:
   - `/home/ubuntu/work/project-registry.json`
5. For GitHub checks, never rely on cwd; use explicit repo flags:
   - `gh issue list -R owner/repo ...`
   - `gh pr list -R owner/repo ...`
6. Keep the digest read-only unless the job is explicitly a sync/mutation job. If another scheduled job owns registry updates, the digest should report only.
7. Update the cron to:
   - `script=<relative script name>`
   - `no_agent=True`
   - `skills=[]` if the prior skill dependency was missing/unnecessary
   - `workdir=/home/ubuntu/work` or another real absolute workdir
8. Run the cron once through `cronjob(action="run")`, not only via direct shell.
9. Add a `/tmp/hermes-verify-*` verifier that checks:
   - `py_compile` passes
   - script executable exists
   - source contains canonical path and `gh -R` markers
   - source does not contain registry mutation markers such as `REGISTRY.write_text` / temp replace when digest is meant to be read-only
   - live job config has expected `script`, `no_agent`, `workdir`, `skills`, and `last_status=ok`
   - direct bounded run returns 0 and contains expected digest sections
   - old failure text is absent

## Pitfalls

- Do not call the job fixed just because `last_status=ok`; LLM jobs can summarize their own failure while the scheduler reports ok.
- Do not leave a missing skill dependency attached to a deterministic no-agent script.
- Do not let a daily digest mutate the project registry unless mutation is the explicit purpose of that job.
- Do not use `gh pr list` without `-R` inside cron jobs; cron cwd is not a reliable repo context.
