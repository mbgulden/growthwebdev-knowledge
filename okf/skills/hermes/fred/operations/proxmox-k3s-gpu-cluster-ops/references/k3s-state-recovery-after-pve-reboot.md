# K3s state recovery after PVE reboot

Use this when PVE1 (or any host that boots a K3s-server VM) reboots and the
K3s server inside the VM comes back with an empty etcd database. All
namespaces, Deployments, Services, PVCs, and Secrets are gone. The host
filesystem (model files, ctr images, PV directory mounts) is intact.

**When this happens:**
- `kubectl get all -A` returns nothing
- `kubectl get nodes` may show the node as `NotReady` (no etcd)
- The VM is up, `ssh` works, `docker ps` works, but the cluster is empty
- Model files at `/models/` are intact
- ctr images at `/var/lib/rancher/k3s/agent/containerd/` are intact

**Five-step recovery recipe:**

1. **Recover the kubeconfig** (see SKILL.md step 6 for the full recipe):
   ```bash
   sshpass -p "$PVE_PASS" ssh -o HostKeyAlgorithms=+ssh-rsa root@<pve-ip> \
       "qm guest exec <vmid> -- bash -c 'cat /etc/rancher/k3s/k3s.yaml'" \
       > /tmp/k3s-raw.json 2>&1
   python3 -c "
   import json
   with open('/tmp/k3s-raw.json') as f:
       print(json.load(f)['out-data'], end='')
   " > /tmp/k3s.yaml
   sed -i 's|server: https://127.0.0.1:6443|server: https://<vm-lan-ip>:6443|' /tmp/k3s.yaml
   KUBECONFIG=/tmp/k3s.yaml kubectl get nodes
   ```

2. **Verify the host filesystem is intact** (what we have to work with):
   ```bash
   # Models
   sshpass -p "$PVE_PASS" ssh root@<pve-ip> \
       "qm guest exec <vmid> -- bash -c 'ls -la /models/qwen3.8-27b-q4/ /models/qwen3.8-27b-q5/'"
   # Should show Q4_K_M.gguf, Q5_K_M.gguf, mmproj-F16.gguf in each dir
   ```

3. **Verify ctr images are intact** (otherwise re-import):
   ```bash
   sshpass -p "$PVE_PASS" ssh root@<pve-ip> \
       "qm guest exec <vmid> -- bash -c 'ctr -n k8s.io images ls | grep -E llama-cuda'"
   ```
   If the images are gone, the tars at `/tmp/llama-cuda-v*.tar` are still
   on the host (or the local `/tmp/` on webtop-hermes). Re-import:
   ```bash
   # From webtop, HTTP server the tar first
   cd /tmp && python3 -m http.server 8766 --bind 0.0.0.0 --directory /tmp &
   # Then inside VM
   sshpass -p "$PVE_PASS" ssh root@<pve-ip> \
       "qm guest exec <vmid> -- bash -c 'cd /tmp && wget -q http://<hermes-ip>:8766/llama-cuda-v6.tar && ctr -n k8s.io images import llama-cuda-v6.tar'"
   ```

4. **Reapply the manifests** (the actual recovery):
   ```bash
   # Recreate the namespace + ServiceAccount
   KUBECONFIG=/tmp/k3s.yaml kubectl apply -f - <<EOF
   apiVersion: v1
   kind: Namespace
   metadata:
     name: llm-inference
   ---
   apiVersion: v1
   kind: ServiceAccount
   metadata:
     name: default
     namespace: llm-inference
   EOF

   # Reapply the PV (hostPath mounts)
   KUBECONFIG=/tmp/k3s.yaml kubectl apply -f - <<EOF
   apiVersion: v1
   kind: PersistentVolume
   metadata:
     name: qwen-models-hostpath
   spec:
     capacity:
       storage: 100Gi
     accessModes: [ReadOnlyMany]
     hostPath:
       path: /models
       type: Directory
     persistentVolumeReclaimPolicy: Retain
   EOF

   # Reapply the nvidia-device-plugin (CRITICAL — without it, no GPUs)
   KUBECONFIG=/tmp/k3s.yaml kubectl apply -f /tmp/nvidia-ds.yaml

   # Reapply each deployment (kai, ned, fred)
   KUBECONFIG=/tmp/k3s.yaml kubectl apply -f /tmp/kai-ned-llama.yaml
   KUBECONFIG=/tmp/k3s.yaml kubectl apply -f /tmp/newfred-llama.yaml
   ```

5. **Verify the cluster is healthy**:
   ```bash
   # GPUs registered
   KUBECONFIG=/tmp/k3s.yaml kubectl get nodes -o jsonpath='{.items[*].status.capacity}' | tr ' ' '\n' | grep nvidia
   # 3 pods running
   KUBECONFIG=/tmp/k3s.yaml kubectl get pods -n llm-inference -o wide
   # Endpoints respond
   KUBECONFIG=/tmp/k3s.yaml run -n llm-inference --rm -it --image=curlimages/curl --restart=Never -- \
       curl -s http://localhost:31002/health
   ```

**Common pitfalls:**

- **Forgetting the nvidia-device-plugin.** The deployments will be Pending
  with `Insufficient nvidia.com/gpu` until the device plugin is reapplied.
  Symptom: pods stuck in Pending indefinitely.
- **Image pull never finishes.** The Deployment needs `imagePullPolicy: Never`
  AND the image must be in ctr. If the image is gone, re-import (step 3).
- **PV hostPath mismatch.** If the PV's `hostPath.path` doesn't match the
  actual filesystem path, pods will mount empty directories and the model
  loader will fail with "No such file or directory". Verify with
  `kubectl describe pv` and `ls -la /models/<subdir>/` on the host.
- **Missing DeviceMode in the pod spec.** If you copy-paste from a working
  deployment, the `runtimeClassName: nvidia` must be at the **pod** level,
  not the container level. K3s v1.34 strict decoder rejects container-level
  runtimeClassName with a strange error.

**Manifest YAML preservation rule:** Store the recovery manifests in a
known location on webtop-hermes (e.g. `/tmp/llama-cuda-k8s-manifests/`).
The manifests are the source of truth for the recovery — if PVE1 reboots
again, the manifests are still on webtop-hermes and the recovery is one
`kubectl apply` away.

**Time to recover:** 5-10 minutes if the manifests are at hand. The slow
steps are the ctr import (if needed) and the model load on each pod after
restart (30-60s per pod).

**Why this is non-obvious:** the failure mode is silent. The VM is up, the
API server is reachable, `kubectl get nodes` returns the node. But `kubectl
get all -A` returns nothing. The agent that doesn't know this pattern will
spend time debugging "why are the pods gone" instead of "the K3s server
needs to be re-bootstrapped from the manifests."
