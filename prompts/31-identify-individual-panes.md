# 31 · Identify Individual Panes

> **Customization**  ·  Complexity `▰▰▱▱▱`
> **Thesis:** panes share the global terminal theme — so you make each one identifiable by its **tab name** and its **printed content** (a colored banner + a colored prompt), not by a per-pane color setting.
> **cmux verbs:** `new-split` · `rename-tab` · `send` (ANSI banner + prompt) · `trigger-flash`
> **Customizes:** each surface's identity within one workspace

---

## 🗣 The prompt

> "Split a workspace into 4 panes and make each one instantly identifiable — give each its own tab name, a bold colored banner at the top, and a matching colored prompt, so I can tell **reviewer / fixer / tester / builder** apart at a glance."

## 🎯 What it showcases

The honest shape of *per-pane* customization. Unlike workspaces (which have a real `set-color`), a surface has **no color attribute** — font and theme are a single global Ghostty config. So you identify panes two ways cmux *does* give you: a distinct **tab name** (`rename-tab`) and **content you print into them** — an ANSI banner and a colored shell prompt — plus `trigger-flash` to point at one.

## 🧠 What the orchestrator does (answer key)

```bash
read WS A < <(cmux workspace create --name panes --cwd "$(mktemp -d /tmp/cmux-pane.XXXXXX)" --json \
              | jq -r '[.workspace_ref,.surface_ref]|@tsv')
B=$(cmux new-split right --surface "$A" --json | jq -r .surface_ref)
C=$(cmux new-split down  --surface "$A" --json | jq -r .surface_ref)
D=$(cmux new-split down  --surface "$B" --json | jq -r .surface_ref)

ident() {   # $1=surface  $2=NAME  $3=colornum(1-6: 1=red 2=grn 3=yel 4=blu 5=mag 6=cyn)  $4=emoji
  cmux rename-tab --workspace "$WS" --surface "$1" "$2"                  # tab-bar name (rename-tab needs --workspace)
  cmux send --surface "$1" "clear; printf '\033[1;97;4${3}m\n   $4  $2  \n\033[0m\n'"  # ANSI banner
  cmux send-key --surface "$1" enter
  cmux send --surface "$1" "PROMPT='%K{$3}%F{15} $2 %f%k %# '"           # colored zsh prompt (persists)
  cmux send-key --surface "$1" enter
}
ident "$A" REVIEWER 4 "🔵";  ident "$B" FIXER 2 "🟢";  ident "$C" TESTER 3 "🟡";  ident "$D" BUILDER 5 "🟣"

cmux trigger-flash --surface "$D"     # point at one pane on demand
```

## 🔑 Concepts introduced

- **`rename-tab --workspace <ws> --surface <ref> "<title>"`** names a single surface in its tab bar — pass `--workspace` or it errors `Tab not found`. (A surface also takes a `name` at creation in a layout.)
- **No per-pane color setting.** Surfaces have no `set-color` (workspaces do, prompt 26). To "color" a pane, print into it: an ANSI banner (`\033[…m`) and a colored prompt (`PROMPT='%K{n}…'` in zsh / `PS1='\[\e[…m\]…'` in bash).
- **`trigger-flash --surface <ref>`** flashes one pane for attention — the non-destructive "this one" cue.

## ✅ Done when

- [ ] One workspace shows a 2×2 of panes named REVIEWER / FIXER / TESTER / BUILDER.
- [ ] Each pane has a distinct colored banner + matching prompt, and `trigger-flash` highlights a chosen one.
