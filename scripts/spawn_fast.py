#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Scripted fast-path spawn of a 5-agent Flotion team in cmux.

Boots all five panes at once from cmux/fs-team.layout.json (lead on the left
half, plan/build-be/build-fe/test in a 2x2 on the right), colors and labels the
workspace, writes a .team/<feature>.spawn.json the orchestrator can attach to,
then execs the chosen orchestrator (Claude Code or pi) in THIS terminal so it
takes command already oriented via /cmux-did-spawn.

Usage:
    uv run scripts/spawn_fast.py <cc|pi> <feature-slug> [--orch-pi-model MODEL]

Invoked by the `just fastcc` / `just fastpi` recipes. This is the heavy logic
that used to live inline in the justfile.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

# scripts/ lives at the repo root; the repo is its parent.
REPO = Path(__file__).resolve().parent.parent
LAYOUT_FILE = REPO / "cmux" / "fs-team.layout.json"
ENV_FILE = REPO / ".env"

DEFAULT_ORCH_PI_MODEL = "openrouter/z-ai/glm-5.2"
ROLES = ["lead", "plan", "build-be", "build-fe", "test"]
MODELS = {
    "lead": "openrouter/z-ai/glm-5.2",
    "plan": "openrouter/z-ai/glm-5.2",
    "build-be": "openrouter/minimax/minimax-m3",
    "build-fe": "openrouter/minimax/minimax-m3",
    "test": "openrouter/minimax/minimax-m3",
}
UUID_RE = re.compile(r"[0-9a-fA-F-]{36}")


def die(msg: str) -> None:
    print(msg, file=sys.stderr)
    sys.exit(1)


def sh(*args: str) -> subprocess.CompletedProcess:
    """Run a command, capturing stdout/stderr as text. Never raises."""
    return subprocess.run(list(args), capture_output=True, text=True)


def cmux(*args: str) -> subprocess.CompletedProcess:
    return sh("cmux", *args)


def cmux_json(*args: str):
    out = cmux(*args).stdout.strip()
    if not out:
        return None
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return None


def slugify(feature: str) -> str:
    """lowercase, spaces -> dashes, keep only [a-z0-9-] (matches the old `tr` pipe)."""
    feature = feature.lower().replace(" ", "-")
    return re.sub(r"[^a-z0-9-]", "", feature)


def ensure_cmux_running() -> None:
    """Preflight: if the socket is down, launch cmux and wait (don't stop)."""
    if cmux("identify", "--json").returncode == 0:
        return
    sh("open", "-a", "cmux")  # cmux owns the socket
    for _ in range(30):  # poll ~15s
        if cmux("identify", "--json").returncode == 0:
            return
        time.sleep(0.5)
    if cmux("identify", "--json").returncode != 0:
        die("cmux failed to start; aborting.")


def build_layout(feature: str) -> str:
    """Interpolate the layout template and strip its _comment; return compact JSON."""
    text = LAYOUT_FILE.read_text()
    text = text.replace("__FEATURE__", feature).replace("__REPO__", str(REPO))
    obj = json.loads(text)
    obj.pop("_comment", None)
    return json.dumps(obj, separators=(",", ":"))


def find_or_create_window() -> tuple[str, bool, str | None]:
    """Reuse the open window (UUID is the only stable handle); create one only if none."""
    windows = cmux_json("list-windows", "--json") or []
    win = next((w["id"] for w in windows if w.get("key")), None)
    if not win and windows:
        win = windows[0].get("id")
    if win:
        return win, False, None

    created = cmux("new-window").stdout
    match = UUID_RE.search(created or "")
    if not match:
        die("failed to create a window")
    win = match.group(0)
    wslist = cmux_json("workspace", "list", "--window", win, "--json") or {}
    workspaces = wslist.get("workspaces") or []
    default_ws = workspaces[0].get("ref") if workspaces else None
    return win, True, default_ws


def write_spawn_file(feature: str, win: str, agent: str) -> Path:
    spawn = REPO / ".team" / f"{feature}.spawn.json"
    spawn.parent.mkdir(parents=True, exist_ok=True)
    spawn.write_text(
        json.dumps(
            {
                "feature": feature,
                "window": win,
                "workspace_name": feature,
                "orchestrator": agent,
                "roles": ROLES,
                "models": MODELS,
                "layout": "cmux/fs-team.layout.json",
            },
            indent=2,
        )
        + "\n"
    )
    return spawn


def exec_orchestrator(agent: str, feature: str, orch_pi_model: str) -> None:
    """Replace this process with the orchestrator, oriented to the spawned team."""
    os.chdir(REPO)  # so the relative spawn-file arg resolves for /cmux-did-spawn
    sys.stdout.flush()
    attach = f"/cmux-did-spawn .team/{feature}.spawn.json"
    if agent == "cc":
        os.execvp("claude", ["claude", "--dangerously-skip-permissions",
                             "--model", "opus[1m]", attach])
    else:  # pi
        os.execvp("pi", ["pi", "--name", f"orchestrator-{feature}",
                          "--model", orch_pi_model, attach])


def main() -> None:
    parser = argparse.ArgumentParser(description="Fast-path spawn of a 5-agent Flotion team in cmux.")
    parser.add_argument("agent", choices=["cc", "pi"], help="orchestrator: cc (Claude Code) or pi")
    parser.add_argument("feature", help="feature slug (dash-case); names the team's workspace")
    parser.add_argument("--orch-pi-model", default=DEFAULT_ORCH_PI_MODEL,
                        help=f"model for the pi orchestrator (default: {DEFAULT_ORCH_PI_MODEL})")
    args = parser.parse_args()

    feature = slugify(args.feature)
    if not feature:
        die(f"usage: just fast{args.agent} <feature-slug>")

    os.environ["CMUX_QUIET"] = "1"

    ensure_cmux_running()
    layout = build_layout(feature)
    win, created_win, default_ws = find_or_create_window()

    created = cmux_json(
        "workspace", "create", "--window", win, "--name", feature,
        "--cwd", str(REPO), "--env-file", str(ENV_FILE),
        "--layout", layout, "--focus", "true", "--json",
    ) or {}
    ws = created.get("workspace_ref")
    lead = created.get("surface_ref")
    if not ws or not lead:
        die("failed to create the team workspace from the layout")

    cmux("focus-window", "--window", win)
    # only drop the empty default workspace if WE created the window
    if created_win and default_ws and default_ws != ws:
        cmux("close-workspace", "--workspace", default_ws)

    cmux("workspace-action", "--action", "set-color", "--workspace", ws, "--color", "Purple")
    cmux("set-status", "team", feature, "--workspace", ws,
         "--color", "#8E44AD", "--icon", "person.3.fill")

    spawn = write_spawn_file(feature, win, args.agent)

    print(f"team window={win} workspace={ws} lead={lead}  spawn={spawn}", flush=True)
    print(f"launching {args.agent} orchestrator, already aware via /cmux-did-spawn ...", flush=True)

    exec_orchestrator(args.agent, feature, args.orch_pi_model)


if __name__ == "__main__":
    main()
