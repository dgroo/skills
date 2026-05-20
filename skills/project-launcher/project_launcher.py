#!/usr/bin/env python3
"""Per-project GUI launcher generator. Builds a `.app` bundle + inner
`.launch.sh` script in the current project directory, both gitignored.

The .app opens a new terminal window (preferred app via $PROJLAUNCH_TERMINAL,
~/.config/projlaunch/terminal, or iTerm default), cd's into the project,
calls `roci` to attach to a tmux session on Rocinante24, and after that
session ends drops into a fresh interactive shell.

Run inside the project root. Re-running is idempotent.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

# Per-terminal AppleScript snippet. `{cmd}` placeholder gets the absolute
# path to the project's `.launch.sh`, which is what the new window runs.
# Adding a new terminal app = one entry here. The shape is: an AppleScript
# fragment that opens a new window running the given command.
#
# For terminals controlled by AppleEvents (iTerm, Terminal), the snippet
# wraps the create-window call in `ignoring application responses` so the
# applet returns immediately rather than waiting for the target app to
# acknowledge. Without this, slow iTerm starts produce a spurious
# "AppleEvent timed out (-1712)" error dialog even though the window
# successfully opens. (The .app doesn't use the return value, so there's
# nothing to wait for.)
TERMINAL_LAUNCH_SCRIPTS: dict[str, str] = {
    "iTerm": (
        'tell application "iTerm"\n'
        "    activate\n"
        "    ignoring application responses\n"
        '        create window with default profile command "/bin/zsh -i {cmd}"\n'
        "    end ignoring\n"
        "end tell"
    ),
    "Ghostty": (
        # Ghostty doesn't expose a full AppleScript model; use `open -na`
        # via `do shell script` instead. Same fallback shape that other
        # AppleScript-poor terminals can follow.
        'do shell script "/usr/bin/open -na Ghostty.app --args -e /bin/zsh -i {cmd}"'
    ),
    "Terminal": (
        'tell application "Terminal"\n'
        "    activate\n"
        "    ignoring application responses\n"
        '        do script "/bin/zsh -i {cmd}"\n'
        "    end ignoring\n"
        "end tell"
    ),
    "Alacritty": (
        'do shell script "/usr/bin/open -na Alacritty.app --args -e /bin/zsh -i {cmd}"'
    ),
    "Kitty": ('do shell script "/usr/bin/open -na kitty.app --args /bin/zsh -i {cmd}"'),
    "WezTerm": (
        'do shell script "/usr/bin/open -na WezTerm.app --args start --always-new-process -- /bin/zsh -i {cmd}"'
    ),
}

# `do shell script` runs in /bin/sh and inherits Launch Services' minimal
# env. We need an absolute path for whichever terminal CLI we use. The
# .app pathway will only ever shell out to /usr/bin/open or /usr/bin/osascript;
# never relies on PATH.


def detect_terminal() -> str:
    """Pick the preferred terminal app for new windows.

    Priority: $PROJLAUNCH_TERMINAL → ~/.config/projlaunch/terminal → iTerm.
    Returns a key into TERMINAL_LAUNCH_SCRIPTS.
    """
    explicit = os.environ.get("PROJLAUNCH_TERMINAL", "").strip()
    if explicit:
        return _normalize_terminal(explicit)

    config = Path.home() / ".config" / "projlaunch" / "terminal"
    if config.is_file():
        text = config.read_text().strip().splitlines()[0].strip()
        if text:
            return _normalize_terminal(text)

    return "iTerm"


def _normalize_terminal(name: str) -> str:
    """Map common aliases (with/without `.app`, lowercase, etc.) to a canonical key."""
    stripped = name.removesuffix(".app").strip()
    canonical = {
        "iterm": "iTerm",
        "iterm2": "iTerm",
        "ghostty": "Ghostty",
        "terminal": "Terminal",
        "apple_terminal": "Terminal",
        "alacritty": "Alacritty",
        "kitty": "Kitty",
        "wezterm": "WezTerm",
    }
    key = canonical.get(stripped.lower(), stripped)
    if key not in TERMINAL_LAUNCH_SCRIPTS:
        sys.exit(
            f"project-launcher: unknown terminal '{name}'. "
            f"Known: {', '.join(TERMINAL_LAUNCH_SCRIPTS)}. "
            f"Add an entry to TERMINAL_LAUNCH_SCRIPTS to support it."
        )
    return key


def load_project_toml(project_dir: Path) -> dict:
    """Read `.groot-project.toml` if present. Returns {} if not."""
    toml_path = project_dir / ".groot-project.toml"
    if not toml_path.is_file():
        return {}
    with toml_path.open("rb") as f:
        return tomllib.load(f)


def write_launch_script(project_dir: Path) -> Path:
    """Write `<project>/.launch.sh` and chmod it executable.

    The script cd's locally (triggering `/terminal-setup`'s OSC 11 chpwd
    hook to set the window background) and then calls `roci`, which
    `tailscale ssh`s to Rocinante24 and attaches/creates the tmux session.
    After roci returns, we exec a fresh interactive shell so the window
    stays usable instead of slamming shut.
    """
    script_path = project_dir / ".launch.sh"
    script_path.write_text(
        "#!/bin/zsh -i\n"
        "# Generated by /project-launcher. Re-run the skill to regenerate.\n"
        "# Don't hand-edit — your edits will be overwritten.\n"
        "\n"
        f"cd {shlex_quote(str(project_dir))}\n"
        "roci\n"
        "exec zsh -i\n"
    )
    script_path.chmod(0o755)
    return script_path


def shlex_quote(s: str) -> str:
    """POSIX shell quoting (cheap stand-in for shlex.quote with stable behavior)."""
    import shlex

    return shlex.quote(s)


def write_app(project_dir: Path, app_name: str, launch_script: Path, term: str) -> Path:
    """Generate `<project>/<AppName>.app` via osacompile. Overwrites if present."""
    app_path = project_dir / f"{app_name}.app"

    if app_path.exists():
        shutil.rmtree(app_path)

    snippet = TERMINAL_LAUNCH_SCRIPTS[term].format(cmd=str(launch_script))

    result = subprocess.run(
        ["/usr/bin/osacompile", "-o", str(app_path), "-e", snippet],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        sys.exit(
            f"project-launcher: osacompile failed ({result.returncode}).\n"
            f"stderr: {result.stderr}"
        )
    return app_path


def update_gitignore(project_dir: Path, entries: list[str]) -> list[str]:
    """Append entries to project `.gitignore` if not already present.

    Returns the list of entries actually added (empty if all were already there).
    """
    gi_path = project_dir / ".gitignore"
    existing = gi_path.read_text().splitlines() if gi_path.is_file() else []
    existing_stripped = {line.strip() for line in existing}

    to_add = [e for e in entries if e not in existing_stripped]
    if not to_add:
        return []

    block = []
    if existing and existing[-1].strip():
        # Add a blank line separator if the file doesn't end with one.
        block.append("")
    block.append("# Generated by /project-launcher (don't commit these)")
    block.extend(to_add)

    with gi_path.open("a") as f:
        f.write("\n".join(block) + "\n")

    return to_add


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate a per-project GUI launcher (.app + .launch.sh)."
    )
    parser.add_argument(
        "app_name",
        nargs="?",
        help="Override the .app name. Default: Title-cased cwd basename.",
    )
    parser.add_argument(
        "--terminal",
        help="Override the preferred terminal app for this run.",
    )
    args = parser.parse_args()

    project_dir = Path.cwd().resolve()
    if not project_dir.is_dir():
        sys.exit(f"project-launcher: not a directory: {project_dir}")

    toml = load_project_toml(project_dir)
    launcher_meta = toml.get("launcher", {}) if isinstance(toml, dict) else {}

    project_name = launcher_meta.get("name") or project_dir.name
    app_name = (
        args.app_name or launcher_meta.get("app_name") or project_name.capitalize()
    )

    # Sanitize: .app names can't contain `/` (or other path separators).
    if "/" in app_name or app_name.startswith("."):
        sys.exit(f"project-launcher: invalid app name '{app_name}'.")

    term = _normalize_terminal(args.terminal) if args.terminal else detect_terminal()

    launch_script = write_launch_script(project_dir)
    app_path = write_app(project_dir, app_name, launch_script, term)
    added = update_gitignore(
        project_dir, [".launch.sh", f"{app_name}.app", f"{app_name}.app/"]
    )

    print(f"Created {app_path}")
    print(f"Created {launch_script}")
    if added:
        print(f"Added to .gitignore: {', '.join(added)}")
    else:
        print(".gitignore already covers the generated files.")
    print()
    print(f"Project name:   {project_name}")
    print(f"Terminal:       {term}")
    print()
    print("To use:")
    print(f"  - Spotlight / Launchpad: search for '{app_name}'")
    print(f"  - Dock: drag {app_path.name} from Finder")
    print("Smoke test: open it from a cold state. New terminal window should appear,")
    print("cd into the project, attach to the tmux session on rocinante24, and the")
    print(
        "project's background color should be applied (if .groot-project.toml has one)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
