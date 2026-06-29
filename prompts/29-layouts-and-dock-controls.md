# 29 · Reusable Layouts & Dock Controls

> **Customization**  ·  Complexity `▰▰▰▱▱`
> **Thesis:** save the *shapes* you keep rebuilding — named workspace layouts, plus a right-sidebar Dock of one-tap tools.
> **cmux verbs:** `cmux.json` `commands` · `.cmux/dock.json` `controls` · `reload-config`
> **Customizes:** repeatable workspace shapes + always-on tool controls

---

## 🗣 The prompt

> "Two things: a one-command **dev** workspace (dev server on the left, live browser preview on the right), and a **Dock** in the right sidebar with quick buttons for lazygit, a test watcher, and the cmux Feed."

## 🎯 What it showcases

Two complementary customizations. **`commands`** turn a split layout you keep rebuilding into a named entry you launch from the palette. **Dock controls** (`.cmux/dock.json`) put recurring side-tools — a git TUI, a test watcher, a dev server, the Feed — one tap away in the right sidebar, per project or globally.

## 🧠 What the orchestrator does (answer key)

```jsonc
// ~/.config/cmux/cmux.json (global) or .cmux/cmux.json (per-repo)
{
  "commands": [
    { "name": "dev",
      "workspace": { "name": "Dev", "cwd": ".",
        "layout": { "direction": "horizontal", "children": [
          { "pane": { "surfaces": [ { "type": "terminal", "command": "bun dev" } ] } },
          { "pane": { "surfaces": [ { "type": "browser",  "url": "http://localhost:3000" } ] } }
        ] } } }
  ]
}
```

```jsonc
// .cmux/dock.json  (or ~/.config/cmux/dock.json) — right-sidebar terminal controls
{
  "controls": [
    { "id": "git",   "title": "Git",   "command": "lazygit",                 "cwd": ".", "height": 300 },
    { "id": "tests", "title": "Tests", "command": "bun test --watch",        "height": 240 },
    { "id": "feed",  "title": "Feed",  "command": "cmux feed tui --opentui", "height": 260 }
  ]
}
```

```bash
cmux config doctor && cmux reload-config        # validate + apply
# launch "dev" from ⌘⇧P, or imperatively:
cmux workspace create --name Dev --cwd "$PWD" --layout '{"direction":"horizontal","children":[
  {"pane":{"surfaces":[{"type":"terminal","command":"bun dev"}]}},
  {"pane":{"surfaces":[{"type":"browser","url":"http://localhost:3000"}]}}]}'
```

## 🔑 Concepts introduced

- **`commands[]`** = named, palette-launchable workspace layouts; the same layout tree also works one-shot via `workspace create --layout`.
- **Dock controls** (`.cmux/dock.json` → right sidebar) keep lazygit / test watchers / dev servers / `cmux feed tui` always reachable.
- **Travels with the repo.** Put both in `.cmux/…` and the whole team gets the same layouts and dock on checkout.

## ✅ Done when

- [ ] "dev" launches a 2-pane (terminal + browser) workspace by name.
- [ ] The right sidebar Dock shows Git / Tests / Feed controls.
