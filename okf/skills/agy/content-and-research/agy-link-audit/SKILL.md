---
name: agy-link-audit
description: Scan, parse, and verify URL links in site documents or markdown pages.
version: 1.0.0
---

# AGY Link Audit

Scan documents and codebases, extract URLs, verify responses, and report dead links.

## Trigger Conditions

Use when auditing documentation, validating website links, or prepping articles for release.

## Numbered Steps with Exact Commands

1. **Find files containing URLs**:
   ```bash
   rg -o "https?://[a-zA-Z0-9./?=&_-]+" --glob "*.md"
   ```

2. **Run link auditor script**:
   Save a Python script to check URLs:
   ```python
   # /home/ubuntu/.gemini/antigravity-cli/scratch/check_links.py
   import urllib.request
   import sys
   
   urls = sys.argv[1:]
   for url in urls:
       try:
           req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
           with urllib.request.urlopen(req, timeout=5) as r:
               print(f"{url} -> OK ({r.status})")
       except Exception as e:
           print(f"{url} -> BROKEN ({e})")
   ```
   Execute it:
   ```bash
   python3 /home/ubuntu/.gemini/antigravity-cli/scratch/check_links.py "https://google.com" "https://broken-link-example-xyz.com"
   ```

3. **Report results**:
   Write the output list to `/tmp/link-report.txt` and reference it in artifacts.

## Pitfalls

- **Network timeouts**: Set a strict timeout (e.g. 5s) on requests to avoid infinite hangs.
- **User-Agent blocking**: Many websites return 403 to default Python urllib user agents. Always set a browser User-Agent header.

## Verification Steps

- Verify output text lists broken links clearly:
  ```bash
  cat /tmp/link-report.txt
  ```
