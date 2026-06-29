# 26 · Color-Code & Label the Fleet

> **Customization**  ·  Complexity `▰▰▱▱▱`
> **Thesis:** customization is **ad-hoc and per-workspace** — every sidebar row can carry its own color, pill, icon, and name, set live from a script.
> **cmux verbs:** `workspace-action set-color` · `set-status --color --icon` · `rename-workspace` · `workspace-action set-description`
> **Customizes:** each workspace's identity, independently

---

## 🗣 The prompt

> "I'm about to run a dozen agents. Make them scannable: give each workspace its own **color**, a **role pill** with an **icon** (reviewer / fixer / tester), and a clear name, so I can tell them apart at a glance."

## 🎯 What it showcases

The most-asked customization question: *can different workspaces look different, on the fly?* Yes. Workspace identity (color, name, description, status pill, icon, progress) is **per-workspace and fully scriptable** — no config file, no restart. This is how 20 agents stay legible.

## 🧠 What the orchestrator does (answer key)

```bash
color_role() {                          # $1=ws  $2=ColorName  $3=role  $4=hex  $5=sf-symbol
  cmux workspace-action --action set-color --workspace "$1" --color "$2"
  cmux set-status role "$3" --workspace "$1" --color "$4" --icon "$5"
}
color_role "$WS_REVIEWER" Blue  reviewer "#1565C0" eye
color_role "$WS_FIXER"    Green fixer    "#196F3D" wrench.and.screwdriver
color_role "$WS_TESTER"   Amber tester   "#7D6608" checkmark.seal

# names + descriptions are per-workspace too:
cmux rename-workspace --workspace "$WS_FIXER" "fixer · auth"
cmux workspace-action --action set-description --workspace "$WS_FIXER" --description "patches the login bug"
```

## 🔑 Concepts introduced

- **16 named colors** (`Red, Crimson, Orange, Amber, Olive, Green, Teal, Aqua, Blue, Navy, Indigo, Purple, Magenta, Rose, Brown, Charcoal`) or any `#RRGGBB` hex.
- **`set-status <key> <value> --color --icon --priority`** — a labeled pill per workspace; `--icon` takes an **SF Symbol** name.
- **Per-workspace, not global.** Color/name/description/pill belong to the workspace and persist; they don't touch any other row. (Terminal *theme/font* is global — see prompt 27.)

## ✅ Done when

- [ ] Each workspace shows a distinct sidebar color + a role pill with an icon.
- [ ] `cmux list-status --workspace <ref>` reflects each one's role.
