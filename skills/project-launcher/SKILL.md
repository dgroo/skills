---
name: project-launcher
description: Generate a per-project GUI launcher (.app + inner shell script) that opens a new terminal window, cd's into the project, and attaches to a tmux session on Rocinante24 over Tailscale. Lives in the project directory itself (gitignored). Run inside the project root. Reuses the `roci` shell function from dotfiles and `/terminal-setup`'s OSC 11 color mechanism — does not reimplement either. Use when asked to "create a launcher", "make a .app for this project", "project launcher", or `/project-launcher`.
argument-hint: [app-name]
---

# Per-project GUI launcher

For each project that you remotely tmux into on `rocinante24`, get a `.app` bundle in the project root (e.g. `~/code/<project>/<Name>.app`) that:

- Launches from Spotlight, Launchpad, or the Dock.
- Opens a new terminal window in the user's preferred terminal (defaults to iTerm2; detection via `$TERM_PROGRAM` and `~/.config/projlaunch/terminal` overrides).
- `cd`s into the project locally (`/terminal-setup`'s OSC 11 chpwd hook fires and sets the window background from `.groot-project.toml` — but only briefly; see note below).
- Calls `roci` (the `tailscale ssh ... tmux new-session -A` shorthand from `~/.shrc`) to attach/create the project's tmux session on Rocinante24.
- After the SSH session ends, drops into a fresh interactive shell so the window stays usable.

## How this fits with neighbors

- **`/terminal-setup`** handles per-project background color (`.groot-project.toml` + OSC 11). This skill does **not** touch color — the launcher's local `cd` fires the chpwd hook and emits the OSC 11 escape, but **once `roci` (SSH) takes over the terminal, the local window's background reverts and does not persist into the remote tmux session.** OSC 11 doesn't travel over SSH. Per-project visual identity for the remote tmux session lives in the tmux status bar on Rocinante24 (color/name), not in the local window chrome. Run `/terminal-setup` if you want a color signal for the local Serenity-side moments (a brief flash during launch, or any non-SSH shells in that project).
- **`roci` / `remote_tmux`** in `~/.shrc` handles SSH + tmux. This skill does not reimplement either. The `.launch.sh` it generates calls `roci` with no args (defaults: session name = cwd basename, remote path = local cwd).
- This skill **supersedes** the earlier `scripts/projlaunch` + `scripts/projlaunch-make-app` pair in the `remote-coding-setup` repo. That pair built `.app`s under `~/Applications/`; this skill builds them into the project directory, gitignored. Old scripts will be retired by the same commit that lands this skill.

## How to invoke

```
/project-launcher          # use Title-cased project basename for the .app name
/project-launcher Warball  # explicit app name (e.g., when basename is "warball2" but you want "Warball")
```

Run from the project root (anywhere with a `.groot-project.toml`, or anywhere — the TOML is optional). The skill is idempotent: re-running regenerates the launcher.

## What it does

The actual work is done by `~/.claude/skills/project-launcher/project_launcher.py`. Steps it takes:

1. Read `.groot-project.toml` if present (used for `[launcher].name` override; everything else has sensible defaults).
2. Compute the project name (CLI arg → TOML → cwd basename) and `.app` name (Title-cased project name).
3. Write `<project>/.launch.sh` — a `#!/bin/zsh -i` script that:
   ```zsh
   cd "<project-abs-path>"
   roci
   exec zsh -i
   ```
4. Compile `<project>/<AppName>.app` with `osacompile` from a tiny AppleScript:
   ```applescript
   tell application "iTerm"
       activate
       create window with default profile command "/bin/zsh -i <project-abs-path>/.launch.sh"
   end tell
   ```
   For other terminals (Ghostty / Alacritty / Kitty / WezTerm / Terminal.app), the AppleScript dispatches via a case block — same shape, different `tell ... command` line.
5. Add `.launch.sh` and `<AppName>.app` to the project's `.gitignore` if not already present.
6. Print a summary: where the files are, how to drag-to-Dock, and the smoke-test steps.

## Adding a new project later

```
cd ~/code/<newproject>
/project-launcher
# then drag the generated <Newproject>.app to the Dock if you want it pinned
```

## Adding a new terminal app

Edit `~/.claude/skills/project-launcher/project_launcher.py` — there's one `TERMINAL_LAUNCH_SCRIPTS` map. Add an entry. No other change needed.

## Why script-file indirection (not inline AppleScript heredocs)

The previous approach (`scripts/projlaunch`) constructed AppleScript on the fly via a heredoc and tried to embed a multi-quoted `zsh -i -c '...'` command inside. It worked in reduced reproductions but failed via the real `.app` pathway in a way that turned out to be a separate dotfiles bug (zsh `local path=` shadowed `$PATH`). Even so, the script-file indirection (write a `#!/bin/zsh -i` script to disk, have iTerm invoke it directly) is the cleaner pattern — it sidesteps multi-layer quoting and makes the inner command trivially inspectable on disk.

## Background

Original spec: `~/code/0.llm/remote-coding-setup/design/notes/archived/2026-05-19-serenity26-launcher-prompt.md`. Refactor spec: same dir, `2026-05-20-phase-5c-launcher-refactor.md`. (Both moved to `archived/` 2026-05-20 once consumed.) The launcher unblocks Phase 6 (Apple Container memory isolation) on Rocinante24.
