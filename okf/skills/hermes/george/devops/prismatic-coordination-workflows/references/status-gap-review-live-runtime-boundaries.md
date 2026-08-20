# Status/gap review: live runtime and merge-boundary proof

Use this when Michael asks whether George/Prismatic is “on track” or asks for current gaps after an event-driven slice.

## Durable pattern

1. Start from the current handoff, but treat it as a claim set to re-check, not as proof by itself.
2. Verify lightweight live state before answering:
   - UTC timestamp and handoff mtime/size.
   - Gateway health and dashboard HTTP status.
   - Any known intentionally absent route separately (for example OpenAPI 404) and label it as a discoverability/control-plane gap only if relevant.
3. Verify git boundary from the relevant worktree:
   - `origin/main` / remote merge commit.
   - local candidate `HEAD`.
   - tracked status versus untracked operator artifacts.
   - changed paths for the reviewed candidate.
4. Report in Michael’s preferred order: Problem → Changed → Why it matters → State → Next move → IDs/hashes/logs.
5. Use an explicit proof block with `AD_HOC_OR_CANONICAL=ad-hoc targeted verification` unless a canonical suite was actually run.

## Pitfalls

- Do not say `WORKTREE_CLEAN=true` when tracked files are clean but untracked operator artifacts exist, such as `.prismatic-task/*` or `STARTED.md`. Say `TRACKED_STATUS_CLEAN` and disclose untracked artifacts.
- Do not convert a merged test/design contract into production enforcement. If changed paths are test/docs only, boundary must say no hook/deployment/runtime mutation is claimed.
- Do not treat GitHub infrastructure no-run as CI proof. It can support a provider-neutral/local-proof merge boundary only when exact-head independent review and local archive proof are present.
- Do not admit another producer, deploy, restart, mutate cron/timers, or write Linear completion unless explicitly authorized for that specific next action.

## Compact status block template

```text
COMMAND=<date/stat + live HTTP + git boundary checks>
RESULT=<PASS_WITH_OPEN_GATES|PARTIAL|BLOCKED>
LOG=<paths or in-chat command output summary>
SCOPE=<handoff freshness, live route checks, exact merge/candidate boundary>
AD_HOC_OR_CANONICAL=ad-hoc targeted verification
NOT_CLAIMING=<deployment, production hook, canonical suite green, CI code execution, Linear write, etc.>
MARKER=<current handoff marker>
```
