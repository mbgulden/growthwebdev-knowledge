# Immutable review artifacts for Prismatic planning packets

Use this reference when coordinating Prismatic Linear manifests, approval packets, or any artifact sent for independent review.

## Lesson

Do not send a mutable path for final approval while continuing to edit it. Async reviewers may verify the original hash, then correctly return `BLOCKED` when the file changes under them. Treat that as a process failure even when the content changes are valid.

## Required pattern

1. Draft on a mutable working path.
2. Incorporate all stale-review findings by exact hash:
   - identify whether the reviewer inspected an obsolete artifact;
   - port any still-valid findings into the current draft;
   - do not dismiss findings solely because the reviewed hash is stale.
3. Freeze final bytes to a versioned path, e.g. `*_V5_YYYY-MM-DD.md`.
4. Record:
   - frozen path;
   - SHA-256;
   - line count;
   - file mode;
   - local verification log path and log SHA-256;
   - explicit `LINEAR_MUTATED=false` or equivalent no-side-effect proof.
5. Dispatch independent review only against the frozen versioned path and exact hash.
6. Do not modify the frozen artifact. If another blocker appears, create the next versioned artifact and re-review that hash.

## Graph/relation packet pitfalls observed

- Avoid redundant transitive edges. If `A -> B -> C`, do not also add `A -> C` unless the direct edge has distinct non-transitive semantics.
- Keep planning approval separate from executable write authority. A planning packet may approve architecture and future drafting but must not imply Linear mutation approval.
- Future symbolic edges are non-actionable until both endpoints exist with approved exact content.
- Before any later write packet, require a full re-read of titles, descriptions, labels, states, parents, relations, and `updatedAt`; abort the whole packet on any drift.
- If a stale async review finds a real issue, repair it in the next version and rerun independent review; do not ask the user to approve around it.
