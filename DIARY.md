# Engineering Diary

Latest entries first. Record significant decisions, architecture changes, and non-obvious context.

---

## 2026-05-18 — iterm-setup → terminal-setup, decoupled from iTerm Dynamic Profiles

Reworked the skill to be terminal-agnostic, prompted by exploring Ghostty as an iTerm2 replacement. Two iTerm-specific mechanisms were doing the load-bearing work: (1) Automatic Profile Switching reading a Dynamic Profile JSON in `~/Library/Application Support/iTerm2/DynamicProfiles/`, and (2) `OSC 1337 SetUserVar=claudeState` consumed by the profile's Custom Title interpolation. Neither survives a terminal switch.

Both moved into the shell. **Background color**: `~/.shrc` chpwd hook walks up for `.groot-project.toml`, reads `[terminal].background`, and emits OSC 11. Works in iTerm2, Ghostty, Alacritty, Kitty, WezTerm — anything that honors OSC 11. **State glyph + title**: per-TTY state files under `~/.claude/state/<tty_slug>.{glyph,topic,project}` written by the Claude hooks, assembled by `~/.shrc` precmd into a single OSC 2 emit. Hooks still emit OSC 1337 alongside for iTerm Custom-title back-compat during the transition window.

**TOML schema migration was the trickiest design call.** Renamed `[iterm]` → `[terminal]` and `color` → `background`, since "iterm" / "color" lost their meaning. Read side accepts both transparently (legacy keys translated to canonical on output). Write side always emits `[terminal]` and removes any leftover `[iterm]` block — silent in-place migration on every save. Plus a standalone `--migrate-toml` flag for batch use over `~/code/*/.groot-project.toml`.

**Dropped iTerm-specific surface**: `build_profile`, `pick_title_format_interactive`, `shell_integration_installed`, `color_components`, `DYNAMIC_PROFILES_DIR`, `--pattern/--title-format/--no-title/--force` flags, `ProfileExistsError`. Palette "in-use" awareness now scans `~/code/*/.groot-project.toml` instead of reading DynamicProfiles JSON — same shape of data, sourced from the git-tracked file users actually maintain.

**Back-compat aliases**: `read_groot_project_iterm` / `write_groot_project_iterm` / `ItermSetupError` still resolve to the new names so external callers don't break.

**Test seam**: 51 pytest cases. New coverage: legacy `[iterm]` read paths, the migration write path (drops `[iterm]`, preserves other sections), `--migrate-toml` (`migrated` / `already-current` / `no-file` statuses). All 51 pass.

**What's not yet terminal-agnostic**: `~/.claude/hooks/_waiting_queue.py` and `~/.claude/scripts/claude-waiting`. The cross-tab cycling (`cwcycle` and friends) uses iTerm AppleScript via `$ITERM_SESSION_ID`. On Ghostty the queue files still get written, but the cycling commands won't switch tabs until that side is reworked. Filed as separate follow-up.

**Old iTerm2 Dynamic Profile JSON files** at `~/Library/Application Support/iTerm2/DynamicProfiles/<project>.json` are now harmless leftovers — superseded but not load-bearing. Documented as a manual `rm` cleanup in SKILL.md; not auto-deleting in case users have hand-edited any.

**Coordinated branch**: `~/.claude` and `~/code/claude/skills` both on `terminal-setup-rework`; merged together so the hook + ~/.shrc + skill all land at once.

---

## 2026-05-16 — iterm-setup respects `~/.shrc` shared shell config

Bug fix surfaced immediately after the `.groot-project.toml` feature landed. Smoke-test in this repo: `--cwd-aliases` returned empty for a cwd that demonstrably has a `skills` alias. Cause: `iterm-setup.py` hardcoded `ZSHRC_PATH = ~/.zshrc` for every alias read and write, but the actual `skills` alias lives in `~/.shrc:109` — the shared shell config sourced by both `~/.zshrc:39` and `~/.bashrc:17`. Same root cause broke the alias-write path (would write to `~/.zshrc` for a user whose convention is `~/.shrc`) and the `code;cd X` chain-shorthand detection (because `alias code='cd ~/code'` also lives in `~/.shrc:30`).

Fix is small but touches several call sites. Added `shell_config_files(home)` (discovery — returns existing files in `[~/.shrc, ~/.zshrc]` order, with shrc included only when sourced) and `primary_shell_config_file(home)` (write target — shrc when sourced, zshrc otherwise). Refactored `aliases_targeting_cwd` to read the combined text of all discovered files; renamed `add_alias_to_zshrc` → `add_alias_to_shell_config` with the conflict check scanning combined text (so a `skills` alias in shrc blocks a duplicate write to zshrc) and the write going to the primary file.

**Detection regex for the source statement.** First cut required `source ~/.shrc` (or `. ~/.shrc`) at line-start. Real-world failure: my own `~/.zshrc` has `[ -f ~/.shrc ] && source ~/.shrc` — a defensive guarded source. Relaxed the regex to allow leading `;`, `&`, `|`, or whitespace before `source`/`.` so guarded patterns (`&& source X`, `if [ ... ]; then source X; fi`) all match. Comment-only lines stripped before regex runs; mid-line comments (`echo X # source ~/.shrc`) could in theory false-positive, but the cost is "wrote to .shrc instead of .zshrc," which is harmless and easy to spot.

**Belt-and-suspenders side: global CLAUDE.md.** Added a "Shell config layout" section to `~/.claude/CLAUDE.md` capturing the convention (shared aliases live in `~/.shrc`, sourced by both `~/.zshrc` and `~/.bashrc`). Reasoning: the `~/.zshrc` top-of-file comment ("IF YOU ARE AN LLM: most things should live in .shrc") is invisible to any tool that doesn't actually open `~/.zshrc` — and most tools don't. CLAUDE.md is auto-loaded into every session, so it's the closest thing to "always read." This routes future LLM-driven things (other scripts, ad-hoc bash one-liners, anything that doesn't have its own discovery code) to the right file from the start. The script fix above is for non-LLM code paths (e.g., `/groot-project --auto` invoking iterm-setup non-interactively).

**Tests:** 16 new pytest cases in `test_shell_config.py` using a `fake_home` tmp_path fixture and a `home=` kwarg threaded through the new discovery helpers. Covers: zshrc-only fallback, shrc-present-but-unsourced fallback, shrc+sourced-by-zshrc primary, `.` vs `source` forms, `$HOME` vs `~` forms, guarded `&&` source, `if [...]; then` source, commented-out source ignored, multi-file alias reads, chain-resolution anchored in shrc, primary-file write targeting, noop/conflict detection across both files, anchored insertion. The chain-resolution test uses an absolute path instead of `~/code` because `_resolve_one_alias_body` calls real `Path.home()` — an existing assumption the tests document with a comment rather than refactor away.

**Threaded the `home=` parameter through the new helpers but not `_resolve_one_alias_body`.** The old function uses real `Path.home()` for `~/` expansion; threading `home=` through it would touch six functions and `build_alias_resolver`'s signature for a benefit only the tests see. Documented the constraint in the test instead.

---

## 2026-05-16 — `.groot-project.toml` for portable per-project workstation setup

Adding an in-repo TOML so a fresh clone on a new machine can reproduce per-project iTerm setup without re-picking a color. Today the iTerm Dynamic Profile JSON lives in `~/Library/Application Support/iTerm2/DynamicProfiles/` and the alias lives in `~/.zshrc` — both outside the repo, both lost on a new machine. The new file is `.groot-project.toml` at repo root, tracked in git, with a single `[iterm]` section for v1.

**Decisions:**

- **General `.groot-project.toml`, not iTerm-specific `.iterm.json`.** The user waffled between iTerm-only and a broader file; landed on broader because it composes with future workstation concerns (editor, direnv, etc.) without a rename later. Tooling-keyed sections (`[iterm]`) instead of concern-keyed (`[terminal]`) so switching tools means switching sections — no ambiguous migration of a single block.
- **TOML, not JSON.** Hand-edited file with comments; sections compose naturally; Python 3.11+ stdlib `tomllib` reads it; no new dep.
- **Hex storage (`color = "#3A5F2C"`), not palette name/index.** The palette is _project-name-seeded_ so the same index resolves to different colors per project. Hex is lossless and palette-algorithm-independent. Stored uppercase and validated against the existing `HEX_COLOR_RE` so it round-trips through `--hex`.
- **Hand-rolled writer, no `tomli-w` dep.** The schema is tiny and well-known; the writer is ~30 lines (`_splice_iterm_block`) that finds the `[iterm]` block by regex over top-level section headers and replaces it in place, preserving everything else. Worth the line count to keep the dep surface at zero.
- **Write is intended-state, not patch.** `write_groot_project_iterm` accepts the full intended state of the section; omitting `alias` removes a previously-stored alias. Avoids the partial-update ambiguity that bites you on every config-file API.
- **`name` field is opt-in (`--groot-toml-write-name`), not default.** Profile name is almost always `basename $(pwd)`; storing it would make the file non-portable across worktrees with different basenames. Only write `name` when the project genuinely needs a fixed profile name.
- **Skill orchestrates; Python helpers stay pure.** SKILL.md gets a new step 0 (read-and-prompt) and new step 7 (offer-to-write); the Python script gains `--groot-toml-read` and `--groot-toml-write` as standalone verbs that exit before the normal flow, like `--list-colors` and `--cwd-aliases`. The skill calls them as separate invocations rather than having the normal flow conditionally write the TOML — clearer separation, easier to test.
- **`/groot-project` Phase 7 doesn't need new orchestration.** It already delegates fully to `/iterm-setup`. The new file-detect logic lives in the iterm-setup skill, so `/groot-project` gets the behavior for free. Pre-flight summary surfaces the file's presence/absence so the user sees what Phase 7 will do before it runs.
- **Auto mode auto-applies if the file is present.** The persistence file is exactly the "already decided" signal that justifies auto-apply — no prompt needed. If absent, auto mode auto-writes after profile creation. Matches the "no prompts, sensible defaults" contract.

**Test seam:** 23 pytest cases in `skills/iterm-setup/test_groot_project_toml.py`. Covers absent file, missing/extra sections, malformed TOML, type errors, full round-trip, write-merge-preserves-other-sections, hex normalization, intended-state semantics, invalid alias/name rejection. First Python test file in this repo — earlier skills had no test infrastructure. Tests are stdlib + pytest only; runnable directly with `python3 -m pytest test_groot_project_toml.py`.

**Known drift surfaced (not fixed in this change):** `iterm-setup` skill is missing from the README skills table. Filing as separate cleanup — fixing it here would silently expand scope.

---

## 2026-05-12 — Portability pass on Derek-authored skills

Tried running `/groot-project` against a personal sibling project and it failed because the skill referenced another personal project as the canonical source for stories/helping-hands templates. That kicked off an audit: are these skills portable, or are they personal-config skills disguised as portable ones? Answer: mostly portable but with three real bugs that would break a fresh install (or anyone else picking them up — e.g., if Joe ever wanted these in return).

**Changes made:**

- `/groot-project`: removed all references to a specific personal project; the embedded templates are now the sole canonical source for stories/, helping-hands/, notes/, plans/, design/README. Updated tree-diagram annotations and Reference section accordingly.
- `iterm-setup.py` moved out of `~/.claude/scripts/` and into `skills/iterm-setup/iterm-setup.py` so the skill is self-contained. Left a symlink at the old path for backwards compat with my hooks (`_iterm_title.py`).
- Script's alias-body logic now reads `~/.zshrc` and only emits the `'code;cd X'` shortcut when an `alias code='cd ~/code'` line is detected. Without that anchor, falls back to plain `'cd ~/<rel>'`. The shortcut is now an _optimization_, not a _dependency_.
- `iterm-setup/SKILL.md`: genericized example project names (personal project names → `myproject`/`webapp`) and accurately documented the conditional shortcut.
- `skills-review/SKILL.md`: replaced a hardcoded skills-repo path with runtime discovery via `readlink ~/.claude/skills/<any-local-skill>`. The skill no longer assumes the repo lives at any specific path.

**Decisions:**

- **Move script, don't copy.** Considered `cp` + leaving the original, but two copies invite drift. Move + back-symlink keeps a single canonical file and preserves every existing reference unchanged.
- **Conditional `code;cd` shortcut, not removed.** Considered just stripping the optimization since it's Derek-specific. But it's genuinely useful for me, and the runtime check is one regex; degrading gracefully for everyone else is cheap.
- **Runtime discovery for skills-source, not env var.** Considered a `$LOCAL_SKILLS_REPO` env var pattern. Rejected — `readlink` on any installed symlinked skill already tells you where the repo lives, no config required. Self-bootstrapping beats configuration.
- **Stop having external files outside the skill directory.** New rule (implicit): if a Derek-authored skill depends on a script, the script lives _in the skill directory_, not in `~/.claude/scripts/`. The skills repo is the unit of distribution; anything a skill needs ships with it.

---

## 2026-05-11 — /groot-project coexistence with Joe's upstream

Spent a session sharpening how `/groot-project` plays with `/project-setup` and Joe's tracker skills (`/todo`, `/bug`, `/bug-bash`). The thread connecting all the work: Joe's upstream is a moving target, our local skill needs to coexist without rotting when he changes things, and the original conventions block had a real gap — `DIARY.md` was hand-waved away as "captured in `design/notes/` + `design/plans/`" which isn't honest. Notes are frozen snapshots, plans are forward-looking; neither is a rolling chronological log.

Trigger was looking at two sibling personal projects ahead of running `/groot-project` on them. One had two dated `*.md` files sitting at `design/` root (a plan and its companion spec). Default `/groot-project` would build the canonical subtree _around_ those files and leave them stranded — not great. So the cleanup work piled up: migration defaults, DIARY integration, upstream-drift handling.

**Changes made:**

- New Phase 2 sub-step in `/groot-project`: detects markdown files at `design/` root (other than README.md/DESIGN.md), classifies them confidently (`*-plan.md` → plans/, `author:`/`priority:` frontmatter → stories/ready/, plan-companion → stories/ready/, dated unsignaled → notes/), and prompts to `git mv` them as a single batched confirmation. Default behavior, not aggressive-mode-only.
- Phase 3 renamed "Project docs skeleton" — now creates `CLAUDE.md`, `DIARY.md`, and `TODO.md` together. DIARY uses /project-setup's verbatim format. TODO uses /project-setup's verbatim format so Joe's tracker skills find it without modification.
- Conventions block rewritten: was numbered ("items 2/3/4/8/10b are candidates"), now semantic ("engineering diary covered by root DIARY.md", etc.). Joe can renumber upstream without breaking us.
- `MAINTAINERS.md` gained an upstream-merge ritual: after every `upstream/main` pull, re-read `skills/project-setup/SKILL.md` and reconcile with /groot-project's conventions skeleton.
- Global `~/.claude/CLAUDE.md` got a "Decision recap" rule under "How We Work Together" — restate decisions in end-of-turn summaries when there's a lot of work between the decision and the wrap-up.

**Decisions:**

- **DIARY.md at repo root, not `design/`.** Project-meta, parallel to README, visible at top level, matches the convention everyone recognizes. Putting it under `design/` would obscure it.
- **Adopt root `TODO.md` as the light-tracker convention.** Considered forking `/todo` and `/bug-bash` to teach them about `design/stories/`. Rejected — Joe's skills are well-built, the only "conflict" is location, and forking creates indefinite maintenance burden for marginal gain. Three lanes now: `TODO.md` for "fix the flicker", `design/stories/` for feature specs, `design/helping-hands/` for user-action items.
- **Don't have `/groot-project` call into `/project-setup`.** Coupling to upstream's item structure is brittle. `/groot-project` owns DIARY/TODO end-to-end; conventions block tells `/project-setup` what's covered semantically.
- **Auto-merge meta-skill for upstream forks: premature.** Clever idea but only one fork case (and we rejected that one). Revisit if 3+ accumulate.
- **`design/` root migration prompts by default, not aggressive-mode-only.** Aggressive mode narrowed to its real scope: project-root structural moves (top-level `docs/` → `design/`, renaming non-canonical dirs).

Dogfooded `/claude-md-add` to insert the Decision-recap rule into global CLAUDE.md — first real use of that skill. The copy-editor pass was a no-op (the entry was clean) but the workflow felt right.

---

## 2026-03-31 — Repo hygiene pass

Ran `/scorecard` on the repo — got **C+** overall. Main findings: massive DRY violation between `/bug` and `/todo` (95% identical), README only listed 2 of 8 skills, no `.gitignore`, and `plugin.json` had wrong GitHub URL.

**Changes made:**

- Deduplicated `/bug` into a thin 1-line wrapper that delegates to `/todo`. Chose the "thin wrapper" approach over a symlink because it preserves a separate name/description in frontmatter.
- Updated README with all 8 skills.
- Created `CLAUDE.md` with project conventions (first-time setup, adding-a-skill checklist).
- Created `/import-skill` as a project-local skill (`.claude/skills/`) — it discovers skills from `~/.claude/skills/` and sibling project directories, then walks through importing them. Kept it project-local since it's specific to this repo's structure.
- Created `/project-setup` skill for walking through AI-friendly project setup improvements.

**Decisions:**

- Skills that are aliases (like `/bug` → `/todo`) use a thin wrapper SKILL.md rather than symlinks, so they can have distinct names and descriptions.
- Project-specific skills live in `.claude/skills/`, shared/distributable skills live in `skills/`. The Makefile only installs `skills/`.
- Sibling project discovery in `/import-skill` assumes all git repos are checked out in the same parent directory — matches the user's workflow.

---

## 2026-03-31 — Initial commit

Bootstrapped shared skills repo with Makefile-based symlink installation (global or plugin mode). Started with 2 skills (hello-world, sitrep), then added 6 more (bug, bug-bash, readme, scorecard, todo, tool-web) in a second commit.

Key design choice: skills are symlinked, not copied. Edits in any project write back to this repo, making it easy to iterate on skills and push upstream.
