# Runtime recovery review/repair patterns

Use this reference when reviewing or taking over a raw-output-to-completed-work recovery/reconciliation producer after the completed-work integration gate has merged.

## Session-derived repair checklist

When a producer claims crash-safe recovery is implemented, do not stop at canonical/focused pass. Independently probe these semantic hazards:

1. **Terminal retention cap semantics**
   - The configured terminal-row retention limit must apply only to terminal audit rows.
   - Pending, retry-wait, and in-progress rows must remain lossless and must not consume terminal-cap slots.
   - Add tests with mixed states where old undelivered rows survive cleanup while terminal rows are capped.

2. **CAS result truthfulness**
   - Terminal-failure and retry helpers must inspect the actual compare-and-set update result.
   - A failed token CAS is `stale_claim`/requeueable, not a successful terminal or retry transition.
   - Race tests should simulate another claimant changing the row between read and update.

3. **Post-claim succeeded race**
   - If a claimant fails to acquire because another worker completed the same row, do not report `succeeded` from stale pre-claim metadata.
   - Reload the durable completed-work row and verify exact markers before returning a success result.
   - If the row cannot be proven, fail closed with an unavailable/stale status rather than synthesized success markers.

4. **Failure marker hygiene and exact marker typing**
   - Public reconciliation result dataclasses must not default to success markers on failure.
   - `completed_work_id`, integration marker, and completed-work persisted marker should exist only after validated success or idempotent confirmation.
   - Success markers must be exact built-in `str` instances with exact values. Reject `str` subclasses, objects with custom equality, bytes-like values, and marker-looking wrappers even when `==` would pass; these can smuggle authorization through Python equality semantics.
   - Add adversarial regressions that construct a `str` subclass returning the right marker text and prove it does not authorize completed-work persistence, recovery success, integration markers, or `agent.completed` eligibility.

5. **Public lease-owner metadata**
   - Lease owner appears in public metadata, so accept only bounded safe identifiers such as `[A-Za-z0-9_.:-]` with a strict length cap.
   - Reject control characters, whitespace, shell/userinfo/traversal-looking strings, and credential-shaped text.

6. **No external side effects as executable proof**
   - Add a real recovery-batch test with bus, Linear, subprocess/quality/promotion hooks patched to raise if called.
   - This is stronger than source-string checks; it proves the recovery path itself does not publish completion-visible effects.

7. **Startup/watchdog ordering**
   - Prove startup recovery runs before new worker launches.
   - Prove watchdog recovery runs before later Linear/writeback or quality work.
   - Keep this as behavior tests, not only comments or handoff language.

8. **Authoritative runtime package resolution**
   - Supervisor/import bootstrap must prefer the executing repository or immutable release root and stop once a complete current package is found.
   - Do not allow later mutable worktrees, profile-script paths, `os.getcwd()` fallbacks, or live production checkouts to override the candidate/release package after import.
   - Add a fresh-process supervisor-file-alone regression that imports the supervisor from the candidate and asserts the queue/completed-work modules resolve from that same candidate/release root and expose the expected current API.

9. **Strict-valid legacy artifact handling**
   - A syntactically valid JSON packet embedded in legacy `RESULT.md` is still legacy/unvalidated unless canonical artifact provenance such as `AGY_RESULT_PACKET.json` is present and bound.
   - Recovery must not create completed-work rows, success markers, or terminal success state from strict-looking legacy Markdown alone.
   - Add a strict-valid legacy fixture that would pass JSON parsing but remains terminally ineligible with no completed-work database side effect.

10. **Immediate reconciliation exception boundary**
   - Immediate capture/reconciliation must share the same fail-closed, sanitized boundary as recovery/watchdog paths.
   - Storage/coordinator exceptions must not escape into public packets or leak raw exception text; the worker should return an unavailable/error classification that remains non-completing and requeueable as appropriate.

11. **Duplicate raw provenance immutability**
   - Duplicate raw-output IDs must preserve the original payload/provenance/locator and only retain allowed delivery-state/idempotency behavior.
   - Prefer `ON CONFLICT DO NOTHING` or equivalent immutable insert semantics for raw provenance; do not rewrite `received_at`, payload, source path, or locator on duplicate persistence after success.
   - Add a duplicate-persist test that tries to replace payload/provenance after a first insert and verifies the original row remains unchanged.

## Takeover discipline

If the producer result is `PARTIAL`, preserve the producer snapshot but treat it as untrusted. Repair the same exact task in place; do not launch the next issue while cap 1 is occupied. After every repair commit:

- rerun focused recovery tests and exact-scope lint/format delta;
- run canonical/release/build gates before PR claims;
- open/update the PR at the exact committed head;
- invalidate previous review evidence and request a fresh independent exact-head review;
- keep merge blocked until fresh review and exact-head CI are both clean.

## Proof packet addendum

```text
COMMAND=<focused race/retention/no-side-effect/startup tests + canonical/release/build + exact-head CI>
RESULT=<PASS|FAIL|BLOCKED>
SCOPE=raw-output-to-completed-work recovery semantic repair
AD_HOC_OR_CANONICAL=<focused suite|canonical suite|GitHub CI|ad-hoc targeted>
NOT_CLAIMING=live replay; external writeback; production supervisor switch; exactly-once global delivery
MARKER=AGY_COMPLETED_WORK_RECOVERY_RECONCILIATION_OK
```
