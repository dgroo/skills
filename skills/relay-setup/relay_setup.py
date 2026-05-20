#!/usr/bin/env python3
"""Per-project initializer for the Roci↔Serenity Relay.

Creates the mailbox files committed to a project repo so that two (or more)
hosts running Claude Code can use the relay's scripts to hand work back and
forth via git commits.

Run from anywhere inside the target project. Refuses to clobber an existing
relay setup. Does NOT commit — stages changes for the human to review.
"""

from __future__ import annotations

import argparse
import socket
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_HOSTS = ["rocinante24", "serenity26"]
DEFAULT_POLL_INTERVAL_SECONDS = 60
DEFAULT_WAIT_TIMEOUT = "30m"

GITIGNORE_MARKER_START = "# === relay (added by /relay-setup) ==="
GITIGNORE_MARKER_END = "# === /relay ==="
GITIGNORE_LINES = [
    GITIGNORE_MARKER_START,
    "design/relay/.wait-status",
    "design/relay/.wait-exit",
    GITIGNORE_MARKER_END,
]


class SetupError(RuntimeError):
    """Surface-level setup failure with a clear message."""


def short_hostname() -> str:
    return socket.gethostname().split(".")[0].lower()


def run_git(args: list[str], cwd: Path) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise SetupError(
            f"git {' '.join(args)} failed:\n{result.stderr.strip() or result.stdout.strip()}"
        )
    return result.stdout.strip()


def discover_project_root(start: Path) -> Path:
    try:
        toplevel = run_git(["rev-parse", "--show-toplevel"], cwd=start)
    except SetupError as exc:
        raise SetupError(f"not inside a git working tree (from {start}): {exc}") from exc
    return Path(toplevel)


def verify_origin_remote(root: Path) -> str:
    try:
        return run_git(["remote", "get-url", "origin"], cwd=root)
    except SetupError as exc:
        raise SetupError(
            "no `origin` remote configured. The relay polls origin for handoffs; "
            "add a remote first (`git remote add origin <url>`)."
        ) from exc


def current_branch(root: Path) -> str:
    # `symbolic-ref --short HEAD` works on unborn branches (no commits yet) and
    # for normal branches alike; `rev-parse --abbrev-ref HEAD` errors out on
    # unborn branches because HEAD doesn't resolve.
    branch = run_git(["symbolic-ref", "--short", "HEAD"], cwd=root)
    if not branch:
        raise SetupError(
            "couldn't determine current branch (detached HEAD?). The mailbox branch needs a name."
        )
    return branch


def render_state_md(initial_active: str, hosts: list[str], at: str) -> str:
    body_when_human = (
        "Relay newly initialized; no host holds the ball yet.\n\n"
        f"Edit `active:` above to one of {hosts} and commit + push when you're "
        "ready to start a relay cycle.\n"
    )
    body_when_host = (
        f"Relay newly initialized. `{initial_active}` holds the ball first; "
        "its CC can use `relay-handoff` to pass to another host whenever its first "
        "chunk of work is done.\n"
    )
    body = body_when_human if initial_active == "human-required" else body_when_host
    return (
        "---\n"
        f"active: {initial_active}\n"
        f"since: {at}\n"
        "last_handoff: null\n"
        "budget_attempts_remaining: null\n"
        "human_question: null\n"
        "---\n"
        "\n"
        "# Current task\n"
        "\n"
        f"{body}\n"
        "# Path ownership this cycle\n"
        "\n"
        "_(none declared yet — set by the first real handoff)_\n"
    )


def render_config_toml(hosts: list[str], branch: str) -> str:
    hosts_str = ", ".join(f'"{h}"' for h in hosts)
    return (
        "# design/relay/config.toml — Roci↔Serenity Relay per-project config.\n"
        "# Edited by /relay-setup; rarely touched after.\n"
        "\n"
        f"hosts = [{hosts_str}]\n"
        f'branch = "{branch}"\n'
        f"poll_interval_seconds = {DEFAULT_POLL_INTERVAL_SECONDS}\n"
        f'default_wait_timeout = "{DEFAULT_WAIT_TIMEOUT}"\n'
    )


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def update_gitignore(root: Path) -> bool:
    """Append the relay block to the project's .gitignore if not already there.

    Returns True if changes were made.
    """
    gitignore = root / ".gitignore"
    existing = gitignore.read_text() if gitignore.exists() else ""
    if GITIGNORE_MARKER_START in existing:
        return False
    needs_leading_newline = existing and not existing.endswith("\n")
    addition = ("\n" if needs_leading_newline else "") + "\n".join(GITIGNORE_LINES) + "\n"
    if not existing:
        gitignore.write_text(addition.lstrip("\n"))
    else:
        # Add a blank line of separation if the existing file doesn't end in one
        sep = "\n" if not existing.endswith("\n\n") else ""
        gitignore.write_text(existing + sep + addition)
    return True


def check_relay_scripts_installed() -> list[str]:
    """Return the list of relay-* scripts that are NOT on PATH."""
    expected = ["relay-status", "relay-handoff", "relay-wait", "relay-flag-human"]
    missing = []
    for cmd in expected:
        # `command` is a shell builtin; spawn through sh -c to exercise it.
        result = subprocess.run(
            ["sh", "-c", f"command -v {cmd}"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            missing.append(cmd)
    return missing


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Initialize a project for the Roci↔Serenity Relay.",
    )
    parser.add_argument(
        "--hosts",
        default=",".join(DEFAULT_HOSTS),
        help=f"Comma-separated participating hosts (default: {','.join(DEFAULT_HOSTS)}).",
    )
    parser.add_argument(
        "--branch",
        default=None,
        help="Mailbox branch (default: the current branch in the project repo).",
    )
    parser.add_argument(
        "--initial-active",
        default="human-required",
        help=(
            "Initial holder of the ball. One of the hosts in --hosts, or "
            "'human-required' (default — Derek picks via post-bootstrap STATE.md edit)."
        ),
    )
    args = parser.parse_args()

    hosts = [h.strip() for h in args.hosts.split(",") if h.strip()]
    if len(hosts) < 2:
        print(
            f"ERROR: need at least 2 hosts; got {hosts}. "
            "The relay needs at least two parties to hand off between.",
            file=sys.stderr,
        )
        return 2

    initial_active = args.initial_active
    if initial_active != "human-required" and initial_active not in hosts:
        print(
            f"ERROR: --initial-active={initial_active!r} must be one of {hosts} "
            "or 'human-required'.",
            file=sys.stderr,
        )
        return 2

    try:
        root = discover_project_root(Path.cwd())
        origin_url = verify_origin_remote(root)
    except SetupError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    branch = args.branch or current_branch(root)
    relay_dir = root / "design" / "relay"

    if relay_dir.exists():
        print(
            f"ERROR: {relay_dir} already exists. Refusing to clobber. "
            "If you want to reinitialize, remove the directory manually first.",
            file=sys.stderr,
        )
        return 1

    me = short_hostname()
    if me not in hosts:
        print(
            f"WARNING: this host ({me!r}) is not in the chosen hosts list ({hosts}). "
            "Setup will proceed, but you won't be able to use the relay scripts "
            "from this host until you add it.",
            file=sys.stderr,
        )

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    write_file(relay_dir / "STATE.md", render_state_md(initial_active, hosts, now))
    write_file(relay_dir / "handoffs" / ".gitkeep", "")
    write_file(relay_dir / "config.toml", render_config_toml(hosts, branch))
    gitignore_changed = update_gitignore(root)

    paths_to_stage = [
        relay_dir / "STATE.md",
        relay_dir / "handoffs" / ".gitkeep",
        relay_dir / "config.toml",
    ]
    if gitignore_changed:
        paths_to_stage.append(root / ".gitignore")

    try:
        run_git(["add", "--", *(str(p) for p in paths_to_stage)], cwd=root)
    except SetupError as exc:
        print(
            f"WARNING: files were written but `git add` failed: {exc}\n"
            "You'll need to `git add` them manually before committing.",
            file=sys.stderr,
        )

    missing_scripts = check_relay_scripts_installed()

    print(f"✓ Relay initialized in {relay_dir.relative_to(root)}/")
    print(f"  hosts:           {hosts}")
    print(f"  mailbox branch:  {branch}")
    print(f"  initial active:  {initial_active}")
    print(f"  origin remote:   {origin_url}")
    if gitignore_changed:
        print(f"  .gitignore:      relay block appended")
    else:
        print(f"  .gitignore:      already had relay block (skipped)")
    print()
    if missing_scripts:
        print(
            "⚠ The following relay scripts are NOT installed on this host's PATH:\n"
            f"    {', '.join(missing_scripts)}\n"
            "  Install them via dotfiles (`dotpull` on the host once they're "
            "pushed to ~/bin/ in the dotfiles repo) before trying to use the relay."
        )
        print()
    print("Next steps for Derek:")
    print("  1. Review the staged changes:  git diff --cached")
    if initial_active == "human-required":
        print("  2. Commit + push the bootstrap:")
        print('       git commit -m "Relay: initialize via /relay-setup"')
        print("       git push")
        print(
            f"  3. Edit {relay_dir.relative_to(root)}/STATE.md to set `active:` to "
            f"one of {hosts}, commit + push to start the first cycle."
        )
    else:
        print("  2. Commit + push the bootstrap (this also sets the first active host):")
        print(
            f'       git commit -m "Relay: initialize, {initial_active} starts"'
        )
        print("       git push")
        print(f"  3. On {initial_active}, run `relay-status` to confirm the ball is there.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
