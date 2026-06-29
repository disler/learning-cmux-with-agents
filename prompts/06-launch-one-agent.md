# 06 · Launch One Agent

> **Tier 2 — Driving a Single Agent**  ·  Complexity `▰▰▱▱▱`
> **Thesis:** the terminal an agent drives can itself contain *another agent*. This is the seed of the whole idea.
> **cmux verbs:** `new-pane` · `send` · `send-key` · `read-screen`
> **Agents under control:** **Claude Code** ×1

---

## 🗣 The prompt

> "Open a fresh pane, start **Claude Code** in it, ask it to write a haiku about terminals, give it a few seconds, then read me back exactly what it wrote."

## 🎯 What it showcases

The pivot point of this entire guide: an orchestrator agent **boots a second coding agent inside a cmux pane and prompts it** — agent-driving-agent, entirely over `send` / `read-screen`. Everything in Tier 3 is just this, multiplied.

## 🧠 What the orchestrator does (answer key)

```bash
S=$(cmux new-pane --type terminal --direction right --json | jq -r .surface_ref)

# Boot the agent in the pane.
cmux send --surface "$S" "claude"; cmux send-key --surface "$S" enter

# Agents need a beat to start. Production code polls read-screen (or events, prompt 14);
# here we just give it a moment.
sleep 6

# Prompt the agent, then submit.
cmux send --surface "$S" "Write a haiku about terminals."
cmux send-key --surface "$S" enter
sleep 8

# Read the agent's rendered answer back out of the TUI.
cmux read-screen --surface "$S" --lines 40
```

## 🔑 Concepts introduced

- **Agent-in-a-pane.** `claude` (interactive TUI) or `claude -p "…"` (headless, prints and exits) both work; the interactive form is what you *watch*, the `-p` form is what you *script deterministically*.
- **The settle problem.** Agents boot and think asynchronously — a naive immediate `read-screen` sees a half-rendered screen. Re-read, or wait on completion (prompt 15) / events (prompt 14).

## ✅ Done when

- [ ] A pane is running Claude Code.
- [ ] `read-screen` shows a 3-line haiku.
- [ ] The orchestrator relays the haiku to you verbatim.
