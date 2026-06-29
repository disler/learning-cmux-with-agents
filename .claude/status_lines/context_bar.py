#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# ///

"""
Status Line — model name + context window.
Display:  Opus 4.8  [##########----------] 47.3%
A stripped v6: model name prefix, then the usage bar + percentage, color-coded
by how full the context window is (green < 50, yellow < 75, red < 90,
bright-red >= 90).
"""

import json
import sys

GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
BRIGHT_RED = "\033[91m"
CYAN = "\033[36m"
BOLD = "\033[1m"
DIM = "\033[90m"
RESET = "\033[0m"


def usage_color(pct: float) -> str:
    if pct < 50:
        return GREEN
    if pct < 75:
        return YELLOW
    if pct < 90:
        return RED
    return BRIGHT_RED


def progress_bar(pct: float, width: int = 20) -> str:
    filled = max(0, min(width, int(round((pct / 100) * width))))
    color = usage_color(pct)
    return f"[{color}{'#' * filled}{DIM}{'-' * (width - filled)}{RESET}]"


def main() -> None:
    try:
        data = json.loads(sys.stdin.read())
    except Exception:
        print(f"[{DIM}{'-' * 20}{RESET}] --%")
        return

    model = (data.get("model") or {}).get("display_name") or "Claude"

    cw = data.get("context_window") or {}
    pct = cw.get("used_percentage")
    if pct is None:
        pct = 0.0

    print(f"{BOLD}{CYAN}{model}{RESET}  {progress_bar(pct)} {usage_color(pct)}{pct:.1f}%{RESET}")


if __name__ == "__main__":
    main()
