# 12 · Fan-Out / Fan-In

> **Tier 3 — Fleet Orchestration**  ·  Complexity `▰▰▰▰▱`
> **Thesis:** the orchestrator *partitions* work — each agent gets a different slice, results merge into one.
> **cmux verbs:** `new-split` · per-surface `send` (distinct prompts) · `read-screen` ×N
> **Agents under control:** four agents, four assignments

---

## 🗣 The prompt

> "Split this repo's work four ways. Give each of four agents one top-level directory — `src/`, `tests/`, `docs/`, and `scripts/` — and have each summarize *only its directory* in five bullets. Then collect all four summaries into a single map of the codebase."

## 🎯 What it showcases

Divide-and-conquer. Where prompt 11 *broadcasts* one task, this **shards** a big task into independent units, runs them in parallel, and **reduces** the outputs — the map/reduce pattern, expressed in terminals.

## 🧠 What the orchestrator does (answer key)

```bash
read WS S1 < <(cmux workspace create --name shard --cwd "$PWD" --env-file ./.env --json \
               | jq -r '[.workspace_ref, .surface_ref] | @tsv')
S2=$(cmux new-split right --surface "$S1" --json | jq -r .surface_ref)
S3=$(cmux new-split down  --surface "$S1" --json | jq -r .surface_ref)
S4=$(cmux new-split down  --surface "$S2" --json | jq -r .surface_ref)

cmux send --surface "$S1" "claude"; cmux send --surface "$S2" "claude"
cmux send --surface "$S3" "pi";     cmux send --surface "$S4" "pi"
for S in "$S1" "$S2" "$S3" "$S4"; do cmux send-key --surface "$S" enter; done
sleep 8

# DIFFERENT assignment per surface — this is the fan-out.
assign() { cmux send --surface "$1" "Summarize ONLY the $2 directory in 5 bullets."; cmux send-key --surface "$1" enter; }
assign "$S1" "src/" ; assign "$S2" "tests/" ; assign "$S3" "docs/" ; assign "$S4" "scripts/"
sleep 15

# Fan-in: collect each shard, then synthesize.
echo "===== src ====="    ; cmux read-screen --surface "$S1" --lines 30
echo "===== tests ====="  ; cmux read-screen --surface "$S2" --lines 30
echo "===== docs ====="   ; cmux read-screen --surface "$S3" --lines 30
echo "===== scripts =====" ; cmux read-screen --surface "$S4" --lines 30
```

## 🔑 Concepts introduced

- **Sharding.** One `send` per surface with a *different* payload — the orchestrator decides the partition.
- **Parallel wall-clock.** Four directories summarized in the time of the slowest one, not the sum.
- **Reduce.** The orchestrator owns the merge step; agents never see each other.

## ✅ Done when

- [ ] Each agent summarized a *different* directory.
- [ ] The orchestrator returns one combined codebase map citing all four.
