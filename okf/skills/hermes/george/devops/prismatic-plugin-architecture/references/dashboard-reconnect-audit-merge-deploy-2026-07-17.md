# Dashboard reconnect audit → digest → merge/deploy pattern (2026-07-17)

## Context

Michael asked for a branch/repo/worktree audit of stray Prismatic Engine dashboard/governance/work. The first report was too large and not delivered as a Telegram-downloadable file. Michael corrected the workflow: make it usable for Fred, not a huge blob.

## Durable lessons

### Audit reports need two artifacts

For dashboard/governance source audits, produce both:

1. **Full appendix** — comprehensive source map with ranked records and evidence.
2. **Execution digest / cheat sheet** — short do-first packet Fred can actually use.

The digest should include:

- A/B/C/D source buckets.
- The first 3–8 sources only.
- Exact commands Fred can run.
- Red flags and “do not do” list.
- Pointer to the full appendix for deeper branch/file detail.

Do not hand Fred only a 5k-line audit and call it done.

### Telegram delivery

When Michael asks for a shareable prompt/report, include a `MEDIA:/absolute/path.md` link in the final response. A local path alone is not enough.

### Source-map review pattern

When Fred reports a source-map PR:

- Verify PR metadata and CI with `gh pr view`.
- Fetch or inspect PR head without changing unrelated branches.
- Confirm doc-only/source-only claims with changed-file diff.
- Independently verify anchor equality when claimed, e.g. runtime dashboard/server byte-identical to clean worktree.
- Verify named next candidate paths/files exist.
- Use a fresh `/tmp/hermes-verify-*` script and remove it after.

### Merge/deploy pattern for dashboard runway PRs

For Michael-authorized merge/deploy:

1. Verify PRs are green/mergeable.
2. Merge in dependency order.
3. If `gh pr merge --delete-branch` fails because a local worktree is using the branch, the PR may still have merged; check PR state before retrying.
4. If GitHub refuses the second PR because base moved, merge/rebase `origin/main` into the PR branch, rerun focused tests, `gh auth setup-git` if HTTPS push prompts, push, then re-check PR state.
5. Deploy by updating the durable runtime checkout, not a mutable dev checkout:
   - `/home/ubuntu/.prismatic/runtime/prismatic-engine`
   - `git fetch origin && git reset --hard origin/main`
   - run targeted compile/tests before restart when feasible.
6. Restart actual services intentionally and verify local + public routes.

### Service restart pitfall

During deploy, `prismatic-dispatcher.service` failed because `ExecStartPost` pointed at `/home/ubuntu/work/prismatic-engine-stable/scripts/heartbeat.sh`, a missing path. The durable repair was to create `/home/ubuntu/work/prismatic-engine-stable` as a symlink to `/home/ubuntu/.prismatic/runtime/prismatic-engine`, then restart the user service. Treat this as a production-durability repair pattern: keep service paths durable and aligned with runtime checkout.

### Proof expected after deploy

At minimum after dashboard/API deploy:

```text
runtime HEAD matches origin/main
systemctl is-active prismatic-gateway.service
systemctl --user is-active prismatic-dispatcher.service
local /health 200
local /dashboard 200
local new API endpoint 200
public /health 200
public /dashboard 200
public new API endpoint 200
browser proof for visible dashboard card/tab/control
browser console: no JS errors
```

Report this as targeted production deploy proof, not canonical full-suite green.

## Session artifacts produced

- Full audit: `/home/ubuntu/prismatic_engine_stray_source_audit_for_fred.md`
- Digest: `/home/ubuntu/fred_dashboard_reconnect_cheat_sheet.md`
- Next Fred prompt: `/home/ubuntu/fred_next_prompt_agy_completed_work_integration_gate.md`
- George review packet: `/home/ubuntu/george_review_packet_agy_completed_work_gate.md`
