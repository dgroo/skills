#!/usr/bin/env python3
"""Upstream issues/PRs with news — silent unless something moved.

Two passes, one report:

  watched   Every `**Watch:** <github issue/PR url>` in an unresolved entry of
            any REVISIT.md under the code root (`/revisit add --watch <url>`
            writes these). Covers issues Derek only upvoted, not just filed.
  authored  Issues Derek filed on repos he doesn't own (his own repos are the
            self-check / substrate-sync issue flow's job). The catch-all for
            bugs nobody wrote a REVISIT entry for.

An item has news when it's closed/merged (watched: any time, since its REVISIT
entry is still open; authored: within CLOSED_DAYS), or when its latest comment
is from someone other than Derek within NEWS_DAYS. "Last comment isn't mine"
is the "haven't answered yet" signal, so no seen-state file is needed.

Run rarely and centrally — remote-coding-setup's CLAUDE.md wires it into /sup
there only. Each run costs GitHub API calls, and most runs find nothing.
Prints nothing when gh is missing, offline, or unauthenticated. Needs network:
run sandbox-disabled.

Usage: upstream-watch.py [--watched-only | --authored-only]
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

NEWS_DAYS = int(os.environ.get("UPSTREAM_WATCH_NEWS_DAYS", "30"))
CLOSED_DAYS = int(os.environ.get("UPSTREAM_WATCH_CLOSED_DAYS", "14"))
CODE_ROOT = Path(os.environ.get("UPSTREAM_WATCH_CODE_ROOT", Path.home() / "code"))
MAX_ISSUES = 50

# Where REVISIT.md files live, relative to the code root: top-level repos and
# one level of grouping dirs (e.g. 0.llm/<repo>), canonical design/ or legacy root.
REVISIT_GLOBS = [
    "*/REVISIT.md",
    "*/design/REVISIT.md",
    "*/*/REVISIT.md",
    "*/*/design/REVISIT.md",
]
SKIP_TOP_DIRS = {"worktrees"}  # worktree copies would double-count entries

ENTRY_SPLIT_RE = re.compile(r"^## ", re.MULTILINE)
RESOLVED_RE = re.compile(r"^\*\*Resolved:\*\*", re.MULTILINE)
WATCH_RE = re.compile(r"^\*\*Watch:\*\*(.+)$", re.MULTILINE)
GITHUB_ITEM_RE = re.compile(r"https://github\.com/[\w.-]+/[\w.-]+/(?:issues|pull)/\d+")

ITEM_FIELDS = """
  __typename
  ... on Issue { number title url state closedAt stateReason
    repository { nameWithOwner }
    comments(last: 1) { nodes { author { login } createdAt } } }
  ... on PullRequest { number title url state closedAt
    repository { nameWithOwner }
    comments(last: 1) { nodes { author { login } createdAt } } }
"""

SEARCH_QUERY = (
    "query($q: String!, $n: Int!) { search(query: $q, type: ISSUE, first: $n) { nodes {"
    + ITEM_FIELDS
    + "} } }"
)


def gh(*args: str) -> str | None:
    try:
        out = subprocess.run(
            ["gh", *args], capture_output=True, text=True, timeout=30, check=True
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout


def graphql(query: str, **variables) -> dict | None:
    args = ["api", "graphql", "-f", f"query={query}"]
    for key, value in variables.items():
        flag = "-F" if isinstance(value, int) else "-f"
        args += [flag, f"{key}={value}"]
    raw = gh(*args)
    if not raw:
        return None
    try:
        return json.loads(raw).get("data")
    except json.JSONDecodeError:
        return None


def parse_ts(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def watched_urls() -> dict[str, str]:
    """url -> 'repo-dir/slug' of the open REVISIT entry that watches it."""
    found: dict[str, str] = {}
    for pattern in REVISIT_GLOBS:
        for path in sorted(CODE_ROOT.glob(pattern)):
            if path.relative_to(CODE_ROOT).parts[0] in SKIP_TOP_DIRS:
                continue
            owner = (
                path.parent.parent.name
                if path.parent.name == "design"
                else path.parent.name
            )
            for entry in ENTRY_SPLIT_RE.split(path.read_text())[1:]:
                if RESOLVED_RE.search(entry):
                    continue
                slug = entry.splitlines()[0].split("—")[-1].strip()
                for field in WATCH_RE.findall(entry):
                    for url in GITHUB_ITEM_RE.findall(field):
                        found.setdefault(url, f"{owner}/{slug}")
    return found


def fetch_urls(urls: list[str]) -> list[dict]:
    if not urls:
        return []
    aliases = "\n".join(
        f'i{n}: resource(url: "{url}") {{ {ITEM_FIELDS} }}'
        for n, url in enumerate(urls)
    )
    data = graphql("query {" + aliases + "}") or {}
    return [item for item in data.values() if item]


def search(q: str) -> list[dict]:
    data = graphql(SEARCH_QUERY, q=q, n=MAX_ISSUES) or {}
    return [n for n in (data.get("search") or {}).get("nodes", []) if n]


def label(item: dict) -> str:
    return f"{item['repository']['nameWithOwner']}#{item['number']}"


def reply_news(item: dict, me: str, now: datetime) -> str | None:
    last = (item.get("comments") or {}).get("nodes") or []
    if not last:
        return None
    author = (last[0].get("author") or {}).get("login", "ghost")
    when = parse_ts(last[0]["createdAt"])
    if author == me or now - when > timedelta(days=NEWS_DAYS):
        return None
    return f"{author} replied {(now - when).days}d ago"


def close_news(item: dict) -> str | None:
    if item.get("state") == "OPEN":
        return None
    reason = (item.get("stateReason") or item["state"]).lower().replace("_", " ")
    return f"{reason} {item['closedAt'][:10]}"


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    me = (gh("api", "user", "-q", ".login") or "").strip()
    if not me:
        return 0
    now = datetime.now(timezone.utc)
    lines: list[str] = []
    seen: set[str] = set()

    if mode != "--authored-only":
        watched = watched_urls()
        for item in fetch_urls(list(watched)):
            seen.add(item["url"])
            closed, reply = close_news(item), reply_news(item, me, now)
            if closed or reply:
                glyph = "✅" if closed else "💬"
                lines.append(
                    f"{glyph} {label(item)} — {closed or reply}: {item['title']} "
                    f"{item['url']}  (watched by REVISIT {watched[item['url']]})"
                )

    if mode != "--watched-only":
        closed_since = (now - timedelta(days=CLOSED_DAYS)).date().isoformat()
        for item in search(f"author:{me} is:issue is:open -user:{me}"):
            if item["url"] in seen:
                continue
            reply = reply_news(item, me, now)
            if reply:
                lines.append(
                    f"💬 {label(item)} — {reply}: {item['title']} {item['url']}"
                )
        for item in search(
            f"author:{me} is:issue is:closed closed:>={closed_since} -user:{me}"
        ):
            if item["url"] in seen:
                continue
            lines.append(
                f"✅ {label(item)} — {close_news(item)}: {item['title']} {item['url']}"
            )

    if lines:
        print("Upstream issues with news:")
        for ln in lines:
            print(f"  {ln}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
