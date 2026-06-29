# 10 · Native Sessions & Resume

> **Tier 2 — Driving a Single Agent**  ·  Complexity `▰▰▰▱▱`
> **Thesis:** an agent the orchestrator launches should *survive a restart* — picked up by its real session, not replayed.
> **cmux verbs:** `new-surface --provider` · `hooks setup` · `surface resume` · `autoResumeAgentSessions`
> **Agents under control:** **Claude Code** as a first-class cmux agent session

---

## 🗣 The prompt

> "Spawn Claude Code as a **native cmux agent session** — not just the word 'claude' typed into a shell — and set things up so that if cmux restarts, this session resumes exactly where it left off."

## 🎯 What it showcases

cmux's two-phase restore. Layout comes back from a JSON snapshot; **agents** come back because cmux captured each one's *native session ID* via lifecycle hooks. `new-surface --provider` creates an agent surface cmux understands as an agent, so resume is automatic.

## 🧠 What the orchestrator does (answer key)

```bash
# 1) Make sure resume hooks are installed for every agent CLI on PATH
#    (capture native session IDs: claude, codex, gemini, pi, opencode, …).
cmux hooks setup --yes

# 2) Create a native agent surface (provider-aware), not a bare terminal.
cmux new-surface --type agent-session --provider claude --json

# 3) Inspect what cmux captured for resume, on the calling surface.
cmux surface resume show

# 4) Auto-resume is ON by default; this is the opt-out knob in cmux.json:
#    { "terminal": { "autoResumeAgentSessions": true } }
#    Manual restore any time:  cmux restore-session   (or ⌘⇧O)
```

## 🔑 Concepts introduced

- **`new-surface --provider <claude|codex|opencode>`** creates an agent-aware surface, vs. `send "claude"` into a plain terminal.
- **Hooks capture the session ID.** Install them *after* the agent CLI is on PATH; without them, the pane reopens as a normal terminal.
- **Boundary by design.** cmux resumes *supported agents*, not arbitrary live process state — tmux/vim/shells reopen fresh.

## ✅ Done when

- [ ] `cmux hooks setup` reports installed hooks.
- [ ] A native Claude Code agent surface is running.
- [ ] `surface resume show` reports a captured session for it.
