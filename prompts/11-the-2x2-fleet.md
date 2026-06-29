# 11 · The 2×2 Fleet

> **Tier 3 — Fleet Orchestration**  ·  Complexity `▰▰▰▰▱`
> **Thesis:** ⭐ the headline. One orchestrator boots **four different coding agents at once**, broadcasts a task, and reads them all.
> **cmux verbs:** `workspace create --env-file` · `new-split` ×3 · `send`/`send-key` ×4 · `read-screen` ×4
> **Agents under control:** **Claude Code · Codex · Gemini · pi**

---

## 🗣 The prompt

> "Stand up four coding agents in a 2×2 grid — **Claude Code**, **Codex**, **Gemini**, and **pi** — in a workspace called **fleet** with my `.env` loaded. Give all four the same task: *'List the top 3 security risks you can find in this repo.'* Then read all four answers back and tell me which risks they agree on."

## 🎯 What it showcases

This is the picture on the cover: a primary agent operating *a whole slew of agents* through one terminal. Four heterogeneous models, one prompt, one control loop — `send` to push, `read-screen` to pull. Add `close-surface` and you have the full lifecycle.

## 🧠 What the orchestrator does (answer key)

```bash
# 0 — one workspace, keys loaded, captured with its first surface (A).
read WS A < <(cmux workspace create --name fleet --cwd "$PWD" --env-file ./.env --json \
              | jq -r '[.workspace_ref, .surface_ref] | @tsv')

# 1 — split A into a 2×2; each split returns the new surface ref.
B=$(cmux new-split right --surface "$A" --json | jq -r .surface_ref)
C=$(cmux new-split down  --surface "$A" --json | jq -r .surface_ref)
D=$(cmux new-split down  --surface "$B" --json | jq -r .surface_ref)

# 2 — boot four DIFFERENT agents, one per pane.
cmux send --surface "$A" "claude"; cmux send-key --surface "$A" enter
cmux send --surface "$B" "codex";  cmux send-key --surface "$B" enter
cmux send --surface "$C" "gemini"; cmux send-key --surface "$C" enter
cmux send --surface "$D" "pi";     cmux send-key --surface "$D" enter
sleep 8

# 3 — broadcast one task to all four.
Q="List the top 3 security risks you can find in this repo."
for S in "$A" "$B" "$C" "$D"; do
  cmux send --surface "$S" "$Q"; cmux send-key --surface "$S" enter
done
sleep 15

# 4 — read every agent back.
for S in "$A" "$B" "$C" "$D"; do echo "===== $S ====="; cmux read-screen --surface "$S" --lines 40; done
```

## 🔑 Concepts introduced

- **The fleet is just Tier-1 verbs × N.** Nothing new is needed to go from one agent to four — only refs to thread through.
- **Heterogeneous by default.** `claude`/`codex`/`gemini`/`pi` are peers; swap any of them freely.
- **Panes vs. tabs vs. windows.** This packs four agents into one 2×2 workspace; the next prompts spread them across sidebar workspaces (13) and macOS windows (21).

## ✅ Done when

- [ ] `cmux tree --all` shows workspace `fleet` with four agent surfaces.
- [ ] All four were prompted and produced answers.
- [ ] The orchestrator returns the risks the agents **agree** on.
