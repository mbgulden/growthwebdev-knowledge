# HDE guide-neutral deconditioning runtime — 2026-07-15

## Session learning

Michael corrected an important architecture leak: “George” is only a working/persona name, not the bot architecture. HDE customer guide runtimes must be guide-neutral and configurable.

## Durable rule

Do not hardcode `George` into guest runtime prompts, canaries, docs, or workflow language except when explicitly discussing one user-selected guide name or a legacy reference. Prefer:

- `guide`
- `guide_name`
- `Guide Constitution`
- `Guide Culture`
- `Guide Freedoms`
- “needing the guide less”

Runtime prompt identity should be configurable:

```python
guide_name = (
    os.getenv("GUEST_GUIDE_NAME")
    or os.getenv("HDE_GUIDE_NAME")
    or "the user's Human Design guide"
).strip()
```

Prompt identity:

```text
You are {guide_name} inside Human Design Engine Sanctuary.
Reply as {guide_name} in plain text.
```

## Belief-work capstone

The missing layer was explicit **Graceful Deconditioning + Belief Work**:

- identify inherited/conditioned beliefs,
- treat survival patterns as old protection, not personal failure,
- name the loop without shame,
- identify the protective belief,
- respect why it formed,
- show the cost of keeping it,
- offer a practical/testable replacement belief,
- give one small real-world experiment,
- close toward self-trust and needing the guide less.

Add `belief_work` as a prompt-native creative tool handle next to `pattern_read`, `experiment_builder`, and `authority_check`.

## Verification pattern

The HDE guest canary should guard both behavior and prompt contract:

- template deployed to live guest runtime,
- `Guide Constitution/Culture/Freedoms` markers present,
- take-the-swing / uncertainty etiquette / consentful depth present,
- Graceful Deconditioning + Belief Work markers present,
- `belief_work` handle present,
- no hardcoded `George` literal in the guest runtime,
- non-George greeting such as `Hi Ember` works,
- full guest canary passes.

For repeated verification nudges, rerun a fresh `/tmp/hermes-verify-*` script using `tempfile.mkstemp`, remove it, and call it focused ad-hoc verification.

## Documentation destination

For this class of work, update both:

1. Belief Deprogrammer OKF for durable methodology/source-map notes.
2. HDE/humandesignengine.com docs for operational workflow and deployment/canary commands.
