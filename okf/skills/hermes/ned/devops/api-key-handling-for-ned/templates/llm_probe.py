#!/usr/bin/env python3
"""
llm_probe.py — on-host health probe for an OpenAI-compatible model server.
Copy to the model host (e.g. /usr/local/bin/llm_probe.py, mode 644).

Usage:  python3 llm_probe.py <model> <port> <key_file>
Prints: HTTP:<status>  (plus exception class on transport failure)
Exit:   0 on 2xx, 2 if key file missing/unreadable, 3 on any other failure.

The key is read locally on the host and never crosses the SSH wire — this is
the fix for the "false 401 with the correct key" shell-quoting trap.
The Autobot watchdog (~/.hermes/profiles/autobot/scripts/llm_server_watchdog.py)
invokes this over SSH per TARGETS entry.
"""
import sys
import json
import urllib.request
import urllib.error


def main():
    model, port, key_file = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    try:
        key = open(key_file).read().strip().splitlines()[0]
    except OSError:
        print("HTTP:0")
        sys.exit(2)
    req = urllib.request.Request(
        "http://127.0.0.1:%d/v1/chat/completions" % port,
        data=json.dumps({"model": model,
                         "messages": [{"role": "user", "content": "ping"}],
                         "max_tokens": 1}).encode(),
        headers={"Content-Type": "application/json",
                 "Authorization": "Bearer " + key})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            r.read(100)
            print("HTTP:%d" % r.status)
            sys.exit(0 if 200 <= r.status < 300 else 3)
    except urllib.error.HTTPError as e:
        print("HTTP:%d" % e.code)
        sys.exit(0 if 200 <= e.code < 300 else 3)
    except Exception as e:
        print("HTTP:0 %s" % e.__class__.__name__)
        sys.exit(3)


if __name__ == "__main__":
    main()
