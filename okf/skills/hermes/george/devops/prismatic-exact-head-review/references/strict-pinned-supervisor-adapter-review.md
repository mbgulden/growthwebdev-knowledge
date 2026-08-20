# Strict pinned-supervisor adapter review

Use this reference when reviewing a Prismatic curator/dispatcher candidate that bridges one CLI layer into another, especially when strict runtime pinning is controlled by environment variables or optional `supervisor_path` / `python_executable` arguments.

## Durable lesson

A compatibility-looking adapter fix is not accepted until adversarial review proves both sides of the contract:

1. the producer/dispatcher emits exactly the argv schema the supervisor accepts; and
2. strict mode validates concrete runtime objects, not just nonempty strings.

In GRO-4407, the first candidate fixed the canonical argv mismatch but adversarial review found strict mode still accepted malformed pins such as missing supervisor files or non-executable interpreters. The repair added persistent fail-closed tests and exact-head review before acceptance.

## Review probes to require

For `PRISMATIC_REQUIRE_PINNED_SUPERVISOR=1` or equivalent strict mode, fixtures should cover:

- missing release root;
- release root path that is a file, not a directory;
- relative release root path;
- missing supervisor path;
- supervisor path that is a directory;
- relative supervisor path;
- supervisor outside the release root, including symlink escapes and prefix-trick paths;
- missing interpreter path;
- interpreter path that is a directory;
- interpreter path that is relative/PATH-resolved rather than absolute;
- interpreter path that exists but is not executable;
- accepted case with absolute existing release root, supervisor regular file inside root, and executable interpreter.

For user/event values passed into argv, require fail-closed validation for:

- `None`;
- empty strings;
- option-like values beginning with `-` or containing `--key=value` patterns where a positional value is expected;
- NUL bytes or other values that cannot be safely represented in argv.

## Parser/schema preservation proof

If moving parser construction between modules or turning `main()` parsing into `build_parser()`, add an AST-level or equivalent assertion that the `add_argument` sequence/digest is unchanged. This prevents accidental CLI drift while making dispatcher/supervisor integration testable.

## Acceptance boundary

A candidate that passes focused behavior tests but lacks strict object-validation probes remains `review_pending` or `blocked`, not accepted. A same-branch repair may be valid, but it creates a new exact head requiring:

```text
HEAD=<new repair commit>
TREE=<new tree>
PARENT=<prior candidate>
STRICT_PINNING_PROBES=PASS
ADAPTER_SCHEMA_PRESERVATION=PASS
INDEPENDENT_REVIEW=<fresh exact-head verdict>
NOT_CLAIMING=old CLEAN/PASS carries forward
```
