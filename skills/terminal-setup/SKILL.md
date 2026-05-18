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

0. **Check for `.groot-project.toml` (the persistence file).** Before anything else, run:

   ```
   ~/.claude/skills/iterm-setup/iterm-setup.py --groot-toml-read
   ```

   The script reads `./.groot-project.toml` and prints `KEY=VALUE` lines for the `[iterm]` section (empty output if file or section absent). Parse the output into a dict.

   **If non-empty** (file exists with recorded settings), prompt via AUQ — frame it around the recorded color, and include the recorded alias if present:

   - **Option 1 — Apply recorded settings:** *"Apply `[iterm].color = <hex>` (and `alias = <alias>`, if present) from .groot-project.toml — skip the palette."* On selection, jump to **step 5** with `--hex <color>` and `--alias <alias>` from the file (or `--no-alias` if absent). Don't prompt for color or alias. Title format prompt (step 4) still runs normally unless `auto` mode.
   - **Option 2 — Pick a new color:** *"Run the normal palette flow. File stays untouched until end-of-flow, then I'll ask whether to update it."* Remember "file existed; may need update at end."
   - **Option 3 — Cancel:** *"Don't change anything."* Exit.

   **Auto mode:** if the file exists with a valid `[iterm].color`, apply it silently (no prompt). The persistence file is *exactly* the "already decided" signal that justifies auto-apply. If alias is absent in the file but the cwd has no matching alias yet, auto mode still skips the alias (no prompt, no add — match the existing auto-mode discipline of "lowest-friction defaults, never surprises").

   **If empty** (no file, or no `[iterm]` section): continue to step 1. Remember "no file" — step 7 (offer-to-write) will fire at the end.

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

   **Dark-only rule for defaults.** The suggested color (Option 1) and any auto-mode pick **must come from the dark palette (1–14), never the vivid palette (15–28).** Vivid is reserved for special-case highlight projects the user explicitly opts into (e.g. `~/.claude` itself). The user can still *choose* vivid via the AUQ Notes — just don't ever *suggest* it.

   Pick a **suggested color** (the first AUQ option) from the dark palette, preferring:
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

7. **Offer to write `.groot-project.toml` (persistence).** After a successful create / change-color, prompt to record the current settings so a fresh clone on another machine can reproduce them. Decide what to offer based on the file's state at step 0:

   - **No file at step 0** (fresh setup, or already-configured project that's never been persisted): always offer. AUQ with three options — *Write color + alias / Write color only (skip alias) / Skip*. On accept, run:

     ```
     ~/.claude/skills/iterm-setup/iterm-setup.py --hex <chosen-hex> [--alias <alias>] --groot-toml-write
     ```

     The script prints `written <path>` or `unchanged <path>`.

   - **File existed at step 0 and user picked "Apply recorded settings"**: no prompt — the file already matches. Skip.

   - **File existed at step 0 and user picked "Pick a new color"**: settings just diverged from the file. Prompt: *"Update .groot-project.toml from `<old-hex>` → `<new-hex>`?"*. On accept, run the same `--groot-toml-write` invocation; it'll merge into the existing file and report `updated <path>`.

   The persistence file also covers the *backfill* case: if the user runs `/iterm-setup` on a project that has an existing iTerm profile already (the change-color path) and no `.groot-project.toml`, this step is the moment to capture the current settings into the file for the first time. Phrase the prompt accordingly: *"This project's profile isn't recorded in .groot-project.toml yet. Write it so a fresh clone can reproduce the setup?"*

   **Auto mode:** if the file is absent at step 0, write it automatically using the just-applied color and alias. (Auto mode's contract is "no prompts, sensible defaults" — and persisting the choice you just made is the sensible default.)

   **What gets written.** The script stores `color` (always), `alias` (if you pass `--alias`), and `name` only if you pass `--groot-toml-write-name` together with a positional name. **Default is to omit `name`** — the profile name almost always equals `basename $(pwd)` and storing it in the file makes the file non-portable across worktrees with different basenames. Only set it when the project has a genuine reason for a fixed profile name (rare).

## One-time iTerm Default profile setup

The state-glyph behavior also works for sessions that *don't* have a per-project profile (i.e. running under iTerm's Default profile). To enable it: open iTerm Preferences → Profiles → **Default** → General, set the Title dropdown to **Custom**, and use the same format string as above. All Dynamic Profiles inherit this unless they explicitly override it (which is what `iterm-setup.py` does by default — you can opt out with `--no-title` to inherit instead).

## What this does NOT do

- Doesn't manage profiles created via the iTerm2 GUI.
- Doesn't list or remove profiles. To remove: `rm ~/Library/Application\ Support/iTerm2/DynamicProfiles/<name>.json`.
- Doesn't remove aliases from `~/.zshrc` when a profile is deleted — left as a manual step so we never edit shell config destructively.
- Doesn't auto-fire on `git init` or `git clone` — invocation is always explicit.
- Doesn't auto-fire on `cd` either. `.groot-project.toml` is the *recorded preference*; `/iterm-setup` (or `/groot-project` during bootstrap) is what reads it and applies.

## `.groot-project.toml` — the persistence file

A tracked-in-git, per-project TOML at repo root that records the iTerm choices (and, later, other workstation-conventions sections). The point: a fresh clone on another machine can reproduce the per-project terminal setup via `/iterm-setup` without re-picking a color.

Schema (v1 — `[iterm]` only):

```toml
[iterm]
color = "#3A5F2C"       # background; always uppercase #RRGGBB after write
# alias = "mp"          # optional; what to add to ~/.zshrc
# name  = "myproject"   # optional; profile-name override (rare — see step 7 caveat)
```

Other top-level sections are preserved verbatim by the write helper. Unknown keys inside `[iterm]` are silently dropped on read (forward-compatible).

Helper flags on `iterm-setup.py`:

- `--groot-toml-read [DIR]` — print `[iterm]` as `KEY=VALUE` lines (default cwd; empty output if file/section absent; exit 1 on malformed TOML).
- `--groot-toml-write [DIR] --hex #RRGGBB [--alias NAME] [--groot-toml-write-name]` — standalone (does NOT create a profile); merges into existing file, preserves other sections, normalizes color to uppercase, prints `written|updated|unchanged <path>`.

## Reference

- Profile output dir: `~/Library/Application Support/iTerm2/DynamicProfiles/`
- Color usage is read directly from on-disk profiles (matches background RGB to palette) — no separate state file to drift.
- `.groot-project.toml` lives at the project root, tracked in git, format described above.
- iTerm2 Dynamic Profiles: https://iterm2.com/documentation-dynamic-profiles.html
- iTerm2 names and titles (interpolated string variables like `\(session.name)`, `\(user.foo)`): https://iterm2.com/documentation-session-title.html
- The `claudeState` user variable is set by `~/.claude/hooks/{stop,notify,submit}-status.py` via the iTerm `OSC 1337;SetUserVar` escape sequence.
