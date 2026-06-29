# 13 · Live Status Board

> **Tier 3 — Fleet Orchestration**  ·  Complexity `▰▰▰▰▱`
> **Thesis:** a fleet you can't see is a fleet you can't trust — the orchestrator paints a **dashboard** as it works.
> **cmux verbs:** `set-status --color` · `set-progress --label` · `log` · `list-status`
> **Agents under control:** N agents, each a sidebar workspace with live metadata

---

## 🗣 The prompt

> "Run four agents on four refactors, but give each its **own sidebar workspace**, and keep the sidebar live: show each one's status as a colored pill (**working** = blue, **done** = green, **error** = red), a progress bar, and a one-line log of what it's doing. I want to glance at the sidebar and know the whole fleet's state."

## 🎯 What it showcases

cmux's sidebar is programmable telemetry. `set-status`, `set-progress`, and `log` turn each workspace row into a live readout — so a human (or the orchestrator itself) reads fleet health at a glance instead of scraping terminals.

## 🧠 What the orchestrator does (answer key)

```bash
TASKS=("refactor auth" "refactor db" "refactor api" "refactor ui")
declare -a WS SURF
for i in "${!TASKS[@]}"; do
  read w s < <(cmux workspace create --name "agent-$i" --cwd "$PWD" --env-file ./.env --json \
               | jq -r '[.workspace_ref, .surface_ref] | @tsv')
  WS[$i]=$w; SURF[$i]=$s
  cmux set-status state "working" --workspace "$w" --color "#1565C0"   # blue pill
  cmux set-progress 0.0 --label "starting" --workspace "$w"
  cmux log --workspace "$w" "assigned: ${TASKS[$i]}"
  cmux send --surface "$s" "claude"; cmux send-key --surface "$s" enter
done
sleep 8

for i in "${!TASKS[@]}"; do
  cmux send --surface "${SURF[$i]}" "${TASKS[$i]} — keep it small and runnable."
  cmux send-key --surface "${SURF[$i]}" enter
  cmux set-progress 0.5 --label "in progress" --workspace "${WS[$i]}"
done

# …as each agent finishes (see prompt 14/15 for the signal), flip its pill:
# cmux set-status state "done"  --workspace "${WS[$i]}" --color "#196F3D"   # green
# cmux set-progress 1.0 --label "complete" --workspace "${WS[$i]}"
# on failure:
# cmux set-status state "error" --workspace "${WS[$i]}" --color "#C0392B"   # red
```

## 🔑 Concepts introduced

- **`set-status KEY VALUE --color #hex [--icon NAME] [--priority N]`** — a named pill on the workspace row.
- **`set-progress 0.0–1.0 --label`** — a progress bar in the sidebar; `clear-progress` removes it.
- **`log` / `list-log`** — an append-only activity line per workspace.

## ✅ Done when

- [ ] Four workspaces appear in the sidebar, each with a colored status pill + progress bar.
- [ ] Pills transition blue → green (or red) as agents finish.
- [ ] `cmux list-status --workspace <ref>` reflects the current state.
