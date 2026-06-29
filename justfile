# cmux Capabilities Guide — task runner.
#
# The centerpiece is the single-page visual guide in guide/. Start there:
#
#     just guide                         # serve + open the guide at localhost:8080/guide/
#
# The demo app the agent team builds:
#
#     just flotion                       # boot Flotion (FastAPI :8000 + Vite :5173)
#
# The agentic proof — one orchestrator driving a 5-agent team inside cmux.
# The orchestrator runs HERE, in a normal terminal (NOT inside cmux). Teams go
# in cmux: one team = one workspace, sharing a window (reuse the open window;
# only create one if cmux has none). Two ways to boot a team:
#
#   AGENT-DRIVEN (natural language; orchestrator builds the team live):
#     just devcc                         # Claude Code orchestrator -> /spawn-fs-team
#     just devpi                         # pi orchestrator          -> /spawn-fs-team
#
#   SCRIPTED FAST PATH (declarative layout boots all 5 panes at once, then the
#   orchestrator attaches already-aware via /cmux-did-spawn):
#     just fastcc my-feature             # Claude Code orchestrator
#     just fastpi my-feature             # pi orchestrator
#     (the feature slug names the team's workspace and suffixes each pi --name)
#
# App-level dev tasks live in apps/flotion/justfile.

set dotenv-load := true

orch_pi_model := "openrouter/z-ai/glm-5.2"

default:
    @just --list

# ─── The guide (start here) ──────────────────────────────────────────────────

# Serve + open the single-page visual guide at localhost:<port>/guide/
guide port="8080":
    #!/usr/bin/env bash
    set -euo pipefail
    # Served from the repo root so the guide's links into ../prompts/ resolve.
    echo "cmux guide → http://localhost:{{port}}/guide/   (Ctrl-C to stop)"
    ( sleep 1 && open "http://localhost:{{port}}/guide/" >/dev/null 2>&1 || true ) &
    exec python3 -m http.server {{port}}

# ─── The demo app the agent team builds ──────────────────────────────────────

# Boot the Flotion demo app: FastAPI :8000 + Vite :5173 (installs deps on first run)
flotion:
    cd apps/flotion && just install && just dev

# ─── Agentic orchestration (the thesis, proven) ──────────────────────────────

# Claude Code orchestrator, agent-driven (builds the team live via /spawn-fs-team)
devcc *args:
    claude --dangerously-skip-permissions --model "opus[1m]" "/spawn-fs-team {{args}}"

# pi orchestrator, agent-driven (builds the team live via /spawn-fs-team)
devpi *args:
    pi --model "{{orch_pi_model}}" "/spawn-fs-team {{args}}"

# FAST: scripted spawn from the layout, then Claude Code orchestrator attaches
fastcc feature:
    uv run --script scripts/spawn_fast.py cc {{feature}} --orch-pi-model "{{orch_pi_model}}"

# FAST: scripted spawn from the layout, then pi orchestrator attaches
fastpi feature:
    uv run --script scripts/spawn_fast.py pi {{feature}} --orch-pi-model "{{orch_pi_model}}"
