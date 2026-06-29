# 24 · Crash-Proof: Resume the Fleet

> **Tier 5 — Scale, Remote, Resilience**  ·  Complexity `▰▰▰▰▱`
> **Thesis:** a long-running fleet must **survive a restart** — layout rebuilt, every agent resumed on its own session.
> **cmux verbs:** `hooks setup` · `surface resume show` · `restore-session` · `autoResumeAgentSessions`
> **Agents under control:** a multi-agent fleet that lives through a quit + relaunch

---

## 🗣 The prompt

> "Make my fleet restart-proof. Install the resume hooks for every agent, start several agents working, then quit and relaunch cmux — and confirm the layout came back **and** each agent picked up its own session where it left off."

## 🎯 What it showcases

cmux's two-phase restore. **Phase 1** rebuilds windows/workspaces/panes from a JSON snapshot. **Phase 2** resumes *supported agents* from the native session IDs the hooks captured — not by replaying process state. The orchestrator verifies both halves.

## 🧠 What the orchestrator does (answer key)

```bash
# 1) Install hooks FIRST (they capture each agent's native session id as it runs).
cmux hooks setup --yes
cmux config doctor                                   # sanity-check config

# 2) Stand up a fleet and get them working (agent surfaces, not bare shells).
#    new-surface --provider makes them resume-aware.
read WS S < <(cmux workspace create --name durable --cwd "$PWD" --env-file ./.env --json \
              | jq -r '[.workspace_ref, .surface_ref] | @tsv')
cmux send --surface "$S" "claude"; cmux send-key --surface "$S" enter
# …give it a task so it has a real session…

cmux surface resume show --surface "$S"              # confirms a captured session BEFORE restart

# 3) Quit + relaunch (autoResumeAgentSessions defaults to true).
osascript -e 'tell application "cmux" to quit'
open -a cmux                                          # …or History ▸ Restore (⌘⇧O) / cmux restore-session

# 4) After relaunch, verify the layout + sessions returned.
cmux tree --all                                      # workspace 'durable' is back
cmux surface resume show                             # the agent resumed on its own session id
```

## 🔑 Concepts introduced

- **Hooks before agents.** Install `cmux hooks setup` once the agent CLI is on PATH, or there's no session id to capture.
- **`surface resume show|get`** reports what cmux will resume; **`restore-session`** (⌘⇧O) triggers a manual restore.
- **Boundary.** Only supported agents resume; tmux/vim/plain shells reopen fresh by design.

## ✅ Done when

- [ ] Hooks install cleanly.
- [ ] Before restart, `surface resume show` reports a captured session.
- [ ] After quit + relaunch, `cmux tree` shows the workspace back and the agent resumed.
