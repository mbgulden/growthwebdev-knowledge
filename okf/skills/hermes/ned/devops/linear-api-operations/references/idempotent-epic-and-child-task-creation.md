# Idempotent Epic + Child Task Creation (PWP Provisioning Pattern)

## When to use

You're spinning up a multi-task initiative in Linear (an "epic" with
several child issues). You need the script to be **safe to re-run**:
running it twice must not create duplicate epics or duplicate children.

This is the pattern used to bootstrap the `PE-KPI-FUNNEL` epic (GRO-4356
+ GRO-4357..GRO-4366) and is reusable for any future multi-issue Linear
initiative from Ned / PE / HF workflows.

## The four-step pattern

```text
1. Probe the API key + viewer + team(s) + labels
2. Find-or-create the parent epic (search by title fragment + type:epic label)
3. For each child:
     a. Find existing child by exact title under the parent
     b. If found → skip (or add a "re-submitted" comment)
     c. If not → create with parentId = epic.id, labelIds = [...]
4. Persist a local mapping (epic_id + child_id) so the next run can re-use it
```

## Code skeleton

```python
import json, os, urllib.request

TOKEN = os.environ["LINEAR_API_KEY"]  # already sourced
TEAM_ID = os.environ.get("LINEAR_TEAM_ID", "b6fb2651-...epic-id-here...")
API_URL = "https://api.linear.app/graphql"

def graphql(query, variables=None):
    body = {"query": query, "variables": variables or {}}
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "Authorization": TOKEN},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())

def find_existing_issue_by_title(team_id, title, parent_id=None):
    """Find issue by case-insensitive title, optionally scoped to parent."""
    issues = graphql("""
      query($id: ID!) {
        issues(filter: { team: { id: { eq: $id } } }, first: 100) {
          nodes { id identifier title state { name } }
        }
      }
    """, {"id": team_id})["data"]["issues"]["nodes"]
    title_lower = title.lower()
    for issue in issues:
        if issue["title"].lower() == title_lower:
            if parent_id is None or issue.get("parent", {}).get("id") == parent_id:
                return issue
    return None

def find_parent_epic(team_id, title_fragment, epic_label_name="type:epic"):
    """Find the parent epic by title fragment + epic-label."""
    issues = graphql("""
      query($id: ID!, $label: String!) {
        issues(filter: {
          team: { id: { eq: $id } }
          labels: { name: { containsCaseInsensitive: $label } }
        }, first: 50) {
          nodes { id identifier title }
        }
      }
    """, {"id": team_id, "label": epic_label_name})["data"]["issues"]["nodes"]
    for issue in issues:
        if title_fragment.lower() in issue["title"].lower():
            return issue
    return None

def create_issue(title, description, label_ids, parent_id=None, priority=2):
    """Create an issue with parentId + labelIds (returns issue dict)."""
    payload = {
        "teamId": TEAM_ID,
        "title": title,
        "description": description,
        "labelIds": label_ids,
        "priority": priority,
    }
    if parent_id:
        payload["parentId"] = parent_id
    result = graphql("""
      mutation($input: IssueCreateInput!) {
        issueCreate(input: $input) {
          success
          issue { id identifier title url state { name } }
        }
      }
    """, {"input": payload})
    return result["data"]["issueCreate"]["issue"]

# --- Main ---
epic_title = "[PE-X] my epic"
epic = find_existing_issue_by_title(TEAM_ID, epic_title)
if epic is None:
    epic = create_issue(
        title=epic_title,
        description="...",
        label_ids=["type:epic", "plugin:pwp", ...],
        priority=1,
    )

child_specs = [
    {"title": "[PE-X] F1 — ...", "description": "...", "label_ids": [...]},
    {"title": "[PE-X] F2 — ...", "description": "...", "label_ids": [...]},
]
for spec in child_specs:
    existing = find_existing_issue_by_title(TEAM_ID, spec["title"], parent_id=epic["id"])
    if existing:
        print(f"[exists] {existing['identifier']} {existing['title']}")
        continue
    issue = create_issue(
        title=spec["title"],
        description=spec["description"],
        label_ids=spec["label_ids"],
        parent_id=epic["id"],
    )
    print(f"[created] {issue['identifier']} {issue['title']}")
```

## Why this shape

- **Find-before-create is mandatory.** Linear does not enforce title
  uniqueness within a team; re-running a naive `issueCreate` loop will
  duplicate every child. With `find_existing_issue_by_title` in front
  of each create, the script is safe to re-run.
- **Scope to `parent_id` when finding children.** The epic + child have
  the same label set (`plugin:pwp`, `agent:ned`). Without parent-scoping
  you'd match the parent itself in the children's search, causing
  confusion in the output.
- **Use `teamId` filter, not bare `issues` query.** A bare `issues` query
  without a team filter returns issues across every team the user has
  access to. Always pass `teamId` so the script is portable.
- **Use GraphQL variables, not Python f-string interpolation.** A label
  name containing a quote character or a backslash will break a
  `f"...{label}..."` interpolation. The `containsCaseInsensitive` filter
  accepts a `$label: String!` variable — wire it as a variable, not as
  inline substitution.
- **`labelIds` requires resolving label names to UUIDs first.** Linear's
  `IssueCreateInput` accepts `labelIds: [String!]`, not label names.
  Resolve `plugin:pwp` → `71baf7d0-...-ce09` once via
  `query { team(id) { labels { nodes { id name } } } }`, cache the
  result in a dict, and pass UUIDs into the create call.

## Probe recipe (first 60 seconds of any Linear initiative)

```python
# 1. Confirm token works + find viewer
graphql("{ viewer { id name email } }")

# 2. List teams the user can post to
graphql("{ teams { nodes { id name key } } }")

# 3. List labels in the target team
graphql("""query($id: ID!) { team(id: $id) { labels { nodes { id name color } } } }""",
        {"id": TEAM_ID})

# 4. List existing PWP-related issues for context (avoid collisions)
graphql("""query($id: ID!) {
  issues(filter: { team: { id: { eq: $id } } labels: { name: { containsCaseInsensitive: "plugin:pwp" } } }, first: 20) {
    nodes { identifier title state { name } }
  }
}""", {"id": TEAM_ID})
```

## Idempotent-resubmit semantics for child issues

When the same user re-submits the form for the same site, you have two
reasonable behaviors:

1. **Find + add comment** (preferred for funnel-config flows). Comment
   body: `"Re-submitted for {slug} at {timestamp}. Latest context:
   {primary_goal}"`. Leave issue state alone; PE will pick up the
   comment and re-trigger its workflow.
2. **Find + reopen + re-assign.** If the prior task is `Done`, post a
   comment AND transition back to `Todo` so it shows up in PE's queue
   again. Use `issueUpdate(id, input: {stateId: <todo-id>})`.

Option 1 is what the `funnel_config.dispatch` flow uses (GRO-4358).

## Common pitfalls

- **Forgetting to scope child search by `parent_id`.** Without the
  parent filter, a child named "F1" will match the parent's F1 child in
  another epic and the script will skip a real create.
- **Title case mismatches.** Use `title.lower() == issue["title"].lower()`
  for the match; Linear preserves case but humans vary it.
- **`labelIds` mistake: passing names instead of UUIDs.** The mutation
  fails silently with `success: false` and no error code in the payload;
  re-check your label-id resolution cache.
- **`priority` values: 0=None, 1=Urgent, 2=High, 3=Medium, 4=Low.**
  Most PWP tasks should be 2 (High) unless explicitly urgent.

## Related skill

See `linear-api-operations/SKILL.md` for the broader Linear API pitfalls
(no `Bearer` prefix, `commentCreate` vs `commentUpdate` asymmetry, etc.).
