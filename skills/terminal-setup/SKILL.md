---
name: terminal-setup
description: Set a per-project terminal background color (and optional shell alias) that follows you across iTerm2, Ghostty, Alacritty, Kitty, WezTerm. The color is recorded in `.groot-project.toml` and applied via the OSC 11 chpwd hook in ~/.shrc. Use when starting a new project, asked to "set up terminal", "set terminal color", "color this project", "add a project alias", or when bootstrapping a new repo. Successor to /iterm-setup — handles `[iterm]` → `[terminal]` migration automatically.
argument-hint: [name-or-alias | auto]
---

# Per-Project Terminal Background + Alias

Each project gets a deterministic background color that the shell applies on `cd` via OSC 11. Visually distinct projects at a glance — without any terminal-specific configuration. Optionally also adds a shell alias to `~/.shrc` (or `~/.zshrc`) for quick navigation.

The actual work is done by `~/.claude/skills/terminal-setup/terminal-setup.py`. This skill is the interactive wrapper.

## How this differs from /iterm-setup (the predecessor)

| Old (`/iterm-setup`)                                                   | New (`/terminal-setup`)                                                             |
| ---------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| Wrote iTerm2 Dynamic Profile JSON                                      | Writes only `.groot-project.toml`                                                   |
| iTerm-only (used Automatic Profile Switching)                          | Any terminal supporting OSC 11                                                      |
| State glyph via iTerm `OSC 1337 SetUserVar`                            | State glyph via shell precmd + OSC 2                                                |
| Title format string `\(user.claudeState)…` lived in iTerm Custom Title | Shell precmd assembles the title from `~/.claude/state/<tty>.{glyph,project,topic}` |
| `[iterm]` TOML section with `color` key                                | `[terminal]` TOML section with `background` key (legacy reads transparently)        |

The chpwd + precmd plumbing lives in `~/.shrc` (block labeled "Claude terminal state"). It's installed once and works for every project.

## How to Invoke

```
/terminal-setup              # use cwd basename as the project name
/terminal-setup myproject    # explicit name (e.g., for worktree dirs)
/terminal-setup mp           # if cwd basename is `myproject`, this is the alias shorthand
/terminal-setup auto         # let the agent pick color + alias autonomously (no prompts)
```

## Process

> **Personal-preference rule (read first).** Color and alias are personal preference — the **user** picks them. This holds **even when the session is operating under a "work without stopping for clarifying questions" / "no clarifying questions" directive**. That directive applies to ambiguities the agent can resolve from context, not to taste choices that are inherently the user's call. The whole purpose of this skill is to surface those choices.
>
> **The only exception:** the user explicitly invoked `/terminal-setup auto`. In that mode, the agent picks color + alias without asking and proceeds end-to-end. Any other invocation form **must** prompt.

0. **Check for `.groot-project.toml`.** Before anything else:

   ```
   ~/.claude/skills/terminal-setup/terminal-setup.py --groot-toml-read
   ```

   The script reads `./.groot-project.toml` and prints `KEY=VALUE` lines for the `[terminal]` section (empty output if file/section absent). **Legacy `[iterm]` sections read transparently** — the `color` key is renamed to `background` on the way out, so the parsed dict looks the same whether the file is old or new.

   **If non-empty** (file exists with recorded settings), prompt via AUQ — frame it around the recorded color, and include the recorded alias if present:
   - **Option 1 — Apply recorded settings:** _"Apply `[terminal].background = <hex>` (and `alias = <alias>`, if present) — skip the palette."_ On selection, jump to **step 5** with `--hex <color>` and `--alias <alias>` (or `--no-alias` if absent). Don't prompt for color or alias.
   - **Option 2 — Pick a new color:** _"Run the normal palette flow. File stays untouched until end-of-flow, then I'll ask whether to update it."_ Remember "file existed; may need update at end."
   - **Option 3 — Cancel:** _"Don't change anything."_ Exit.

   **Auto mode:** if the file exists with a valid background, apply it silently (no prompt).

   **Legacy `[iterm]` files migrate automatically.** Step 5's write replaces the `[iterm]` block with a `[terminal]` block. If a user wants to migrate a project _without_ changing the color, they can run:

   ```
   ~/.claude/skills/terminal-setup/terminal-setup.py --migrate-toml
   ```

   directly. For a batch migration across `~/code/*`:

   ```
   find ~/code -name .groot-project.toml -maxdepth 2 -exec \
     ~/.claude/skills/terminal-setup/terminal-setup.py --migrate-toml {} \;
   ```

   **If empty** (no file, or no `[terminal]`/`[iterm]` section): check for a legacy iTerm2 Dynamic Profile before falling through to a fresh palette pick.

   ```
   ~/.claude/skills/terminal-setup/terminal-setup.py --legacy-iterm-read
   ```

   This reads `~/Library/Application Support/iTerm2/DynamicProfiles/<basename>.json` and prints `background=#RRGGBB` if found. **If non-empty** — the user has an existing iTerm-era color for this project but no `.groot-project.toml` yet — prompt via AUQ:
   - **Option 1 — Import iTerm color (recommended):** _"Found `<hex>` recorded for this project in iTerm. Save it to `.groot-project.toml` so it follows you to other terminals."_ On selection, jump to **step 5** with `--hex <color>` (and `--no-alias` if step 1 found an existing alias targeting cwd; otherwise let the alias prompt run).
   - **Option 2 — Pick a new color:** Run the normal palette flow.
   - **Option 3 — Cancel:** Exit.

   **Auto mode:** if a legacy iTerm color exists, import it silently — same contract as "the file is the recorded preference" applied to the iTerm-era source of truth.

   **If both are empty** (no TOML, no iTerm JSON for this project): continue to step 1, the normal new-project flow.

1. **Determine the project name and the alias name.**
   - **Project name** (used as the `name` field if explicitly persisted, and for the AUQ prompt): defaults to `basename $(pwd)`.
   - **Alias name** (used for the `~/.shrc` shell alias): defaults to the project name.
   - If the user passed an arg, interpret as follows:
     - **Arg is exactly `auto`** → enter auto mode (see step 2 / step 3).
     - **Arg looks like an abbreviation** of cwd basename → treat arg as **alias**, project name comes from cwd. Confirm.
     - **Arg differs from cwd basename in a non-abbreviation way** → treat arg as **project name** (worktree case). Confirm.
     - **Arg matches cwd basename** → treat arg as project name; ask separately whether they want a different alias.
   - Confirm with the user when cwd is suspicious (`~`, `~/Downloads`, anywhere not obviously a project root) — even in `auto` mode, since picking the wrong directory is a footgun, not a preference.

   **Then check for an existing alias for this directory:**

   ```
   ~/.claude/skills/terminal-setup/terminal-setup.py --cwd-aliases
   ```

   This prints alias names from `~/.shrc` (and `~/.zshrc` as fallback) whose `cd` target resolves to the current directory. Handles direct `cd ~/X` / `cd /abs/X` / `cd $HOME/X` and chained `code;cd X`-style aliases.
   - **If non-empty**: default to **reusing the existing alias** (skip the alias step), and only add a new alias if they explicitly want one (then pass `--force-alias`).
   - **If empty:** proceed with the alias suggestion as normal.

2. **Present the palette via `AskUserQuestion` (AUQ).**

   Gather palette data with two bash calls (can run in parallel):

   ```
   ~/.claude/skills/terminal-setup/terminal-setup.py <project> --list-colors
   ~/.claude/skills/terminal-setup/terminal-setup.py <project> --list-colors --vivid
   ```

   Parse both outputs to extract:
   - **Dark palette (1–14):** RGB tuples, names, and `used by:` annotations (from the first call).
   - **Vivid palette (15–28):** RGB tuples and names (from the second call — the script numbers vivid 1–14 there; _re-number to 15–28_ for continuous numbering in the AUQ).
   - **Other existing projects' colors** (from the first call's footer): hex values from sibling `~/code/*/.groot-project.toml` files that sit outside the palette — used for near-clash awareness when picking the suggested color.

   **Dark-only rule for defaults.** The suggested color (Option 1) and any auto-mode pick **must come from the dark palette (1–14), never the vivid palette (15–28).** Vivid is reserved for special-case highlight projects the user explicitly opts into (e.g. `~/.claude` itself).

   Pick a **suggested color** (the first AUQ option) from the dark palette, preferring:
   - An unused color (no `used by:` annotation).
   - A hue distinct from the "Other existing projects" hexes (avoid near-clashes).
   - A name/aesthetic that fits the project.

   Build the AUQ with **exactly 3 options**:
   - **Option 1 — `"<Name> (#<n>) — use suggested"`:** Preview shows the color's swatch + 2–3 line rationale.
   - **Option 2 — `"Browse dark palette (1–14)"`:** Preview shows all 14 dark swatches numbered 1–14 with their names, annotating `(used by ...)` on the used colors and marking the suggested one with `← suggested`.
   - **Option 3 — `"Browse vivid palette (15–28)"`:** Preview shows all 14 vivid swatches numbered 15–28.

   **AUQ formatting (learned the hard way — must follow):**
   - **Preview truncates around ~17 lines.** Don't combine palettes into a single preview — it gets cut off with a "N lines hidden" indicator.
   - **Do not add an explicit "Other" / "Type something" option.** AUQ has a built-in `Notes` field (user presses `n`) — that _is_ the free-text path. Mention it explicitly in each option's description: _"Press 'n' to type your choice in Notes."_
   - **ANSI swatches DO render in previews — but ONLY if a real ESC byte (0x1b) reaches the AUQ JSON.** Build the swatch as the literal 12-character ESC sequence `\u001b[48;2;R;G;Bm      \u001b[0m` — write **six characters** `\`, `u`, `0`, `0`, `1`, `b` for each ESC; the AUQ JSON parser converts each to a real ESC byte. **Never paste a raw 0x1b byte into your JSON** — it gets stripped on the way to AUQ and renders as visible text like `[48;2;R;G;Bm`. If you see that in a preview, the ESC byte was eaten somewhere; rebuild the payload with the explicit `\u001b` form.
   - Each browse-preview's first line should remind: _"Press 'n' to type your choice (e.g. '20', 'Teal', 'vivid Indigo')."_

   **Interpreting the response:**
   - **Option 1 selected, no notes** → use the suggested color.
   - **Notes contain a number 1–14** → dark palette at that index.
   - **Notes contain a number 15–28** → vivid palette; pass `--vivid --color <N−14>` to the script in step 5.
   - **Notes contain a color name** → default to dark. Prefix `vivid ` or `v ` means vivid.
   - **Option 2 or 3 selected with no notes** → ask in a follow-up message for the specific number.

   **Auto mode (only when invoked as `/terminal-setup auto`):** skip the AUQ. Still run the two bash calls to read the palette data, then pick the lowest-numbered swatch in the dark palette with no `used by:` annotation and no near-clash with other projects' colors. Proceed straight to step 3.

   **Change-color path (project's `.groot-project.toml` already has a `background`):** the first bash call's output begins with a banner like `Existing background for 'myproject': Plum (#3A5F2C)` and the current color is marked `★ current` in the palette. In this case:
   - Frame the AUQ question as _"You're already on Plum — change to?"_
   - Pick a _different_ unused color as the suggestion.
   - The alias is almost certainly already set up (step 1's `--cwd-aliases` will have caught it) — default to `--no-alias`.

3. **Confirm the alias (or skip).**
   - If the user already implied an alias name in step 1, confirm: _"Adding `alias <name>='cd ...'` to ~/.shrc — sound good?"_
   - If no alias name yet, ask: _"Want a shell alias too? Default would be `<project>`. Type a different name, ENTER to accept, or 'no' to skip."_
   - If they skip, pass `--no-alias` in step 5.
   - **Auto mode:** use the project name as the alias and proceed without confirmation.

4. _(no separate title-format step — the shell handles title assembly now)_

5. **Write `.groot-project.toml` (and the alias).** Run:

   ```
   ~/.claude/skills/terminal-setup/terminal-setup.py <project> --color <N> --alias <alias>
   ```

   Or with `--no-alias` to skip the alias. The script will:
   - Write `[terminal].background` (and `alias`) to `./.groot-project.toml`. If a legacy `[iterm]` block exists, it's removed in the same pass.
   - Pick the right alias body. If `~/.shrc` (or `~/.zshrc`) contains `alias code='cd ~/code'` AND the target is a direct child of `~/code/`, it uses the `'code;cd <project>'` shorthand. Otherwise falls back to `'cd ~/<rel>'` for paths under `$HOME`, or `'cd <abs>'`.
   - Insert the alias after `alias code='cd ~/code'` when present (clusters with existing nav aliases); otherwise appends at end of file. Idempotent.
   - Warn (not overwrite) if a different alias with the same name already exists.
   - **Refuse to add the alias** (without `--force-alias`) if a _different_ alias already resolves to the current cwd.

6. **Verify.**
   - **Background**: open a new tab and `cd` into the project — the background color should change immediately (the chpwd hook in `~/.shrc` emits OSC 11). Or run `cd .` in the current shell to retrigger the hook.
   - **Alias**: tell the user to `source ~/.shrc` or open a new shell.
   - **Title state**: a fresh shell with Claude Code running should show `<state> <project> - <topic>` once the state hooks have fired. The `<state>` prefix comes from `~/.claude/state/<tty_slug>.glyph` (updated by Claude's status hooks); the rest is assembled by the precmd in `~/.shrc`.

## One-time install: ~/.shrc plumbing

The chpwd + precmd functions live in `~/.shrc`, under a block headed `# Claude terminal state (terminal-agnostic; replaces iTerm Dynamic Profiles)`. This is installed once per machine — re-running `/terminal-setup` per project does _not_ touch `~/.shrc` beyond the alias insertion. If you're setting up a brand-new machine, copy the block from a working machine or re-run the rework recipe.

The block depends on `~/.shrc` being sourced by `~/.zshrc` (and optionally `~/.bashrc`). The `direnv hook` line right below it confirms that pattern is in place.

## What this does NOT do

- Doesn't write iTerm Dynamic Profile JSON. (Old JSON at `~/Library/Application Support/iTerm2/DynamicProfiles/<project>.json` is harmless to leave in place — it's superseded but not load-bearing. Delete manually if cleanup is wanted.)
- Doesn't manage profiles created via any terminal's GUI.
- Doesn't auto-fire on `cd`, `git init`, or `git clone` — invocation is always explicit. `.groot-project.toml` is the _recorded preference_; `/terminal-setup` (or `/groot-project` during bootstrap) is what writes it and applies the alias.
- Doesn't restore the iTerm cross-tab waiting-queue feature on non-iTerm terminals (that's iTerm-AppleScript-bridge-only; see `~/.claude/hooks/_waiting_queue.py`). Switching to Ghostty temporarily disables `cwcycle`-style cross-tab cycling.

## `.groot-project.toml` — the persistence file

A tracked-in-git, per-project TOML at repo root that records the terminal choices. A fresh clone on another machine reproduces the per-project setup via `/terminal-setup`.

Schema (current):

```toml
[terminal]
background = "#3A5F2C"   # always uppercase #RRGGBB after write
# alias = "mp"           # optional; what to add to ~/.shrc
# name  = "myproject"    # optional; project-name override (rare)
```

Legacy schema (still readable; auto-migrated on next write):

```toml
[iterm]
color = "#3A5F2C"
# alias = "mp"
```

Other top-level sections are preserved verbatim by the write helper. Unknown keys inside `[terminal]` are silently dropped on read.

Helper flags on `terminal-setup.py`:

- `--groot-toml-read [DIR]` — print `[terminal]` (or translated `[iterm]`) as `KEY=VALUE` lines. Default cwd; empty output if file/section absent; exit 1 on malformed TOML.
- `--groot-toml-write [DIR] --hex #RRGGBB [--alias NAME] [--groot-toml-write-name]` — standalone (does NOT run the picker); merges into existing file, removes legacy `[iterm]`, preserves other sections, normalizes color to uppercase.
- `--migrate-toml [DIR-or-FILE]` — standalone migration of `[iterm]` → `[terminal]`; prints `migrated <path>` / `already-current <path>` / `no-file <path>`.

## Help

When invoked as `/terminal-setup help`, print the following block verbatim:

```
terminal-setup — Per-project terminal background color (and optional shell
alias). Terminal-agnostic via OSC 11 chpwd hook in ~/.shrc; works in iTerm2,
Ghostty, Alacritty, Kitty, WezTerm.

Usage: /terminal-setup [name-or-alias | auto]

Arguments:
  (none)            Use cwd basename as the project name.
  <name>            Explicit project name (e.g. for worktree dirs).
  <alias>           If it looks like an abbreviation of cwd basename, use as alias.
  auto              Pick color + alias autonomously, no prompts. Always picks
                    from dark palette (1-14); uses project basename as alias.
  help              Show this message.

Flow (interactive):
  0. Check .groot-project.toml     Apply / new / cancel if present.
  1. Resolve project + alias names Confirm if cwd looks suspicious.
  2. Palette via AskUserQuestion   Dark (1-14) suggested; vivid (15-28) opt-in.
  3. Confirm alias                 Or skip with --no-alias.
  5. Write .groot-project.toml     And ~/.shrc alias insertion.
  6. Verify                        New tab cd; OSC 11 fires.

Personal-preference rule:
  Color and alias are USER picks, even under no-clarifying-questions mode.
  Exception: explicit `auto` invocation.

Legacy iTerm support:
  Legacy [iterm] TOML reads transparently; renames to [terminal] on next write.
  Legacy iTerm Dynamic Profile JSON detected and offered for import.

State persistence: .groot-project.toml at repo root.
Color application: OSC 11 emitted by _claude_project_bg_chpwd in ~/.shrc.

See SKILL.md for full reference.
```

## Reference

- Persistence: `<project>/.groot-project.toml` (`[terminal]` section, schema above).
- Color application: OSC 11 emitted by `_claude_project_bg_chpwd` in `~/.shrc`.
- Title state: per-TTY files under `~/.claude/state/`, assembled into OSC 2 by `_claude_title_assemble` in `~/.shrc`. Written by `~/.claude/hooks/_terminal_state.py`.
- Color usage is read from sibling `~/code/*/.groot-project.toml` files (no separate state file to drift).
