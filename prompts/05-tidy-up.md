# 05 · Tidy Up

> **Tier 1 — Foundations**  ·  Complexity `▰▰▱▱▱`
> **Thesis:** lifecycle is a loop, not a launch — a good orchestrator also *renames, signals, and tears down* cleanly.
> **cmux verbs:** `rename-workspace` · `trigger-flash` · `focus-pane` · `close-surface` · `workspace close`
> **Agents under control:** _terminal lifecycle_

---

## 🗣 The prompt

> "Take the **dash** workspace from before: rename it to **retired**, flash it so I can spot it, then close its extra panes one by one, and finally close the whole workspace."

## 🎯 What it showcases

Graceful teardown. Because `send-key` only sends *single named keys* (no `Ctrl-C` chord), the canonical way to stop a running program and reclaim a pane is to **close the surface** — clean, deterministic, scriptable. This is how fleets are dismantled in Tier 3.

## 🧠 What the orchestrator does (answer key)

```bash
# In a real session you already hold $WS from when you created it (prompt 03).
# To re-find it by name, pull the ref straight out of the tree:
WS=$(cmux tree --all | grep '"dash"' | grep -oE 'workspace:[0-9]+' | head -1)

cmux rename-workspace --workspace "$WS" "retired"
cmux trigger-flash --workspace "$WS"          # blue flash so the human can see which one

# Close every pane but the first by closing its surface (portable; no bash-4 builtins).
cmux list-panes --workspace "$WS" --json | jq -r '.panes[].surface_refs[]' | tail -n +2 \
  | while read -r S; do cmux close-surface --surface "$S"; done

cmux workspace close --workspace "$WS"        # …or just do this to reclaim everything at once
```

## 🔑 Concepts introduced

- **`trigger-flash`** is a non-destructive "look here" cue — useful before any disruptive action.
- **`close-surface`** is the safe substitute for `Ctrl-C`: it kills whatever runs in the pane.
- **`workspace close`** removes the workspace and everything in it (the legacy alias `close-workspace` still works).

## ✅ Done when

- [ ] The workspace is renamed `retired` and visibly flashes.
- [ ] Extra panes close one at a time, then the workspace disappears from `cmux tree`.
