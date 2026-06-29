# 21 · Multi-Window Command Center

> **Tier 5 — Scale, Remote, Resilience**  ·  Complexity `▰▰▰▰▰`
> **Thesis:** the orchestrator scales *out* — multiple macOS windows, each a themed fleet, all one control plane.
> **cmux verbs:** `new-window` · `move-workspace-to-window` · `focus-window` · `list-windows`
> **Agents under control:** three fleets across three windows

---

## 🗣 The prompt

> "Don't cram everything into one window. Open three macOS windows — **frontend**, **backend**, and **ops** — put a small agent fleet in each, route the right tasks to each window, then gather all the results into one summary for me."

## 🎯 What it showcases

The top of the hierarchy: **Window**. When one window gets crowded, the orchestrator spreads fleets across several real macOS windows (one per concern) and still drives them all through the same socket — physical separation, single brain.

## 🧠 What the orchestrator does (answer key)

```bash
# One macOS window per concern; create and populate each in the same pass.
for name in frontend backend ops; do
  W=$(cmux new-window | awk '{print $2}')            # new-window prints: OK <window-uuid>
  read ws s < <(cmux workspace create --name "$name" --cwd "$PWD" --env-file ./.env \
                --window "$W" --json | jq -r '[.workspace_ref, .surface_ref] | @tsv')
  cmux send --surface "$s" "claude"; cmux send-key --surface "$s" enter
  # …split $ws into a small fleet and assign window-appropriate tasks…
done

cmux list-windows                       # confirm three windows, each with its fleet
# …read each window's agents and synthesize one cross-window summary…
```

## 🔑 Concepts introduced

- **`new-window`** opens an independent macOS window (own sidebar + workspaces); `--window <ref>` targets it.
- **`move-workspace-to-window`** relocates an existing workspace between windows.
- **One socket, many windows.** Every verb takes a `--window` route, so the orchestrator addresses any window deterministically.

## ✅ Done when

- [ ] `cmux list-windows` shows three windows.
- [ ] Each window holds its own agent fleet with window-appropriate tasks.
- [ ] The orchestrator returns one summary spanning all three.
