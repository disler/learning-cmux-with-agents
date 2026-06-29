# 04 · Map the World

> **Tier 1 — Foundations**  ·  Complexity `▰▰▱▱▱`
> **Thesis:** before an agent can *orchestrate* a layout, it must be able to *perceive* it — fully and structurally.
> **cmux verbs:** `identify --json` · `tree --all` · `list-panes` · `list-pane-surfaces` · `top` · `memory`
> **Agents under control:** _introspection only_

---

## 🗣 The prompt

> "Show me everything cmux is running right now — every window, workspace, pane and surface — and for each terminal tell me the process, CPU, and memory. Give it to me as a tidy report, and flag anything using more than 50% CPU."

## 🎯 What it showcases

Deterministic **self-awareness**. An orchestrator that can dump the whole topology as JSON can place new work precisely, detect runaway processes, and never act blindly. This is the read-side counterpart to all the create/send verbs.

## 🧠 What the orchestrator does (answer key)

```bash
cmux identify --json        # who am I? which workspace/surface is calling?
cmux tree --all             # the full Window → Workspace → Pane → Surface tree
cmux list-panes --json
cmux list-pane-surfaces --pane pane:1 --json
cmux top --processes --sort cpu     # per-surface process + CPU/MEM
cmux memory                 # memory grouped by workspace
```

## 🔑 Concepts introduced

- **`identify`** answers "where is the agent itself running?" via `CMUX_WORKSPACE_ID` / `CMUX_SURFACE_ID`.
- **`tree --all`** is the human-readable map; the `--json` listers are the machine-readable one.
- **`top` / `memory`** turn cmux into a process supervisor — essential once a fleet is live.

## ✅ Done when

- [ ] The report enumerates every live surface with its ref and process.
- [ ] CPU/memory figures are present and any >50% CPU surface is flagged.
