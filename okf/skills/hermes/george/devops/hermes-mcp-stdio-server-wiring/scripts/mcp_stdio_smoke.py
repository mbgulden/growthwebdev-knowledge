#!/usr/bin/env python3
"""Generic stdio MCP smoke test — no Hermes required.

Speaks raw JSON-RPC over the server's stdio transport:
  initialize -> notifications/initialized -> tools/list -> optional tools/call

Usage:
  mcp_stdio_smoke.py <server.py path> <python path> [tool_name arg1=... arg2=...]
Example:
  mcp_stdio_smoke.py ~/work/okf-mcp-server/server.py \
      /home/ubuntu/.local/share/pipx/venvs/hermes-agent/bin/python \
      search query=linear rate limit

Exit 0 = all checks pass; prints a [PASS]/[FAIL] line per check.
"""
import json
import subprocess
import sys
import time


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    server_path, py = sys.argv[1], sys.argv[2]
    tool_call = None
    if len(sys.argv) >= 4:
        name = sys.argv[3]
        args = {}
        for a in sys.argv[4:]:
            k, _, v = a.partition("=")
            # numeric coercion keeps schemas happy
            args[k] = int(v) if v.lstrip("-").isdigit() else v
        tool_call = (name, args)

    proc = subprocess.Popen(
        [py, server_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    def send(payload: dict) -> None:
        proc.stdin.write(json.dumps(payload) + "\n")
        proc.stdin.flush()

    def recv(expect_id, deadline=30.0):
        """Read lines until the response for expect_id (or any error)."""
        end = time.time() + deadline
        while time.time() < end:
            line = proc.stdout.readline()
            if not line:
                if proc.poll() is not None:
                    raise RuntimeError(
                        f"server exited early ({proc.returncode}): "
                        + (proc.stderr.read() or "")[:2000]
                    )
                continue
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                raise RuntimeError(f"non-JSON on stdout (protocol pollution): {line[:200]}")
            if isinstance(msg, dict) and msg.get("id") == expect_id:
                return msg
        raise RuntimeError(f"no response for id={expect_id} within {deadline}s")

    ok = True

    def check(label: str, cond: bool, detail: str = "") -> None:
        nonlocal ok
        mark = "PASS" if cond else "FAIL"
        if not cond:
            ok = False
        print(f"[{mark}] {label}" + (f" :: {detail[:300]}" if detail else ""))

    try:
        # 1. initialize
        send({"jsonrpc": "2.0", "id": 1, "method": "initialize",
              "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                         "clientInfo": {"name": "smoke", "version": "0"}}})
        init = recv(1)
        check("initialize", "result" in init and "serverInfo" in init.get("result", {}),
              json.dumps(init.get("result", {}).get("serverInfo", {})))

        # 2. initialized notification
        send({"jsonrpc": "2.0", "method": "notifications/initialized"})

        # 3. tools/list
        send({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
        tools = recv(2)
        names = [t["name"] for t in tools.get("result", {}).get("tools", [])]
        check("tools/list", len(names) > 0, f"{len(names)} tools: {', '.join(names)}")

        # 4. optional tools/call
        if tool_call:
            name, args = tool_call
            send({"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                  "params": {"name": name, "arguments": args}})
            res = recv(3)
            content = res.get("result", {}).get("content", [])
            text = "".join(c.get("text", "") for c in content if c.get("type") == "text")
            is_err = res.get("result", {}).get("isError", False) or "error" in res
            check(f"tools/call {name}", (not is_err) and len(text) > 0,
                  text[:200] if text else json.dumps(res)[:200])
    except Exception as exc:  # noqa: BLE001 — report, don't crash the report
        check("exception", False, repr(exc))
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()

    print("RESULT=" + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
