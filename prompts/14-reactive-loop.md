# 14 · Reactive Loop (Don't Poll)

> **Tier 3 — Fleet Orchestration**  ·  Complexity `▰▰▰▰▰`
> **Thesis:** a real orchestrator is **event-driven** — it reacts to the fleet instead of busy-waiting on it.
> **cmux verbs:** `events --name --no-heartbeat --cursor-file` · `read-screen` · `send`
> **Agents under control:** a work queue dispatched across agents as they free up

---

## 🗣 The prompt

> "Here's a queue of ten tasks and three agents. Don't poll the screens. **Subscribe to cmux's event stream**, and the moment an agent finishes (its surface notifies or goes idle), read that agent, hand it the next task from the queue, and keep going until the queue is empty."

## 🎯 What it showcases

The difference between a script and a *system*. cmux emits a reconnectable NDJSON event stream — surface selection/focus, pane changes, and (with hooks) agent-completion notifications. The orchestrator consumes it and dispatches reactively, with a **cursor file** so it never misses or double-processes an event.

## 🧠 What the orchestrator does (answer key)

```bash
# Resume-safe subscription: --cursor-file persists the last seq so restarts continue cleanly.
# Filter to the events that mean "an agent wants attention":
#   agent.hook         — fired by an agent's lifecycle hooks (e.g. Stop) once hooks are installed
#   notification.created — an agent (or you) raised a cmux notification
cmux events \
  --name agent.hook \
  --name notification.created \
  --no-heartbeat \
  --cursor-file /tmp/fleet.cursor | while read -r evt; do

    SURF=$(jq -r '.surface_id // .payload.surface_id // empty' <<<"$evt")
    [ -z "$SURF" ] && continue

    # An agent signalled — read it, then feed it the next queued task.
    cmux read-screen --surface "$SURF" --lines 20
    NEXT=$(pop_task_from_queue)               # your queue; empty string when drained
    if [ -n "$NEXT" ]; then
      cmux send --surface "$SURF" "$NEXT"; cmux send-key --surface "$SURF" enter
    else
      cmux close-surface --surface "$SURF"    # done — reclaim the pane
    fi
done
```

## 🔑 Concepts introduced

- **`cmux events`** streams `{name, seq, surface_id, workspace_id, payload}` as newline-delimited JSON.
- **`--cursor-file`** records the last `seq`; reconnect resumes exactly where you left off (also `--after <seq>`, `--reconnect`).
- **Completion signal.** Pair with prompt 15's notification hooks so "agent finished" is a first-class event, not a guess.
- **Full cookbook.** Read-to-decide, the `wait-for` rendezvous, and the complete push-vs-poll guide live in [`PATTERNS-read-and-notify.md`](PATTERNS-read-and-notify.md).

## ✅ Done when

- [ ] No `read-screen` happens until an event fires.
- [ ] Each agent is fed a new task immediately after it frees up.
- [ ] The queue drains and idle surfaces are closed.
