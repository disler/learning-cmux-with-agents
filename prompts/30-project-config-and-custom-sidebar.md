# 30 · Make It Yours: Project Config + Custom Sidebar

> **Customization**  ·  Complexity `▰▰▰▰▱`
> **Thesis:** the deep end — a repo carries its own cmux behavior, and you can **rebuild the sidebar itself** from a hot-reloading file.
> **cmux verbs:** `.cmux/cmux.json` (project override) · `~/.config/cmux/sidebars/<name>.swift` · `cmux sidebar validate/select`
> **Customizes:** per-project behavior + the sidebar UI

---

## 🗣 The prompt

> "Two things. Make this repo's cmux behavior travel with it (its own layouts/actions/dock). And build me a **custom sidebar** that lists my workspaces with a live clock and each one's PR status, where clicking a row jumps to it."

## 🎯 What it showcases

The two strongest customization levers. **Project-local `.cmux/cmux.json`** layers repo-specific actions, commands, UI wiring, and notification hooks on top of your globals — so a checkout reconfigures cmux for that project. And **custom sidebars** let you replace the sidebar UI with a small SwiftUI-style file that binds to **live cmux state** (workspaces, PRs, clock) and runs real `cmux` commands on tap — hot-reloaded on save, no build step.

## 🧠 What the orchestrator does (answer key)

**A) Per-project behavior** — commit `.cmux/cmux.json` (overrides globals by ID/name, travels with the repo):

```jsonc
// .cmux/cmux.json — shipped in the repo
{ "commands": [ { "name": "review", "workspace": { "name": "Review", "cwd": ".",
      "layout": { "direction": "horizontal", "children": [
        { "pane": { "surfaces": [ { "type": "terminal", "command": "git log --oneline -20" } ] } },
        { "pane": { "surfaces": [ { "type": "browser", "url": "https://github.com/OWNER/REPO/pulls" } ] } } ] } } } ] }
```

**B) A custom sidebar** — a hot-reloading SwiftUI-style file bound to live data:

```bash
mkdir -p ~/.config/cmux/sidebars
cat > ~/.config/cmux/sidebars/fleet.swift <<'SWIFT'
VStack(alignment: .leading, spacing: 8) {
    Text("Fleet").font(.title3).bold()
    Text(clock.time).font(.caption).foregroundColor(.secondary)
    Divider()
    Reorderable(workspaces, move: "workspace.reorder") { w in
        Button(action: { cmux("workspace.select", workspace_id: w.id) }) {
            HStack {
                Text(w.selected ? "●" : "○").foregroundColor(w.color ?? .secondary)
                Text(w.title)
                Spacer()
                if let pr = w.pr { Text("#\(pr.number) \(pr.status)").font(.caption2) }
            }.padding(4)
        }
    }
}
SWIFT
cmux sidebar validate fleet && cmux sidebar select fleet   # enable beta: customSidebars.beta.enabled
```

## 🔑 Concepts introduced

- **`.cmux/cmux.json`** = per-repo override; project actions/commands win over global ones of the same ID/name. Don't put global app *preferences* there — only repo behavior.
- **Custom sidebars** are interpreted at runtime (no Xcode/build): bind to `workspaces` / `clock` / `pr` data, run `cmux(...)` on tap, hot-reload on save. `cmux docs sidebars` is the full authoring contract.
- **Graceful degradation.** Unsupported syntax is skipped, never crashes; a broken save keeps the last good render.

## ✅ Done when

- [ ] Opening the repo gives it its own `review` layout/behavior via `.cmux/cmux.json`.
- [ ] The custom **fleet** sidebar shows live workspaces + clock + PR status, and a row tap selects that workspace.
