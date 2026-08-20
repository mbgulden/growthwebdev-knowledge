# AGY shared skill pool placement — session detail (2026-08-18)

Task: create the `agy-okf-infrastructure-update` skill so AGY updates the OKF hub
when it builds new infrastructure or changes infra, and make sure Fred/Kai/Ned
carry the lean memory pointer.

## Discovery chain (what cost time — do not re-derive)

1. AGY is launched by `prismatic-consumer` with `AGY_CLI_HOME` pointing at the
   **kai** profile's home.
2. Candidate skill dirs: `~/.gemini/antigravity/skills` and `~/.gemini/config/skills`.
3. Decisive evidence: kai's home `~/.gemini` is a **symlink** to
   `/home/ubuntu/.gemini` — so every AGY run (regardless of which profile's home
   `AGY_CLI_HOME` resolves to) shares ONE pool: `/home/ubuntu/.gemini/config/skills/`.
4. Pool layout: flat `*.md` files (not subdirs with SKILL.md), ~66-67 files,
   lane pattern `agy-as-*` (architect, coder, ...), each with frontmatter:
   `name`, `description`, `tags`, `related_skills`.
5. Routing: `~/.gemini/config/skills/agy-lane-system-index.md` lists every lane
   skill as a list line. A skill that is not in the index is not routed.

## Placement recipe (verified working)

1. Write flat `<name>.md` into `~/.gemini/config/skills/` (mode 644 — `write_file`
   defaults to 600; siblings are 644, align permissions).
2. Append one list line to `agy-lane-system-index.md`.
3. Verify: `ls -la` (size/mode), `head -14` (frontmatter), `grep -n '<name>' agy-lane-system-index.md`.
4. Label closeout `NOT_CLAIMING=...not exercised by an AGY run yet...`.

## Pitfalls hit

- `~/.hermes/profiles/agy/skills/` is the **Hermes agy profile's** skill dir
  (had only `audits/pwp-visual-qa-proof`) — NOT AGY CLI discovery. Do not place
  AGY skills there.
- The pool is **not a git repo** (`git rev-parse --is-inside-work-tree` → fatal).
  No version trail exists; back up before edits, and offer committing a copy
  into `growthwebdev-knowledge` (e.g. `okf/playbooks/`) for durability.
- The pool is shared across ALL agents/lanes — a name collision or a bad
  `related_skills` entry affects every AGY run, not one lane.

## Cross-profile memory mirror (same session)

- `profiles/fred` is a **symlink to `profiles/orchestrator`** (same inode) —
  one write covers both; verify with `stat -c '%i'` / `readlink -f`.
- Memory design principle mirrored into kai/ned/orchestrator MEMORY.md:
  "memory stays lean with short pointers; long/complex detail lives in OKF
  (growthwebdev-knowledge), referenced from memory." Canonical example:
  `okf/integrations/llama-cpp-george-local-server.md`.
- Kai has dual `SOUL.md` (6968B, authoritative) and `soul.md` (403B, pointer
  stub to the uppercase file) — divergent but intentional; do not "fix" it.

## Related defect found (not fixed — needs Michael approval)

`/home/ubuntu/.hermes/profiles/orchestrator/skills/agent-operations/projector-aware-communication-discipline/`
contains a **self-referential symlink** named the same as its own directory,
pointing at itself (created Jul 29 03:29, inherited by fred via the profile
symlink). This is what produces the 20+ levels deep nested
`projector-aware-communication-discipline/projector-aware-.../` chain in
skills lists. Fix: delete the inner symlink (approval-gated), then re-verify
the skills list depth.
