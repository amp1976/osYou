#!/usr/bin/env python3
"""
OSDone Capture: single-purpose task intake.

- Captures tasks fast, without categorization.
- Appends to a single Markdown inbox with timestamps.
- Can also list the most recent captured tasks.

Usage:
  python src/osdone_capture.py "Call art director about dummy copy"
  python src/osdone_capture.py --list
  python src/osdone_capture.py --list 20
"""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import sys


DEFAULT_INBOX = Path("inbox/tasks_inbox.md")


def ensure_inbox(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(
            "# Tasks inbox\n\n"
            "New tasks you enter appear here; then you can prioritize them.\n\n"
            "---\n\n",
            encoding="utf-8",
        )


def timestamp() -> str:
    # Local time, readable, sortable enough for humans
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def capture_task(path: Path, task: str) -> None:
    task = task.strip()
    if not task:
        raise ValueError("Please enter some text here.")

    ensure_inbox(path)

    line = f"- [{timestamp()}] {task}\n"
    with path.open("a", encoding="utf-8") as f:
        f.write(line)


def list_tasks(path: Path, limit: int) -> None:
    ensure_inbox(path)
    text = path.read_text(encoding="utf-8")
    lines = [ln for ln in text.splitlines() if ln.startswith("- [")]
    for ln in lines[-limit:]:
        print(ln)


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(add_help=True)
    p.add_argument(
        "task",
        nargs="*",
        help="Name and describe your task briefly, with quotation marks around it. If you don't use quotation marks, begin your text with --list.",
    )
    p.add_argument(
        "--inbox",
        default=str(DEFAULT_INBOX),
        help=f"Path to inbox markdown file (default: {DEFAULT_INBOX})",
    )
    p.add_argument(
        "--list",
        nargs="?",
        const="10",
        help="List your most urgent tasks (default 10). Optionally pass a number, e.g. --list 25",
    )
    return p.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    inbox_path = Path(args.inbox)

    if args.list is not None:
        try:
            limit = int(args.list)
            if limit <= 0:
                raise ValueError
        except ValueError:
            print("Error: --list expects a positive number.", file=sys.stderr)
            return 2
        list_tasks(inbox_path, limit)
        return 0

    task_text = " ".join(args.task).strip()
    if not task_text:
        print('Error: Provide a task with quotation mark around it, or type --list before your text.', file=sys.stderr)
        return 2

    try:
        capture_task(inbox_path, task_text)
    except Exception as e:
        print(f"Error capturing task: {e}", file=sys.stderr)
        return 1

    print(f"Captured → {inbox_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
