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

| Skill | Description |
|-------|-------------|
| `bug` | Add a new bug to the project's tracker (alias for `/todo`) |
| `bug-bash` | Autonomously work through a project's bug list, fixing bugs in priority order |
| `claude-md-add` | Add a single entry to a CLAUDE.md file with a copy-edit pass — sharpens vague triggers, flags redundancy, picks the right section, preserves the user's voice |
| `cleanup-design` | Audit and refresh a project's `design/` corpus — flag staleness, surface drift between recent decisions and docs, suggest moves to `done/` |
| `groot-project` | Bootstrap a project the Derek way — git, `design/` subtree with readiness-by-directory stories, CLAUDE.md skeleton, Makefile, iTerm profile, optional GitHub remote and gbrain. Coexists with `/project-setup`. Re-runnable |
| `hello-world` | A simple test greeting skill |
| `helping-hands` | Work through a project's `helping-hands/` items — tasks needing the user's hands, eyes, credentials. Validates each item, extends LLM-side scaffolding, surfaces a single concrete ask. `/helping-hands new <slug>` files a new entry from the canonical template |
| `idea` | Capture a quick spark to the project's sparkfile (`design/IDEAS.md`). `/idea <text>` to add, `/idea review` to list, `/idea iterate` to walk each entry |
| `integrate-comments` | Generic comment-driven iteration: integrate `<!-- @<user>: -->` review comments into prose, mark processed in place, emit tabular review-log |
| `iterm-setup` | Create a uniquely-colored iTerm2 profile for a project with Automatic Profile Switching, plus optional shell alias. Reads/writes `.groot-project.toml` so a fresh clone on another machine reproduces the per-project setup |
| `prior-art` | 20-minute prior-art check before building a new project — surfaces 1–3 closest existing tools and asks "what's your honest reason to build anyway?" |
| `project-setup` | Walk through project setup improvements for AI-assisted development |
| `readme` | Generate or update project README documentation |
| `release-setup` | Set up automated cross-platform binary releases for a Go project |
| `scorecard` | Comprehensive codebase quality audit with letter grades |
| `sitrep` | Quick situation report — recap progress, uncommitted work, gaps, and next steps |
| `skill-add` | Evaluation gate for proposing a new skill — scans the catalog for collisions, overlaps, and wrap candidates; pushes back on thin value; interviews and creates if it proceeds |
| `skills-review` | Audit installed Claude Code skills — enumerate, categorize, flag duplicates and conflicts. Generates an HTML report and can act on its recommendations |
| `subagent` | Evaluate whether a task is actually suited to a subagent (four-check heuristic), then either spawn with a well-formed prompt or push back with specific reasons |
| `sup` | Local extension of `/sitrep` — adds active backlog scan + specific pick recommendation, plus a high-confidence new-session check |
| `todo` | Add a new bug or todo to the project's tracker |
| `tool-web` | Build a lightweight single-file web application with no external dependencies |
| `walkthrough` | Produce a narrative walkthrough of how an app or system is used end-to-end from a specific user's perspective — tutorial-quadrant docs, story-shaped |

## Development

Test locally:

```bash
claude --plugin-dir .
```

## License

MIT
