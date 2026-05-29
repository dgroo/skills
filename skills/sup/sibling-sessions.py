#!/usr/bin/env python3
"""Emit a markdown block describing sibling Claude Code sessions active in this project's cwd.

A "sibling session" is another CC conversation whose jsonl log lives under
`~/.claude/projects/<encoded-cwd>/` and was modified within ACTIVE_WINDOW_MIN
minutes, excluding the current session (identified via $CLAUDE_CODE_SESSION_ID).

Topic hint per session, in priority order:
  1. Latest `system/away_summary` content (CC writes this as a natural-language summary)
  2. `custom-title` customTitle from the file's first line (initial user message snippet)
  3. Last user `message.content` text

Prints nothing if no siblings found — caller can suppress the section.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

ACTIVE_WINDOW_MIN = int(os.environ.get("SUP_SIBLING_WINDOW_MIN", "120"))
MAX_SIBLINGS = int(os.environ.get("SUP_SIBLING_MAX", "5"))
TOPIC_MAX_LEN = 120


def encode_cwd(cwd: str) -> str:
    """Match Claude Code's project-dir encoding: replace `/` and `.` with `-`."""
    return cwd.replace("/", "-").replace(".", "-")


def human_age(seconds: float) -> str:
    if seconds < 60:
        return f"{int(seconds)}s ago"
    if seconds < 3600:
        return f"{int(seconds // 60)}m ago"
    if seconds < 86400:
        return f"{int(seconds // 3600)}h ago"
    return f"{int(seconds // 86400)}d ago"


def truncate(s: str, n: int = TOPIC_MAX_LEN) -> str:
    s = " ".join(s.split())
    return s if len(s) <= n else s[: n - 1] + "…"


def extract_topic(jsonl_path: Path) -> str | None:
    """Find the best one-line topic hint from a session jsonl.

    Reads the file once, tracking the latest away_summary, the custom-title,
    and the latest user message text. Picks in priority order at the end.
    """
    latest_away_summary = None
    custom_title = None
    latest_user_text = None

    try:
        with jsonl_path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue

                t = obj.get("type")
                if t == "custom-title" and custom_title is None:
                    custom_title = obj.get("customTitle")
                elif t == "system" and obj.get("subtype") == "away_summary":
                    content = obj.get("content")
                    if content:
                        latest_away_summary = content
                elif t == "user":
                    msg = obj.get("message", {})
                    content = msg.get("content")
                    if isinstance(content, str):
                        latest_user_text = content
                    elif isinstance(content, list):
                        for part in content:
                            if isinstance(part, dict) and part.get("type") == "text":
                                latest_user_text = part.get("text", "")
                                break
    except OSError:
        return None

    return latest_away_summary or custom_title or latest_user_text


def main() -> int:
    cwd = os.getcwd()
    project_dir = Path.home() / ".claude" / "projects" / encode_cwd(cwd)
    if not project_dir.is_dir():
        return 0

    current_session = os.environ.get("CLAUDE_CODE_SESSION_ID", "")
    cutoff = time.time() - ACTIVE_WINDOW_MIN * 60

    siblings = []
    for jsonl in project_dir.glob("*.jsonl"):
        session_id = jsonl.stem
        if session_id == current_session:
            continue
        mtime = jsonl.stat().st_mtime
        if mtime < cutoff:
            continue
        siblings.append((mtime, session_id, jsonl))

    if not siblings:
        return 0

    siblings.sort(reverse=True)
    siblings = siblings[:MAX_SIBLINGS]

    now = time.time()
    lines = [
        f"**Sibling sessions:** {len(siblings)} active in this project's cwd within the last {ACTIVE_WINDOW_MIN}m:"
    ]
    for mtime, session_id, path in siblings:
        topic = extract_topic(path) or "(no topic hint available)"
        lines.append(
            f"- `{session_id[:8]}` · {human_age(now - mtime)} · {truncate(topic)}"
        )
    lines.append("")
    lines.append(
        "_If one matches what this `/sup` is for, consider continuing there rather than starting fresh here._"
    )

    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
