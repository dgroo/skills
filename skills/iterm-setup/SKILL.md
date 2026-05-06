---
name: iterm-setup
description: Create a uniquely-colored iTerm2 profile for a project with Automatic Profile Switching, plus an optional shell alias for quick `cd`. Use when starting a new project, asked to "set up iterm", "set terminal color", "iterm profile", "automatic profile switching", "color this terminal", "add a project alias", or when bootstrapping a new repo.
argument-hint: [name-or-alias]
---

# iTerm2 Per-Project Profile Setup

Creates an iTerm2 Dynamic Profile with a custom background color and an Automatic Profile Switching (APS) rule that fires when the user `cd`s into the project's directory. Each project gets a visually distinct terminal so the user can tell at a glance which project they're in. Optionally also adds a shell alias to `~/.zshrc` for quick navigation.

The actual work is done by `~/.claude/scripts/iterm-setup.py`. This skill is a thin wrapper that walks the user through naming, color selection, and alias setup.

## How to Invoke

```
/iterm-setup              # use cwd basename as the project name
/iterm-setup myproject    # explicit profile name (e.g., for worktree dirs)
/iterm-setup chgr         # if cwd basename is `changer`, this is the alias shorthand
```

## Process

1. **Determine the profile name and the alias name.**
   - **Profile name** (used for the iTerm2 profile + APS rule): defaults to `basename $(pwd)`.
   - **Alias name** (used for the `~/.zshrc` shell alias): defaults to the profile name.
   - If the user passed an arg, interpret as follows:
     - **Arg looks like an abbreviation** of cwd basename (shorter, often a substring or initials, e.g. `chgr` for `changer`, `gos` for `grootOS`) → treat arg as **alias**, profile name comes from cwd. Confirm.
     - **Arg differs from cwd basename in a non-abbreviation way** (e.g. you're in `myproject-feature-x` and they pass `myproject`) → treat arg as **profile name** (worktree case). Confirm.
     - **Arg matches cwd basename** → treat arg as profile name; ask separately whether they want a different alias.
   - Confirm with the user when cwd is suspicious (`~`, `~/Downloads`, anywhere not obviously a project root).

   **Then check for an existing alias for this directory** before suggesting a new one:

   ```
   ~/.claude/scripts/iterm-setup.py --cwd-aliases
   ```

   This prints alias names from `~/.zshrc` whose `cd` target resolves to the current directory (one per line; empty if none). Handles direct `cd ~/X` / `cd /abs/X` / `cd $HOME/X` and chained `code;cd X`-style aliases.

   - **If the output is non-empty** (e.g. user is in `~/code/grootOS` and `gos` already targets it): tell the user, default to **reusing the existing alias** (skip the alias step), and only add a new alias if they explicitly want one (then pass `--force-alias`).
   - **If empty:** proceed with the alias suggestion as normal.

2. **Show the palette and let them pick.** Run via Bash:

   ```
   ~/.claude/scripts/iterm-setup.py <profile> --list-colors
   ```

   **Critical:** the script's stdout contains ANSI truecolor escape codes that the user's terminal renders as actual colored swatches. The user *needs* to see these to make a meaningful pick — that's the whole point.
   - **DO NOT paraphrase, summarize, or reformat the output.** Don't write your own numbered list of color names.
   - **DO NOT wrap the output in a markdown code block** when relaying — code blocks suppress ANSI rendering in many UIs.
   - The natural Bash tool flow is fine: run the command, the user sees the raw stdout, you then prompt them.

   The output annotates colors already used by other profiles (e.g. `Plum  used by: changer`). Steer the user toward an **unused** color so neighboring terminals stay visually distinct. Ask them to pick a number (1-10).

   **If a profile for `<profile>` already exists**, the output begins with a banner like `Existing profile 'changer': Plum (#4), APS=/*/changer*` and the current color is marked `★ current` in the palette. This is the **change-color** path:
   - Frame the question accordingly: *"You're already on Plum. Which would you like to change to?"*
   - Pass `--force` in step 4 (the script otherwise refuses to overwrite).
   - The alias is almost certainly already set up (step 1's `--cwd-aliases` will have caught it) — default to `--no-alias`.

3. **Confirm the alias (or skip).**
   - If the user already implied an alias name in step 1, confirm: *"Adding `alias <name>='cd ...'` to ~/.zshrc — sound good?"*
   - If no alias name yet, ask: *"Want a shell alias too? Default would be `<profile>`. Type a different name, ENTER to accept, or 'no' to skip."*
   - If they skip, pass `--no-alias` in step 4.

4. **Confirm the title format (or skip / customize).** The script sets a Custom tab/window title that pairs with the Claude Code state hooks (`🟢` / `❓` / `☑️`). Default format:

   ```
   \(user.claudeState)\(session.profileName) - \(session.name)
   ```

   When run interactively, the script prompts: *Accept default? [Y/n=skip/c=customize]*. The skill normally lets that interactive prompt do its job — only steer the user when they want a non-default for a specific project (uncommon).
   - **Default (just hit ENTER):** title format is set on this profile.
   - **`n` / skip:** profile inherits the Default profile's title (use this if the user has already configured a global Custom Title on the iTerm Default profile and doesn't want per-project overrides).
   - **`c` / customize:** prompt for a different interpolated string.

   **Non-interactive equivalents:**
   - `--title-format '\(custom format)'` — explicit format.
   - `--no-title` — don't set title keys at all (inherit).

5. **Create the profile (and alias).** Run:

   ```
   ~/.claude/scripts/iterm-setup.py <profile> --color <N> --alias <alias>
   ```

   Or with `--no-alias` to skip the alias. Add `--force` only if the user explicitly wants to overwrite an existing profile. Add `--pattern <PAT>` if they want a non-default APS rule (default is `/*/<profile>*`). Add `--title-format` / `--no-title` if step 4 resolved non-interactively.

   The script will:
   - Write the iTerm2 profile JSON to `~/Library/Application Support/iTerm2/DynamicProfiles/`.
   - Pick the right alias body: `'code;cd <project>'` for projects directly under `~/code/`, `'cd ~/<rel>'` for other paths under `$HOME`, `'cd <abs>'` otherwise.
   - Insert the alias after `alias code='cd ~/code'` in `~/.zshrc` (clusters with existing nav aliases). Idempotent — skips silently if the exact line is already there.
   - Warn (not overwrite) if a different alias with the same name already exists.
   - **Refuse to add the alias** (without `--force-alias`) if a *different* alias in `~/.zshrc` already resolves to the current cwd. Prevents duplicates like adding `grootOS` when `gos='code;cd grootOS'` already exists. The skill should normally have already caught this in step 1, but this is the safety net.

6. **Verify.**
   - For the profile: open a new tab and `cd` into the project — the background color should switch automatically.
   - For the alias: tell the user to `source ~/.zshrc` or open a new shell.
   - For the title: a fresh shell with the new profile should show `<state> <project> - <topic>` once Claude Code's state hooks have fired at least once (the `claudeState` user variable is empty until the first hook runs, in which case the prefix is just blank).
   - The script warns if iTerm2 shell integration isn't detected (APS won't fire without it).

## One-time iTerm Default profile setup

The state-glyph behavior also works for sessions that *don't* have a per-project profile (i.e. running under iTerm's Default profile). To enable it: open iTerm Preferences → Profiles → **Default** → General, set the Title dropdown to **Custom**, and use the same format string as above. All Dynamic Profiles inherit this unless they explicitly override it (which is what `iterm-setup.py` does by default — you can opt out with `--no-title` to inherit instead).

## What this does NOT do

- Doesn't manage profiles created via the iTerm2 GUI.
- Doesn't list or remove profiles. To remove: `rm ~/Library/Application\ Support/iTerm2/DynamicProfiles/<name>.json`.
- Doesn't remove aliases from `~/.zshrc` when a profile is deleted — left as a manual step so we never edit shell config destructively.
- Doesn't auto-fire on `git init` or `git clone` — invocation is always explicit.

## Reference

- Profile output dir: `~/Library/Application Support/iTerm2/DynamicProfiles/`
- Color usage is read directly from on-disk profiles (matches background RGB to palette) — no separate state file to drift.
- iTerm2 Dynamic Profiles: https://iterm2.com/documentation-dynamic-profiles.html
- iTerm2 names and titles (interpolated string variables like `\(session.name)`, `\(user.foo)`): https://iterm2.com/documentation-session-title.html
- The `claudeState` user variable is set by `~/.claude/hooks/{stop,notify,submit}-status.py` via the iTerm `OSC 1337;SetUserVar` escape sequence.
