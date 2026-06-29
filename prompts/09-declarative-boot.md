# 09 · Declarative Boot

> **Tier 2 — Driving a Single Agent**  ·  Complexity `▰▰▰▱▱`
> **Thesis:** layouts are *code*. A repeatable agent environment should be one declaration, not a script you re-run.
> **cmux verbs:** `cmux.json` `commands[]` + `layout` · `config doctor` · `workspace create --layout`
> **Agents under control:** **Claude Code** (booted by a saved layout)

---

## 🗣 The prompt

> "Add a reusable **AI Pair** layout to my cmux config: a left pane running Claude Code and a right pane that's a plain shell in the current project. Validate it, then launch it."

## 🎯 What it showcases

The declarative half of cmux. The same **layout tree** can live persistently in `cmux.json` (launched by name from the Command Palette) *or* be handed to `workspace create --layout` for a one-shot, fully CLI-testable boot. One description, two ways to run it.

## 🧠 What the orchestrator does (answer key)

**A) Persist it in `~/.config/cmux/cmux.json`** (launch from the Command Palette, ⌘⇧P → "AI Pair"):

```jsonc
{
  "commands": [
    {
      "name": "AI Pair",
      "keywords": ["ai", "pair", "claude"],
      "workspace": {
        "name": "AI Pair", "cwd": ".",
        "layout": {
          "direction": "horizontal", "split": 0.5,
          "children": [
            { "pane": { "surfaces": [ { "type": "terminal", "name": "Claude", "command": "claude", "focus": true } ] } },
            { "pane": { "surfaces": [ { "type": "terminal", "name": "Shell",  "command": "" } ] } }
          ]
        }
      }
    }
  ]
}
```

```bash
cmux config doctor          # validate JSONC before reloading (exits non-zero on error)
cmux reload-config          # apply with no restart
```

**B) Or boot the identical tree imperatively (great for tests/CI):**

```bash
cmux workspace create --name "AI Pair" --cwd "$PWD" --layout '{
  "direction":"horizontal","split":0.5,
  "children":[
    {"pane":{"surfaces":[{"type":"terminal","name":"Claude","command":"claude","focus":true}]}},
    {"pane":{"surfaces":[{"type":"terminal","name":"Shell","command":""}]}}
  ]}'
```

## 🔑 Concepts introduced

- **Layout tree.** `split` nodes (`direction` + `split` ratio 0.1–0.9, exactly two `children`) nest down to `pane` nodes holding `surfaces`.
- **Per-surface startup `command`** auto-runs on open — so the layout *is* the boot script.
- **`config doctor`** validates without a socket; **`reload-config`** applies live.

## ✅ Done when

- [ ] `config doctor` reports `ok: true`.
- [ ] Launching "AI Pair" (palette **or** `--layout`) yields a 2-pane workspace with Claude Code already running on the left.
