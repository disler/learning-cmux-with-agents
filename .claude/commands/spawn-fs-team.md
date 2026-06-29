---
model: opus
description: Boot a 5-agent full-stack Flotion team as a new workspace in the cmux window (reuse the open window; only create one if none exists) — lead on the left half, plan/build-be/build-fe/test in a 2×2 on the right, each a pi agent loaded with its role. You drive cmux yourself in natural language; no scripts.
argument-hint: [team-name] [feature description...]
---

# Spawn Full-Stack Team

## Purpose

You are an orchestrator running in a terminal (not inside cmux). Boot a fresh
5-agent team for Flotion as **a new workspace in the cmux window** and, if given a
feature, hand it to the team's lead. **One team = one workspace = one feature**,
and teams **share a window** — reuse the window that's already open and only create
a new one if cmux has none. You do this by driving the `cmux` CLI yourself — there
is no script; this command *is* the recipe.

## Variables

TEAM: $1                 # short slug for the team; default "fs-team" if omitted
FEATURE: $2              # everything after the slug — optional feature to ship now

# Model blend (reasoning roles on GLM-5.2, build/verify on Minimax-M3)
LEAD_MODEL:  openrouter/z-ai/glm-5.2
PLAN_MODEL:  openrouter/z-ai/glm-5.2
BE_MODEL:    openrouter/minimax/minimax-m3
FE_MODEL:    openrouter/minimax/minimax-m3
TEST_MODEL:  openrouter/minimax/minimax-m3

ROLES_DIR: .claude/agents          # lead.md, plan.md, build-be.md, build-fe.md, test.md
ROSTER:    .team/<TEAM>.roster.json

## Codebase Structure

```
.claude/agents/*.md     # the 5 role system prompts each teammate boots with
.team/                  # shared memory: <team>.roster.json, backlog.md, <role>.md notes
apps/flotion/           # the app the team builds (Vue 3 + TS / FastAPI + SQLite)
```

## Instructions

- **Learn the verbs first.** Run `cmux --help` (and consult the `cmux` skill if
  available). The whole boot is just these verbs: `new-window`,
  `workspace create`, `new-split <dir>`, `rename-tab`, `workspace-action`,
  `set-status`, `send`, `send-key`, `read-screen`, `workspace close`.
- You are **outside** cmux; the socket is in `allowAll` mode, so your `cmux`
  calls drive it directly. Confirm with `cmux identify --json` before starting.
- **If cmux isn't running, start it — don't stop.** A refused socket
  (`Connection refused`) just means the app isn't up yet. Run `open -a cmux`,
  wait for the socket, then carry on. Only abort if it never comes online.
- **`send` types, `send-key enter` submits.** There are no Ctrl-chords; to stop a
  pane, `close-surface` it.
- **Capture refs as you create them.** `workspace create --json` returns
  `workspace_ref` + the lead's `surface_ref`; each `new-split --json` returns the
  new `surface_ref`. Thread these through — never guess refs.
- Launch each agent by typing its `pi …` line **into its pane** (via `cmux send`
  + `send-key enter`), not from your own shell.
- **Reuse the open window; one team = one workspace.** If cmux already has a
  window open, add this team as a **new workspace inside that existing window** —
  do **not** open another OS window. Only run `new-window` when cmux has no window
  at all. Multiple teams coexist as sibling workspaces in one window; each team is
  its own workspace (its lead + 2×2 workers).
- The **lead** drives the workers; you drive only the lead. Keep every agent
  observable — read panes, don't assume.

## Workflow

1. **Preflight (auto-launch cmux if needed).** Set `TEAM` (default `fs-team`) and
   `FEATURE` from the arguments. Ensure the cmux socket is reachable — and if it
   isn't, **launch cmux yourself** and wait, rather than stopping:
   ```bash
   if ! cmux identify --json >/dev/null 2>&1; then
     open -a cmux                                   # start the app (it owns the socket)
     for i in $(seq 1 30); do                       # poll up to ~15s for the socket
       cmux identify --json >/dev/null 2>&1 && break
       sleep 0.5
     done
   fi
   cmux identify --json >/dev/null 2>&1 || { echo "cmux failed to start — aborting."; exit 1; }
   ```
   Only abort if the socket never comes up. Then skim `cmux --help` for the verbs.

2. **Find the window — reuse if one's open, else create one.** Only `new-window`
   when cmux has no window at all; otherwise this team becomes a new workspace in
   the existing window. Track whether you created it (so you only clean up the
   empty default workspace when you did):
   ```bash
   CREATED_WIN=0
   WIN=$(cmux list-windows --json | jq -r 'map(select(.key))[0].id // .[0].id // empty')
   if [ -z "$WIN" ]; then
     WIN=$(cmux new-window | grep -oiE '[0-9a-f-]{36}' | head -1)
     CREATED_WIN=1
     DEFAULT_WS=$(cmux workspace list --window "$WIN" --json | jq -r '.workspaces[0].ref // empty')
   fi
   ```

3. **Lead on the left half.** Add the team workspace to that window with the repo
   as cwd and `.env` loaded, then **focus the window** (so short surface refs
   resolve there). Drop the empty default workspace **only if you just created the
   window** — never close a workspace that belongs to another team already living
   there:
   ```bash
   read WS LEAD < <(cmux workspace create --window "$WIN" --name "$TEAM" --cwd "$PWD" \
                      --env-file ./.env --focus true --json | jq -r '[.workspace_ref,.surface_ref]|@tsv')
   cmux focus-window --window "$WIN"
   [ "$CREATED_WIN" = 1 ] && [ -n "$DEFAULT_WS" ] && [ "$DEFAULT_WS" != "$WS" ] && cmux close-workspace --workspace "$DEFAULT_WS"
   ```

4. **Workers in a 2×2 on the right.** Split from the lead surface, capturing each
   new ref. **Scope every split with `--workspace "$WS"`** — the team lives in a
   fresh window, so a bare short ref can otherwise resolve against the wrong
   (focused) window and fail with "Surface not found". This yields: plan =
   top-left, build-be = top-right, build-fe = bottom-left, test = bottom-right.
   ```bash
   PLAN=$(cmux new-split right --workspace "$WS" --surface "$LEAD" --json | jq -r .surface_ref)  # lead now = left half
   BFE=$(cmux  new-split down  --workspace "$WS" --surface "$PLAN" --json | jq -r .surface_ref)
   BBE=$(cmux  new-split right --workspace "$WS" --surface "$PLAN" --json | jq -r .surface_ref)
   TEST=$(cmux new-split right --workspace "$WS" --surface "$BFE"  --json | jq -r .surface_ref)
   ```

5. **Identity (tell lead from workers at a glance).**
   ```bash
   cmux rename-tab --workspace "$WS" --surface "$LEAD" "👑 lead"
   cmux rename-tab --workspace "$WS" --surface "$PLAN" "📐 plan"
   cmux rename-tab --workspace "$WS" --surface "$BBE"  "⚙️ build-be"
   cmux rename-tab --workspace "$WS" --surface "$BFE"  "🎨 build-fe"
   cmux rename-tab --workspace "$WS" --surface "$TEST" "✅ test"
   cmux workspace-action --action set-color --workspace "$WS" --color Purple
   cmux set-status team "$TEAM" --workspace "$WS" --color "#8E44AD" --icon person.3.fill
   ```

6. **Boot a pi agent in each pane** by typing its launch line into the pane and
   pressing enter. Each loads its role file as the system prompt, the right model,
   and a session name. Launch the **four workers first**, then the lead. The
   worker kickoff tells it to acknowledge and wait; the lead kickoff hands it the
   roster (and the feature, if any). Example for one worker and the lead:
   ```bash
   cmux send --surface "$PLAN" "pi --append-system-prompt $ROLES_DIR/plan.md --model $PLAN_MODEL --name plan-$TEAM \"You are the plan worker on team $TEAM. Reply 'ready: plan' and wait for the lead.\""
   cmux send-key --surface "$PLAN" enter
   # …repeat for build-be ($BBE,$BE_MODEL), build-fe ($BFE,$FE_MODEL), test ($TEST,$TEST_MODEL)…
   sleep 6   # let workers boot before the lead starts dispatching
   cmux send --surface "$LEAD" "pi --append-system-prompt $ROLES_DIR/lead.md --model $LEAD_MODEL --name lead-$TEAM \"You are the LEAD of team $TEAM. Workers: plan=$PLAN, build-be=$BBE, build-fe=$BFE, test=$TEST. Roster: .team/$TEAM.roster.json. Drive them with cmux send/read-screen; poll for 'FLOTION-DONE: '. ${FEATURE:+Feature to ship: $FEATURE. Begin: send it to plan, then coordinate build/test.}${FEATURE:-No feature yet — confirm your roster and wait.}\""
   cmux send-key --surface "$LEAD" enter
   ```

7. **Write the roster** so the team (and you) can recover refs:
   ```bash
   jq -n --arg t "$TEAM" --arg w "$WS" --arg f "$FEATURE" \
     --arg l "$LEAD" --arg p "$PLAN" --arg be "$BBE" --arg fe "$BFE" --arg te "$TEST" \
     '{team:$t,workspace:$w,feature:($f|select(.!="")),agents:{lead:{surface:$l},plan:{surface:$p},"build-be":{surface:$be},"build-fe":{surface:$fe},test:{surface:$te}}}' \
     > .team/$TEAM.roster.json
   ```

8. **Bring the window forward and confirm.** `cmux focus-window --window "$WIN"`,
   then read the lead once (`cmux read-screen --surface "$LEAD" --scrollback --lines 40`)
   to confirm it booted. Now follow the `Report` section.

## Report

```
## Team "[TEAM]" — booted as a workspace in window [WIN]

**Window**: [WIN] ([reused existing | new])   ·   **Workspace**: [WS]   ·   **Layout**: lead (left half) + 2×2 workers (right)

| Role | Surface | Model |
|------|---------|-------|
| 👑 lead | [LEAD] | [model] |
| 📐 plan | [PLAN] | [model] |
| ⚙️ build-be | [BBE] | [model] |
| 🎨 build-fe | [BFE] | [model] |
| ✅ test | [TEST] | [model] |

**Roster**: .team/[TEAM].roster.json
```
