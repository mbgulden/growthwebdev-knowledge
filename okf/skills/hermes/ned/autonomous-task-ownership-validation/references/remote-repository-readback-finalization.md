# Remote repository acceptance + finalization readback

Use this for a Ned-owned remote-repository configuration child (default branch, private visibility, topics, protection) that is already compliant when inspected.

1. Read the issue/comments and query the remote API/CLI first. Record canonical owner/name, URL, requested fields, default-branch HEAD, and readback time.
2. If the remote state satisfies acceptance, do **not** recreate or mutate it just to manufacture activity. Commit a narrowly scoped result/readback document on a `ned/<ISSUE>` branch in the target repository, then open a focused PR if documentation must be preserved.
3. Before `finalize_task.sh`, set `PRISMATIC_REPO_ROOT` to the actual target checkout and `FINALIZE_LOCK_FILES` to the exact lock acquired. Source a valid Linear key explicitly when the script's canonical env may not provide one.
4. Treat finalizer output as non-authoritative. Re-query the issue state and comments immediately. The finalizer can print an `In Review` transition while another dispatcher/automation leaves the issue `In Progress`.
5. Correct genuine state drift through the Linear variables API using the issue UUID and the **issue team's** `In Review` state ID. Post a concise evidence refresh with remote readback, branch/head, PR, and test evidence; query again until state and evidence are present.
6. `comments(last: 1)` ordering is not a safe “latest comment” assertion. Fetch several comments and assert that the expected comment ID is present.
7. Verify the pushed branch SHA equals the remote ref, PR base/head/changed-file count, clean target checkout, and lock release. Result packets must contain only values actually read back (especially Git tree IDs).

For src-layout standalone Python repositories, raw system `pytest` may fail before installation. Use a disposable venv, install `.[dev]`, then run `python -m pytest`; record the original collection failure as environment/boundary context, not a source regression if the installed test run passes.
