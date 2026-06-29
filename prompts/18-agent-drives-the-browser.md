# 18 · Agent Drives the Browser

> **Tier 4 — Terminals + Browser**  ·  Complexity `▰▰▰▰▱`
> **Thesis:** the orchestrator can act on the **DOM** — navigate, read, click, type, and verify — not just on terminals.
> **cmux verbs:** `browser open` · `snapshot --interactive` · `click` · `screenshot` · `get`
> **Agents under control:** browser automation as a tool the agent wields

---

## 🗣 The prompt

> "Open `https://example.com` in a cmux browser, snapshot the page so you know what's there, click the **'More information…'** link, wait for the new page, and screenshot the result so I can confirm it worked."

## 🎯 What it showcases

cmux's browser automation suite — a Playwright-style API over the embedded WKWebView. The orchestrator inspects the page with an **interactive snapshot** (which assigns clickable refs), acts on a ref, waits for the result, and captures proof. This is how agents test and operate real web UIs.

## 🧠 What the orchestrator does (answer key)

```bash
B=$(cmux new-pane --type browser --url "https://example.com" --json | jq -r .surface_ref)

# Snapshot returns an interactive map of elements with stable refs.
cmux browser "$B" snapshot --interactive --compact

# Act by selector or ref, then wait for the navigation, then prove it with a screenshot.
cmux browser "$B" click "a"                     # the "More information…" link
cmux browser "$B" wait --url-contains "iana.org" --timeout-ms 10000
cmux browser "$B" get url
cmux browser "$B" screenshot --out /tmp/cmux-proof.png
```

## 🔑 Concepts introduced

- **`snapshot --interactive`** is the agent's structured view of the page (refs > brittle CSS guessing).
- **Wait conditions:** `--selector`, `--text`, `--url-contains`, `--load-state`, `--function` — act only when the page is ready.
- **`get url|title|text|value|attr|count`** reads state; **`screenshot --out`** captures verifiable proof.

## ✅ Done when

- [ ] The snapshot lists the page's link.
- [ ] After the click, `get url` shows an `iana.org` URL.
- [ ] A screenshot file exists proving the navigation.
