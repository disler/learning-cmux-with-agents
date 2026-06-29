# Patterns — Reading to Decide, and Getting Notified

Two questions every orchestrator hits: **"what is this agent doing right now?"** (read → decide) and **"tell me the moment something happens"** (get notified). cmux answers both with real primitives, and you only fall back to polling for the one case that genuinely needs it. Every snippet below was run against cmux `0.64.17`.

## TL;DR — when you're *pushed* vs. when you *poll*

| You want to know… | Mechanism | Push or poll? |
|---|---|---|
| "An agent finished / needs input" | `cmux events --name agent.hook --name notification.created` | **Push** — cmux streams you a line |
| "Block here until task X is done" | `cmux wait-for X`  ⇄  worker `cmux wait-for -S X` | **Push** — blocks, unblocks on signal |
| "Any notification, durably" | `cmux events --category notification --reconnect` | **Push** — survives restarts |
| "What did the agent actually *say*?" | `cmux read-screen --surface <ref> --scrollback` | **Poll** — content is free-form |
| "Is it done yet?" (no hooks installed) | `read-screen` loop until a marker | **Poll** — the honest fallback |

**Rule of thumb:** discrete *events* (finished, errored, notified) are **pushed** to you; free-form *content* (what an agent wrote, whether output contains "PASS") is **polled**, because there is no event for "the text now contains the word I care about." So no, you don't have to build a notification system or busy-poll for completion — you poll only to *read what was said*.

---

## 1 · Read to decide (parse output → branch)

The orchestrator's core skill: read a surface, extract a signal, act on it. Make the agent print a **sentinel** you can grep instead of parsing prose.

```bash
cmux send --surface "$S" 'pytest -q && echo VERDICT=GREEN || echo VERDICT=RED'
cmux send-key --surface "$S" enter
sleep 2

OUT=$(cmux read-screen --surface "$S" --scrollback --lines 200)
VERDICT=$(printf '%s\n' "$OUT" | grep -oE 'VERDICT=(GREEN|RED)' | tail -1 | cut -d= -f2)

case "$VERDICT" in
  GREEN) cmux send --surface "$S" "Great — open a PR.";        cmux send-key --surface "$S" enter ;;
  RED)   cmux send --surface "$S" "Tests failed — fix & rerun."; cmux send-key --surface "$S" enter ;;
  *)     echo "no verdict on screen yet; read again" ;;
esac
```
> Verified: `RESULT=PASS → DECISION: proceed`.

### Detect "the agent is waiting for me"
Agents pause on questions. Read for the prompt, then answer it:
```bash
SCREEN=$(cmux read-screen --surface "$S" --lines 40)
if printf '%s' "$SCREEN" | grep -qiE '\(y/n\)|approve\?|continue\?|\[Y/n\]|press enter'; then
  cmux send-key --surface "$S" enter        # or: cmux send --surface "$S" "yes"; cmux send-key … enter
fi
```

---

## 2 · Wait until a marker (content poll — the one honest poll)

With no completion hook, watch the screen until the work signals done. Prefer a sentinel echo over guessing when a TUI "looks idle."

```bash
wait_for_marker() {                 # $1=surface  $2=regex  $3=max polls (1s each)
  for i in $(seq 1 "${3:-60}"); do
    cmux read-screen --surface "$1" --lines 30 | grep -qE "$2" && return 0
    sleep 1
  done
  return 1                          # timed out
}

cmux send --surface "$S" 'long_build.sh; echo BUILD_DONE_$?'
cmux send-key --surface "$S" enter
wait_for_marker "$S" 'BUILD_DONE_[0-9]+' 120 && echo "build finished"
```
> Verified: detected the marker on the first poll. Keep `--lines` small so each poll is cheap.

---

## 3 · Get pushed: the event stream is your message bus

`cmux events` is a reconnectable NDJSON feed. Subscribe once and cmux **pushes you a line per event** — no polling.

```bash
cmux events \
  --name agent.hook \              # fired by agent lifecycle hooks (needs `cmux hooks setup`)
  --name notification.created \    # fired whenever anyone calls `cmux notify`
  --reconnect \                    # survive cmux restarts
  --cursor-file /tmp/cmux-fleet.seq | while read -r evt; do
    WS=$(jq -r '.workspace_id // empty'  <<<"$evt")
    SURF=$(jq -r '.surface_id  // empty' <<<"$evt")
    echo "→ attention on workspace=$WS surface=$SURF"
    cmux read-screen --surface "$SURF" --scrollback --lines 40   # the event is the doorbell; read the details
  done
```
> Verified: `cmux notify` pushed a `notification.created` event to the consumer instantly.
>
> **Privacy design (verified):** the event payload carries `workspace_id`, `surface_id`, `notification_id`, `is_read`, and content **lengths** — but `title`/`subtitle`/`body` are **redacted** (`redacted_fields`). The event is the *doorbell*; get the actual text from `cmux list-notifications` or by reading the surface.

Real event names from the live catalog: `agent.hook` · `notification.created` · `surface.created` · `surface.closed` · `surface.focused` · `pane.focused` · `workspace.created` · `workspace.prompt`.

---

## 4 · Get pushed: block on a rendezvous (`wait-for`)

When you want the orchestrator to **block until a specific task signals done** — no stream parsing, no polling — use a named token.

```bash
# Orchestrator: block (up to 10 min) until the "migration" token fires.
cmux wait-for migration --timeout 600 && echo "migration done — continue"

# The worker (or its Stop hook) signals the token the moment it finishes:
cmux wait-for -S migration
```
> Verified: the waiter blocked, then unblocked the instant the signal fired. Use one token per task (`build-api`, `seed-db`) and background a waiter per token to fan several workers back in.

---

## 5 · Make completion an event: wire the Stop hook

`cmux events` only sees `agent.hook` if the agent's lifecycle hooks call cmux. `cmux hooks setup` wires this for supported agents (Claude Code, Codex, Copilot, OpenCode, …) — the hook is just a `cmux notify` on stop:

```bash
cmux hooks setup --yes        # installs Stop/agentStop hooks for every agent CLI on PATH
```
After that, an agent finishing a turn fires `cmux notify`, which records in the panel, raises a desktop alert (only when you're looking elsewhere), **and** emits the `notification.created` event your stream (pattern 3) catches. Manual equivalent for any script or non-hooked tool:
```bash
command -v cmux >/dev/null && cmux notify --title "worker-7" --body "done" \
  || osascript -e 'display notification "done" with title "worker-7"'   # macOS fallback
```

---

## Putting it together — a reactive dispatcher (no polling for completion)

```bash
cmux hooks setup --yes
cmux events --name agent.hook --name notification.created --reconnect \
            --cursor-file /tmp/cmux-q.seq | while read -r evt; do
  SURF=$(jq -r '.surface_id // empty' <<<"$evt"); [ -z "$SURF" ] && continue
  OUT=$(cmux read-screen --surface "$SURF" --scrollback --lines 60)        # read to decide
  if grep -qiE 'error|failed' <<<"$OUT"; then
     cmux send --surface "$SURF" "Fix the failure above, then say DONE."; cmux send-key --surface "$SURF" enter
  else
     NEXT=$(pop_queue) && { cmux send --surface "$SURF" "$NEXT"; cmux send-key --surface "$SURF" enter; } \
                       || cmux close-surface --surface "$SURF"             # queue drained → reclaim the pane
  fi
done
```

This is prompts **[14 · Reactive Loop](14-reactive-loop.md)** and **[15 · Race & Notify](15-race-and-notify.md)** fused: pushed by events, decisions made by reading, polling only the content you actually have to inspect.
