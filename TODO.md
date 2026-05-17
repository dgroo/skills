# Todo

<!-- Format: [status] P<priority> (category) Title -->
<!-- Status: [ ] open, [~] in progress, [x] done, [-] won't fix -->
<!-- Priority: P0 critical, P1 high, P2 medium, P3 low -->
<!-- Category: bug, feature, chore, docs -->

## Open

- [ ] **P2** (bug) iterm-setup reads/writes `~/.zshrc` only — misses `~/.shrc`
  `aliases_targeting_cwd`, `add_alias_to_zshrc`, and `has_code_chain_alias` all
  hardcode `ZSHRC_PATH = ~/.zshrc`. On a setup where shared aliases live in
  `~/.shrc` (sourced by both `.zshrc` and `.bashrc`), the script can't see
  existing aliases, writes new ones to the wrong file, and the `code;cd X`
  chain-shorthand detection fails. Surfaced while smoke-testing the
  `.groot-project.toml` feature: `--cwd-aliases` returned empty for a directory
  that does have a `skills` alias (in `~/.shrc:109`). Fix: add a
  `shell_config_files()` discoverer that returns `[~/.shrc, ~/.zshrc]` when
  shrc exists, and `primary_shell_config_file()` that prefers shrc for writes
  when zshrc sources it. Update the three touchpoints + their print messages.
  Add tests covering both single-file and shrc+zshrc scenarios.

- [ ] **P3** (chore) iterm-setup missing from README skills table
  Pre-existing drift surfaced while updating docs for the
  `.groot-project.toml` feature. CLAUDE.md says to add new skills to the
  table (alphabetical); iterm-setup was never added. One-line fix.

## Done

- [x] **P3** (chore) Standardize frontmatter fields across skills — 2026-03-31
  Resolved: Added `argument-hint` to all skills that accept arguments (bug-bash, project-setup, readme, scorecard, tool-web). Removed redundant `user_invocable: true` from tool-web. Documented frontmatter convention in CLAUDE.md: `name` and `description` required, `argument-hint` when args accepted, `allowed-tools` optional and enforced.


- [x] **P2** (bug) plugin.json has wrong repository URL — 2026-03-31
  Resolved: Changed `"repository"` from `joe/skills` to `joewalnes/skills` in `.claude-plugin/plugin.json`

- [x] **P2** (bug) Broken placeholder link in tool-web skill — 2026-03-31
  Resolved: Removed the "Onesies Integration" section entirely — it was project-specific boilerplate with a placeholder URL, not appropriate for a shared skill

- [x] **P3** (chore) Add .gitignore — 2026-03-31
  Resolved: Added `.gitignore` with standard exclusions (OS files, editor swap files, env files, logs)

- [x] **P1** (chore) Deduplicate /bug and /todo skills — 2026-03-31
  Resolved: Replaced 118-line copy-paste in `bug/SKILL.md` with thin wrapper delegating to `/todo`

- [x] **P1** (docs) README missing 6 of 8 skills — 2026-03-31
  Resolved: Added all 8 skills to README table in alphabetical order
