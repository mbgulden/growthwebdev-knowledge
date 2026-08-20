# Allowlisted Linear exporter normalized output shape

Use this reference when consuming exports from `/home/ubuntu/.hermes/profiles/george/scripts/linear_read_export_allowlisted.py`.

## Current invocation shape

The exporter is intentionally non-executable; invoke it through Python. For one parent, pass `--parent <ID>`:

```bash
umask 077
mkdir -p /home/ubuntu/.hermes/profiles/george/private/linear-exports
python3 /home/ubuntu/.hermes/profiles/george/scripts/linear_read_export_allowlisted.py \
  --parent GRO-4263 \
  > /home/ubuntu/.hermes/profiles/george/private/linear-exports/GRO4263_FRESH_<timestamp>.json
chmod 600 /home/ubuntu/.hermes/profiles/george/private/linear-exports/GRO4263_FRESH_<timestamp>.json
```

For all approved parents, use `--all`.

## Normalized schema notes

The exporter returns normalized JSON, not raw GraphQL connection objects:

```text
root.ok=true
root.read_only=true
root.parents=[...]
parent.children=[issue, ...]
issue.labels=["label-name", ...]
issue.state={"id":"...","name":"...","type":"..."}
issue.relations=[...]
```

Do not assume labels are objects with `name` fields. Consumers should accept labels as strings, and only tolerate dict labels defensively when reading older artifacts.

## Safe summarizer pattern

```python
import json
payload = json.load(open(export_path))
assert payload.get("ok") is True
assert payload.get("read_only") is True
for parent in payload["parents"]:
    for child in parent.get("children", []):
        labels = [v if isinstance(v, str) else v.get("name", "") for v in child.get("labels", [])]
        state = child.get("state", {})
        state_name = state.get("name", "") if isinstance(state, dict) else str(state)
        print(child["identifier"], state_name, sorted(labels))
```

## Pitfall

If shell redirection fails because the private output directory does not exist, no credentialed request may have been made. Create the restricted directory first, then rerun the read-only export. Treat failed CLI invocation artifacts, including empty redirected files, as non-evidence.
