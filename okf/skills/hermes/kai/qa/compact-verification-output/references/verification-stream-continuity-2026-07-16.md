# Verification stream continuity — 2026-07-16

## Problem

Michael observed that detector/verifier runs can consume the assistant stream and cause the actual final handoff message to be incomplete or drowned in logs. This showed up during Prismatic/Fred handoffs where `/tmp/hermes-verify-*` output and test output were useful for detectors but bad for conversational continuity.

## Durable rule

Verification must use two channels:

1. **Machine/log channel:** detailed stdout/stderr goes to `/tmp/<agent>-<issue>-verify.log` or a durable artifact.
2. **Conversation/Linear channel:** only a compact proof packet is posted.

The human-facing answer must come **after** the compact verification block, so detector output does not replace the final explanation.

## Required compact proof fields

```text
COMMAND=<exact command or grouped command summary>
RESULT=<PASS|FAIL|BLOCKED>
LOG=<path to detailed log or "not needed">
SCOPE=<files/features verified>
AD_HOC_OR_CANONICAL=<ad-hoc targeted|canonical suite>
NOT_CLAIMING=<explicit non-claims>
MARKER=<required marker>
```

## Prompt insertion rule

Any Fred/Ned/AGY/Kai prompt that asks for tests, browser proof, route probes, Lighthouse, builds, or detector markers should include the verification-output-discipline block directly. Do not rely on memory alone.

## Pitfall

Do not ask agents to paste full pytest/curl/browser/systemctl logs into chat unless the user explicitly asks. A one-line failure summary + log path is enough for normal workflow.
