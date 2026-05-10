---
name: groot-project
description: Bootstrap a project the Derek way — git, design/ subtree, CLAUDE.md skeleton, Makefile, iTerm profile, optional GitHub remote and gbrain registration. Independent of /project-setup. Re-runnable; works for new and existing projects.
argument-hint: [status|--auto|--public]
---

# Groot Project

Bootstraps a project Derek's way. Idempotent — safe to run on a brand-new directory, a just-cloned repo, or an older project that drifted from the canonical layout. Each phase detects what's already in place and only offers what's missing.

Independent of `/project-setup` (which is Joe Walnes's upstream skill that retrofits 10 conventions onto established projects). `/groot-project` is the *structural skeleton*; `/project-setup` is the convention layer that goes on top, if wanted.

## How to Invoke

```
/groot-project              # interactive walkthrough at cwd
/groot-project status       # read-only audit; report what's in place vs missing
/groot-project --auto       # skip prompts; sensible defaults; external integrations skipped
/groot-project --public     # if a GitHub remote is created, make it public (default: private)
```

`--auto` and `--public` can combine. `status` is standalone.

**Aggressive mode via prompt language.** If the user invokes with phrasing like *"be aggressive"*, *"restructure"*, or *"reorganize existing files"* (e.g., `/groot-project — be aggressive about restructuring docs into design/`), expand scope to also offer structural moves: renaming non-standard directories, moving misplaced docs into `design/`, consolidating scattered design notes. Always confirm each structural move before acting; never silently restructure files. Conservative additive retrofit is the default.

## Pre-flight (always runs first)

Gather state and print a summary before asking anything:

- Is this a git repo? (`git rev-parse --is-inside-work-tree 2>/dev/null`)
- Does a recent `/office-hours` design doc exist at `~/.gstack/projects/<basename>/*.md`? Take the most recent.
- What language signals exist? Presence of `pyproject.toml`, `setup.py`, `package.json`, `Cargo.toml`, `go.mod`.
- What standard files / directories are present? `README.md`, `Makefile`, `design/`, `design/DESIGN.md`, `design/helping-hands/`, `design/plans/`, `design/stories/`, `design/notes/`, `.gitignore`, `CLAUDE.md`.
- Is there an iTerm profile bound to this directory? (`~/.claude/scripts/iterm-setup.py <basename> --list-colors` shows the existing-profile banner if so.)
- Is the directory under `~/code/`? (Affects alias suggestion in iTerm phase.)

Print a "found / will create / will skip" summary so the user sees the scope before any phase fires.

## Phases (in order)

Each phase has one of three modes: **auto-default-Y** (skill announces and proceeds; user only stops it by saying "skip"), **always-asks** (genuine decision point), or **detection-skip** (skill skips silently if already present and conforming). `--auto` mode bypasses prompts; see the `--auto` section.

| # | Phase                          | Mode                | What it does                                                              |
|---|--------------------------------|---------------------|---------------------------------------------------------------------------|
| 1 | Git init                       | auto-default-Y      | `git init` if not a repo. Skip otherwise.                                 |
| 2 | `design/` subtree              | auto-default-Y      | Create missing pieces of the canonical subtree.                           |
| 3 | CLAUDE.md skeleton             | auto-default-Y      | Generate skeleton if missing.                                             |
| 4 | Office-hours import            | auto-default-Y      | If a design doc exists, layer its content into DESIGN.md and CLAUDE.md.   |
| 5 | Language detection + .gitignore | always-asks        | Ask Python / TypeScript / Rust / Go / Other / None.                       |
| 6 | Makefile                       | auto-default-Y / drift-flag | Create if missing; flag drift if present but missing standard targets.   |
| 7 | iTerm profile                  | always-interactive  | Invoke `/iterm-setup` (delegates fully).                                  |
| 8 | GitHub remote                  | always-asks         | Ask y/skip; default `--private`.                                          |
| 9 | gbrain registration            | always-asks         | Ask y/skip; if yes, invoke `/sync-gbrain`.                                |
| 10 | Final summary                 | —                   | Print done / skipped / next-steps table.                                  |

### Phase 1: Git init

If `git rev-parse --is-inside-work-tree` fails, run `git init`. Print one line: *"Initialized git repo."* If already a repo, print: *"Existing git repo — skipped."*

### Phase 2: `design/` subtree

Create the canonical subtree, leaving any existing pieces alone:

```
design/
├── DESIGN.md         # skeleton (or seeded from office-hours doc in phase 4)
├── helping-hands/
│   └── README.md     # the helping-hands convention doc (see "Helping-hands template" below)
├── plans/
│   └── README.md     # one-liner: "Implementation plans live here. One file per plan."
├── stories/
│   └── README.md     # one-liner: "User stories / scenarios live here."
└── notes/
    └── README.md     # one-liner: "Free-form notes, todos, rough thinking."
```

For each subdir or file: skip if it exists, create if it doesn't. Never overwrite.

The DESIGN.md skeleton (used when no office-hours doc exists):

```markdown
# <Project name>

<one-line description>

## Problem

<what are we solving?>

## Approach

<how, at a high level?>

## Constraints

<what bounds the design?>

## Open questions

- <thing we haven't decided>
```

### Phase 3: CLAUDE.md skeleton

If `CLAUDE.md` doesn't exist at the project root, generate:

```markdown
# <Project name>

<one-line description from office-hours doc, or placeholder>

See `design/DESIGN.md` for the full design and
`design/helping-hands/README.md` for tasks needing my hands.

## Build / run

See `Makefile`. Standard targets: init, build, run, lint, test, dist, clean.

## <Language>-specific notes

<placeholder — fill in as conventions emerge>
```

If `CLAUDE.md` exists, leave it alone. Print: *"Existing CLAUDE.md — left untouched."* The skeleton intentionally relies on `~/.claude/CLAUDE.md` (global) and `~/.claude/rules/*.md` (path-scoped) for the bulk of behavioral rules. Project-level CLAUDE.md only holds project-specific things.

### Phase 4: Office-hours import

Check for the most recent `~/.gstack/projects/<basename>/*.md`. If found:

- Ask: *"Found /office-hours design doc at <path> (last modified <date>). Import its content into DESIGN.md and seed CLAUDE.md project blurb? (Y/n)"*
- If Y: parse the doc, copy substantive content into `design/DESIGN.md` (replacing the skeleton), and pull a 1-2 sentence project description into the CLAUDE.md heading.
- If n: leave skeletons in place.

If no doc found, print: *"No /office-hours doc found. Run /office-hours later to backfill DESIGN.md."*

### Phase 5: Language detection + .gitignore

Ask: *"Project language? Python / TypeScript / Rust / Go / Other / None"*. Pre-select the answer based on detected files (e.g., presence of `pyproject.toml` → Python is the default).

Based on the answer, generate or append to `.gitignore`:

| Language    | Patterns to add                                                                  |
|-------------|----------------------------------------------------------------------------------|
| Python      | `__pycache__/`, `.venv/`, `venv/`, `*.pyc`, `dist/`, `build/`, `*.egg-info/`     |
| TypeScript  | `node_modules/`, `dist/`, `.next/`, `*.tsbuildinfo`, `.turbo/`, `.cache/`        |
| Rust        | `target/`, `Cargo.lock` (only for libraries — ask the user)                      |
| Go          | `vendor/`, `*.test`, build artifacts                                             |
| Other/None  | Minimal: `.DS_Store`, `*.log`                                                    |

If `.gitignore` exists, append missing patterns; never remove or rewrite existing ones.

After the language is known, print a hint: *"Run `uv init` (Python) / `npm init` (TS) / `cargo init` (Rust) / `go mod init <module>` (Go) when ready — this skill won't run language tools for you."*

### Phase 6: Makefile

If no Makefile exists, generate one with Derek's standard targets:

```makefile
.PHONY: all init build run lint test dist clean help

# Default target: init, build, lint, test, dist (per ~/.claude/CLAUDE.md)
all: init build lint test dist  ## Run init, build, lint, test, dist in sequence

init:  ## Install prerequisites
	# <language-specific>

build:  ## Compile / bundle
	# <language-specific>

run:  ## Run the program
	# <language-specific>

lint:  ## Code checks
	# <language-specific>

test:  ## All automated tests
	# <language-specific>

dist:  ## Package for distribution
	# <language-specific>

clean:  ## Clean generated assets
	# <language-specific>

help:  ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?##.*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
```

Per-language target bodies (filled based on phase 5):

- **Python (uv):** `init: uv sync` · `build: uv build` · `run: uv run python <main>` · `lint: ruff check && mypy .` · `test: pytest` · `dist: uv build` · `clean: rm -rf dist/ build/ *.egg-info __pycache__/ .pytest_cache/`
- **TypeScript:** `init: npm install` · `build: npm run build` · `run: npm start` · `lint: npm run lint` · `test: npm test` · `dist: npm pack` · `clean: rm -rf node_modules/ dist/ .next/`
- **Rust:** `init: cargo fetch` · `build: cargo build` · `run: cargo run` · `lint: cargo clippy` · `test: cargo test` · `dist: cargo build --release` · `clean: cargo clean`
- **Go:** `init: go mod download` · `build: go build ./...` · `run: go run .` · `lint: go vet ./... && golangci-lint run` · `test: go test ./...` · `dist: go build -o dist/` · `clean: rm -rf dist/`
- **Other/None:** Leave bodies as `# TODO` placeholders.

If a Makefile exists, check for the standard targets (`init`, `build`, `run`, `lint`, `test`, `dist`, `clean`). For any missing:

- Print: *"Existing Makefile is missing standard targets: <list>. Add them? (Y/n)"*
- If Y: append the missing targets to the existing Makefile without modifying existing ones. Use `# Standard targets added by /groot-project` as a separator comment.

### Phase 7: iTerm profile

Invoke `/iterm-setup` with the project basename. The iterm-setup skill handles its own interactive flow — color picker (with vivid section), alias prompt, title format. Don't second-guess it. In `--auto` mode, run with `--auto` (which iterm-setup will eventually support; until then, pass `--no-alias` only if there's no existing alias for cwd).

### Phase 8: GitHub remote

Ask: *"Create a GitHub remote? (y/skip)"*. If y:

- Default visibility is `--private`. (Switching private→public is easy via GitHub Settings → Danger Zone → Change visibility.)
- If `--public` flag was passed at invocation, use `--public` instead.
- If the working tree has no commits yet, run `git add . && git commit -m "Initial commit"` first.
- Run `gh repo create <basename> --<visibility> --source=. --remote=origin --push`.
- Print the resulting remote URL.

If `gh` isn't installed, print: *"`gh` not found. Install via `brew install gh` and re-run /groot-project to add the remote."* Don't fail the rest of the skill.

### Phase 9: gbrain registration

Ask: *"Sync this project with gbrain? (y/skip)"*. If y, invoke `/sync-gbrain`. If skip, just move on.

### Phase 10: Final summary

Print a concise table:

```
/groot-project: done in <project>

Done:
  ✓ git init
  ✓ design/ subtree (DESIGN.md + helping-hands, plans, stories, notes)
  ✓ CLAUDE.md skeleton
  ✓ Office-hours import (from <doc-path>)
  ✓ .gitignore (Python)
  ✓ Makefile (Python)
  ✓ iTerm profile (Plum, alias=foo)

Skipped:
  - GitHub remote (you said skip)
  - gbrain registration (you said skip)

Next:
  - Run `uv init` to initialize the Python project
  - Run `/project-setup` to layer Joe's 10-convention checklist on top, if wanted
  - Run `/office-hours` to backfill DESIGN.md if you didn't already
  - Run `/groot-project status` later for a re-audit
```

## `--auto` mode

`--auto` skips all prompts and picks sensible defaults:

- **Language**: detect from existing files (`pyproject.toml` → Python, `package.json` → TypeScript, `Cargo.toml` → Rust, `go.mod` → Go). If ambiguous or none, skip language-specific scaffolding (no `.gitignore` patterns, Makefile bodies left as `# TODO`).
- **iTerm**: invoke iterm-setup non-interactively (first unused color, alias = project basename, default title format).
- **GitHub remote**: SKIPPED. Creating an external resource without explicit consent is too consequential for `--auto`.
- **gbrain**: SKIPPED. Same reason.
- **Office-hours import**: still imports if a doc is found (low risk, just file content).
- All `auto-default-Y` phases just happen.

End-of-run summary calls out skipped external integrations: *"Re-run without `--auto` to handle GitHub remote and gbrain registration."*

## `status` mode

`/groot-project status` is a read-only audit. Walk the same detection logic as Pre-flight, format as a checklist:

```
Project audit for myproject:

  [✓] Git initialized
  [✓] design/ subtree (DESIGN.md, helping-hands/, plans/, stories/, notes/)
  [✓] CLAUDE.md
  [⚠] Makefile (missing targets: dist, clean)
  [✓] .gitignore (Python)
  [✓] iTerm profile (claude-config, Plum)
  [ ] GitHub remote
  [ ] gbrain registered
  [✓] /office-hours doc imported

7/10 in place. Want to address the missing/drifted items? (Y/n)
```

If the user says Y, fall through into the regular interactive walkthrough, only running phases for missing/drifted items.

## Aggressive retrofit

When the user invokes with aggressive/restructure language (*"be aggressive"*, *"restructure"*, *"reorganize"*, *"move things into design/"*, etc.), expand scope:

- Offer to move misplaced docs (e.g., a top-level `docs/` directory) into `design/` or `design/notes/`.
- Offer to rename non-standard directories that map to canonical names (e.g., `specs/` → `design/plans/`).
- Offer to consolidate scattered design notes into `design/notes/`.

**Always confirm each structural move before acting**, and use git operations (`git mv`) so history is preserved. Never silently restructure files. Aggressive mode is opt-in by user phrasing — never the default.

## Helping-hands template

The skill should populate `design/helping-hands/README.md` from `~/code/iDM/design/helping-hands/README.md` (the canonical reference) if it exists. This keeps every project's helping-hands convention current with iDM as the source of truth.

If `~/code/iDM/design/helping-hands/README.md` doesn't exist (e.g., this skill runs on a different machine), use this minimal embedded template as a fallback:

```markdown
# Helping hands

Tasks that need Derek's hands, eyes, account credentials, paid subscription, or physical access.

## Format

- One markdown file per item, date-prefixed: `YYYY-MM-DD-<slug>.md`
- YAML frontmatter: `status` (open/in-progress/done/dropped), `created`, `priority`, `estimated_time`
- Body sections: title (a request, not a directive), what's needed, why, **what I already did to reduce the work**, concrete steps, what changes when it's done.
- The "what I already did" section is non-decorative — if it would be empty, the entry should not have been created. Do that work first instead.

## Surfacing in chat

Filed entries surface as a one-liner only: `Filed: <title> — see design/helping-hands/`. Not a paragraph. Not a recap. The artifact is the source of truth.

## Just-in-time, not session-start

When picking up work, check whether any open helping-hands item is referenced as a blocker by the current task, its parent story, or its plan. If so, name the specific blocker before pressing on. Do not auto-scan the directory at session start.
```

## What this skill does NOT do

- Doesn't run `/project-setup` (mention it as a final pointer; separate skill, separate concern).
- Doesn't write `pyproject.toml` / `package.json` / `Cargo.toml` directly — delegates to the language tool's own init flow (`uv init`, `npm init`, `cargo init`).
- Doesn't do detailed code architecture or design-system work — use `/design-consultation` or `/init` for that.
- Doesn't manage worktrees — separate concern.
- Doesn't push to GitHub aggressively or set up CI/CD — out of scope; use `/setup-deploy` and friends for that.
- Doesn't restructure files unless the user explicitly invokes aggressive/restructure mode.
- Doesn't maintain or update CLAUDE.md content beyond the initial skeleton — use `/claude-md-add` for ongoing additions.

## Reference

- Helping-hands convention (canonical): `~/code/iDM/design/helping-hands/README.md`
- iDM design layout (template for `design/` subtree): `~/code/iDM/design/`
- iterm-setup: `~/.claude/scripts/iterm-setup.py`
- `gh` CLI for GitHub remote: https://cli.github.com/
- `/sync-gbrain` skill (gstack)
- `/project-setup` skill (Joe Walnes upstream): retrofits 10 conventions to existing projects (independent of this skill)
- `/office-hours` skill (gstack): produces a design doc at `~/.gstack/projects/<basename>/*.md` that this skill can import
