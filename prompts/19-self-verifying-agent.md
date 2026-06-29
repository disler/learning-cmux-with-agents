# 19 · Self-Verifying Agent

> **Tier 4 — Terminals + Browser**  ·  Complexity `▰▰▰▰▰`
> **Thesis:** close the loop — an agent that **runs, inspects, and fixes its own UI** until the evidence says it's clean.
> **cmux verbs:** `send` (dev server) · `browser navigate` · `browser console list` · `browser errors list` · `screenshot`
> **Agents under control:** **Claude Code** in a build → verify → fix loop

---

## 🗣 The prompt

> "Agent: build a small page and run its dev server. Then drive the cmux browser against your own UI — load the page, read the browser **console and error log**, and if anything's broken, fix the code and re-check. Loop until the console is clean, then screenshot the working page."

## 🎯 What it showcases

The full agentic loop with **machine-readable feedback**. The orchestrator gives the agent its own eyes: `browser console list` and `browser errors list` return real runtime errors, which the agent treats as a failing test and iterates against — no human in the loop.

## 🧠 What the orchestrator does (answer key)

```bash
read WS CODE < <(cmux workspace create --name verify --cwd "$PWD" --env-file ./.env --json \
                 | jq -r '[.workspace_ref, .surface_ref] | @tsv')
B=$(cmux new-pane --workspace "$WS" --type browser --url "http://localhost:5173" --json | jq -r .surface_ref)

cmux send --surface "$CODE" "claude"; cmux send-key --surface "$CODE" enter
sleep 6
cmux send --surface "$CODE" "Build a page with a button that fetches /api/hello and renders it. Run dev on 5173."
cmux send-key --surface "$CODE" enter

# Verify → fix loop (orchestrator-driven):
for round in 1 2 3; do
  cmux browser "$B" navigate "http://localhost:5173" --snapshot-after
  ERRORS=$(cmux browser "$B" errors list; cmux browser "$B" console list | grep -i error)
  [ -z "$ERRORS" ] && break
  cmux send --surface "$CODE" "The browser console shows: $ERRORS — fix it."
  cmux send-key --surface "$CODE" enter
  sleep 12
done
cmux browser "$B" screenshot --out /tmp/cmux-clean.png
```

## 🔑 Concepts introduced

- **`browser console list` / `errors list`** surface real runtime diagnostics as text the agent can consume.
- **Evidence-driven iteration.** The loop exits on *observed* cleanliness, not on the agent's say-so.
- **Feedback you can trust.** The same view a human dev would open in DevTools, handed to the agent.

## ✅ Done when

- [ ] The agent serves a page and the orchestrator reads its console/errors.
- [ ] At least one fix round is driven by a real console error.
- [ ] The loop ends with a clean console and a screenshot.
