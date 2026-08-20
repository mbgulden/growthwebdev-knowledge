# Threaded consumer launcher safety

Session lesson from the Prismatic task-admission one-shot consumer repair.

## Trigger

A Prismatic consumer, dispatcher, or admission worker holds/renews a lease from one thread while launching an external producer/worker command from the same Python process.

## Durable rule

Do not use `subprocess.Popen(..., preexec_fn=...)` in a process with active threads. Python documents `preexec_fn` as unsafe in threaded programs because the child can deadlock before `exec` while locks are inherited from another thread.

## Safer launcher pattern

For lease-renewing consumers that must invoke a bounded local command:

1. Avoid `shell=True`.
2. Resolve and validate the executable path before launch.
3. Reject untrusted executable ownership and unsafe writable parent directories.
4. Start the child in a new session/process group with `start_new_session=True` rather than using `preexec_fn` for process-group setup.
5. Use selector/nonblocking bounded reads for stdout/stderr instead of unbounded `communicate()` when output limits are part of the contract.
6. Enforce monotonic wall-clock timeout.
7. On timeout or output overflow, terminate/kill the entire process group and requeue/release the lease according to the consumer contract.
8. Test overflow, timeout cleanup, unsafe executable path, and unsafe parent-directory cases, not only the happy-path launch.

## Verification packet expectations

Bind the proof to the exact candidate head/tree and distinguish:

```text
AD_HOC_OR_CANONICAL=ad-hoc targeted|canonical suite
THREAD_UNSAFE_PREEXEC=absent
BOUNDED_OUTPUT=proved
PROCESS_GROUP_CLEANUP=proved
LEASE_REQUEUE_ON_FAILURE=proved
NOT_CLAIMING=<merge/release/deploy/successor admission unless separately proven>
```

## Pitfall

A canonical suite can miss a launcher-safety defect when tests do not model threaded lease renewal plus subprocess launch. For admission/consumer slices, add a focused security/concurrency review before exact-head acceptance.
