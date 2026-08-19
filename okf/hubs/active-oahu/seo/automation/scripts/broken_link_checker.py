#!/usr/bin/env python3
"""Audit all internal links on the Active Oahu Tours static site - v3 final."""

import os
import re
import sys
from urllib.parse import urlparse

SITE_ROOT = "/home/ubuntu/work/active-oahu-tours-mirror/site"
DOMAIN = "activeoahutours.com"

def find_html_files(root):
    html_files = []
    for dirpath, dirnames, filenames in os.walk(root):
        if "_templates" in dirpath:
            continue
        for f in filenames:
            if f.endswith(".html"):
                full_path = os.path.join(dirpath, f)
                html_files.append(full_path)
    return sorted(html_files)

def extract_hrefs(filepath):
    hrefs = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
    except Exception as e:
        print(f"ERROR reading {filepath}: {e}", file=sys.stderr)
        return hrefs

    pattern = r'<a[^>]*?\s+href\s*=\s*["\']([^"\']+)["\']'
    matches = re.findall(pattern, content, re.IGNORECASE)
    pattern2 = r'<a[^>]*?\s+href\s*=\s*([^\s>"\']+)'
    matches2 = re.findall(pattern2, content, re.IGNORECASE)
    
    all_hrefs = list(set(matches + matches2))
    for href in all_hrefs:
        href = href.strip()
        if href:
            hrefs.append(href)
    return hrefs

def should_skip(href):
    if not href or href.startswith("#") or href.startswith("mailto:") or href.startswith("tel:") or href.startswith("javascript:"):
        return True
    if "wp-content/" in href or "/wp-content" in href:
        return True
    if "/cdn-cgi/l/email-protection" in href:
        return True
    if href.startswith("http://") or href.startswith("https://"):
        parsed = urlparse(href)
        if parsed.netloc and DOMAIN not in parsed.netloc and "activeoahutours" not in parsed.netloc:
            return True
    return False

def strip_anchor(url):
    return url.split("#")[0] if "#" in url else url

def resolve_link(href, base_dir, site_root):
    # Handle full URLs with our domain
    if href.startswith("http://") or href.startswith("https://"):
        parsed = urlparse(href)
        path = parsed.path
        if not path or path == "/":
            path = "/index.html"
        href = path
    
    href = strip_anchor(href)
    if not href:
        return None
    
    if href.startswith("/"):
        resolved = os.path.join(site_root, href.lstrip("/"))
    else:
        resolved = os.path.normpath(os.path.join(base_dir, href))
    
    resolved = os.path.normpath(resolved)
    return resolved

def check_target(resolved_path):
    """Check if the target exists. Handles various URL-to-file mappings."""
    if not resolved_path:
        return False
    
    resolved_path = os.path.normpath(resolved_path)
    
    # Direct file exists
    if os.path.exists(resolved_path):
        return True
    
    # If it's a directory, check for index.html inside
    if os.path.isdir(resolved_path):
        return os.path.exists(os.path.join(resolved_path, "index.html"))
    
    # Try with trailing / + index.html (for directory-style paths)
    if not resolved_path.endswith(".html"):
        if os.path.exists(resolved_path + "/index.html"):
            return True
        if os.path.exists(resolved_path + ".html"):
            return True
        # Also try as directory
        if os.path.isdir(resolved_path):
            return os.path.exists(os.path.join(resolved_path, "index.html"))
    
    # If path ends with /, try index.html
    if resolved_path.endswith("/") or resolved_path.endswith("/index.html"):
        alt = resolved_path.rstrip("/")
        if os.path.exists(alt):
            return True
        if os.path.exists(alt + ".html"):
            return True
    
    # If path ends with /index (no .html), try /index.html
    if resolved_path.endswith("/index"):
        if os.path.exists(resolved_path + ".html"):
            return True
        if os.path.exists(resolved_path):
            return True
    
    return False

def main():
    html_files = find_html_files(SITE_ROOT)
    print(f"Found {len(html_files)} HTML files to check")
    
    total_links = 0
    broken_links = []
    skipped_count = 0
    
    for filepath in html_files:
        rel_path = os.path.relpath(filepath, SITE_ROOT)
        base_dir = os.path.dirname(filepath)
        
        hrefs = extract_hrefs(filepath)
        unique_hrefs = list(set(hrefs))
        
        for href in unique_hrefs:
            if should_skip(href):
                skipped_count += 1
                continue
            
            total_links += 1
            resolved = resolve_link(href, base_dir, SITE_ROOT)
            
            if resolved is None:
                continue
            
            if not check_target(resolved):
                broken_links.append((rel_path, href))
    
    broken_links = list(set(broken_links))
    broken_links.sort()
    
    # Output
    print(f"\n{'='*65}")
    print(f"  LINK AUDIT SUMMARY")
    print(f"{'='*65}")
    print(f"  Total HTML files checked:  {len(html_files)}")
    print(f"  Total internal links:      {total_links}")
    print(f"  Links skipped (ext/etc):   {skipped_count}")
    print(f"  Total broken links:        {len(broken_links)}")
    print(f"{'='*65}\n")
    
    if broken_links:
        broken_by_page = {}
        for page, url in broken_links:
            if page not in broken_by_page:
                broken_by_page[page] = []
            broken_by_page[page].append(url)
        
        print("BROKEN LINKS (grouped by page):")
        for page in sorted(broken_by_page.keys()):
            print(f"\n  FILE: /{page}")
            for url in broken_by_page[page]:
                print(f"    -> BROKEN LINK: {url}")
    
    # Write report
    output_path = "/home/ubuntu/broken_links_report_v3.txt"
    with open(output_path, "w") as f:
        f.write(f"LINK AUDIT SUMMARY\n")
        f.write(f"{'='*65}\n")
        f.write(f"Total HTML files checked: {len(html_files)}\n")
        f.write(f"Total internal links: {total_links}\n")
        f.write(f"Links skipped (ext/etc): {skipped_count}\n")
        f.write(f"Total broken links: {len(broken_links)}\n")
        f.write(f"{'='*65}\n\n")
        
        if broken_links:
            broken_by_page = {}
            for page, url in broken_links:
                if page not in broken_by_page:
                    broken_by_page[page] = []
                broken_by_page[page].append(url)
            
            for page in sorted(broken_by_page.keys()):
                f.write(f"\nFILE: /{page}\n")
                for url in sorted(broken_by_page[page]):
                    f.write(f"  -> BROKEN LINK: {url}\n")
        
        f.write(f"\n{'='*65}\n")
        f.write(f"END OF REPORT\n")
    
    print(f"\nReport saved to: {output_path}")
    return 1 if broken_links else 0

if __name__ == "__main__":
    sys.exit(main())
