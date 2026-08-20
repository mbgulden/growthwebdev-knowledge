# Prismatic P1 hardening fresh-verification guard lesson — 2026-07-21

## Context

During Prismatic production dashboard hardening, source, report, and temporary verifier files were edited across multiple phases: CSS asset build, dashboard cache-key wiring, overflow fixes, public browser proof, Nginx route fixes, production handoff, and control-state receipts.

Hermes' post-edit guard flagged the workspace as unverified even after several successful verifiers because later edits and stale temporary verifier files were still in the changed-path set.

## Durable workflow lesson

For long multi-phase verification closeouts, do not rely on earlier successful verifier output once more files are edited. After the last source/report/control-state write, run one final explicit terminal-invoked `/tmp/hermes-verify-*` verifier that:

1. Is created with an OS-safe temporary filename (`tempfile.NamedTemporaryFile` or `mktemp /tmp/hermes-verify-name-XXXXXX.py`).
2. Covers every behavior class represented in the final changed paths, not just the last edited file.
3. Checks durable receipt/handoff/control-state markers.
4. Checks exact source behavior for the changed implementation, e.g. content-hashed CSS URL and no CDN reference.
5. Checks live runtime when production was touched: service active, immutable cwd, public asset/API routes, and signature-canary log markers.
6. Writes noisy output to a compact log and prints only a proof packet.
7. Deletes the temporary verifier and any stale `/tmp/hermes-verify-*` files created by the session when safe.
8. Labels the result `AD_HOC_OR_CANONICAL=ad-hoc targeted closeout`, never canonical suite green, unless the project canonical suite also ran after the last edit.

## Cloudflare / public URL verifier pitfall

Python's default `urllib` user agent can be rejected by Cloudflare with `403 Forbidden` even when browser proof is already green. For public dashboard closeout scripts, use an explicit verification user agent in `urllib.request.Request` before classifying the failure as product behavior.

Example:

```python
UA = {"User-Agent": "Mozilla/5.0 PrismaticCloseoutVerification"}
def fetch(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20)
```

If the default-UA attempt fails but the explicit-UA retry passes, report the first as a verifier transport issue, not a product regression.

## Compact proof shape

```text
COMMAND=<mktemp-created /tmp/hermes-verify-* script run via terminal>
RESULT=<PASS|FAIL|BLOCKED>
LOG=<path>
LOG_SHA256=<sha256>
SCOPE=<changed paths/behavior classes covered>
AD_HOC_OR_CANONICAL=ad-hoc targeted closeout
VERIFIER_CLEANUP=<PASS|FAIL>
NOT_CLAIMING=canonical full-suite green unless rerun after final edit
MARKER=<fresh closeout marker>
```
