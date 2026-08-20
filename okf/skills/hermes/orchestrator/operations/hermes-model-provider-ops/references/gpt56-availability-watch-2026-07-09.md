# GPT-5.6 availability watch pattern — 2026-07-09

## Trigger

Michael expected GPT-5.6 variants to land and wanted Hermes to scream when any target became visible in the authenticated model/provider lists.

Targets used:

```text
gpt-5.6
gpt-5.6-sol
gpt-5.6-terra
gpt-5.6-luna
```

## Implementation pattern

- Script location: active profile `scripts/`, e.g. `/home/ubuntu/.hermes/profiles/orchestrator/scripts/gpt56_availability_watch.py`.
- Schedule: `every 3h`.
- Cron mode: `no_agent=True` so empty stdout stays silent.
- State file: active profile `state/`, e.g. `state/gpt56_availability_watch.json`.
- Data source: refreshed Hermes provider model cache/catalog; treat public release notes as secondary context only.

## Matching rules

Normalize model strings before comparison:

- lowercase
- strip provider prefix after `/`
- convert non-alphanumeric separators to `-`
- collapse variants so these all match appropriately:
  - `openai/gpt-5.6-sol`
  - `GPT 5.6 Sol`
  - `gpt_5_6_terra`
  - `gpt-5-6-luna`

## Verification contract

Create a temporary verifier with a `hermes-verify-` prefix under `/tmp` and clean it up. Cover:

```text
py_compile=passed
normalization_variants=gpt-5.6,sol,terra,luna passed
absent_detection=silent_no_hits
present_detection=base,sol,terra,luna passed
escalation_message=it’s_here_to_ITS_HERE passed
real_smoke_run=exit0 last_result=absent|present
cron_job=<id> every_3h origin enabled
cleanup_exists=false
```

Label the result as ad hoc targeted verification, not suite green.
