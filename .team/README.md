# `.team/` — shared memory & coordination for the agent fleet

This directory is the **shared workspace** for a spawned 5-agent team. It is how
domain-specific agents with memory (the pattern this repo argues for) stay
coordinated without a central server — just files plus cmux's `send` /
`read-screen` control loop.

## Files

| File | Written by | Purpose |
|------|-----------|---------|
| `<team>.roster.json` | the orchestrator running `/spawn-fs-team` | Maps each role → its cmux `surface:N` ref. **The lead reads this to address its workers.** Gitignored (runtime state). |
| `backlog.md` | the **lead** | The living task list for the current feature. Lead appends tasks and checks them off as workers report done. |
| `<role>.md` | each **worker** | That agent's running notes / decisions / memory, so context survives a restart and the lead can catch up by reading. |

## The coordination contract

1. An orchestrator (in a terminal, via `just devcc` / `just devpi`) runs
   `/spawn-fs-team`, which boots 5 `pi` agents in **one cmux window** (lead left,
   workers in a 2×2 on the right) and writes `<team>.roster.json`.
2. The **lead** reads the roster, breaks the feature into tasks (recorded in
   `backlog.md`), and dispatches each task to the right worker with
   `cmux send --surface <ref> "<task>"` + `cmux send-key --surface <ref> enter`.
3. Each **worker** does its specialty in `apps/flotion/`, writes a short note to
   `.team/<role>.md`, and finishes every task by printing the sentinel:

   ```
   FLOTION-DONE: <role> | <one-line summary>
   ```

4. The **lead** polls `cmux read-screen --surface <ref>` for `FLOTION-DONE`,
   integrates, updates `backlog.md`, and reports up to the orchestrator.

Roster files are regenerated on every spawn, so this directory is safe to wipe
between teams.
