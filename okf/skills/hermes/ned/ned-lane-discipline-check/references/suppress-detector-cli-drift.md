---
title: suppress_class_detect.py CLI drift (2026-06-29)
---

## Symptom

The detector aborts before any check runs:

```
usage: suppress_class_detect.py [-h] --issues ISSUES --repo REPO
                                --cron-output-dir CRON_OUTPUT_DIR
                                [--include-linear]
suppress_class_detect.py: error: the following arguments are required: --repo, --cron-output-dir
```

## Cause

The script's argparse signature was tightened — `--repo` and `--cron-output-dir` are now **required**, not optional. The canonical recipe in SKILL.md §"Canonical recipe" originally showed them omitted; that example will now fail. Also: `LINEAR_API_KEY` is read from the inherited env, not from `--include-linear` (that flag just enables the GraphQL probe), so a missing env produces a `linear_state_audit.per_issue[].dequeue_count` of 0 for every issue, which makes the suppress check fail open as if the batch were eligible to execute.

## Working invocation

```bash
source /home/ubuntu/.hermes_env && python3 \
  ~/.hermes/profiles/ned/skills/ned-lane-discipline-check/scripts/suppress_class_detect.py \
  --issues "GRO-503,GRO-504,GRO-505,GRO-507,GRO-508,GRO-509,GRO-510,GRO-511,GRO-512,GRO-537" \
  --repo /home/ubuntu/work/prismatic-engine \
  --cron-output-dir /home/ubuntu/.hermes/profiles/ned/cron/output \
  --include-linear
```

Three required positional fixes:
1. `source /home/ubuntu/.hermes_env` BEFORE the python invocation (cron has no `.bashrc` early-exit path).
2. `--repo <prismatic-engine root>` — pass the actual checkout, not a placeholder.
3. `--cron-output-dir ~/.hermes/profiles/ned/cron/output` — needed for the `prior_cron_output_fresh` probe.

## When to suspect this drift

- Detector exits 2 with "the following arguments are required" → CLI drift, supply the flags.
- Detector runs but `checks.linear_state_audit.pass` is `false` with `dequeue_count: 0` everywhere → env not sourced, re-source `~/.hermes_env` and re-run.
- Detector runs and `checks.triage_doc_fresh.pass` is `false` with `reason: "no triage doc found in git log"` → freshness check failing open; the `prior_cron_output_fresh` probe is the co-equal gate and is what actually sustains SUPPRESS between triage-doc writes.

## What the script encodes (don't reinvent)

- The **4-of-4 5a.7a-bis check**: issue IDs match the recurring-batch signature, triage doc fresh, prior cron output fresh, Linear state audit clean.
- The **canonical GraphQL query shape** — do NOT use `labels(nodes:{first:10})` (schema footgun, see "Linear API footguns" in SKILL.md).
- The **freshness probes**: triage doc OR cron output must be <2-4h old.
- Output schema: `{suppress_eligible, verdict, finalize_mode, rationale, linear_state_audit}`.

## Invocation gotchas

- MUST invoke with `python3 <path>` (not `bash <path>` — the shebang doesn't fire when bash is the parent).
- `--issues` is comma-separated (not space-separated).
- `source /home/ubuntu/.hermes_env` is required BEFORE the python invocation in cron context.
