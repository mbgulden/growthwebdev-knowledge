# Infrastructure Health Sweep — <DATE>

## GPU
- **GPU Tailscale Node (100.78.237.7)**: [Healthy/Unhealthy] (Ping: <packet loss>%, Latency: <ms>)
- **GPU LAN Node (192.168.1.230)**: [Healthy/Unhealthy] (Ping: <packet loss>%)
- **Ollama API Status (http://100.78.237.7:31434/api/tags)**: [Healthy/Unhealthy] (HTTP: <status_code>, Model Registry: <non-empty JSON/empty body>)
- **ZFS & Storage Plan (PVE6 Host)**: <status/ZFS pools size/NVMe activation/capacity>

## Disk
- **Local Disk Usage (/)**: <Usage %> (df -h / output: `<output>`)
- **NAS Mount Status (/home/ubuntu/mounts/synology-photo/)**: [Healthy/Unhealthy] (File count: <count>)
- **Database File Sizes**:
  - `event_router.db`: <size> (VACUUM status: <reclaimed/not reclaimed>)

## GitHub
- **API Connectivity & Status**: [Healthy/Unhealthy]
- **Uncommitted WIP / Working Tree Check**: [Clean/Dirty]
- **Branch/PR Status**: <active branches, PR build checks>

## CF (Cloudflare)
- **Cloudflare Pages / DNS Health**:
  - `growthwebdev.com`: dns=[OK/Fail] http=[HTTP_code] https=[HTTP_code] -> Status: [Healthy/Unhealthy/Not a finding]
  - `belief-deprogrammer.com`: dns=[OK/Fail] http=[HTTP_code] https=[HTTP_code] -> Status: [Healthy/Unhealthy/Not a finding]
  - `beyondsaas.com`: dns=[OK/Fail] http=[HTTP_code] https=[HTTP_code] -> Status: [Healthy/Unhealthy/Not a finding]
- **CF Tunnel Status**: [Healthy/Unhealthy/Dashboard Check Needed]

## Swarm Agents
- **Gateway Process (ps -ef | grep gateway)**: [Running/Stopped]
- **Active Swarm Nodes**: <list of active/inactive agent IDs>
- **Cascade-Kill / Sibling State Check**: [No issues / Cascade kill detected]

## Cron Health
- **Cron Dequeue Activity**: <active/stale>
- **Heartbeat & Silent Detector State**:
  - Last Heartbeat Timestamp: <timestamp>
  - Silent-Watchdog Status: [Healthy/Failing]
