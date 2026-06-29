# 07 · Keys & Credentials

> **Tier 2 — Driving a Single Agent**  ·  Complexity `▰▰▰▱▱`
> **Thesis:** to "kick off agents," the orchestrator must hand them *credentials* — cleanly, without leaking them.
> **cmux verbs:** `workspace create --env-file` · `workspace env --mask` · `send` · `read-screen`
> **Agents under control:** **pi** ×1

---

## 🗣 The prompt

> "Spin up a workspace that has my API keys from `.env` loaded into its environment, launch the **pi** coding agent there, and ask it to confirm it can reach a model. Read me what it says — but never print my actual keys."

## 🎯 What it showcases

The credential pathway. `--env-file` seeds a workspace's environment **once**, and *every* pane, split, and agent spawned in it inherits those variables — no re-exporting, no keys in shell history. This is how a fleet of agents all come up authenticated.

## 🧠 What the orchestrator does (answer key)

```bash
ENVF="./.env"   # OPENROUTER_API_KEY, OPENAI_API_KEY, …

# Every shell in this workspace inherits the keys. CMUX_* vars are protected and can't be overridden.
read WS S < <(cmux workspace create --name pi-agent --cwd "$PWD" --env-file "$ENVF" --json \
              | jq -r '[.workspace_ref, .surface_ref] | @tsv')

# Prove the injection without ever echoing a secret value:
cmux workspace env --workspace "$WS" --mask      # shows KEY=sk•••• , values redacted

# Boot pi (it picks up the keys from the inherited env) and ask it something.
cmux send --surface "$S" "pi"; cmux send-key --surface "$S" enter
sleep 6
cmux send --surface "$S" "In one short sentence, confirm which model you're running."
cmux send-key --surface "$S" enter
sleep 8
cmux read-screen --surface "$S" --lines 40
```

## 🔑 Concepts introduced

- **`--env-file <path>`** (and repeatable `--env KEY=VALUE`) sets per-workspace env inherited by all descendants.
- **`workspace env --mask`** lets the agent *verify* secrets are present without exposing them.
- **Protected `CMUX_*`.** Workspace env can never clobber `CMUX_WORKSPACE_ID`/`SURFACE_ID`/`SOCKET_PATH` — the control plane stays intact.

## ✅ Done when

- [ ] `workspace env --mask` lists the `.env` keys, redacted.
- [ ] pi boots inside that workspace and answers.
- [ ] No raw key value ever appears in the orchestrator's output.
