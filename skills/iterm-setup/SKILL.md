---
name: iterm-setup
description: Create a uniquely-colored iTerm2 profile for a project with Automatic Profile Switching, plus an optional shell alias for quick `cd`. Use when starting a new project, asked to "set up iterm", "set terminal color", "iterm profile", "automatic profile switching", "color this terminal", "add a project alias", or when bootstrapping a new repo.
argument-hint: [name-or-alias | auto]
---

# iTerm2 Per-Project Profile Setup

Creates an iTerm2 Dynamic Profile with a custom background color and an Automatic Profile Switching (APS) rule that fires when the user `cd`s into the project's directory. Each project gets a visually distinct terminal so the user can tell at a glance which project they're in. Optionally also adds a shell alias to `~/.zshrc` for quick navigation.

The actual work is done by `~/.claude/skills/iterm-setup/iterm-setup.py`. This skill is a thin wrapper that walks the user through naming, color selection, and alias setup.

## How to Invoke

```
/iterm-setup              # use cwd basename as the project name
/iterm-setup myproject    # explicit profile name (e.g., for worktree dirs)
/iterm-setup mp           # if cwd basename is `myproject`, this is the alias shorthand
/iterm-setup auto         # let the agent pick color + alias autonomously (no prompts)
```

## Process

> **Personal-preference rule (read first).** Color and alias are personal preference — the **user** picks them. This holds **even when the session is operating under a "work without stopping for clarifying questions" / "no clarifying questions" directive**. That directive applies to ambiguities the agent can resolve from context, not to taste choices that are inherently the user's call. The whole purpose of this skill is to surface those choices.
>
> **The only exception:** the user explicitly invoked `/iterm-setup auto`. In that mode, the agent picks color + alias without asking and proceeds end-to-end. Any other invocation form **must** prompt.

1. **Determine the profile name and the alias name.**
   - **Profile name** (used for the iTerm2 profile + APS rule): defaults to `basename $(pwd)`.
   - **Alias name** (used for the `~/.zshrc` shell alias): defaults to the profile name.
   - If the user passed an arg, interpret as follows:
     - **Arg is exactly `auto`** → enter auto mode (see step 2 / step 3). Profile name = cwd basename, alias = profile name. No further confirmation.
     - **Arg looks like an abbreviation** of cwd basename (shorter, often a substring or initials, e.g. `mp` for `myproject`, `wa` for `webapp`) → treat arg as **alias**, profile name comes from cwd. Confirm.
     - **Arg differs from cwd basename in a non-abbreviation way** (e.g. you're in `myproject-feature-x` and they pass `myproject`) → treat arg as **profile name** (worktree case). Confirm.
     - **Arg matches cwd basename** → treat arg as profile name; ask separately whether they want a different alias.
   - Confirm with the user when cwd is suspicious (`~`, `~/Downloads`, anywhere not obviously a project root) — this confirmation runs even in `auto` mode, since picking the wrong directory is a footgun, not a preference.

   **Then check for an existing alias for this directory** before suggesting a new one:

   ```
   ~/.claude/skills/iterm-setup/iterm-setup.py --cwd-aliases
   ```

   This prints alias names from `~/.zshrc` whose `cd` target resolves to the current directory (one per line; empty if none). Handles direct `cd ~/X` / `cd /abs/X` / `cd $HOME/X` and chained `code;cd X`-style aliases.

   - **If the output is non-empty** (e.g. user is in `~/code/webapp` and `wa` already targets it): tell the user, default to **reusing the existing alias** (skip the alias step), and only add a new alias if they explicitly want one (then pass `--force-alias`).
   - **If empty:** proceed with the alias suggestion as normal.

2. **Present the palette via `AskUserQuestion` (AUQ).**

   Gather palette data with two bash calls (can run in parallel):

   ```
   ~/.claude/skills/iterm-setup/iterm-setup.py <profile> --list-colors
   ~/.claude/skills/iterm-setup/iterm-setup.py <profile> --list-colors --vivid
   ```

   Parse both outputs to extract:
   - **Dark palette (1–14):** RGB tuples, names, and `used by:` annotations (from the first call).
   - **Vivid palette (15–28):** RGB tuples and names (from the second call — the script numbers vivid 1–14 there; *re-number to 15–28* for continuous numbering in the AUQ).
   - **Other existing profiles** (from the first call's footer): hex values from other projects that sit outside the palette — used for near-clash awareness when picking the suggested color.

   Pick a **suggested color** (the first AUQ option). From the dark palette, prefer:
   - An unused color (no `used by:` annotation).
   - A hue distinct from the "Other existing profiles" hexes (avoid near-clashes).
   - A name/aesthetic that fits the project (warm/earthy for library-ish, cool/deep for systems, etc.).

   Build the AUQ with **exactly 3 options**:

   - **Option 1 — `"<Name> (#<n>) — use suggested"`:** Preview shows the color's swatch + 2–3 line rationale.
   - **Option 2 — `"Browse dark palette (1–14)"`:** Preview shows all 14 dark swatches numbered 1–14 with their names, annotating `(used by ...)` on the used colors and marking the suggested one with `← suggested`.
   - **Option 3 — `"Browse vivid palette (15–28)"`:** Preview shows all 14 vivid swatches numbered 15–28.

   **AUQ formatting (learned the hard way — must follow):**
   - **Preview truncates around ~17 lines.** Don't combine palettes into a single preview — it gets cut off with a "N lines hidden" indicator.
   - **Do not add an explicit "Other" / "Type something" option.** AUQ has a built-in `Notes` field (user presses `n`) — that *is* the free-text path. Mention it explicitly in each option's description: *"Press 'n' to type your choice in Notes."* The hint is easy to miss otherwise.
   - **ANSI swatches DO render in previews.** Use a 6-space colored block: `\u001b[48;2;R;G;Bm      \u001b[0m` (write the literal text `\u001b` in the JSON string for AUQ — the JSON parser turns it into a real ESC byte).
   - Each browse-preview's first line should remind: *"Press 'n' to type your choice (e.g. '20', 'Teal', 'vivid Indigo')."*

   **Interpreting the response:**
   - **Option 1 selected, no notes** → use the suggested color.
   - **Notes contain a number 1–14** → dark palette at that index.
   - **Notes contain a number 15–28** → vivid palette; pass `--vivid --color <N−14>` to the script in step 5.
   - **Notes contain a color name** (e.g. `Teal`, `Crimson 2`) → default to dark. Prefix `vivid ` or `v ` means vivid (e.g. `vivid Teal`).
   - **Option 2 or 3 selected with no notes** → ask in a follow-up message for the specific number.

   **Auto mode (only when invoked as `/iterm-setup auto`):** skip the AUQ. Still run the two bash calls to read the palette data, then pick the lowest-numbered swatch in the dark palette with no `used by:` annotation and no near-clash with "Other existing profiles." Proceed straight to step 3. Mention the chosen color in the wrap-up so the user can override on a follow-up turn.

   **Change-color path (profile for `<profile>` already exists):** the first bash call's output begins with a banner like `Existing profile 'myproject': Plum (#4), APS=/*/myproject*` and the current color is marked `★ current` in the palette. In this case:
   - Frame the AUQ question as *"You're already on Plum — change to?"*
   - Pick a *different* unused color as the suggestion (don't suggest the current one).
   - Pass `--force` in **step 5** (the script otherwise refuses to overwrite).
   - The alias is almost certainly already set up (step 1's `--cwd-aliases` will have caught it) — default to `--no-alias`.
   - The script preserves the existing APS pattern when `--force` is used without `--pattern`. You don't need to re-pass the binding.

3. **Confirm the alias (or skip).**
   - If the user already implied an alias name in step 1, confirm: *"Adding `alias <name>='cd ...'` to ~/.zshrc — sound good?"*
   - If no alias name yet, ask: *"Want a shell alias too? Default would be `<profile>`. Type a different name, ENTER to accept, or 'no' to skip."*
   - If they skip, pass `--no-alias` in step 4.
   - **Auto mode:** use the profile name as the alias and proceed without confirmation. (If the alias name turns out to be awkward, the user can rename it later — `auto` is opt-in convenience, not perfection.)

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
   ~/.claude/skills/iterm-setup/iterm-setup.py <profile> --color <N> --alias <alias>
   ```

   Or with `--no-alias` to skip the alias. Add `--force` only if the user explicitly wants to overwrite an existing profile. Add `--pattern <PAT>` if they want a non-default APS rule (default is `/*/<profile>*`). Add `--title-format` / `--no-title` if step 4 resolved non-interactively.

   The script will:
   - Write the iTerm2 profile JSON to `~/Library/Application Support/iTerm2/DynamicProfiles/`.
   - Pick the right alias body. If `~/.zshrc` contains `alias code='cd ~/code'` (or its `$HOME` variant) AND the target is a direct child of `~/code/`, it'll use the `'code;cd <project>'` shorthand. Otherwise it falls back to `'cd ~/<rel>'` for paths under `$HOME`, or `'cd <abs>'`. No `alias code=` required — the shorthand is an optimization, not a dependency.
   - Insert the alias after `alias code='cd ~/code'` in `~/.zshrc` when that line is present (clusters with existing nav aliases); otherwise appends at end of file. Idempotent — skips silently if the exact line is already there.
   - Warn (not overwrite) if a different alias with the same name already exists.
   - **Refuse to add the alias** (without `--force-alias`) if a *different* alias in `~/.zshrc` already resolves to the current cwd. Prevents duplicates like adding `webapp` when `wa='cd ~/webapp'` already exists. The skill should normally have already caught this in step 1, but this is the safety net.

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
