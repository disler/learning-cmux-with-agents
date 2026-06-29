# 20 · Capture & Replay Auth

> **Tier 4 — Terminals + Browser**  ·  Complexity `▰▰▰▰▱`
> **Thesis:** authenticate **once**, then every agent run starts already logged in — state is portable.
> **cmux verbs:** `browser state save` · `browser state load` · `browser cookies` · `browser storage`
> **Agents under control:** any agent that needs an authenticated web session

---

## 🗣 The prompt

> "I'll log into the app once in a cmux browser. Save that whole browser session to a file. Then, for every future agent run, load that saved state first so the agent's browser is already authenticated — no logging in again."

## 🎯 What it showcases

Session portability. cmux can serialize a browser surface's **cookies, local/session storage, and full state** to disk and replay it into a fresh surface — so an expensive interactive login becomes a one-time cost amortized across an entire fleet.

## 🧠 What the orchestrator does (answer key)

```bash
# --- One-time capture (human logs in, orchestrator saves) ---
B=$(cmux new-pane --type browser --url "https://app.example.com/login" --json | jq -r .surface_ref)
cmux browser "$B" wait --url-contains "/dashboard" --timeout-ms 120000   # wait for human login
cmux browser "$B" state save /tmp/app-auth.json                          # cookies + storage + state

# --- Every later run (no login needed) ---
B2=$(cmux new-pane --type browser --json | jq -r .surface_ref)
cmux browser "$B2" state load /tmp/app-auth.json
cmux browser "$B2" navigate "https://app.example.com/dashboard" --snapshot-after
cmux browser "$B2" get url        # should already be the authenticated dashboard
```

## 🔑 Concepts introduced

- **`browser state save|load <path>`** snapshots/replays the entire session (the durable way).
- **Granular control** via `browser cookies get|set|clear` and `browser storage local|session …` when you need just part of it.
- **Amortized auth.** Pair with prompt 13/16: every agent workspace loads the same state and comes up ready to work.

## ✅ Done when

- [ ] A state file is written after the one-time login.
- [ ] A fresh browser surface that loads it lands on an authenticated page without re-login.
