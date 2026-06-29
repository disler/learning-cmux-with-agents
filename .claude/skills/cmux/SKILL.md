---
name: cmux
description: Drive cmux — the terminal multiplexer / agent-surface control CLI — from natural language. Use this whenever a prompt asks you to open, inspect, prompt, read, or tear down cmux windows, workspaces, panes, surfaces, or agent sessions. Prefix orchestration prompts with /cmux.
argument-hint: [what to do in cmux]
---

# cmux

## Purpose

You are driving **cmux**, a CLI + socket for controlling terminal surfaces (and the
agents running inside them). Every window, workspace, pane, and surface is a real,
addressable object you can spawn, prompt, read, and close from the command line.

## Instructions

### Discover commands first (`--help`)

Before doing anything, run:

```bash
cmux --help
```

Then drill into any subcommand you intend to use:

```bash
cmux <command> --help     # e.g. cmux workspace --help, cmux send --help
```

cmux evolves; **trust `--help` over memory**. Never guess flags — confirm them.

### Understand the hierarchy

Everything nests in one tree. Learn the boxes and the verbs fall out:

- **Window** → a top-level OS window.
- **Workspace** → a sidebar entry ("tab") inside a window.
- **Pane** → a split region within a workspace.
- **Surface** → a tab within a pane (a terminal or a browser).

Use `cmux tree --all` (or `cmux workspace list` / `cmux list-pane-surfaces`) to see
the current state before you act.

### Create a workspace and inject credentials (`--env-file`)

Create a workspace and capture BOTH refs in one call. `--json` returns the
`workspace_ref` and the initial `surface_ref` — grab and thread them; never guess
positional refs.

```bash
cmux workspace create --name <name> --cwd <dir> --env-file .env --json
```

- **`cmux workspace create` supports `--env-file`, which loads that file's
  environment variables into every surface in the workspace** — so an agent
  launched in a pane (`claude`, `pi`, `codex`, `gemini`) comes up already
  authenticated, no manual `export` needed.
- **Default `--env-file` to `.env`** (the repo's `.env`) unless told otherwise:
  `--env-file .env`. That is the canonical source for `OPENROUTER_API_KEY`,
  `ANTHROPIC_API_KEY`, etc.
- Pair it with `--layout <compact-json>` to boot a whole multi-pane team
  declaratively in one call (each pane's `command` auto-launches its agent).
- **Don't inject over a working login.** If an agent is already authenticated
  (e.g. Claude Code), don't push a placeholder key over it via `--env-file`;
  scope credential injection to the agents that actually need it.
- **Assume the keys are already set up — and never read their values.** By
  default, just point `--env-file` at `.env` and proceed; do not `cat .env`,
  `echo $OPENROUTER_API_KEY`, or `read-screen` a surface to capture a key. **Only
  if an agent actually fails to authenticate** should you validate, and do it
  *safely*: `cmux workspace env --workspace <ref> --mask` shows that a var is
  present without revealing it, and `[ -n "$VAR" ]` confirms it is non-empty.
  Report the masked/presence result, never the secret itself.

### The control loop

You operate surfaces the way a person would, but over the CLI:

- `cmux send --surface <ref> "<text>"` — type text into a surface.
- `cmux send-key --surface <ref> enter` — submit it (press a key). **`send` types; `send-key` submits — they are separate steps.**
- `cmux read-screen --surface <ref>` — read what's on screen (add `--scrollback` for history). This is your eyes.
- `cmux close-surface --surface <ref>` — end a surface cleanly.

### Wait for agents via notification events (don't busy-poll)

Instead of looping on `read-screen`, subscribe to cmux's push channel and block
until an agent finishes its turn. **This is verified working for pi, codex,
and Claude Code.**

**`cmux events` is the wait channel — not `cmux wait-for`.** `cmux wait-for <name>`
is an unrelated *named-token rendezvous* (a manual semaphore you signal yourself);
it does **not** know when an agent finishes. The agent-completion signal is the
`notification` event category.

**Prerequisite — install the notification hooks once:**

```bash
cmux hooks setup            # wires pi, codex, opencode, gemini, … to emit on turn-stop
# or per agent:  cmux hooks pi install   /   cmux hooks codex install
```

Claude Code emits notifications out of the box when launched inside cmux (no
`cmux hooks` entry needed). Without hooks, an agent stays silent and you're back to
polling — so install them before relying on the wait.

**What an agent emits when its turn ends** — one event per completed turn:

```json
{ "name": "notification.requested", "category": "notification",
  "workspace_id": "120FC732-…", "surface_id": null, "seq": 1512, … }
```

Match on **`workspace_id`** — for hook-emitted notifications `surface_id` is usually
`null`, but `workspace_id` is always set. The title/body are **redacted** in the
event (you get the signal, not the text), so once it fires, `read-screen` that
workspace's surface for the actual reply. Filter to `--name notification.requested`;
a sibling `notification.clear_requested` fires when a surface gains focus and is just
noise.

**Block until a specific agent finishes** (capture its `workspace_id` first via
`cmux list-workspaces --json --id-format both`):

```bash
WS=<agent-workspace-uuid>
# Start the listener to a file BEFORE sending the prompt, then poll the file.
cmux events --name notification.requested --no-heartbeat --no-ack > /tmp/cmux.ev &
EV=$!
cmux send --surface <ref> "<task>"; cmux send-key --surface <ref> enter
# wait (bounded) for this workspace's turn-done event
until grep -q "\"workspace_id\":\"$WS\"" /tmp/cmux.ev; do sleep 1; done
kill $EV
cmux read-screen --surface <ref> --scrollback --lines 40   # now read the reply
```

Pitfall: a `cmux events | jq … &` pipeline in a one-liner can stall on stdout
buffering — stream to a **file** and poll the file (above), or pass
`jq --unbuffered`. For a durable cursor across reconnects use
`cmux events --cursor-file <path> --reconnect`.

### Launching the pi agent

`pi` is an interactive TUI agent — launch it as `pi --model … "<task>"`.

- Launch it **inside a pane** (via `cmux send` + `send-key enter`), not from your
  own non-interactive/batch shell.

### Launching Codex — run it in yolo / auto mode

When launching **Codex** in a pane, start it unattended so it doesn't stall on
approval prompts (it's running inside cmux, driven by an orchestrator). Pass the
flag at launch — do **not** edit Codex's global config:

- **Yolo (full, no sandbox):** `codex --dangerously-bypass-approvals-and-sandbox "<task>"`
  — skips every approval prompt and the sandbox. Use only because the run is
  orchestrated/observed.
- **Auto (sandboxed):** `codex --full-auto "<task>"` — automatic execution inside a
  workspace-write sandbox; safer when full access isn't needed.

Default to yolo for hands-off fleet runs; reach for `--full-auto` when you want a
sandbox. These are per-launch flags, so they never change the user's global Codex setup.

**Always launch Codex with the `gpt-5.5` model unless a prompt specifies otherwise** —
pass `-m gpt-5.5` at launch, e.g. `codex -m gpt-5.5 --dangerously-bypass-approvals-and-sandbox "<task>"`.
If a prompt names a different Codex model/effort, use that instead; gpt-5.5 is just the default.

### Launching Claude Code — use cc bypass mode

Plain `claude` launches in **ask-for-permission mode**: it will *decline* to run
Bash/edits and instead print instructions, then end its turn. For a hands-off fleet
agent, launch it the same way you yolo Codex — bypass permissions at launch:

- **cc bypass:** `claude --dangerously-skip-permissions "<task>"` — Claude's
  equivalent of Codex yolo. The composer then shows `⏵⏵ bypass permissions on` and it
  executes shell/edits without prompting. (`--dangerously-skip-permissions` is a
  per-launch flag; it doesn't change global Claude settings.)

Caveat verified in testing: a notification still fires on turn-completion **even when
Claude refused to do the work** — so if you only watch events, you can mistake a
"declined, nothing happened" turn for success. Always `read-screen` (or check the
artifacts) after the event, don't trust the event alone. Claude Code emits cmux
notifications out of the box (no `cmux hooks` entry needed); see
**Wait for agents via notification events** above.

### Best practices

1. **`--help` before every unfamiliar verb.** Confirm the subcommand and flags exist.
2. **Look before you leap.** Inspect with `tree` / `list` / `read-screen` before sending or closing anything.
3. **Refs are positional and renumber.** `surface:N` / `workspace:N` shift as things open and close. Re-read the tree right before you act; for anything long-lived, anchor to a **stable window UUID**, not a positional ref.
4. **Type then submit.** A prompt isn't sent until you `send-key enter`. Give agents a beat before you `read-screen` their reply.
5. **Read back to verify.** After sending a command, `read-screen` to confirm it actually ran and got the result you expected — don't assume.
6. **Close scoped, never broad.** Close only surfaces you just created or explicitly identified. Never loop a close over the whole `tree` — you'll kill things you didn't mean to. `close`/`close-window` may no-op while a live agent occupies a pane; use `close-surface` per pane.
7. **One window per team.** Keep a unit of work to a single window so it stays monitorable and tearable as a unit.
8. **Never print secrets.** If a surface has credentials/keys loaded, read results back without echoing the secret values.
9. **Prefer push over poll.** Use `cmux events --category notification` (see **Wait for agents via notification events** above) to know the instant an agent finishes instead of polling `read-screen` in a tight loop. Install hooks first (`cmux hooks setup`); match events on `workspace_id`. `cmux wait-for` is a manual named-token semaphore, **not** an agent-finished signal.

## Workflows

### Drive a surface end-to-end

The default loop for any single-surface task: discover, inspect, act, verify, report.

1. `cmux --help` (and per-subcommand `--help`) to confirm the verbs.
2. Inspect current state (`tree --all` / `workspace list`).
3. Take the action (create / send + send-key / read).
4. Read back to verify the result.
5. Report concisely what happened, citing the surfaces/refs involved.

## Report Format

Report concisely in plain English: what you did, the surfaces/refs involved, and
what `read-screen` confirmed. Cite refs (e.g. `workspace:2` / `surface:3`) and never
echo secret values.
