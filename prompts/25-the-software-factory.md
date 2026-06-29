# 25 · The Software Factory (Capstone)

> **Tier 5 — Scale, Remote, Resilience**  ·  Complexity `▰▰▰▰▰`
> **Thesis:** ⭐ everything at once. One orchestrator runs an autonomous, multi-window, multi-agent, browser-verified pipeline — a software factory in one Ghostty terminal.
> **cmux verbs:** _all of them_ — `new-window` · `workspace create` · `new-split` · `send`/`read-screen` · `set-status`/`set-progress` · `events` · `notify` · `browser` · `diff` · `workspace close`
> **Agents under control:** a full fleet across windows, plus a browser verifier

---

## 🗣 The prompt

> "Be my build lead. Take this feature request and ship it: **plan** the work, open a **window per subsystem**, **fan out** the implementation to a fleet of agents (roughly one per file), keep a **live status board** so I can watch, **run the tests** as each agent finishes, **browser-verify** the running app, **notify** me with the result, **collect every agent's diff** into one PR-ready bundle, and **tear the fleet down** when it's green."

## 🎯 What it showcases

The thesis, fully assembled. Every capability in this guide — topology, fleets, credentials, dashboards, events, notifications, the browser, multi-window scale, and teardown — composed into a single autonomous loop driven from one primary agent.

## 🧠 What the orchestrator does (answer key — composition of prompts 01–24)

```bash
# PLAN ───────────────────────────────────────────────
#   Orchestrator decomposes the request → files, subsystems, test plan.

# FAN OUT (prompts 11,12,21) ─────────────────────────
for subsystem in frontend backend; do
  W=$(cmux new-window | awk '{print $2}')                  # prints: OK <window-uuid>
  for file in $(files_for "$subsystem"); do
    read ws s < <(cmux workspace create --name "$file" --cwd "$PWD" --env-file ./.env \
                  --window "$W" --json | jq -r '[.workspace_ref,.surface_ref]|@tsv')
    cmux set-status state working --workspace "$ws" --color "#1565C0"     # prompt 13
    cmux send --surface "$s" "claude"; cmux send-key --surface "$s" enter
    cmux send --surface "$s" "Implement $file per the spec. Keep it small and tested."
    cmux send-key --surface "$s" enter
  done
done

# REACT (prompts 14,15) ──────────────────────────────
cmux events --name agent.hook --name notification.created --no-heartbeat --cursor-file /tmp/factory.cursor | while read -r evt; do
  S=$(jq -r '.surface_id // empty' <<<"$evt"); [ -z "$S" ] && continue
  cmux send --surface "$S" "Run the tests for your change; paste failures."; cmux send-key --surface "$S" enter
  # flip the board green/red based on results:
  cmux set-status state done --workspace "$(ws_of "$S")" --color "#196F3D"
done

# BROWSER-VERIFY (prompts 18,19) ─────────────────────
B=$(cmux new-pane --type browser --url "http://localhost:5173" --json | jq -r .surface_ref)
cmux browser "$B" navigate "http://localhost:5173" --snapshot-after
cmux browser "$B" errors list
cmux browser "$B" screenshot --out /tmp/factory-proof.png

# REPORT + COLLECT (prompts 04,15) ───────────────────
cmux notify --title "Factory" --body "Feature green ✔ — 0 console errors, tests passing"
git diff > /tmp/feature.patch                               # collect the fleet's edits into one bundle
cmux diff /tmp/feature.patch --title "Feature — review"     # …and open it in cmux's diff viewer to review

# TEARDOWN (prompts 05,16) ───────────────────────────
for w in $(cmux list-windows --json | jq -r '.[].ref'); do : ; done   # close fleets when green
```

## 🔑 Concepts introduced

- **Composition over novelty.** Nothing here is a new verb — it's prompts 01–24 wired into one loop.
- **`cmux diff --source last-turn`** harvests the agents' edits into a single reviewable patch.
- **Autonomy with a human seat.** The status board + notifications keep you in the loop without putting you in the path.

## ✅ Done when

- [ ] A feature is planned, fanned out across windows, and implemented by a fleet.
- [ ] The status board tracks each agent; tests run on completion; the browser verifies the app.
- [ ] You get one notification, one collected diff bundle, and a clean teardown.
