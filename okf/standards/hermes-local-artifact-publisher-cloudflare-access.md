---
type: Standard
title: Hermes Local Artifact Publisher Behind Cloudflare Access
description: Canonical standard for publishing local Hermes evidence artifacts through a durable Cloudflare Access-protected surface without leaking secrets or relying on ephemeral Telegram/session cache paths.
resource: okf/standards/hermes-local-artifact-publisher-cloudflare-access.md
tags: [standards, hermes, artifacts, cloudflare-access, evidence, security]
timestamp: 2026-07-14T04:00:00Z
linear_issue: GRO-1948
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/standards/hermes-local-artifact-publisher-cloudflare-access.md
last_verified: 2026-07-14
verified_by: fred
status: current
---

# Hermes Local Artifact Publisher Behind Cloudflare Access

## Purpose

Hermes agents produce useful evidence artifacts: Markdown audits, CSV exports, screenshots, verifier JSON, run logs, and OKF drafts. Telegram delivery paths, `/tmp` files, and Hermes document-cache copies are convenient for a session, but they are not durable operator surfaces.

This standard defines the target contract for a durable local artifact publisher protected by Cloudflare Access.

## Core contract

A published artifact is valid only when it satisfies all of these conditions:

1. **Durable location** — the artifact is copied from scratch/session storage into a stable publisher root.
2. **Access protected** — public access is blocked by Cloudflare Access or an equivalent authenticated boundary.
3. **Secret safe** — the artifact has been scanned for obvious token/credential patterns before publication.
4. **Traceable** — the published record links back to its source task, run, Linear issue, or OKF resource.
5. **Retainable** — the artifact has an explicit retention class instead of living forever by accident.
6. **Verifiable** — the publishing operation emits a small evidence payload with path, URL, checksum, verifier scope, and cleanup status.

## Non-goals

- Do not use this surface as a general file dump.
- Do not publish raw `.env`, credentials, database dumps, browser profiles, or private user exports.
- Do not treat a published artifact as canonical OKF when the artifact should be promoted into `growthwebdev-knowledge`.
- Do not bypass Cloudflare Access for convenience links.

## Publisher root

Recommended local root:

```text
/home/ubuntu/published-artifacts/
```

Recommended layout:

```text
published-artifacts/
  linear/GRO-1948/<timestamp>/...
  runs/<run-id>/<timestamp>/...
  okf-drafts/<slug>/<timestamp>/...
  audits/<slug>/<timestamp>/...
```

Each published directory should include:

```text
artifact.json
README.md
<actual artifacts>
```

## `artifact.json` schema

Minimum fields:

```json
{
  "artifact_id": "linear-GRO-1948-20260714T040000Z",
  "source": {
    "linear_issue": "GRO-1948",
    "session": "optional Hermes session id",
    "run_id": "optional run id"
  },
  "published_at": "2026-07-14T04:00:00Z",
  "published_by": "fred",
  "retention": "operational-evidence-90d",
  "access": {
    "boundary": "cloudflare-access",
    "public": false
  },
  "files": [
    {
      "path": "README.md",
      "sha256": "...",
      "bytes": 1234,
      "media_type": "text/markdown"
    }
  ],
  "verification": {
    "scope": "ad-hoc targeted verification",
    "secret_scan": "pass",
    "link_check": "pass",
    "cleanup": "source scratch file removed or retained intentionally"
  }
}
```

## Secret-scan floor

Before publication, scan text artifacts for at least:

- GitHub personal access token prefixes such as `ghp_`.
- OpenAI-style secret prefixes such as `sk-` followed by a long token body.
- Slack token prefixes such as `xoxb-`, `xoxp-`, `xoxa-`, or `xoxs-`.
- Telegram bot token shape: numeric bot id + colon + long token body.
- AWS access key shape: `AKIA...`.
- Raw `.env` assignment blocks.

A clean regex scan is a floor, not proof that the artifact is safe. Human judgment still applies for client, family, billing, medical, and private business data.

## Cloudflare Access boundary

The published hostname/path must be protected before agents share it as a durable link.

Required properties:

- Access policy requires an authenticated identity or explicit service-token path.
- Anonymous `curl` receives an auth challenge or denial.
- Authenticated access can fetch artifact metadata and files.
- The publisher does not expose directory traversal or arbitrary local paths.

## Operator flow

1. Generate the artifact in scratch space.
2. Run a focused verifier over the artifact.
3. Copy the artifact into the publisher root.
4. Generate `artifact.json` with checksums.
5. Run the secret-scan floor over published text files.
6. Verify anonymous access is denied by Cloudflare Access.
7. Verify authenticated/service-token access can fetch `artifact.json`.
8. Link the durable artifact from Linear/OKF/run record.
9. Remove scratch files unless intentionally retained.

## Done gate for GRO-1948-style work

An implementation task for this standard is **Done** only when evidence shows:

- publisher root exists with the expected layout;
- at least one sample artifact publishes successfully;
- `artifact.json` includes checksums and source links;
- secret-scan floor passes;
- anonymous access is denied;
- authenticated access succeeds;
- Linear/OKF evidence links point at the durable surface;
- cleanup status is explicit.

## Current disposition

As of 2026-07-14, [GRO-1948](https://linear.app/growthwebdev/issue/GRO-1948) is no longer routed as AGY execution work. It is an OKF/Fred documentation and standardization item. Future implementation can be split into a separate execution issue after this standard is accepted.
