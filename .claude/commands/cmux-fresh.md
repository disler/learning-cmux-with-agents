---
model: opus
description: Clear cmux's persisted session so the next launch opens with fresh/blank windows. Quits cmux first (so the clear sticks), backs up, then empties the saved window tree (and its -previous sibling).
allowed-tools: Bash
---

# cmux Fresh

## Purpose

Wipe cmux's saved session so it boots with **fresh, blank windows** next time —
no restored workspaces or panes. cmux replays its window/workspace/pane tree from
a session JSON on launch and rewrites it on quit; this command empties that tree
(after backing it up) so there's nothing to restore.

## Variables

# Static configuration
STATE_DIR: ~/Library/Application Support/cmux
SESSION:   $STATE_DIR/session-com.cmuxterm.app.json
PREVIOUS:  $STATE_DIR/session-com.cmuxterm.app-previous.json

## Instructions

- **Quit cmux first — automatically.** While cmux runs it owns the session file and
  rewrites it, so a clear won't stick. If it's up, `pkill` it and wait for it to exit
  *before* backing up/clearing. cmux flushes its session on a clean quit, so kill it,
  then operate on the file it leaves behind. Report whether you had to kill it.
- **Back up before clearing.** Copy each session file to `<file>.bak-<epoch>`
  before touching it, so the prior layout can be restored.
- Clear by setting the top-level `windows` array to `[]` — keep the rest of the
  JSON (`version`, `createdAt`) intact. Do **not** delete the file outright.
- Handle the `-previous.json` sibling too; it's cmux's one-step-back snapshot.
- If a file doesn't exist, skip it quietly — that's fine, not an error.
- This is a destructive-to-layout op on the user's machine; only clear these two
  session files, nothing else under STATE_DIR.

## Workflow

1. If cmux is running, quit it and wait for it to fully exit (so the clear sticks).
   Try a graceful quit first, then force-kill if it lingers:
   ```bash
   if pgrep -xi cmux >/dev/null; then
     echo "was RUNNING — quitting"
     osascript -e 'quit app "cmux"' 2>/dev/null || pkill -xi cmux
     for i in $(seq 1 20); do pgrep -xi cmux >/dev/null || break; sleep 0.5; done
     pgrep -xi cmux >/dev/null && { pkill -9 -xi cmux; sleep 1; }
     pgrep -xi cmux >/dev/null && echo "STILL RUNNING — abort" || echo "quit OK"
   else
     echo "not running"
   fi
   ```
   If it still reports running after the force-kill, stop and tell the user — don't
   clear, since cmux would just overwrite it.
2. Back up and clear both session files (epoch suffix; skip missing ones):
   ```bash
   STATE="$HOME/Library/Application Support/cmux"; TS=$(date +%s)
   for f in "$STATE/session-com.cmuxterm.app.json" "$STATE/session-com.cmuxterm.app-previous.json"; do
     [ -f "$f" ] || { echo "skip (absent): $f"; continue; }
     cp "$f" "$f.bak-$TS"
     tmp="$f.tmp.$TS"
     jq '.windows = []' "$f" > "$tmp" && mv "$tmp" "$f" \
       && echo "cleared: $f  (backup: $f.bak-$TS)" \
       || echo "FAILED: $f"
   done
   ```
3. Confirm each cleared file now has an empty `windows` array:
   ```bash
   STATE="$HOME/Library/Application Support/cmux"
   for f in "$STATE/session-com.cmuxterm.app.json" "$STATE/session-com.cmuxterm.app-previous.json"; do
     [ -f "$f" ] && echo "$f -> windows: $(jq '.windows | length' "$f")"
   done
   ```
4. Now follow the `Report` section.

## Report

```
## cmux session cleared

- cmux: [quit it for you (was running) | was not running]
- session-com.cmuxterm.app.json:          windows -> 0   (backup: [path])
- session-com.cmuxterm.app-previous.json: windows -> 0   (backup: [path] | absent)

Next launch opens fresh. To restore the old layout: move a `.bak-*` file back over the original.
```
