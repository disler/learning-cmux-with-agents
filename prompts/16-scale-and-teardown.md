# 16 · Scale & Teardown

> **Tier 3 — Fleet Orchestration**  ·  Complexity `▰▰▰▰▱`
> **Thesis:** fleets are **elastic** — the orchestrator grows them, prunes the slow, reassigns, and reclaims resources.
> **cmux verbs:** `top --sort cpu` · `close-surface` · `send` (reassign) · `workspace close`
> **Agents under control:** six agents on a task batch, scaled down to the survivors

---

## 🗣 The prompt

> "Launch six agents on this batch of tasks. After two minutes, look at which ones are still chewing CPU with nothing to show, close the slowest two, reassign their unfinished tasks to agents that already finished, and when the batch is done, tear the whole fleet down."

## 🎯 What it showcases

Resource-aware orchestration. `cmux top` exposes per-surface CPU/memory, so the orchestrator can make **scheduling decisions** — kill stragglers, rebalance work onto idle agents, and free panes — exactly like a job scheduler, but over live coding agents.

## 🧠 What the orchestrator does (answer key)

```bash
read WS S0 < <(cmux workspace create --name batch --cwd "$PWD" --env-file ./.env --json \
               | jq -r '[.workspace_ref, .surface_ref] | @tsv')
SURF=("$S0")
for i in 1 2 3 4 5; do
  dir=$([ $((i % 2)) -eq 0 ] && echo right || echo down)
  last="${SURF[$(( ${#SURF[@]} - 1 ))]}"          # portable "last element" (no bash-4 negative index)
  SURF+=("$(cmux new-split "$dir" --surface "$last" --json | jq -r .surface_ref)")
done
for s in "${SURF[@]}"; do cmux send --surface "$s" "claude"; cmux send-key --surface "$s" enter; done
sleep 8
# …assign tasks 1..6 (one send per surface)…

# After a deadline, rank surfaces by CPU and prune the two hottest-but-stuck.
# TSV columns: cpu_percent  memory_bytes  process_count  kind  ref  parent_ref  title
cmux top --processes --sort cpu --format tsv > /tmp/fleet-top.tsv
SLOW=$(awk -F'\t' '$4=="surface"{print $5}' /tmp/fleet-top.tsv | head -2)   # 2 hottest surfaces
for s in $SLOW; do cmux close-surface --surface "$s"; done

# Reassign their tasks to a finished agent, then tear everything down at the end.
cmux send --surface "${SURF[0]}" "Also finish: <reassigned task>"; cmux send-key --surface "${SURF[0]}" enter
# … when the batch completes:
cmux workspace close --workspace "$WS"
```

## 🔑 Concepts introduced

- **`top --sort cpu --format tsv`** gives machine-readable per-surface resource usage for scheduling.
- **Prune + reassign.** Closing a surface frees the slot; the unfinished task moves to a free agent via `send`.
- **One-shot teardown.** `workspace close` reclaims every pane and process in the fleet at once.

## ✅ Done when

- [ ] Six agents launch; `top` ranks them by CPU.
- [ ] The two slowest are closed and their work is reassigned.
- [ ] `workspace close` leaves no fleet surfaces behind in `cmux tree`.
