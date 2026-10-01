#!/usr/bin/env python3
"""PreToolUse hook (Edit|Write|MultiEdit|NotebookEdit): deny writes into a DIFFERENT git repository.

The rule "don't edit other projects' checkouts — file a /request" is an intention;
this is the mechanism. Same-repo worktrees, scratch/temp dirs, and ~/.claude are allowed.
Install via project-setup (references this file by path; no copy to go stale).
"""
import json, os, subprocess, sys
from pathlib import Path


def common_dir(path: Path):
    try:
        out = subprocess.run(["git", "-C", str(path), "rev-parse", "--path-format=absolute", "--git-common-dir"],
                             capture_output=True, text=True, timeout=5)
        return Path(out.stdout.strip()).resolve() if out.returncode == 0 else None
    except Exception:
        return None


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return
    target = payload.get("tool_input", {}).get("file_path") or payload.get("tool_input", {}).get("notebook_path")
    if not target:
        return
    target = Path(target).expanduser()
    if not target.is_absolute():
        target = Path.cwd() / target
    target = target.resolve()
    project = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()).resolve()

    allowed_prefixes = [project, Path.home() / ".claude", Path("/tmp"), Path("/private/tmp"),
                        Path(os.environ.get("TMPDIR", "/nonexistent")).resolve()]
    if any(str(target).startswith(str(p) + os.sep) or target == p for p in allowed_prefixes):
        return

    mine = common_dir(project)
    theirs = common_dir(target.parent if not target.is_dir() else target)
    if theirs is None or theirs == mine:
        return  # not in a repo, or a worktree of THIS repo

    other = theirs.parent.name
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": (
            f"{target} is inside another project's repository ({other}). Don't edit other projects' "
            f"checkouts — their agents may be mid-change. File a request instead:\n"
            f"  python3 ~/.claude/skills/request/scripts/request.py send {other} \"<title>\" --body \"<observation + goal>\"")}}))


if __name__ == "__main__":
    main()
