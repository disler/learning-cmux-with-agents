---
model: opus
description: Orient yourself as orchestrator over a full-stack team that was just scripted into its own cmux window. Reads the spawn file, locates the team by its (stable) window UUID, rediscovers surface refs, and gets ready to drive the lead.
argument-hint: <spawn-file path>
---

# cmux Did Spawn

## Purpose

A full-stack Flotion team was **already booted** as a workspace in a cmux window
by the `fastcc`/`fastpi` recipe (declarative layout — all 5 pi agents launched at
once). That window may be **shared with other teams** — each team is its own
workspace, so locate *this* team's workspace by name, not by position. Your job is
to take command of it: read the spawn file, find the window and the team's
workspace, confirm the agents are up, and stand ready to drive the **lead**. You
are the orchestrator and you run in a terminal, outside cmux.

## Variables

SPAWN_FILE: $1   # path to the .team/<feature>.spawn.json written at spawn time

## Instructions

- **cmux short refs are positional and renumber.** Never cache a `surface:N`
  across time. The only stable handle is the **window UUID** in the spawn file —
  locate the team by it and rediscover surface refs at the moment you use them,
  scoped to the team's workspace.
- **Talk to the LEAD only.** The lead dispatches its own workers (plan, build-be,
  build-fe, test). You hand the lead a feature; it does the rest.
- The team is already booting — don't re-spawn anything. If a pane shows a shell
  instead of an agent, that one pi failed to start; report it, don't recreate
  the whole team.
- Confirm cmux is reachable first (`cmux identify --json`).

## Workflow

1. Read `SPAWN_FILE`:
   ```bash
   F=$(jq -r .feature "$SPAWN_FILE"); WIN=$(jq -r .window "$SPAWN_FILE")
   WSNAME=$(jq -r '.workspace_name // .feature' "$SPAWN_FILE")
   ```
2. Confirm cmux is reachable (`cmux identify --json`); if not, tell the user to
   `open -a cmux` and stop.
3. Locate **this team's** workspace inside the (possibly shared) window by its
   **name**, not by position — other teams may be sibling workspaces in the same
   window. Then map each role to its **current** surface ref by the layout name:
   ```bash
   WS=$(cmux workspace list --window "$WIN" --json \
        | jq -r --arg n "$WSNAME" '.workspaces[] | select(.custom_title==$n) | .ref' | head -1)
   cmux list-pane-surfaces --workspace "$WS"      # names: lead / plan / build-be / build-fe / test
   ```
   Capture the surface ref on the line named `lead` — that's your dispatch target.
4. Confirm the team is alive: read the lead pane once
   (`cmux read-screen --surface <lead> --scrollback --lines 30`). The workers
   should each be replying `ready: <role>`.
5. You are now oriented. Wait for the user to give you a feature request (they may also give it directly to the leads), then:
   ```bash
   cmux send --surface <lead> "<feature>"; cmux send-key --surface <lead> enter
   cmux read-screen --surface <lead> --scrollback --lines 60   # watch it coordinate
   ```
6. Now follow the `Report` section.

## Report

```
## Orchestrating team "[feature]"  (window [WIN])

| Role | Surface (now) | Model |
|------|---------------|-------|
| 👑 lead | [ref] | [model] |
| 📐 plan | [ref] | [model] |
| ⚙️ build-be | [ref] | [model] |
| 🎨 build-fe | [ref] | [model] |
| ✅ test | [ref] | [model] |

Team is up and the workers reported ready. Give me a feature and I'll hand it to
the lead — or say "status" and I'll read the lead back.
```
