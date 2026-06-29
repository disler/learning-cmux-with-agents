# 23 · Remote & Cloud Fleets

> **Tier 5 — Scale, Remote, Resilience**  ·  Complexity `▰▰▰▰▰`
> **Thesis:** the control plane is **location-independent** — the same verbs drive agents on SSH hosts and cloud VMs.
> **cmux verbs:** `ssh` · `vm new` · `vm ssh` · `vm exec` · `send`/`read-screen` (identical to local)
> **Agents under control:** agents running on a remote box and a cloud sandbox

---

## 🗣 The prompt

> "Run agents where the code actually lives. Open an **SSH workspace** on my dev box and spin up a fresh **cloud VM**, launch a coding agent in each, and drive them with the exact same `send`/`read-screen` commands you use locally."

## 🎯 What it showcases

Reach. A cmux workspace can be backed by a remote PTY (`cmux ssh`) or a cloud sandbox (`cmux vm`), yet every control verb is unchanged — so an orchestrator's fleet can straddle your laptop, a server, and ephemeral VMs without special-casing any of them.

## 🧠 What the orchestrator does (answer key)

```bash
# --- Remote host over SSH (browser panes route through the remote network; auto-reconnect on drops) ---
read RWS RS < <(cmux ssh user@devbox --name remote --json | jq -r '[.workspace_ref, .surface_ref] | @tsv')
cmux send --surface "$RS" "claude"; cmux send-key --surface "$RS" enter   # same verbs as local

# --- Cloud VM sandbox ---
VM=$(cmux vm new --detach --json | jq -r '.id // .vm_id')
cmux vm exec "$VM" -- "git clone <repo> && cd repo"
read VWS VS < <(cmux vm ssh "$VM" --json | jq -r '[.workspace_ref, .surface_ref] | @tsv')
cmux send --surface "$VS" "pi"; cmux send-key --surface "$VS" enter

# From here, the orchestrator treats $RS and $VS exactly like any local surface.
cmux read-screen --surface "$RS" --lines 30
cmux read-screen --surface "$VS" --lines 30
```

> ⚠️ Running this for real needs a reachable SSH host and cloud credentials. The **command surface** is identical to local; only the backing PTY changes.

## 🔑 Concepts introduced

- **`cmux ssh <dest>`** opens a remote-backed workspace (scp drag-upload, exponential-backoff reconnect, optional agent forwarding).
- **`cmux vm new|ssh|exec|ls|rm`** manages cloud sandboxes; `vm exec` runs one-off commands, `vm ssh` attaches a workspace.
- **Parity.** `send`/`send-key`/`read-screen`/`close-surface` don't know or care that a surface is remote.

## ✅ Done when

- [ ] A remote (SSH) and a cloud-VM workspace each run an agent.
- [ ] The orchestrator drives both with the same verbs as local surfaces.
