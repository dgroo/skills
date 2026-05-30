# Skills

A collection of custom Claude Code skills.

## Installation

### Option 1: Global install (recommended)

Symlinks skills into `~/.claude/skills/` so they're available as `/skill-name` in every project, on every machine.

```bash
git clone https://github.com/joewalnes/skills.git
cd skills
make install
```

Skills are symlinked, not copied — edits made by Claude in any project write back to this repo, making it easy to commit and push upstream.

To remove:

```bash
make uninstall
```

### Option 2: Plugin install (namespaced)

Install as a Claude Code plugin. Skills are available as `/skills:skill-name`.

```
/plugin install https://github.com/joewalnes/skills
```

### Other commands

```bash
make list       # Show available skills and install status
```

## Skills

| Skill                | Description                                                                                                                                                                                                                                                                                                                                                                                                            |
| -------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `bug`                | Add a new bug to the project's tracker (alias for `/todo`)                                                                                                                                                                                                                                                                                                                                                             |
| `bug-bash`           | Autonomously work through a project's bug list, fixing bugs in priority order                                                                                                                                                                                                                                                                                                                                          |
| `claude-md-add`      | Add a single entry to a CLAUDE.md file with a copy-edit pass — sharpens vague triggers, flags redundancy, picks the right section, preserves the user's voice                                                                                                                                                                                                                                                          |
| `cleanup-design`     | Audit and refresh a project's `design/` corpus — flag staleness, surface drift between recent decisions and docs, suggest moves to `done/`                                                                                                                                                                                                                                                                             |
| `cmd-add`            | Add a Claude Code slash command — gates command-vs-skill (defaults to command since commands cost no context until used), scans for collisions, writes `~/.claude/commands/<name>.md`, shows the propagation command for dot-claude                                                                                                                                                                                    |
| `groot-project`      | Bootstrap a project the Derek way — git, `design/` subtree with readiness-by-directory stories, CLAUDE.md skeleton, Makefile, terminal background color (via `/terminal-setup`), optional GitHub remote and gbrain. Coexists with `/project-setup`. Re-runnable                                                                                                                                                        |
| `hello-world`        | A simple test greeting skill                                                                                                                                                                                                                                                                                                                                                                                           |
| `helping-hands`      | Work through a project's `helping-hands/` items — tasks needing the user's hands, eyes, credentials. Validates each item, extends LLM-side scaffolding, surfaces a single concrete ask. `/helping-hands new <slug>` files a new entry from the canonical template                                                                                                                                                      |
| `humanize-text`      | Strip AI "tells" from prose without changing meaning or flattening the author's voice. Detects fingerprints (em-dash clusters, "it's not just X, it's Y", rule-of-three cadence, banned vocab), calibrates against the author's own corpus (`~/.claude/voice/profile.md`), and surfaces meaning-affecting word choices separately for sign-off. Companion to `/claude-md-add`; sibling of the planned `/humanize-code` |
| `idea`               | Capture a quick spark to the project's sparkfile (`design/IDEAS.md`). `/idea <text>` to add, `/idea review` to list, `/idea iterate` to walk each entry                                                                                                                                                                                                                                                                |
| `next`               | Forward-only "what should I pick up?" — scans queued-work surfaces (TODO, ready/draft stories, helping-hands, REVISIT, open PRs, stale branches) via `~/bin/backlog-scan` and presents a few dependency- and leverage-ranked candidates via AskUserQuestion. Conservative pick-scaled context-window check. Companion to `/sup`                                                                                        |
| `terminal-setup`     | Set a per-project terminal background color (and optional shell alias) that follows you across iTerm2, Ghostty, Alacritty, Kitty, WezTerm. Records the choice in `.groot-project.toml`; the shell applies it via OSC 11 on `cd`. Successor to `iterm-setup` — handles `[iterm]` → `[terminal]` migration automatically                                                                                                 |
| `prior-art`          | 20-minute prior-art check before building a new project — surfaces 1–3 closest existing tools and asks "what's your honest reason to build anyway?"                                                                                                                                                                                                                                                                    |
| `project-setup`      | Walk through project setup improvements for AI-assisted development                                                                                                                                                                                                                                                                                                                                                    |
| `readme`             | Generate or update project README documentation                                                                                                                                                                                                                                                                                                                                                                        |
| `release-setup`      | Set up automated cross-platform binary releases for a Go project                                                                                                                                                                                                                                                                                                                                                       |
| `scorecard`          | Comprehensive codebase quality audit with letter grades                                                                                                                                                                                                                                                                                                                                                                |
| `sitrep`             | Quick situation report — recap progress, uncommitted work, gaps, and next steps                                                                                                                                                                                                                                                                                                                                        |
| `skill-add`          | Evaluation gate for proposing a new skill — scans the catalog for collisions, overlaps, and wrap candidates; pushes back on thin value; interviews and creates if it proceeds                                                                                                                                                                                                                                          |
| `skill-list`         | Fast plain-text listing of installed skills, grouped by source. `(no arg)` mirrors `make list`; `all` lists everything; `groups` lists group names; `<group>` is one of mine/gstack/installed/plugins/upstream. Single bash call, output verbatim — no LLM analysis                                                                                                                                                    |
| `skills-review`      | Audit installed Claude Code skills — enumerate, categorize, flag duplicates and conflicts. Generates an HTML report and can act on its recommendations                                                                                                                                                                                                                                                                 |
| `statusline-explain` | Explain each segment of the Claude Code statusline — current value, what it means, and a note when the value is in an unusual state. Parses the live `~/.claude/statusline-command.sh` so it stays in sync as segments change                                                                                                                                                                                          |
| `subagent`           | Evaluate whether a task is actually suited to a subagent (four-check heuristic), then either spawn with a well-formed prompt or push back with specific reasons                                                                                                                                                                                                                                                        |
| `sup`                | Local extension of `/sitrep` — adds active backlog scan + specific pick recommendation, plus a high-confidence new-session check                                                                                                                                                                                                                                                                                       |
| `todo`               | Add a new bug or todo to the project's tracker                                                                                                                                                                                                                                                                                                                                                                         |
| `tool-web`           | Build a lightweight single-file web application with no external dependencies                                                                                                                                                                                                                                                                                                                                          |
| `walkthrough`        | Produce a narrative walkthrough of how an app or system is used end-to-end from a specific user's perspective — tutorial-quadrant docs, story-shaped                                                                                                                                                                                                                                                                   |
| `wrapup`             | Action-imperative session-end gate. Inventories in-flight state, proposes prep, asks permission for writes, then emits a definitive READY / WAIT / STAY verdict. With an intent hint, may push back to stay if cache is hot for it. Companion to `/sup`                                                                                                                                                                |
| `yolo-mode`          | Bounded-autonomous "work overnight while I sleep" mode. Pushes forward on the design/docs backlog in an isolated worktree, atomic commits, a `YOLO-LOG.md` review trail, destructive ops deferred to `YOLO-QUEUE.md` instead of run. Fans work to subagents for endurance. Behavioral half only — needs `--dangerously-skip-permissions` for true unattended running. Code work is opt-in (`--code`)                   |

## Development

Test locally:

```bash
claude --plugin-dir .
```

## License

MIT
