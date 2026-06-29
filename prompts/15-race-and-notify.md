# 15 · Race & Notify

> **Tier 3 — Fleet Orchestration**  ·  Complexity `▰▰▰▰▱`
> **Thesis:** when agents compete, the orchestrator wants **the first good answer** — and a ping the instant it lands.
> **cmux verbs:** `notify` · Claude `Stop` hook → `cmux notify` · `jump-to-unread` · `list-notifications` · `close-surface`
> **Agents under control:** three agents racing the same task

---

## 🗣 The prompt

> "Give the same hard task to three agents as a race. Wire each so it fires a cmux notification the moment it's done. Jump me to whichever finishes first, take its answer, and stop the other two."

## 🎯 What it showcases

Completion as a signal. An agent's lifecycle **`Stop` hook** calls `cmux notify`, which lands in the notification panel and (when you're looking elsewhere) raises a clickable alert. The orchestrator races three agents, acts on the first notification, and tears down the losers — no polling, no waiting on the slowest.

## 🧠 What the orchestrator does (answer key)

```bash
# Each agent's Stop hook runs this (installed via `cmux hooks setup`):
#   ~/.claude/hooks/cmux-notify.sh →  cmux notify --title "Claude Code" --body "Session complete"

read WS S1 < <(cmux workspace create --name race --cwd "$PWD" --env-file ./.env --json \
               | jq -r '[.workspace_ref, .surface_ref] | @tsv')
S2=$(cmux new-split right --surface "$S1" --json | jq -r .surface_ref)
S3=$(cmux new-split down  --surface "$S1" --json | jq -r .surface_ref)

for S in "$S1" "$S2" "$S3"; do cmux send --surface "$S" "claude"; cmux send-key --surface "$S" enter; done
sleep 8
TASK="Find and fix the highest-severity bug in this repo; output a unified diff."
for S in "$S1" "$S2" "$S3"; do cmux send --surface "$S" "$TASK"; cmux send-key --surface "$S" enter; done

# Wait for the FIRST completion notification, then jump to it and read it.
cmux events --name notification.created --no-heartbeat --limit 1 >/dev/null
cmux jump-to-unread                       # focuses the winner's workspace/surface
WINNER=$(cmux identify --json | jq -r .surface_ref)
cmux read-screen --surface "$WINNER" --lines 60

# Stop the losers.
for S in "$S1" "$S2" "$S3"; do [ "$S" != "$WINNER" ] && cmux close-surface --surface "$S"; done
```

## 🔑 Concepts introduced

- **`cmux notify --title --subtitle --body [--workspace|--surface]`** — the completion primitive; lands in the panel (Received → Unread → Read → Cleared).
- **`jump-to-unread`** (⌘⇧U) navigates straight to the most recent unread agent.
- **Quiet by default.** Desktop alerts are suppressed while you're already looking at that workspace — you're only pinged for agents you're *not* watching.

## ✅ Done when

- [ ] Three agents race the same task.
- [ ] The first to finish raises a notification; the orchestrator jumps to it and reads it.
- [ ] The other two surfaces are closed.
