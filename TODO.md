# Todo

<!-- Format: [status] P<priority> (category) Title -->
<!-- Status: [ ] open, [~] in progress, [x] done, [-] won't fix -->
<!-- Priority: P0 critical, P1 high, P2 medium, P3 low -->
<!-- Category: bug, feature, chore, docs -->

## Open

- [ ] **P3** (chore) Decide: stay a fork of joewalnes/skills, or restructure as a wrapper/overlay — 2026-06-09
  Derek recalls an rcs-session conversation proposing converting this repo from a fork of Joe's into something that *wraps* it (pull upstream skills without fork history). The outcome was never recorded — searched all design docs, diaries, TODO/REVISIT surfaces, and CC transcripts (2026-06-09); no trace outside the session that re-raised it. Needs a fresh decision: fork (status quo: `upstream-check.sh`/`check-upstream-edits.sh` + `make upstream-*` targets manage drift) vs wrapper (e.g. upstream as a plugin-marketplace install or git submodule/subtree, personal skills as pure overlay — cf. the "third-party skills via plugin marketplace" precedent in rcs auto-memory). Blocks beginners-mind R17 (renaming `upstream-*` scripts to `fork-*` is wasted churn if the restructure happens).
  After a `/clear`, `sibling-sessions.py` reports the *predecessor* transcript as a hot parallel sibling: the clear writes an `away_summary` to the old jsonl, so it shows up as "active Ns ago" with a topic hint that matches the current arc (because it *is* the current arc). This led `/sup` to recommend "switch windows rather than restart here" when there was no real parallel session. Fix idea: suppress a sibling whose latest `away_summary` timestamp ≈ the current session's start time (the `/clear` fingerprint), or whose jsonl stopped being written right as the current one began. Confirmed live on Serenity26 in the Changer theme-prototype worktree.

## Done

- [x] **P3** (chore) iterm-setup missing from README skills table — 2026-05-17
  Resolved: Added the iterm-setup row in alphabetical position. Also fixed a parallel drift in MAINTAINERS.md — 7 Derek-authored skills (cleanup-design, helping-hands, idea, integrate-comments, skill-add, subagent, sup) had been added since the last manifest sync. Single commit.

- [x] **P2** (bug) iterm-setup reads/writes `~/.zshrc` only — misses `~/.shrc` — 2026-05-16
  Resolved: Added `shell_config_files()` discovery and `primary_shell_config_file()` write-target helpers; refactored `aliases_targeting_cwd` to read combined text from all discovered files; renamed `add_alias_to_zshrc` → `add_alias_to_shell_config` with conflict-check across both files. Detection regex handles guarded source patterns (`[ -f ~/.shrc ] && source ~/.shrc`, `if [...]; then source X; fi`) and ignores commented-out lines. 16 new pytest cases in `test_shell_config.py`. Belt-and-suspenders: added a "Shell config layout" section to `~/.claude/CLAUDE.md` so LLM-driven tools route correctly without needing the same discovery code.

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
