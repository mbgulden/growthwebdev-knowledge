---
name: llmcompressor-ignore-regex-prefix
description: Critical gotcha for llmcompressor 0.13.0+ ignore patterns. Bare regex strings are matched as exact substrings and silently never match any module name. Always prefix with "re:" to actually use regex matching. Symptom and verification recipe included.
---

# llmcompressor 0.13.0+ Ignore Pattern Gotcha

## Symptom

You write a quantization recipe with ignore patterns like:

```python
GPTQModifier(
    targets="Linear",
    ignore=[
        r"visual\..*",
        r".*linear_attn\..*",
        r".*mtp_layer.*",
    ],
    ...
)
```

You launch the quantization. Logs show "Applying quantization config: N/N" with a large N (e.g., 768 modules for a 27B hybrid model). You expect maybe 60-80 modules to be quantized after exclusions.

**The ignore patterns are silently not matching anything.**

## Root Cause

In llmcompressor 0.13.0, the `ignore` parameter (and `targets`) supports two matching modes:

1. **Exact substring match** (default): `"linear_attn.in_proj_qkv"` matches only that exact string
2. **Regex match**: requires the `re:` prefix

Plain Python regex strings like `r"visual\..*"` are treated as **exact literal strings**, not regex. So `r"visual\..*"` tries to match the literal string `visual\..*` (with a backslash) against module names — never matches.

The matching happens in `llmcompressor/utils/matching.py:match_name()`:
```python
if target.startswith("re:"):
    return re.match(target.removeprefix("re:"), name) is not None
else:
    return target == name
```

## Fix

Prefix every regex pattern with `"re:"`:

```python
GPTQModifier(
    targets="Linear",
    ignore=[
        "re:visual\..*",           # NOT r"visual\..*"
        "re:model\.layers\.\d+\.linear_attn\..*",
        "re:.*mtp_layer.*",
        "lm_head",                 # exact match is fine for plain names
    ],
    ...
)
```

Literal module names without regex special chars (e.g., `"lm_head"`, `"embed_tokens"`) work fine without the prefix.

## Verification Recipe

After launching quantization, check the log for these markers:

1. **Module count in calibration loop:** `(1/N): Calibrating` — N should match what you expect (e.g., 65 modules for a hybrid 27B model with proper exclusions, not 768+).

2. **SequentialPipeline inferred:** `Inferred SequentialPipeline for GPTQModifier` confirms the recipe was applied.

3. **`Applying quantization config: M/M`** — M is the total modules matching the recipe's `targets`. If M is way larger than expected, the exclusions are not working.

4. **`Found N offset-norm modules to convert`** — RMSNorm layers found. If this number is way off, something is wrong.

## Real-World Numbers (Qwen 3.8 27B)

- **Without `"re:"` prefix:** 768+ modules in config_groups, all quantized including DeltaNet
- **With `"re:"` prefix:** 497 modules in config_groups, only 65 actually calibrated (DeltaNet, vision, MTP, embed_tokens, lm_head all correctly excluded)

## When in Doubt

Test patterns in Python first:

```python
from llmcompressor.utils.matching import match_name

# Should return True
match_name("re:visual\..*", "visual.blocks.0.attn.qkv")
match_name("re:.*linear_attn.*", "model.layers.5.linear_attn.in_proj_qkv")

# Will return False (no re: prefix)
match_name(r"visual\..*", "visual.blocks.0.attn.qkv")
```

## Related

- Applies to both `targets` and `ignore` parameters
- Same prefix convention used elsewhere in llmcompressor (e.g., `target_ids`)