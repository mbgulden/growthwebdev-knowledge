# AOT Queue Triage Example — 2026-07-07

This reference captures reusable patterns from a live “what needs work on activeoahutours.com?” session. Treat the issue numbers as examples of the triage shape, not durable project state.

## What made the answer useful

- Queried live Linear instead of answering from memory.
- Queried GitHub PR state before accepting Linear `[PR REVIEW]` issues as actionable.
- Checked production and mirror headers with `curl -I` before discussing deployment state.
- Grouped the answer by operational layer:
  1. stale PR-review cleanup
  2. DNS / Cloudflare Pages / staging discipline
  3. security / governance
  4. SEO / Lighthouse / CRO
  5. media library / original imagery pipeline
  6. growth/content backlog
- Ended with a short ranked “recommended next moves” list.

## Linear project groupings observed

Relevant AOT project names included:

- `Active Oahu Tours — Static Mirror Migration`
- `Active Oahu Tours — Media Library & Content Engine`
- `Active Oahu Tours — Website Overhaul`
- `Active Oahu Tours`
- `Your Hawaii Guide — Site Resurrection` when content may be consolidated into AOT

## Useful GraphQL query shape

```graphql
query($pid:String!){
  project(id:$pid){
    name
    issues(
      first:100,
      filter:{state:{type:{nin:["completed","canceled"]}}},
      orderBy:updatedAt
    ){
      nodes{
        identifier
        title
        priority
        url
        updatedAt
        state{name type}
        labels{nodes{name}}
        assignee{name}
        description
      }
    }
  }
}
```

Also use a broader issue search when project membership may be stale:

```graphql
query($first:Int!){
  issues(first:$first, filter:{
    and:[
      {state:{type:{nin:["completed","canceled"]}}},
      {or:[
        {labels:{name:{in:["agent:kai","agent:kai-css","agent:kai-content","agent:kai-js"]}}},
        {title:{containsIgnoreCase:"Active Oahu"}},
        {title:{containsIgnoreCase:"AOT"}},
        {description:{containsIgnoreCase:"activeoahutours"}},
        {description:{containsIgnoreCase:"Active Oahu"}},
        {description:{containsIgnoreCase:"FareHarbor"}}
      ]}
    ]
  }, orderBy:updatedAt){
    nodes{
      id identifier title priority url updatedAt
      assignee{name}
      state{name type}
      labels{nodes{name}}
      project{name}
      description
    }
  }
}
```

## GitHub check pattern

```bash
gh pr list --repo mbgulden/active-oahu-tours-mirror --state open \
  --json number,title,headRefName,baseRefName,isDraft,mergeable,updatedAt,url --limit 30

for n in 43 44 45 14; do
  gh pr view "$n" --repo mbgulden/active-oahu-tours-mirror \
    --json state,mergedAt,closed,url,title,headRefName,baseRefName,mergeStateStatus,mergeable
done
```

The important lesson: **Linear PR-review tasks can remain open after the GitHub PR is merged/closed.** Reconcile them before starting new code work.

## Production/mirror header check pattern

```bash
curl -sS -I https://activeoahutours.com/ | sed -n '1,12p'
printf '\n--- mirror ---\n'
curl -sS -I https://active-oahu-tours-mirror.pages.dev/ | sed -n '1,12p'
```

Report this as a lightweight deployment/status check, not a full Lighthouse or canonical QA pass.

## Reporting pattern

Use concise headings and tables:

```markdown
## Highest-priority work

### 1. Clean up stale PR-review Linear issues
| Issue | Current reality |
|---|---|
| [GRO-xxxx](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-xxxx) | GitHub PR is MERGED/CLOSED/etc. |

## My recommended next 5 moves
1. ...
```

Do not bury the lead in raw output. Michael wants the answer to say what to work on next, backed by evidence.