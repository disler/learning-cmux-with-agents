# 03 · Split Into a Grid

> **Tier 1 — Foundations**  ·  Complexity `▰▰▱▱▱`
> **Thesis:** one window becomes a *command center* — many live terminals, visible at once, all under one agent.
> **cmux verbs:** `workspace create` · `new-split <dir> --surface` · `send`
> **Agents under control:** _none yet — four terminals in a 2×2_

---

## 🗣 The prompt

> "Build me a monitoring dashboard in one cmux workspace called **dash** in a temp directory: split it into a 2×2 grid of terminals. Top-left run `htop`, top-right `watch -n1 date`, bottom-left tail a temp log file it owns, and leave the bottom-right as a plain shell."

## 🎯 What it showcases

The **Pane** layer of the hierarchy `Window → Workspace → Pane → Surface`. Splitting is how a single workspace holds several programs side-by-side — the visual foundation for an agent fleet (Tier 3).

## 🧠 What the orchestrator does (answer key)

```bash
# A throwaway temp dir for this dashboard (no $HOME or system-path access needed).
WORK="$(mktemp -d /tmp/cmux-demo.XXXXXX)"

# Top-left is the workspace's initial surface.
read WS TL < <(cmux workspace create --name dash --cwd "$WORK" --json \
               | jq -r '[.workspace_ref, .surface_ref] | @tsv')

# Split off specific surfaces to build a clean 2×2.
TR=$(cmux new-split right --surface "$TL" --json | jq -r .surface_ref)   # top-right
BL=$(cmux new-split down  --surface "$TL" --json | jq -r .surface_ref)   # bottom-left
BR=$(cmux new-split down  --surface "$TR" --json | jq -r .surface_ref)   # bottom-right

# Each pane gets its own program; bottom-right stays a free shell.
# Bottom-left tails a temp log this workspace owns (seed it so tail has something to follow).
cmux send --surface "$TL" "htop";                             cmux send-key --surface "$TL" enter
cmux send --surface "$TR" "watch -n1 date";                   cmux send-key --surface "$TR" enter
cmux send --surface "$BL" "touch run.log && tail -f run.log"; cmux send-key --surface "$BL" enter
# $BR is left as a free shell on purpose.
```

## 🔑 Concepts introduced

- **`new-split <left|right|up|down> --surface <ref>`** splits *from a chosen surface*, so you control exactly where each pane lands.
- A pane's **direction** is relative to the surface you split from — that's how you compose a grid instead of a stack.
- Every split returns a fresh `surface_ref` you thread into later `send`/`read-screen` calls.

## ✅ Done when

- [ ] `cmux tree --all` shows workspace `dash` with **4 surfaces** in a 2×2.
- [ ] `htop`, the clock, and the log tail are visibly running in their panes.
