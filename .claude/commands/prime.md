---
description: Onboard onto the cmux capabilities guide — what cmux is, what we're studying, and the three use cases this repo proves cmux can satisfy.
---

# Purpose

Catch up on this codebase. It is a **study of [cmux](https://cmux.com)** — a native macOS terminal (built on Ghostty) for running many AI coding agents at once — and a hands-on proof, via 31 natural-language prompts, that **one primary agent can stand up, prompt, watch, customize, and tear down a whole fleet of other agents and terminals** through cmux's CLI and Unix socket. We are exploring cmux's capabilities and confirming it satisfies three concrete use cases (it does):

1. **Agentic access to every terminal window** — the orchestrator can see and script every surface (`send` / `read-screen` / `close-surface`). → Tiers 1–5.
2. **Customizable UI panes to distinguish leads from workers** in a 3-tier agent team — per-workspace color/pill/icon (prompt 26) + per-pane identity (prompt 31).
3. **Reusable session files that boot new teams at the speed of agents** — declarative layouts-as-code (prompt 09) + crash-proof resume (prompt 24).

## Workflow

1. List the tracked files to see the shape of the repo: `git ls-files 2>/dev/null || find . -type f -not -path '*/.git/*' -not -path '*/legacy/*' | sort`.
2. Read `README.md` — the thesis, the "## The Problem — Three Things I Need From a Fleet Terminal" section (the three proofs), the mental model (Window ⊃ Workspace ⊃ Pane ⊃ Surface), the control loop (`send` · `send-key` · `read-screen` · `close-surface`), and the tier breakdown.
3. Read `guide/index.html` — the simplified single-page visual guide: hero + concept sections + the full tier library with copy-able prompts. This is the fastest high-level map of every capability.
4. Skim the prompt library in `prompts/` (`01`–`31` + `PATTERNS-read-and-notify.md`). Read at least one per group to learn the file shape — each has a `🗣 The prompt` (plain English), a `🧠 answer key` (the exact `cmux` verbs it compiles to), and `✅ Done when` criteria. Groups: 01–05 Foundations · 06–10 One Agent · 11–16 Fleet · 17–20 Browser · 21–25 Scale · 26–31 Customization.
5. Skim `ai_docs/cmux-skills/` — the 9 agent-facing skills (`cmux`, `cmux-workspace`, `cmux-browser`, `cmux-customization`, `cmux-settings`, `cmux-keyboard-shortcuts`, `cmux-custom-sidebar`, `cmux-diagnostics`, `cmux-markdown`) are the real verb surface that powers the prompts.
6. Summarize your understanding of the project: what cmux is, the thesis, the five-box mental model, the four-verb control loop, the three use cases we're proving, where each proof lives, and how the `prompts/` files are structured.
