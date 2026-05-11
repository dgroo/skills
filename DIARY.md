# Engineering Diary

Latest entries first. Record significant decisions, architecture changes, and non-obvious context.

---

## 2026-05-11 — /groot-project coexistence with Joe's upstream

Spent a session sharpening how `/groot-project` plays with `/project-setup` and Joe's tracker skills (`/todo`, `/bug`, `/bug-bash`). The thread connecting all the work: Joe's upstream is a moving target, our local skill needs to coexist without rotting when he changes things, and the original conventions block had a real gap — `DIARY.md` was hand-waved away as "captured in `design/notes/` + `design/plans/`" which isn't honest. Notes are frozen snapshots, plans are forward-looking; neither is a rolling chronological log.

Trigger was looking at `~/code/changer` and `~/code/games/vfstrategy` ahead of running `/groot-project` on them. Changer has two dated `*.md` files sitting at `design/` root (a plan and its companion spec). Default `/groot-project` would build the canonical subtree *around* those files and leave them stranded — not great. So the cleanup work piled up: migration defaults, DIARY integration, upstream-drift handling.

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
