# Journal Collector: Runtime Skew and Stale-Log Repair

## Symptom pattern
A scheduled journal snapshot reports old incidents as current even though the source log files have recent mtimes. It may also emit Git “commits” or “dirty files” whose value is actually `fatal: not a git repository` stderr.

## Root cause to distinguish
1. **Head-read log parsing:** collector reads the first N bytes of an append-only log. A current file mtime therefore exposes old entries at the file head.
2. **No event timestamp gate:** parser treats matching text anywhere in the sampled content as current.
3. **Git stderr treated as data:** a failed Git command returns stderr, then telemetry code promotes that string into journal events.
4. **Runtime/package skew:** the installed module invoked by the scheduler differs from the repository source; source-only fixes do not change live cron behavior.

## Repair pattern
- Identify the executable’s imported runtime module, not only a repository candidate.
- Make log extraction read a tail window, discard any initial partial line, parse timestamps, and retain only a bounded reporting window (normally 24h).
- Keep genuinely current error detection; fixture-test an old error plus a current error together.
- Make Git helpers return an empty value for non-zero exit (or at minimum recognised non-repository stderr). Never turn stderr into telemetry.
- If the current journal artifacts are already polluted, preserve a timestamped source-manifest backup, rebuild only the current generated inbox/index, run the cron through the scheduler, and assert stale markers and `git_*` events are absent.
- Mark a direct runtime patch as a temporary bridge and promote it into the canonical package/release path afterwards; package upgrades can replace it.

## Focused verifier
Assert all of:
- old timestamped error is excluded;
- current timestamped error is retained;
- non-repository Git probes return no telemetry;
- runtime module compiles;
- a fresh scheduler run is `ok` and the rebuilt artifact excludes stale markers.

Scope wording: **ad hoc targeted verification**, not canonical-suite green.
