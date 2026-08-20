# Nginx edge containment proof pattern

Session-derived pattern for narrow, reversible production edge containment (for example, blocking topology/workspace routes while preserving the app and upstream runtime).

## Trigger

Use when Michael authorizes a scoped Nginx/edge-only containment and explicitly separates it from application implementation, deployment, timers, Git cleanup, DB mutation, or Linear changes.

## Recipe

1. **Bind the starting state**
   - Hash the active config before editing.
   - Confirm whether the active config is a symlink or regular file so rollback targets the right path.
   - Write a root-owned rollback backup before mutation; keep restrictive permissions such as `0600` if appropriate.

2. **Edit only the authorized route surface**
   - Replace/insert only the named `location` blocks.
   - Prefer exact-match locations for exact routes and `^~` prefix locations when the containment needs to win over regex/static handlers.
   - Do not touch upstream service code, DB, timers, Git refs, or task state as part of an edge-only phase.

3. **Validate before reload and fail closed**
   - Run `nginx -t` after the edit.
   - If syntax validation fails, restore the backup, re-run `nginx -t`, and report rollback.
   - Reload only after syntax passes; if reload fails, restore backup, validate, reload, and report rollback.

4. **Prove the boundary**
   - Public edge routes targeted by containment should return the intended code, usually `403`.
   - Preserved public routes such as `/`, `/dashboard`, `/health`, or unrelated API paths should retain their previous status.
   - Direct upstream probes (for example `http://127.0.0.1:<port>/...`) should stay unchanged; this proves containment is edge-only, not application behavior.

5. **Handle HEAD correctly**
   - For Nginx `return 403`, use `curl -I` for HEAD checks.
   - Avoid `curl -X HEAD -o /dev/null` as the primary proof: curl can report `curl: (18) transfer closed with ... bytes remaining` against a valid Nginx error response because it expects body semantics that HEAD will not deliver.
   - Treat this as verifier setup failure, not product failure; rerun with proper HEAD semantics.

6. **Hash root-only rollback artifacts safely**
   - If the rollback backup is mode `0600`, do not weaken permissions just for the verifier.
   - Run only the read/assert verifier phase under `sudo -n python3` or hash it with `sudo -n sha256sum`.

7. **Close out without proof drift**
   - Clean stale temporary verifier scripts.
   - Capture final log SHA.
   - Assert active config hash, rollback hash, effective block count, public route statuses, preserved route statuses, and handoff/readback markers.
   - Prove no post-verifier mutation by comparing config/handoff mtimes before and after the final assertion phase.

## Compact proof packet fields

```text
COMMAND=atomic Nginx config edit + nginx -t + systemctl reload nginx + public route verification
RESULT=PASS|FAIL|ROLLED_BACK
LOG=/tmp/hermes-verify-<project>-nginx-containment-<phase>.log
SCOPE=edge containment only for <routes>
AD_HOC_OR_CANONICAL=ad-hoc targeted production proof
NOT_CLAIMING=application implementation,deployment,timer changes,Git changes,DB changes,Linear changes
MARKER=<PROJECT>_NGINX_<SURFACE>_CONTAINMENT_ACTIVE
```

## Pitfalls

- A successful `systemctl reload nginx` is not enough; route probes must prove both blocked and preserved paths.
- A direct upstream `200` after public edge `403` is expected for edge-only containment; do not report it as a bypass unless the task required upstream removal too.
- Verifier setup failures should be kept in logs but not overclaimed as production failure after a corrected verifier passes.
- Do not delete or hide rollback backups; include path and hash in the handoff.
