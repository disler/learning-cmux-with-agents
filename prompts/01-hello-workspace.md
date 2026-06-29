# 01 · Hello, Workspace

> **Tier 1 — Foundations**  ·  Complexity `▰▱▱▱▱`
> **Thesis:** a single agent takes *programmatic* control of a cmux terminal — no hands on the keyboard.
> **cmux verbs:** `workspace create` · `send` · `send-key` · `read-screen`
> **Agents under control:** _none yet — just the orchestrator and one terminal_

---

## 🗣 The prompt

Give this to your orchestrator agent (Claude Code or pi) running **inside** cmux:

> "In cmux, open a new workspace called **scratch** in a throwaway temp directory, run `uname -a` in it, then tell me exactly what it printed."

## 🎯 What it showcases

The atomic loop of everything that follows: **create a surface → type into it → press a key → read the result.** If an agent can do this, it can drive anything in the terminal programmatically.

## 🧠 What the orchestrator does (answer key)

```bash
# A throwaway working dir the sandboxed agent can touch (no $HOME or bin-dir access needed).
WORK="$(mktemp -d /tmp/cmux-demo.XXXXXX)"

# Create a workspace; capture BOTH its ref and its initial terminal surface ref in one call.
read WS S < <(cmux workspace create --name scratch --cwd "$WORK" --json \
              | jq -r '[.workspace_ref, .surface_ref] | @tsv')

# Type the command, then submit it (send does NOT auto-press Enter — that's send-key's job).
cmux send     --surface "$S" "uname -a"
cmux send-key --surface "$S" enter

# Read the visible screen back and report it.
cmux read-screen --surface "$S" --lines 5
```

## 🔑 Concepts introduced

- **Handles.** Everything is addressable by a short ref: `window:N`, `workspace:N`, `pane:N`, `surface:N`.
- **`send` vs `send-key`.** `send` types raw text; `send-key` presses one named key (`enter`, `tab`, `escape`, arrows…). Submitting always = `send` then `send-key enter`.
- **`read-screen` is the agent's eyes.** It snapshots the visible terminal; it does not block or wait.

## ✅ Done when

- [ ] `cmux tree` shows a workspace named `scratch`.
- [ ] `read-screen` returns the `Darwin … Kernel …` line.
- [ ] The orchestrator reports the kernel string back to you in plain English.
