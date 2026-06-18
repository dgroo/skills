#!/usr/bin/env python3
"""Emit a markdown block describing other Claude Code sessions in this project's cwd.

A "sibling session" is another CC conversation whose jsonl log lives under
`~/.claude/projects/<encoded-cwd>/`, excluding the current session (identified
via $CLAUDE_CODE_SESSION_ID).

Liveness is judged by the timestamp of the session's *last actual turn* (the
newest user/assistant entry), NOT the jsonl file's mtime. The file's mtime bumps
for reasons unrelated to a human working — session-close summary writes, metadata
flushes, the away_summary write itself — so an idle or just-ended session can have
a very recent mtime while its last real turn is minutes old. Reporting mtime as
"20s ago, active" is how a parked session masquerades as a live collision.

Two further guards against false "live" positives:
  * A tight LIVE window (SUP_SIBLING_LIVE_MIN, default 8m): only sessions whose
    last turn is within it are labelled "active"; older ones are "idle".
  * Predecessor detection across /clear: $CLAUDE_CODE_SESSION_ID changes when you
    /clear, so the pre-clear session is no longer caught by the id exclusion and
    comes back as a same-topic "sibling". Any session whose last turn predates the
    CURRENT session's first turn could not have been concurrently live with it, so
    it's flagged as a likely predecessor rather than a collision.

ACTIVE_WINDOW_MIN remains the outer "show it at all" cutoff (default 120m).

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
from datetime import datetime
from pathlib import Path

ACTIVE_WINDOW_MIN = int(os.environ.get("SUP_SIBLING_WINDOW_MIN", "120"))
LIVE_WINDOW_MIN = int(os.environ.get("SUP_SIBLING_LIVE_MIN", "8"))
MAX_SIBLINGS = int(os.environ.get("SUP_SIBLING_MAX", "5"))
TOPIC_MAX_LEN = 120

# --- Cold-return mode (--cold) ----------------------------------------------
# When you've been away from a project for a while, the default 120m window and
# this conversation's scrollback are both blind — the live windows are gone (and
# may have died in a reboot), but the transcripts persist on disk. Cold mode
# reconstructs "what you had going last time you were here" from those files.
#
# Self-gating: cold mode prints nothing when the gap since last presence is below
# COLD_THRESHOLD_HOURS, so the caller can invoke it unconditionally and treat any
# output as the cold signal.
COLD_THRESHOLD_HOURS = float(os.environ.get("SUP_COLD_THRESHOLD_HOURS", "20"))
COLD_LOOKBACK_DAYS = int(os.environ.get("SUP_COLD_LOOKBACK_DAYS", "14"))
COLD_CLUSTER_HOURS = float(os.environ.get("SUP_COLD_CLUSTER_HOURS", "48"))
COLD_MAX_ROWS = int(os.environ.get("SUP_COLD_MAX", "10"))
COLD_TOPIC_MAX_LEN = 60


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


def parse_ts(s: str | None) -> float | None:
    """Parse an ISO-8601 timestamp (with trailing Z) to epoch seconds."""
    if not s:
        return None
    try:
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        return datetime.fromisoformat(s).timestamp()
    except (ValueError, TypeError):
        return None


def _user_text(obj: dict) -> str | None:
    content = obj.get("message", {}).get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        for part in content:
            if isinstance(part, dict) and part.get("type") == "text":
                return part.get("text", "")
    return None


def scan_session(jsonl_path: Path) -> dict | None:
    """Single-pass scan of a session jsonl.

    Returns a dict with the best topic hint plus the epoch timestamps of the
    last turn (any user/assistant entry) and the first turn. Returns None if the
    file can't be read.
    """
    latest_away_summary = None
    custom_title = None
    latest_user_text = None
    last_turn_ts = None
    first_turn_ts = None

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
                elif t in ("user", "assistant"):
                    ts = parse_ts(obj.get("timestamp"))
                    if ts is not None:
                        last_turn_ts = ts
                        if first_turn_ts is None:
                            first_turn_ts = ts
                    if t == "user":
                        text = _user_text(obj)
                        if text:
                            latest_user_text = text
    except OSError:
        return None

    return {
        "topic": latest_away_summary or custom_title or latest_user_text,
        "last_turn_ts": last_turn_ts,
        "first_turn_ts": first_turn_ts,
    }


def run_cold(extra_cwds: list[str]) -> int:
    """Reconstruct the session cluster from the last time you were in this project.

    Scans this checkout's project dir plus any worktree checkouts passed as args
    (their sessions live under a differently-encoded project dir, so the default
    cwd-scoped scan can't see them). Computes the gap since you were last present;
    prints nothing — staying silent so the caller can treat output as the cold
    signal — unless that gap exceeds COLD_THRESHOLD_HOURS.
    """
    primary = os.getcwd()
    current_session = os.environ.get("CLAUDE_CODE_SESSION_ID", "")
    now = time.time()
    lookback_cutoff = now - COLD_LOOKBACK_DAYS * 86400

    # (cwd, checkout-label) — the primary checkout plus each worktree path.
    targets: list[tuple[str, str]] = [(primary, "main checkout")]
    for path in extra_cwds:
        path = path.strip()
        if path and path != primary:
            targets.append((path, Path(path).name))

    sessions = []  # (last_turn_ts, session_id, info, checkout_label)
    for cwd, label in targets:
        project_dir = Path.home() / ".claude" / "projects" / encode_cwd(cwd)
        if not project_dir.is_dir():
            continue
        for jsonl in project_dir.glob("*.jsonl"):
            session_id = jsonl.stem
            if session_id == current_session:
                continue
            info = scan_session(jsonl)
            if info is None or info["last_turn_ts"] is None:
                continue
            if info["last_turn_ts"] < lookback_cutoff:
                continue
            sessions.append((info["last_turn_ts"], session_id, info, label))

    if not sessions:
        return 0

    last_presence = max(s[0] for s in sessions)
    gap_hours = (now - last_presence) / 3600.0
    if gap_hours < COLD_THRESHOLD_HOURS:
        return 0  # warm — caller stays terse, this prints nothing

    # The "cluster" = sessions whose last turn falls within COLD_CLUSTER_HOURS
    # before your last presence: the set of windows you had going at the time,
    # not every session in the lookback period.
    cluster_cutoff = last_presence - COLD_CLUSTER_HOURS * 3600
    cluster = sorted((s for s in sessions if s[0] >= cluster_cutoff), reverse=True)[
        :COLD_MAX_ROWS
    ]

    header = (
        f"**Cold-return briefing:** last active here {human_age(now - last_presence)} — "
        f"reconstructing what you had going (transcripts survive reboots; the live "
        f"windows may not)."
    )
    if len(cluster) == 1:
        intro = "Last time you were here, one session was going:"
    else:
        intro = f"Last time you were here, {len(cluster)} sessions were going:"

    rows = [
        "| Session | Working on… | Where | Last turn |",
        "| --- | --- | --- | --- |",
    ]
    for last_turn_ts, session_id, info, label in cluster:
        topic = truncate(info["topic"] or "(no topic hint)", COLD_TOPIC_MAX_LEN)
        rows.append(
            f"| `{session_id[:8]}` | {topic} | {label} | "
            f"{human_age(now - last_turn_ts)} |"
        )

    print("\n".join([header, "", intro, "", *rows]))
    return 0


def main() -> int:
    argv = sys.argv[1:]
    if argv and argv[0] == "--cold":
        return run_cold(argv[1:])

    cwd = os.getcwd()
    project_dir = Path.home() / ".claude" / "projects" / encode_cwd(cwd)
    if not project_dir.is_dir():
        return 0

    current_session = os.environ.get("CLAUDE_CODE_SESSION_ID", "")
    now = time.time()
    cutoff = now - ACTIVE_WINDOW_MIN * 60

    # First-turn timestamp of THIS session, so we can spot predecessors: a sibling
    # whose last turn predates our start was never concurrently live with us.
    my_start_ts = None
    if current_session:
        info = scan_session(project_dir / f"{current_session}.jsonl")
        if info:
            my_start_ts = info["first_turn_ts"]

    siblings = []
    for jsonl in project_dir.glob("*.jsonl"):
        session_id = jsonl.stem
        if session_id == current_session:
            continue
        info = scan_session(jsonl)
        if info is None:
            continue
        # Liveness is driven by the last real turn, falling back to file mtime
        # only when the transcript carried no parseable turn timestamp.
        activity_ts = info["last_turn_ts"]
        if activity_ts is None:
            try:
                activity_ts = jsonl.stat().st_mtime
            except OSError:
                continue
        if activity_ts < cutoff:
            continue
        siblings.append((activity_ts, session_id, info))

    if not siblings:
        return 0

    siblings.sort(reverse=True)
    siblings = siblings[:MAX_SIBLINGS]

    live_cutoff = now - LIVE_WINDOW_MIN * 60
    # A session that ended before we started can't be a live collision. If it
    # ended *just* before (within the live window), it's almost certainly the
    # pre-/clear self; if it ended long before, it's just an older idle session.
    preclear_gap = LIVE_WINDOW_MIN * 60
    any_active = False
    rendered = []
    for activity_ts, session_id, info in siblings:
        ended_before_us = my_start_ts is not None and activity_ts < my_start_ts
        is_predecessor = ended_before_us and (my_start_ts - activity_ts) <= preclear_gap
        is_active = not ended_before_us and activity_ts >= live_cutoff
        any_active = any_active or is_active
        if is_predecessor:
            label = "predecessor"
        elif is_active:
            label = "active"
        else:
            label = "idle"
        topic = info["topic"] or "(no topic hint available)"
        suffix = (
            " · (ended before this session — likely your pre-/clear session)"
            if is_predecessor
            else ""
        )
        rendered.append(
            f"- `{session_id[:8]}` · **{label}** {human_age(now - activity_ts)} · "
            f"{truncate(topic)}{suffix}"
        )

    header = (
        f"**Sibling sessions:** {len(siblings)} other session(s) in this cwd "
        f"(last turn within {ACTIVE_WINDOW_MIN}m):"
    )
    footer = (
        "_**active** = last turn within "
        f"{LIVE_WINDOW_MIN}m, may be a live window worth continuing in. "
        "**idle**/**predecessor** are informational, not collisions._"
        if any_active
        else f"_None are active (no last turn within {LIVE_WINDOW_MIN}m) — "
        "informational only, not live collisions._"
    )

    print("\n".join([header, *rendered, "", footer]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
