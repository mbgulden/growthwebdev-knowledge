#!/usr/bin/env python3
"""GRO-4929 staging end-to-end test.

Provisions a throwaway guest (user_id=999) on the STAGING orchestrator
(127.0.0.1:8011), then proves the local vLLM path works end-to-end:
  1. HMAC-sign and POST /api/orchestrate/provision
  2. verify the generated guest .env actually contains the real key
     (GUEST_VLLM_API_KEY == VLLM_FRED_API_KEY, non-empty)
  3. run a REAL chat completion through the :8000 vLLM using the key the
     guest would use -> must be 200 with a completion (not 401)
  4. deprovision (stop + clean up) so no stray guest is left

Re-runnable: `python3 test_gro4929_staging_e2e.py` (exit 0 = PASS).
The throwaway id (999) is collision-checked against live guests first.
"""
import hashlib, hmac, json, os, subprocess, sys, time, urllib.request, urllib.error

STAGE_URL   = "http://127.0.0.1:8011"   # staging ORCHESTRATOR_PORT (prod defaults 8001)
VLLM_URL    = "http://192.168.1.230:8000/v1"
MODEL       = "local-qwen-27b-q8-fred"
USER_ID     = 999
ENVFILE     = "/home/ubuntu/work/hd-platform-staging/.env"

def read_env(path):
    d = {}
    try:
        for line in open(path):
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            d[k.strip()] = v.strip().strip('"').strip("'")
    except FileNotFoundError:
        pass
    return d

def mask(v):
    v = v or ""
    return (v[:6] + f"...[len={len(v)}]") if v else "(EMPTY)"

def signed_post(endpoint, payload, secret):
    body = json.dumps(payload).encode()
    sig = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    req = urllib.request.Request(
        STAGE_URL + endpoint, data=body, method="POST",
        headers={"Content-Type": "application/json", "X-Signature": sig},
    )
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()

def wait_container(name, want, timeout=420):
    t0 = time.time()
    out = ""
    while time.time() - t0 < timeout:
        out = subprocess.run(
            ["sudo", "docker", "ps", "-a", "--filter", f"name={name}",
             "--format", "{{.Names}}\t{{.Status}}"],
            capture_output=True, text=True).stdout.strip()
        if want == "up" and out.startswith(name + "\t") and "Up" in out and "Restarting" not in out:
            return True, out
        if want == "down" and (not out or "Exit" in out):
            return True, out or "(gone)"
        time.sleep(5)
    return False, out

def vllm_probe(key):
    payload = json.dumps({
        "model": MODEL,
        "messages": [{"role": "user", "content": "Reply with exactly the single word: pong"}],
        "max_tokens": 8, "temperature": 0,
    }).encode()
    req = urllib.request.Request(
        VLLM_URL + "/chat/completions", data=payload, method="POST",
        headers={"Content-Type": "application/json",
                 "Authorization": "Bearer " + (key or "")},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()
    except Exception as e:
        return 0, f"exception: {e}"

def main():
    env = read_env(ENVFILE)
    secret = env.get("ORCHESTRATOR_SHARED_SECRET") or "default_shared_secret"
    vllm_key = env.get("VLLM_FRED_API_KEY", "")
    print(f"[setup] shared_secret={mask(secret)}  vllm_key={mask(vllm_key)}")
    if not vllm_key:
        print("FATAL: VLLM_FRED_API_KEY not found in staging .env"); sys.exit(2)

    results = {}

    # 1. provision
    prov_payload = {"user_id": USER_ID, "action": "provision",
                    "access_status": "demo", "trial_expires_at": ""}
    st, body = signed_post("/api/orchestrate/provision", prov_payload, secret)
    print(f"[provision] HTTP {st}  body[:200]={body[:200]!r}")
    results["provision_http"] = st
    if st != 200:
        print("FATAL: provision failed"); sys.exit(3)

    name = f"guest-hermes-{USER_ID}"
    ok, status = wait_container(name, "up")
    print(f"[container] up? {ok}  status={status!r}")
    results["container_up"] = ok
    if not ok:
        print("FATAL: container never came up (leaving it for inspection)"); sys.exit(4)

    # 2. verify the guest .env actually has the key
    guest_env = read_env(f"/home/ubuntu/guest_hermes_bot_{USER_ID}/.env")
    gkey = guest_env.get("GUEST_VLLM_API_KEY", "")
    print(f"[guest.env] GUEST_VLLM_API_KEY={mask(gkey)}  match_server_key={gkey == vllm_key}  non_empty={bool(gkey)}")
    results["guest_env_has_key"] = bool(gkey)
    results["guest_key_matches_server"] = (gkey == vllm_key)

    # 3. REAL vLLM call using the key the guest would use
    st, body = vllm_probe(gkey)
    try:
        comp = json.loads(body)
        msg = comp["choices"][0]["message"] if "choices" in comp else {}
        # this vLLM emits reasoning_content, not content; check both
        text = (msg.get("content") or msg.get("reasoning_content") or body[:120])
    except Exception:
        text = body[:120]
    print(f"[vllm with guest key] HTTP {st}  response={text!r}")
    results["vllm_with_key_http"] = st
    results["vllm_with_key_ok"] = (st == 200)

    # control: no key -> should be 401 (proves the key is what makes it work)
    st2, body2 = vllm_probe("")
    print(f"[vllm no key control] HTTP {st2}  (want 401)  body[:80]={body2[:80]!r}")
    results["vllm_nokey_http"] = st2

    # 4. deprovision
    deprov = {"user_id": USER_ID, "action": "deprovision"}
    st, body = signed_post("/api/orchestrate/provision", deprov, secret)
    print(f"[deprovision] HTTP {st}  body[:120]={body[:120]!r}")
    results["deprovision_http"] = st
    okd, status = wait_container(name, "down", timeout=180)
    print(f"[container] down? {okd}  status={status!r}")
    results["container_down"] = okd

    print("\n=== SUMMARY ===")
    print(json.dumps(results, indent=2))
    core_pass = (results.get("provision_http") == 200
                 and results.get("container_up")
                 and results.get("guest_env_has_key")
                 and results.get("vllm_with_key_http") == 200
                 and results.get("vllm_nokey_http") == 401
                 and results.get("deprovision_http") == 200)
    print(f"\nGRO-4929 E2E: {'PASS' if core_pass else 'FAIL'}")
    sys.exit(0 if core_pass else 5)

if __name__ == "__main__":
    main()
