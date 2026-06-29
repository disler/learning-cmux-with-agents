# 22 · Organized Sidebar at Scale

> **Tier 5 — Scale, Remote, Resilience**  ·  Complexity `▰▰▰▰▱`
> **Thesis:** at twenty agents, *legibility* is a feature — the orchestrator groups and colors so humans can still navigate.
> **cmux verbs:** `workspace group` · `workspace create --group` · `workspace-action set-color`
> **Agents under control:** twenty agents, organized into collapsible, colored sections

---

## 🗣 The prompt

> "I'm about to run twenty agents. Keep my sidebar legible: organize them into named, colored, collapsible groups — **reviewers** (blue), **fixers** (green), **testers** (amber) — so I can collapse a group and scan the rest."

## 🎯 What it showcases

Workspace **groups**: named, collapsible sidebar sections, each owned by an anchor workspace and stylable with its own icon and color. This is how a 20-agent run stays a glanceable org chart instead of an unreadable wall of tabs.

## 🧠 What the orchestrator does (answer key)

```bash
# One named, colored, collapsible group per role.
# The group header IS its anchor workspace; closing the anchor dissolves the group.
setup_group() {                         # $1=name  $2=hex  $3=member-count
  local G ws s
  G=$(cmux workspace-group create --name "$1" --json | jq -r '.group.ref')   # → workspace_group:N
  cmux workspace-group set-color "$G" --hex "$2"
  cmux workspace-group set-icon  "$G" --symbol person.2.fill
  for i in $(seq 1 "$3"); do
    ws=$(cmux workspace-group new-workspace "$G" --placement end | grep -oE 'workspace:[0-9]+' | head -1)
    s=$(cmux list-pane-surfaces --workspace "$ws" --json | jq -r '.surfaces[0].ref')
    cmux send --surface "$s" "claude"; cmux send-key --surface "$s" enter
  done
}
setup_group reviewers "#1565C0" 6       # blue
setup_group fixers    "#196F3D" 7       # green
setup_group testers   "#7D6608" 7       # amber

cmux workspace-group list               # confirm the three groups
# cmux workspace-group collapse <group> # collapse one to scan the rest
```

## 🔑 Concepts introduced

- **Groups are anchor-owned.** One workspace owns the group; closing the anchor dissolves it (members become ungrouped).
- **`workspace create --group <ref> --group-placement afterCurrent|top|end`** drops a new agent straight into a section.
- **Color/icon per group or workspace** (`workspace-action set-color`, SF Symbol icons) — turn the sidebar into a labeled board. Group config persists in `cmux.json`.

## ✅ Done when

- [ ] Agents appear under named, colored groups in the sidebar.
- [ ] Collapsing a group hides its members; the rest stay readable.
