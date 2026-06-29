# 27 · Theme & Feel

> **Customization**  ·  Complexity `▰▰▱▱▱`
> **Thesis:** the terminal's *look* is owned by Ghostty and applies globally — and it reloads **live**, no restart.
> **cmux verbs:** Ghostty `config` · `cmux themes set` · `cmux config set` · `cmux reload-config`
> **Customizes:** the whole terminal's rendering (all surfaces)

---

## 🗣 The prompt

> "Change the terminal's whole look: switch to a darker theme, bump the font a touch, dial the background to ~92% opacity, and apply it **without restarting**."

## 🎯 What it showcases

The split that keeps cmux simple: **Ghostty owns rendering** (font, theme, cursor, colors, opacity, blur, scrollback), **cmux owns the app**. Anything visual about the terminal goes in the Ghostty config and reloads instantly. The honest caveat: this is **global** — one look for every surface; you can't theme pane A differently from pane B.

## 🧠 What the orchestrator does (answer key)

```bash
# Terminal look lives in the Ghostty config (font/theme/cursor/opacity/blur).
cat >> ~/.config/ghostty/config <<'CFG'
font-family = JetBrains Mono
font-size = 14
theme = Afterglow
background-opacity = 0.92
background-blur = 20
cursor-style = block
CFG

# Themes are first-class — list and set light/dark independently:
cmux themes list
cmux themes set --light "Adwaita" --dark "Afterglow"

# cmux-owned sizes (sidebar / tab bar) via config get/set:
cmux config set sidebar-font-size 15
cmux config set surface-tab-bar-font-size 11

# Apply everything live — reloads BOTH Ghostty config and cmux.json, no restart:
cmux reload-config
```

## 🔑 Concepts introduced

- **`cmux reload-config`** (or ⌘⇧,) reloads Ghostty config *and* `cmux.json` and refreshes terminals in place.
- **`cmux themes list/set [--light/--dark]`** picks from the full Ghostty theme set; **`cmux config get/set`** handles the cmux-owned sidebar/tab-bar font sizes.
- **Global, by design.** Font/theme/opacity apply to every surface. Per-*workspace* differentiation is color/name/pill (prompt 26), not terminal theme.

## ✅ Done when

- [ ] The theme, font size, and opacity change **without** relaunching cmux.
- [ ] `cmux config get sidebar-font-size` reflects the new value.
