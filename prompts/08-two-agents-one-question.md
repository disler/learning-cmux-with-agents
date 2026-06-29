# 08 · Two Agents, One Question

> **Tier 2 — Driving a Single Agent**  ·  Complexity `▰▰▰▱▱`
> **Thesis:** the orchestrator is a *router* — it can broadcast one intent to many agents and reconcile their replies.
> **cmux verbs:** `new-split` · `send` (×2) · `read-screen` (×2)
> **Agents under control:** **Claude Code** + **pi**, side by side

---

## 🗣 The prompt

> "Put **Claude Code** and **pi** side by side in one workspace. Ask both the same question — *'In two sentences, what's the difference between a process and a thread?'* — then read both answers and tell me where they agree and where they differ."

## 🎯 What it showcases

The first true *multi-agent* move: two different models, same prompt, **one orchestrator comparing them**. This is the primitive behind ensembles, A/B model evals, and "ask three agents and vote" patterns.

## 🧠 What the orchestrator does (answer key)

```bash
read WS L < <(cmux workspace create --name duel --cwd "$PWD" --env-file ./.env --json \
              | jq -r '[.workspace_ref, .surface_ref] | @tsv')
R=$(cmux new-split right --surface "$L" --json | jq -r .surface_ref)

cmux send --surface "$L" "claude"; cmux send-key --surface "$L" enter
cmux send --surface "$R" "pi";     cmux send-key --surface "$R" enter
sleep 6

Q="In two sentences, what's the difference between a process and a thread?"
for S in "$L" "$R"; do
  cmux send --surface "$S" "$Q"; cmux send-key --surface "$S" enter
done
sleep 10

echo "===== CLAUDE ====="; cmux read-screen --surface "$L" --lines 50
echo "===== PI ====="    ; cmux read-screen --surface "$R" --lines 50
# …then the orchestrator diffs the two answers in its own head and reports.
```

## 🔑 Concepts introduced

- **Broadcast.** A simple `for S in …; do cmux send …; done` fans one prompt to N agents.
- **Heterogeneous fleet.** Different agent binaries (`claude`, `pi`, `codex`, `gemini`) coexist as peers — the control verbs are identical for all of them.
- **Reconcile.** The orchestrator's value-add is reading both and *synthesizing*, not just relaying.

## ✅ Done when

- [ ] Two agents run side by side, both answered the same question.
- [ ] The orchestrator returns an agree/differ comparison.
