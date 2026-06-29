# 28 · Custom Actions & Buttons

> **Customization**  ·  Complexity `▰▰▰▱▱`
> **Thesis:** you can reshape the *launch UX* — add your own verbs to the Command Palette, the tab bar, and the plus-button.
> **cmux verbs:** `cmux.json` `actions` · `ui.surfaceTabBar.buttons` · `ui.newWorkspace.action/contextMenu` · `reload-config`
> **Customizes:** how new work gets started

---

## 🗣 The prompt

> "Give me one-tap ways to spawn agents: a **Codex** entry in the Command Palette, a **Codex** button on the tab bar, and make the **+** button's right-click menu offer 'New Terminal / New Browser / Spawn Codex'."

## 🎯 What it showcases

cmux's **action registry**. You declare reusable `actions` once, then *wire* them into the surfaces you use: the Command Palette (⌘⇧P), the surface tab-bar buttons, the new-workspace (+) button, and shortcuts. The terminal's entry points become yours to define.

## 🧠 What the orchestrator does (answer key)

```jsonc
// ~/.config/cmux/cmux.json  (or project-local .cmux/cmux.json)
{
  "actions": {
    "codex-new-tab": {
      "type": "agent", "agent": "codex",
      "title": "Codex", "subtitle": "Start Codex in this pane",
      "target": "newTabInCurrentPane", "palette": true,
      "icon": { "type": "symbol", "name": "terminal" }
    }
  },
  "ui": {
    "surfaceTabBar": {
      "buttons": [ "cmux.newTerminal", "cmux.newBrowser",
        { "action": "codex-new-tab", "title": "Codex", "icon": { "type": "symbol", "name": "terminal" } } ]
    },
    "newWorkspace": {
      "contextMenu": [
        { "action": "cmux.newTerminal", "title": "New Terminal" },
        { "action": "cmux.newBrowser",  "title": "New Browser" },
        { "type": "separator" },
        { "action": "codex-new-tab",    "title": "Spawn Codex" }
      ]
    }
  }
}
```

```bash
cmux config doctor      # validate the JSONC
cmux reload-config      # apply live
```

## 🔑 Concepts introduced

- **`actions`** are reusable and typed (`agent`, `workspaceCommand`, …); `palette: true` surfaces them in ⌘⇧P.
- **Wire, don't hardcode.** The same action ID drops into `ui.surfaceTabBar.buttons`, `ui.newWorkspace.contextMenu`, and shortcuts. Keep built-ins (`cmux.newTerminal`, `cmux.newBrowser`, `cmux.splitRight`) only where you still want them.
- **Project-scoped wins.** A `.cmux/cmux.json` action overrides a global one with the same ID, so a repo can ship its own launch buttons.

## ✅ Done when

- [ ] "Codex" appears in the Command Palette and on the tab bar.
- [ ] The **+** right-click menu lists New Terminal / New Browser / Spawn Codex.
