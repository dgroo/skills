# Skill ownership

This repo is `dgroo/skills`, a fork of `joewalnes/skills`. All skills live together in `skills/` (the Makefile globs `skills/*` and symlinks each into `~/.claude/skills/`). To keep that paradigm but still tell origin at a glance, this file is the manifest.

**Source of truth:** git authorship of the first commit under each `skills/<name>/` directory. The lists below should match this command:

```bash
for d in skills/*/; do
  name=$(basename "$d")
  origin=$(git log --reverse --format="%an" -- "$d" 2>/dev/null | head -1)
  echo "$name | $origin"
done | sort
```

If the table drifts, the git output wins. Re-sync the table; don't touch git history.

## Derek-authored (live in this fork only)

| Skill            | First added | Notes                                                                                                                                                                                                                                                    |
| ---------------- | ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `beginners-mind` | 2026-05-28  | Periodic fresh-eyes setup audit; general, profile-driven                                                                                                                                                                                                 |
| `md-add`  | 2026-05-10  |                                                                                                                                                                                                                                                          |
| `cleanup-design` | 2026-05-11  |                                                                                                                                                                                                                                                          |
| `groot-project`  | 2026-05-10  | Wraps `/project-setup`; aware of gstack                                                                                                                                                                                                                  |
| `helping-hands`  | 2026-05-12  | Works the `design/helping-hands/` queue; user-invoked                                                                                                                                                                                                    |
| `idea`           | 2026-05-14  | Captures sparks to `design/IDEAS.md`                                                                                                                                                                                                                     |
| `terminal-setup` | 2026-05-18  | Renamed from `iterm-setup`; decoupled from iTerm Dynamic Profiles, now terminal-agnostic via OSC 11. Has `auto` mode used by `/groot-project --auto`; reads/writes `.groot-project.toml` (`[terminal].background`); migrates legacy `[iterm]` on the fly |
| `prior-art`      | 2026-05-05  |                                                                                                                                                                                                                                                          |
| `skill-add`      | 2026-05-14  | Evaluation gate before creating a new skill                                                                                                                                                                                                              |
| `skills-review`  | 2026-05-10  |                                                                                                                                                                                                                                                          |
| `subagent`       | 2026-05-14  | Four-check heuristic for spawning subagents                                                                                                                                                                                                              |
| `sup`            | 2026-05-13  | Local fork of `/sitrep` with backlog scan + pick recommendation                                                                                                                                                                                          |
| `walkthrough`    | 2026-05-11  |                                                                                                                                                                                                                                                          |

## Upstream (from `joewalnes/skills`)

| Skill           | Notes                                          |
| --------------- | ---------------------------------------------- |
| `bug`           | Alias for `/todo`                              |
| `bug-bash`      |                                                |
| `hello-world`   | Test skill                                     |
| `project-setup` | Convention-layer companion to `/groot-project` |
| `readme`        |                                                |
| `release-setup` |                                                |
| `scorecard`     |                                                |
| `sitrep`        |                                                |
| `todo`          | Reads/writes root-level `TODO.md`              |
| `tool-web`      |                                                |

## Rules

- **Don't edit upstream skills in place.** Pull from `upstream/main` periodically and merge. If you need to change behavior, fork-and-rename (e.g., `todo-derek`) so upstream merges stay clean.
- **New skill from you?** Create at `skills/<name>/`, then add a row to the Derek-authored table.
- **Promoted upstream?** If Joe ever merges one of yours, move the row to the upstream table.
- **After every `upstream/main` merge: re-read `skills/project-setup/SKILL.md`** and reconcile with `skills/groot-project/SKILL.md`'s `## Project conventions` skeleton block. The block describes covered items semantically (by name, not item number) to survive renumbering, but if Joe _adds_ a genuinely new convention, `groot-project` should pick it up explicitly or note it as a new genuine candidate.

## Why not put origin in `SKILL.md` frontmatter?

Tempting, but that requires editing every upstream skill (merge conflicts forever) and Claude Code doesn't surface custom frontmatter anyway. A single manifest at the root is lower friction.
