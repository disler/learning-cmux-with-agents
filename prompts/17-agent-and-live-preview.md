# 17 · Agent + Live Preview

> **Tier 4 — Terminals + Browser**  ·  Complexity `▰▰▰▰▱`
> **Thesis:** a cmux surface isn't only a terminal — it can be a **browser**, so an agent and the app it's building share one window.
> **cmux verbs:** `new-pane --type browser --url` · `browser reload` · `send`
> **Agents under control:** **Claude Code** building a web app, with a live preview beside it

---

## 🗣 The prompt

> "In one workspace, put **Claude Code** on the left building a tiny web app, and an embedded **browser** on the right pointed at its dev server (`http://localhost:5173`). Each time the agent changes the code, reload the preview so I can watch the page evolve."

## 🎯 What it showcases

The **Browser panel** — the second kind of cmux surface. The orchestrator places a terminal agent and a live web view side by side and reloads the preview on demand, so building and seeing happen in the same pane grid.

## 🧠 What the orchestrator does (answer key)

```bash
read WS CODE < <(cmux workspace create --name app --cwd "$PWD" --env-file ./.env --json \
                 | jq -r '[.workspace_ref, .surface_ref] | @tsv')

# Right pane is a BROWSER surface, not a terminal.
PREVIEW=$(cmux new-pane --workspace "$WS" --type browser --url "http://localhost:5173" --json | jq -r .surface_ref)

# Boot the agent and have it scaffold + run a dev server.
cmux send --surface "$CODE" "claude"; cmux send-key --surface "$CODE" enter
sleep 6
cmux send --surface "$CODE" "Create a minimal Vite app with a bright heading, then run the dev server on port 5173."
cmux send-key --surface "$CODE" enter

# After the agent reports a change, refresh the preview:
cmux browser "$PREVIEW" reload
# or re-point it:  cmux browser "$PREVIEW" navigate "http://localhost:5173" --snapshot-after
```

## 🔑 Concepts introduced

- **`new-pane --type browser --url <url>`** creates a web surface addressed by the same `surface:N` handle as any terminal.
- **`cmux browser <surface> reload|navigate`** drives that surface; `--snapshot-after` returns a fresh DOM snapshot inline.
- **One grid, two media.** Terminal and browser panes live together and are scripted with the same targeting.

## ✅ Done when

- [ ] The workspace shows a code pane (Claude Code) + a browser pane.
- [ ] Reloading the browser reflects the agent's latest change.
