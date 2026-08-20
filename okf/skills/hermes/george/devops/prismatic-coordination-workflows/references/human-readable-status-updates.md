# Human-readable Prismatic status updates

For every numbered repair, gate, PR, review, or commit reported to Michael, put plain-English meaning before traceability metadata.

Use this order:

1. **Problem found** — what could fail, be forged, or be misleading.
2. **What changed** — describe the behavioral correction.
3. **Why it matters** — give the practical risk or capability impact.
4. **Current state** — merged, rejected, under review, integrated, deployed, etc.
5. **Next move** — one concrete action and its gate.
6. **Traceability** — task IDs, PRs, commit/tree hashes, logs, and markers.

Never make labels such as `Repair 6`, task IDs, hashes, or internal markers the primary explanation. If Repairs 4–6 are iterations of one feature, say that explicitly so they are not mistaken for three separate product capabilities.