# Security audit pattern for public-ready repos

When shipping a repo (LLM compression, model serving, anything) for public release on GitHub/HuggingFace/etc., run this audit before tagging v1. The class of work: producing an artifact that is clean of credentials, internal hosts, user paths, and other sensitive material that should not leak. Built from the 2026-08-15 review of `/tmp/qwen-quantize/` (the W4A16 quantization repo) before any potential public release.

## The 10 categories of "should-not-be-public"

A repo is safe to publish only if it passes these 10 categories:

1. **No hardcoded API tokens** — patterns: `sk-...`, `sk-ant-...`, `ghp_...`, `gho_...`, `hf_...`, `xai-...`, `AIza...`, `ya29...`, `AKIA...`, `-----BEGIN ... PRIVATE KEY-----`
2. **No hardcoded credentials** — patterns: `password="..."`, `passwd="..."`, `root@<letter>`, `sudo `, `sshpass -p`
3. **No private/internal IP addresses** — patterns: `192.168.x.x`, `10.x.x.x` (172.16-31.x.x is too broad to scan). Allow `0.0.0.0` (default bind address is fine).
4. **No user paths** — patterns: `/home/<user>/`, `.env`, `secrets.yaml|yml|json|toml`, `credentials.json|yaml|yml`
5. **No personal info** — patterns: emails (`@...com|org|net|io`), user mentions (e.g. `mbgulden`, `fred@`, `ned@`, `kai@`, `orchestrator@`)
6. **No hidden files** — except intentional `.gitignore`. Look for `.env`, `.git/`, `__pycache__/`, etc.
7. **No long alphanumeric strings** — 40+ char strings are potential tokens. Allow: hashes, config keys, template variables, model dimensions (`vocab_size`, `hidden_size`, etc.)
8. **Standard project hygiene** — has README, requirements.txt, .gitignore, no `__pycache__/`
9. **License clarity** — README mentions the license (e.g. Apache 2.0)
10. **`.gitignore` quality** — excludes `.env`, `secrets.yaml`, `credentials.json`, `__pycache__/`, model files (`*.safetensors`, `*.gguf`)

## The verifier pattern (10 sections, ~30 checks)

```python
SECRET_PATTERNS = [
    (r"sk-[a-zA-Z0-9]{20,}", "OpenAI API key"),
    (r"sk-ant-[a-zA-Z0-9]{20,}", "Anthropic API key"),
    (r"ghp_[a-zA-Z0-9]{20,}", "GitHub personal token"),
    (r"gho_[a-zA-Z0-9]{20,}", "GitHub OAuth token"),
    (r"hf_[a-zA-Z0-20]{20,}", "HuggingFace token"),
    (r"xai-[a-zA-Z0-9]{20,}", "xAI API key"),
    (r"AIza[0-9A-Za-z\-_]{35}", "Google API key"),
    (r"ya29\.[0-9A-Za-z\-_]{20,}", "Google OAuth token"),
    (r"AKIA[0-9A-Z]{16}", "AWS access key"),
    (r"-----BEGIN [A-Z]+ PRIVATE KEY-----", "Private key"),
]
# Plus CRED_PATTERNS, IP_PATTERNS, PATH_PATTERNS, PERSONAL_PATTERNS
# See /tmp/hermes-verify-qwen-clean-stable.py for the full working implementation
```

Each section scans all files in the repo, prints PASS/FAIL/SKIP per check, and exits non-zero if any FAIL. The `.gitignore` should be **excluded** from the user-paths/secrets scan (it intentionally lists these patterns as things to exclude).

## Common false positives to handle

- **`token` substring** — `tokenizer`, `tokenizer.apply_chat_template`, `num_speculative_tokens`, `HF_TOKEN` env var (correct — user-supplied, not hardcoded) — these are legitimate uses of the word "token", not leaked credentials
- **`0.0.0.0`** — only matches in `HOST` defaults; this is correct for vLLM/llama-server binding
- **`secrets.yaml` etc. in `.gitignore`** — the `.gitignore` file itself lists these as things to exclude, which is the correct behavior; exclude `.gitignore` from the path-patterns scan

## Companion pattern: the `.gitignore` template

Add this to any repo being prepared for public release:

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
 lib64/
parts/
sdist/
var/
wheels/
*.egg-info/

# Virtual environments
venv/
ENV/
env/
.venv

# Editor / IDE
.vscode/
.idea/
*.swp
*.swo
.DS_Store

# Test / coverage
.pytest_cache/
.coverage
htmlcov/
.tox/
.cache

# Secrets — NEVER commit
.env
.env.local
.env.*.local
*.pem
*.key
secrets.yaml
secrets.yml
credentials.json
hf_token.txt

# Model files
output/
checkpoints/
*.safetensors
*.bin
*.gguf
*.pt
*.pth
*.onnx

# Calibration data
calibration_data/
*.parquet
*.arrow

# Logs
*.log
logs/
```

## When this audit applies

- The user says "make sure the repo is clean", "is it ready to publish", "scan for secrets", or "anything sensitive in there?"
- A new repo is being prepared for public release on GitHub
- Before pushing to a public HuggingFace repo
- After a major refactor that touched configuration files

## When NOT to use this audit

- Private/internal repos that will never be public — different threat model
- For verifying internal credentials (use `gitleaks` or `trufflehog` instead — they have full secret-detection databases)
- As a CI gate (this audit is manual review; for CI, use a real secret scanner)

## Companion skills

- `verifier-as-deliverable-discipline` — the verifier is part of the deliverable. The security audit script IS the audit's evidence.
- `prismatic-evidence-handling` — the broader discipline of treating `/tmp/hermes-verify-*` post-edit proof as mandatory
- `references/llm-compression-repos-2026-08-15.md` — the recipe this audit was built against (the W4A16 quantization repo)
