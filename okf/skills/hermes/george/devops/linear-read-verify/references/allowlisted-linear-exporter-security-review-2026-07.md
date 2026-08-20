# Allowlisted Linear exporter security review notes — 2026-07

Reusable details from the GRO-4263/GRO-4336 parent/child export review.

## Failure class 1: exact credential crossing a truncation boundary

A bounded exporter can pass normal secret-pattern tests and still leak a meaningful prefix when an unpatterned exact credential appears in a long text field and truncation runs before exact-secret removal.

Safe order:

1. load credential into memory without printing it;
2. recursively remove the exact credential from the raw bounded API response object;
3. normalize and truncate fields;
4. run generic secret-pattern redaction;
5. recursively remove the exact credential again after normalization as defense in depth;
6. serialize only the normalized redacted object.

Required offline test shape:

- sentinel credential is not matched by generic token regexes;
- sentinel appears across `MAX_DESCRIPTION_CHARS` or equivalent boundary;
- output contains neither the full credential nor a meaningful prefix, e.g. first eight or more characters;
- public CLI error paths still suppress exception text.

## Failure class 2: redirect follow-up can carry Authorization

Python `urllib.request.urlopen()` follows redirects by default. Depending on handler behavior, a redirected request may preserve `Authorization`; a cross-origin 301/302/303 therefore becomes a credential exfiltration risk before the client can inspect the final URL.

Safe pattern:

```python
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise RuntimeError("redirect rejected")

opener = urllib.request.build_opener(NoRedirect)
# route every Linear HTTP request through this opener, not global urlopen
```

Required offline test shape:

- mocked opener/handler observes the original request only;
- redirect response raises before any follow-up request is constructed;
- CLI output is generic and contains no credential, header, exception detail, or redirect target;
- live credential use is blocked until exact script/test hashes receive independent `CLEAN` review.

## Proof packet expectation

```text
PY_COMPILE=PASS
UNIT_TESTS=<N passed>
RUFF=PASS
SCRIPT_SHA256=<exact exporter sha>
TEST_SHA256=<exact test sha>
INDEPENDENT_REVIEW=CLEAN
LIVE_LINEAR_USE=false until CLEAN
LINEAR_MUTATED=false
```
