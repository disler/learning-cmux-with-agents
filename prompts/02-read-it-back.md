# 02 · Read It Back

> **Tier 1 — Foundations**  ·  Complexity `▰▱▱▱▱`
> **Thesis:** the agent doesn't just *send* — it *observes*. Output is a first-class input.
> **cmux verbs:** `send` · `send-key` · `read-screen --scrollback --lines`
> **Agents under control:** _none yet — one terminal_

---

## 🗣 The prompt

> "Open a workspace in a fresh temp directory, create 60 throwaway files in it, list them with `ls -la`, then read the output back from scrollback and tell me how many files there are — and name three."

## 🎯 What it showcases

A terminal scrolls. The visible screen is only the last page, so a real orchestrator must reach into **scrollback** to see everything a command produced. This is the difference between an agent that *fires and forgets* and one that *closes the loop*.

## 🧠 What the orchestrator does (answer key)

```bash
# A throwaway temp dir the agent owns — no $HOME or /usr/bin access required.
WORK="$(mktemp -d /tmp/cmux-demo.XXXXXX)"
read WS S < <(cmux workspace create --name reader --cwd "$WORK" --json \
              | jq -r '[.workspace_ref, .surface_ref] | @tsv')

# Create 60 files in the temp cwd, then list them — the output overflows one screen.
cmux send     --surface "$S" 'touch f{1..60}.txt && ls -la'
cmux send-key --surface "$S" enter

# The visible screen only shows the tail. Pull history with --scrollback + --lines.
cmux read-screen --surface "$S" --scrollback --lines 80
```

## 🔑 Concepts introduced

- **`read-screen --scrollback`** returns terminal history, not just the current viewport.
- **`--lines N`** bounds how much you pull back — keep it tight so the agent's context stays lean.
- **Snapshots, not streams.** `read-screen` is a point-in-time capture; for long-running commands, read again (or watch events — see prompt 14).

## ✅ Done when

- [ ] The agent's answer reflects content that scrolled **off** the visible screen.
- [ ] It returns a count near 60 and names three of the files.
