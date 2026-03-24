#!/usr/bin/env python3
"""Small CLI for common repo checks and status output."""

from __future__ import annotations

import argparse
import compileall
import json
import sys
from pathlib import Path

from project_config import BASE_DIR, PROJECT_AUTHOR, PROJECT_TITLE, chapter_files, project_title

STATE_FILE = BASE_DIR / "state.json"
CORE_PATHS = [
    BASE_DIR / "world.md",
    BASE_DIR / "characters.md",
    BASE_DIR / "outline.md",
    BASE_DIR / "canon.md",
    BASE_DIR / "voice.md",
    BASE_DIR / "program.md",
    BASE_DIR / "evaluate.py",
    BASE_DIR / "run_pipeline.py",
]


def load_state() -> dict:
    if not STATE_FILE.exists():
        return {}
    return json.loads(STATE_FILE.read_text(encoding="utf-8"))


def cmd_status(_args: argparse.Namespace) -> int:
    state = load_state()
    chapters = chapter_files()
    words = sum(len(path.read_text(encoding="utf-8").split()) for path in chapters)

    print(f"Title:    {project_title()}")
    print(f"Author:   {PROJECT_AUTHOR}")
    print(f"Phase:    {state.get('phase', 'unknown')}")
    print(f"Focus:    {state.get('current_focus') or 'unknown'}")
    print(f"Chapters: {len(chapters)}")
    print(f"Words:    {words}")
    return 0


def cmd_smoke_check(_args: argparse.Namespace) -> int:
    missing = [path for path in CORE_PATHS if not path.exists()]
    if missing:
        print("Missing required files:", file=sys.stderr)
        for path in missing:
            print(f"  - {path.relative_to(BASE_DIR)}", file=sys.stderr)
        return 1

    ok = compileall.compile_dir(
        str(BASE_DIR),
        quiet=1,
        maxlevels=10,
    )
    if not ok:
        print("Python compile check failed.", file=sys.stderr)
        return 1

    chapters = chapter_files()
    print("Smoke check passed.")
    print(f"  Project:  {PROJECT_TITLE}")
    print(f"  Author:   {PROJECT_AUTHOR}")
    print(f"  Chapters: {len(chapters)}")
    print(f"  Root:     {BASE_DIR}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="autonovel helper CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("status", help="Show current project state and chapter totals")
    sub.add_parser("smoke-check", help="Run a lightweight compile and file-layout check")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "status":
        return cmd_status(args)
    if args.command == "smoke-check":
        return cmd_smoke_check(args)
    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
