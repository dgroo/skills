---
name: groot-project
description: Bootstrap a project the Derek way — git, design/ subtree (incl. stories/ with readiness-by-directory: drafts/ ready/ done/), CLAUDE.md skeleton with a shared-memory conventions block, Makefile, terminal background color (via /terminal-setup), optional GitHub remote and gbrain registration. Coexists with /project-setup and gstack; detects collisions and never clobbers. Re-runnable.
argument-hint: [status|--auto|--public]
---

# Groot Project

Bootstraps a project Derek's way. Idempotent — safe to run on a brand-new directory, a just-cloned repo, or an older project that drifted from the canonical layout. Each phase detects what's already in place and only offers what's missing.

Independent of `/project-setup` (which is Joe Walnes's upstream skill that retrofits 10 conventions onto established projects). `/groot-project` is the _structural skeleton_; `/project-setup` is the convention layer that goes on top, if wanted.

## How to Invoke

```
/groot-project              # interactive walkthrough at cwd
/groot-project status       # read-only audit; report what's in place vs missing
/groot-project --auto       # skip prompts; sensible defaults; external integrations skipped
/groot-project --public     # if a GitHub remote is created, make it public (default: private)
```

`--auto` and `--public` can combine. `status` is standalone.

**Light migration inside `design/` is default.** When `design/` exists but has misplaced files at its root (e.g., a stray `*-plan.md` sitting beside `DESIGN.md`), Phase 2 _asks_ about migrating them into the canonical subdirs (see Phase 2 → "Migrate misplaced files at `design/` root"). This is on by default — the user generally wants the cleanup — but is always a prompt, never silent.

**Aggressive mode via prompt language.** If the user invokes with phrasing like _"be aggressive"_, _"restructure"_, or _"reorganize existing files"_ (e.g., `/groot-project — be aggressive about restructuring docs into design/`), expand scope to the broader structural moves: renaming non-standard directories at the project root (e.g., `specs/` → `design/plans/`), moving top-level `docs/` into `design/`, consolidating scattered design notes from outside `design/`. Always confirm each structural move before acting; never silently restructure files. Conservative additive retrofit (plus the light `design/`-root migration above) is the default.

## Pre-flight (always runs first)

Gather state and print a summary before asking anything:

- Is this a git repo? (`git rev-parse --is-inside-work-tree 2>/dev/null`)
- Does a recent `/office-hours` design doc exist at `~/.gstack/projects/<basename>/*.md`? Take the most recent.
- What language signals exist? Presence of `pyproject.toml`, `setup.py`, `package.json`, `Cargo.toml`, `go.mod`.
- What standard files / directories are present? `README.md`, `Makefile`, `design/`, `design/DESIGN.md`, `design/helping-hands/`, `design/plans/`, `design/stories/`, `design/stories/llm_generated/`, `design/stories/user_updated/`, `design/stories/z.done/`, `design/stories/STORY_TEMPLATE.md`, `design/notes/`, `.gitignore`, `CLAUDE.md`, `DIARY.md`, `TODO.md`.
- **Misplaced files at `design/` root**: any markdown file directly in `design/` other than `README.md` and `DESIGN.md`. List them — Phase 2's migration step will offer to move them into the right subdir.
- **Collision detection** (read but don't act yet — these inform later phases):
  - Joe-style artifacts: `TODO.md`, `DIARY.md`, `CHANGELOG.md` at the project root (indicates `/project-setup` has run or the user uses that convention).
  - gstack artifacts: `~/.gstack/projects/<basename>/`, gstack hooks in `.claude/settings.json`, gstack-specific CLAUDE.md sections (e.g., a `## gstack` heading).
  - Existing `## Project conventions` section in `CLAUDE.md` — this is the shared memory across `/groot-project`, `/project-setup`, and gstack. If present, **read it and respect it** before suggesting changes.
- Is there a terminal background color recorded for this project? (`~/.claude/skills/terminal-setup/terminal-setup.py <basename> --list-colors` shows the existing-background banner if so.)
- Is the directory under `~/code/`? (Affects alias suggestion in iTerm phase.)
- Is there a `.groot-project.toml` at the repo root? (`~/.claude/skills/terminal-setup/terminal-setup.py --groot-toml-read` — empty output means none; otherwise prints `[terminal]` as `KEY=VALUE` lines, transparently translating legacy `[iterm]` files.) This is the in-repo persistence file used to reproduce per-project workstation setup on a fresh clone. Phase 7 reads it to apply recorded settings; if absent, Phase 7 offers to write it from the just-applied settings.

Print a "found / will create / will skip / collision-detected" summary so the user sees the scope before any phase fires. The collision-detected line surfaces any Joe-style or gstack artifacts that change how subsequent phases behave (see "Coexistence" below).

## Phases (in order)

Each phase has one of three modes: **auto-default-Y** (skill announces and proceeds; user only stops it by saying "skip"), **always-asks** (genuine decision point), or **detection-skip** (skill skips silently if already present and conforming). `--auto` mode bypasses prompts; see the `--auto` section.

| #   | Phase                           | Mode                        | What it does                                                            |
| --- | ------------------------------- | --------------------------- | ----------------------------------------------------------------------- |
| 1   | Git init                        | auto-default-Y              | `git init` if not a repo. Skip otherwise.                               |
| 2   | `design/` subtree               | auto-default-Y              | Create missing pieces of the canonical subtree.                         |
| 3   | Project docs skeleton           | auto-default-Y              | Generate `CLAUDE.md`, `DIARY.md`, and `TODO.md` if missing.             |
| 4   | Office-hours import             | auto-default-Y              | If a design doc exists, layer its content into DESIGN.md and CLAUDE.md. |
| 5   | Language detection + .gitignore | always-asks                 | Ask Python / TypeScript / Rust / Go / Other / None.                     |
| 6   | Makefile                        | auto-default-Y / drift-flag | Create if missing; flag drift if present but missing standard targets.  |
| 7   | Terminal background             | always-interactive          | Invoke `/terminal-setup` (delegates fully).                             |
| 8   | GitHub remote                   | always-asks                 | Ask y/skip; default `--private`.                                        |
| 9   | gbrain registration             | always-asks                 | Ask y/skip; if yes, invoke `/sync-gbrain`.                              |
| 10  | Final summary                   | —                           | Print done / skipped / next-steps table.                                |

### Phase 1: Git init

If `git rev-parse --is-inside-work-tree` fails, run `git init`. Print one line: _"Initialized git repo."_ If already a repo, print: _"Existing git repo — skipped."_

### Phase 2: `design/` subtree

Create the canonical subtree, leaving any existing pieces alone:

```
design/
├── README.md                  # trust-hierarchy index (see "design/README.md template" below)
├── DESIGN.md                  # skeleton (or seeded from office-hours doc in phase 4)
├── helping-hands/
│   └── README.md              # the helping-hands convention doc (see "Helping-hands template" below)
├── plans/
│   └── README.md              # dated implementation plans: YYYY-MM-DD-<slug>.md
├── stories/
│   ├── README.md              # readiness-by-directory convention (see "Stories README" template below)
│   ├── STORY_TEMPLATE.md      # the standard story format (see "STORY_TEMPLATE" template below)
│   ├── drafts/.gitkeep        # explicitly partial / not-yet-ready stories (any author)
│   ├── ready/.gitkeep         # safe to implement from (default landing zone)
│   └── done/.gitkeep          # archive
└── notes/
    └── README.md              # informal materials index (see "notes/README.md template" below)
```

For each subdir or file: skip if it exists, create if it doesn't. Never overwrite.

**Migrate misplaced files at `design/` root.** After ensuring the canonical subtree, scan `design/` for files at its root other than `README.md` and `DESIGN.md`. Classify each one and present a single batched prompt:

- **Filename matches `*plan*.md` (e.g. `2026-05-05-foo-plan.md`)** → propose `design/plans/`.
- **Frontmatter has `author:` or `priority:` fields, OR filename contains `story` / `spec` / `feature`** → propose `design/stories/ready/`. If frontmatter or body indicates a partial draft, propose `design/stories/drafts/` instead.
- **Plan-companion** (e.g., `2026-05-05-foo.md` exists alongside `2026-05-05-foo-plan.md`) → propose `design/stories/ready/` (it's the spec the plan implements).
- **Dated file with no plan/story signal** (`YYYY-MM-DD-*.md`) → propose `design/notes/` (keeps the date prefix per the notes/ snapshot convention).
- **Anything that doesn't classify confidently** → list it but don't pre-classify; ask which subdir (or skip).

Present as a single batched confirmation, e.g.:

```
Found 2 files at design/ root that look misplaced:
  design/2026-05-05-foo-plan.md  →  design/plans/             (matches *-plan.md)
  design/2026-05-05-foo.md       →  design/stories/ready/     (plan-companion: implements above)

Migrate with `git mv` (preserves history)?
  [Y] all   [n] none   [p] per-file walk-through
```

- **Y**: run `git mv` for every proposal.
- **n**: leave files in place; surface "design/ root has unmigrated files: <list>" under "Drift" in the final summary so it's not forgotten.
- **p**: walk one file at a time — confirm target subdir (with the classifier's suggestion as default) or skip.

This step is **default behavior** — no aggressive flag required. It only touches files _inside_ `design/`. Broader moves (top-level `docs/` → `design/`, renaming non-canonical sibling dirs) still require aggressive-mode opt-in (see top of file). `--auto` mode runs the classifier but, since the prompt would otherwise block, defaults to **n** (leave in place) and surfaces the list under Drift — never auto-moves without user input.

**Canonical source for stories/ docs:** the embedded templates below are the single source of truth. If you want to evolve the stories convention, edit it here in `skills/groot-project/SKILL.md` and re-run `make install` — that's what propagates the change to every new project, on any machine.

**Stories README:**

```markdown
# Stories

Feature specifications. **Readiness** is encoded by directory; **authorship** lives in frontmatter.

## Directory structure

\`\`\`
stories/
├── STORY_TEMPLATE.md # the format
├── drafts/ # explicitly partial / not-yet-ready (any author)
├── ready/ # implementation-ready (default landing zone)
└── done/ # archived after implementation
\`\`\`

## Where does a new story go?

- **Default: `ready/`.** A new story should be written to a quality bar of "implementable as-is". If it isn't, it shouldn't exist yet — flesh it out before filing.
- **Exception: `drafts/`.** Use only when the story is explicitly partial — e.g., the user dropped a sentence and asked the LLM to expand it; or the LLM is blocked on input it can't get.
- **`done/`.** Move here when the feature ships.

LLM-authored stories in `ready/` are _still_ "review carefully" by convention — the author field tells the next reader what kind of review to expect (see below). `ready/` is not a stamp of correctness, just a quality threshold.

## Frontmatter

## \`\`\`yaml

author: claude # claude | user | both
priority: medium # high | medium | low

---

\`\`\`

**No `status:` field** — the directory is the status. **No `created:` / `updated:` dates** — LLMs hallucinate dates, and absolute date is the wrong question anyway. What matters is _drift relative to the codebase_, which is computed from git mtime against recent code activity (see drift check below).

## How an LLM should pick up a story

In order:

1. **Drift check first.** Get the story's last commit time:
   \`\`\`bash
   git log -1 --format=%cI -- <story-file>
   \`\`\`
   Compare to recent code activity on the modules the story touches. If meaningful code changes have landed since the story's last update, treat the story as stale: re-read against current code state and surface gaps before implementing. Drift can happen in hours with active development, not just weeks.

2. **Authorship check (frontmatter `author`):**
   - `claude` → "Probably thorough but may not match current code state. Vet against the modules it touches; expect gaps the original author didn't see."
   - `user` → "Intention likely correct but spec likely incomplete. Fill in details and flag your assumptions before implementing."
   - `both` → already iterated; treat as ready, still apply drift check.

3. **Implement from `ready/`.** Do not implement from `drafts/` without first promoting the story to `ready/` (which may involve a conversation with the user).

## Epics

For bodies of work too large for one story but coherent enough not to fragment, use an epic file:

- Lives at `stories/<dir>/<slug>-epic.md` (suffix `-epic.md`).
- Has a `## Stories` section with a checklist of child story files.
- Each child story adds a top line: `**Epic:** [<slug>-epic.md](../<dir>/<slug>-epic.md)`.
- Epic is "done" when every child story is in `done/`.

No new tooling, no folder, no metadata schema. The `-epic.md` suffix and the cross-link are the entire convention.

## When to write a story

- A feature needs design work before coding
- Multiple implementation approaches to compare
- UI/UX decisions to capture
- Complex technical requirements

**Don't** write a story for: simple bug fixes, routine changes, one-liner features.

**Important:** the LLM should ASK before writing a brand-new story unless explicitly invited.
```

**STORY_TEMPLATE.md:**

```markdown
---
author: claude # claude | user | both
priority: medium # high | medium | low
---

# Story Title

## Problem

What problem does this solve? What's the current pain point or gap?

## Proposed Solution

High-level description of the proposed approach. One paragraph.

## Design Notes

Technical considerations, schema sketches, ASCII diagrams, implementation details, alternatives considered.

## Acceptance Criteria

- [ ] Criterion 1
- [ ] Criterion 2

## Open Questions

- Things this story doesn't decide and that should be resolved before or during implementation.

## Related

- `../DESIGN.md` — relevant section
- Other stories: `<slug>.md`
- External reference: paths into `../notes/` or URLs
```

**notes/README.md template:**

```markdown
# Notes

Informal materials. **Not authoritative for project design** — see `../DESIGN.md` for that.

## Conventions

- **Snapshots**: prefix the filename with the date (e.g., `2026-05-07-name.md`). Treat as frozen-in-time.
- **Living vision drafts**: keep the original filename; location signals non-canonical status.
- **External reference**: keep the original filename; document the source at the top of the file.

If a piece of thinking here graduates into a real decision, capture it in `../DESIGN.md` or in a story under `../stories/`. If a note is contradicted by `DESIGN.md`, `DESIGN.md` wins.
```

**plans/README.md template:**

```markdown
# Plans

Dated implementation plans. One file per plan: `YYYY-MM-DD-<slug>.md`.

A plan is a concrete blueprint for a piece of work: scope, steps, decision points, fallbacks. Distinct from stories (which are _what and why_) and notes (which are exploratory).

The most recent dated plan for any given concern is the one to trust.
```

**design/README.md template** (the trust-hierarchy index for the whole subtree):

```markdown
# Design

Design artifacts for this project. The structure separates **living/authoritative** docs from **snapshots and notes** so future sessions know which to trust.

## What's here

\`\`\`
design/
├── README.md # this file
├── DESIGN.md # ← canonical, living. Source of truth for project design.
├── stories/ # ← living. Feature specs, trust-tiered.
├── plans/ # ← living. Dated implementation plans.
├── helping-hands/ # ← living. Open asks for actions only the user can take.
└── notes/ # ← informal, may be stale. Snapshots, vision braindumps, external reference.
\`\`\`

## Trust hierarchy

When in doubt, trust this order:

1. **`DESIGN.md`** — canonical project design. If something here disagrees with anything else in this directory, this wins.
2. **`stories/ready/`** — feature specs at implementation-ready quality. Apply drift + authorship checks (see `stories/README.md`) before treating as a spec.
3. **`stories/drafts/`** — explicitly partial stories. Reference only; do not implement from.
4. **`plans/`** — implementation plans, dated. Trust the latest dated plan for any given concern.
5. **`notes/`** — exploratory thinking and external reference. **Do not assume any note is current.**

Authorship of any individual story lives in its frontmatter, not its directory.

## Helping-hands

`helping-hands/` is a parallel track: tasks needing the user's hands, eyes, account credentials, or physical access. Surfaced just-in-time when a story or plan cites one. See `helping-hands/README.md`.
```

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

### Phase 3: Project docs skeleton

Creates three top-level docs if missing: `CLAUDE.md` (project-level rules + shared-memory conventions), `DIARY.md` (rolling narrative log of decisions), and `TODO.md` (light task tracker compatible with Joe's `/todo` and `/bug-bash` skills). Grouped together because all three are project-meta and reference each other from the conventions block.

**`CLAUDE.md`** — generate if missing:

```markdown
# <Project name>

<one-line description from office-hours doc, or placeholder>

See `design/DESIGN.md` for the full design and `design/README.md` for the trust hierarchy.
`design/helping-hands/README.md` documents tasks needing the user's hands.
`DIARY.md` is the rolling narrative log of decisions and architectural changes.

## Build / run

See `Makefile`. Standard targets: init, build, run, lint, test, dist, clean.

## Engineering diary

Maintain `DIARY.md` — add an entry when making significant changes, architectural decisions, or non-obvious tradeoffs. Latest entries at top. Write in narrative form, not bullet dumps. Focus on _why_ and _context_, not _what_ (that's in the commits).

## Project conventions

<!-- This section is the SHARED MEMORY across /groot-project, /project-setup, and gstack.
     Each tool reads this before suggesting structural changes. Edit deliberately. -->

This project uses the `/groot-project` `design/` subtree, a root-level `DIARY.md`, and a root-level `TODO.md` for light task tracking. Three lanes, no overlap:

- **Light task tracking** — root `TODO.md`. For "fix the sidebar flicker" / "add this shortcut" / quick bugs. Compatible with `/todo`, `/bug`, and `/bug-bash` (Joe's upstream skills) without modification.
- **Feature specs** — `design/stories/` (trust-tiered: drafts/ready/done). For work that needs design thinking before code. Heavier than a TODO entry; use when there's genuine spec work.
- **User-action items** — `design/helping-hands/`. For tasks that need the user's hands, credentials, paid subscriptions, or physical access. Not for things Claude can do.
- **Engineering diary** — root `DIARY.md`, rolling chronological narrative (latest entries on top). Separate from `design/notes/` (frozen snapshots) and `design/plans/` (forward-looking implementation blueprints).
- **Changelog** — `git log` is canonical. No separate `CHANGELOG.md` by default.
- **Atomic commits, pre-commit test/lint, test-first, mistake retrospectives, encoding preferences** — covered globally in `~/.claude/CLAUDE.md`. Do not duplicate here.

If `/project-setup` is invoked later, it should _infer skips_ from this block (and from the file/heading evidence above) rather than from item numbers — Joe's upstream may renumber. Specifically:

- Already covered here, skip: **bug tracker** (root `TODO.md` is in place — Joe's tracker convention applies as-is), **engineering diary** (root `DIARY.md` + `## Engineering diary` rule above), **changelog** (`git log` is canonical).
- Already covered globally in `~/.claude/CLAUDE.md`, skip: atomic commits, pre-commit test/lint, test-first development, mistake retrospectives, encoding preferences.
- Genuine candidates if not yet present: scorecard cadence note, README-currency rule, multi-request organization rule, and anything new Joe's `/project-setup` has added since this block was last reviewed.

## <Language>-specific notes

<placeholder — fill in as conventions emerge>
```

If `CLAUDE.md` exists but lacks a `## Project conventions` section, _offer_ to insert one (don't auto-insert). Print: _"Existing CLAUDE.md found. It has no `## Project conventions` block, which acts as shared memory between /groot-project, /project-setup, and gstack. Want me to add one? (Y/n)"_ — and if Y, append the section (plus the `## Engineering diary` rule, if not already present) without modifying anything else.

If `CLAUDE.md` exists and has a `## Project conventions` section, leave it alone. Print: _"Existing CLAUDE.md with conventions section — left untouched."_

The skeleton intentionally relies on `~/.claude/CLAUDE.md` (global) and `~/.claude/rules/*.md` (path-scoped) for the bulk of behavioral rules. Project-level CLAUDE.md only holds project-specific things plus the shared-memory conventions block.

**`DIARY.md`** — generate if missing:

```markdown
# Engineering Diary

Latest entries first. Record significant decisions, architecture changes, and non-obvious context. Narrative form, not bullet dumps. Focus on _why_ and _context_, not _what_ (that's in the commits).

---

## <YYYY-MM-DD> — Initial project setup

Set up the project with [brief description from office-hours doc, or placeholder]. Key decisions:

- <decision and rationale>
- <decision and rationale>
```

Substitute the current date for `<YYYY-MM-DD>` at generation time. If an office-hours doc was found in Phase 4 detection, pull a 1–2 sentence project description into the initial-setup entry; otherwise leave the placeholder.

If `DIARY.md` already exists at project root, leave it untouched. Print: _"Existing DIARY.md — left untouched."_

**`TODO.md`** — generate if missing. Use Joe's `/project-setup` format verbatim, since `/todo` and `/bug-bash` are built to read it:

```markdown
# Todo

<!-- Format: [status] P<priority> (category) Title -->
<!-- Status: [ ] open, [~] in progress, [x] done, [-] won't fix -->
<!-- Priority: P0 critical, P1 high, P2 medium, P3 low -->
<!-- Category: bug, feature, chore, docs -->

## Open

(no open items yet — use `/todo <description>` to add one)

## Done
```

If `TODO.md` already exists, leave it untouched (even if its format diverges — don't reformat). Print: _"Existing TODO.md — left untouched."_

### Phase 4: Office-hours import

Check for the most recent `~/.gstack/projects/<basename>/*.md`. If found:

- Ask: _"Found /office-hours design doc at <path> (last modified <date>). Import its content into DESIGN.md and seed CLAUDE.md project blurb? (Y/n)"_
- If Y: parse the doc, copy substantive content into `design/DESIGN.md` (replacing the skeleton), and pull a 1-2 sentence project description into the CLAUDE.md heading.
- If n: leave skeletons in place.

If no doc found, print: _"No /office-hours doc found. Run /office-hours later to backfill DESIGN.md."_

### Phase 5: Language detection + .gitignore

Ask: _"Project language? Python / TypeScript / Rust / Go / Other / None"_. Pre-select the answer based on detected files (e.g., presence of `pyproject.toml` → Python is the default).

Based on the answer, generate or append to `.gitignore`:

| Language   | Patterns to add                                                              |
| ---------- | ---------------------------------------------------------------------------- |
| Python     | `__pycache__/`, `.venv/`, `venv/`, `*.pyc`, `dist/`, `build/`, `*.egg-info/` |
| TypeScript | `node_modules/`, `dist/`, `.next/`, `*.tsbuildinfo`, `.turbo/`, `.cache/`    |
| Rust       | `target/`, `Cargo.lock` (only for libraries — ask the user)                  |
| Go         | `vendor/`, `*.test`, build artifacts                                         |
| Other/None | Minimal: `.DS_Store`, `*.log`                                                |

If `.gitignore` exists, append missing patterns; never remove or rewrite existing ones.

After the language is known, print a hint: _"Run `uv init` (Python) / `npm init` (TS) / `cargo init` (Rust) / `go mod init <module>` (Go) when ready — this skill won't run language tools for you."_

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

- Print: _"Existing Makefile is missing standard targets: <list>. Add them? (Y/n)"_
- If Y: append the missing targets to the existing Makefile without modifying existing ones. Use `# Standard targets added by /groot-project` as a separator comment.

### Phase 7: Terminal background

Invoke `/terminal-setup` with the project basename. The terminal-setup skill handles its own interactive flow — color picker (with vivid section), alias prompt. Don't second-guess it. In `--auto` mode, invoke `/terminal-setup auto` instead — terminal-setup's `auto` mode picks the lowest-numbered unused swatch from the main palette and uses the project basename as the alias, no prompts.

`/terminal-setup` writes `[terminal].background` (and optional `alias`) to `.groot-project.toml`. The shell's chpwd hook in `~/.shrc` reads that file on `cd` and emits OSC 11 to apply the color — terminal-agnostic (iTerm2, Ghostty, Alacritty, Kitty, WezTerm).

**`.groot-project.toml` interaction (handled by `/terminal-setup` itself).** `/terminal-setup` reads `./.groot-project.toml` at the start of its flow and prompts to apply recorded settings if present (legacy `[iterm]` files read transparently and migrate on write); at the end of its flow, it writes the file. `/groot-project` doesn't need to orchestrate this — the delegation is intact. Phase 7's behavior is just: invoke `/terminal-setup`, let it handle file detection.

The pre-flight summary still surfaces "found .groot-project.toml" (or "no .groot-project.toml") so the user sees what Phase 7 will use _before_ Phase 7 fires.

### Phase 8: GitHub remote

Ask: _"Create a GitHub remote? (y/skip)"_. If y:

- Default visibility is `--private`. (Switching private→public is easy via GitHub Settings → Danger Zone → Change visibility.)
- If `--public` flag was passed at invocation, use `--public` instead.
- If the working tree has no commits yet, run `git add . && git commit -m "Initial commit"` first.
- Run `gh repo create <basename> --<visibility> --source=. --remote=origin --push`.
- Print the resulting remote URL.

If `gh` isn't installed, print: _"`gh` not found. Install via `brew install gh` and re-run /groot-project to add the remote."_ Don't fail the rest of the skill.

### Phase 9: gbrain registration

Ask: _"Sync this project with gbrain? (y/skip)"_. If y, invoke `/sync-gbrain`. If skip, just move on.

### Phase 10: Final summary

Print a concise table:

```
/groot-project: done in <project>

Done:
  ✓ git init
  ✓ design/ subtree (README.md, DESIGN.md, helping-hands/, plans/, stories/ with trust-tier subdirs + STORY_TEMPLATE.md, notes/)
  ✓ Migrated 2 files inside design/:
      design/2026-05-05-foo-plan.md → design/plans/
      design/2026-05-05-foo.md      → design/stories/ready/
  ✓ CLAUDE.md skeleton (with ## Engineering diary rule + ## Project conventions shared-memory block)
  ✓ DIARY.md (seeded with initial-setup entry)
  ✓ TODO.md (light tracker for /todo, /bug, /bug-bash)
  ✓ Office-hours import (from <doc-path>)
  ✓ .gitignore (Python)
  ✓ Makefile (Python)
  ✓ Terminal background (Plum, alias=foo)

Collision-detected:
  - Found root-level TODO.md from /project-setup. Did not create design/TODO.md.
    The CLAUDE.md conventions block notes this so future /project-setup runs respect it.
  - Found ~/.gstack/projects/<name>/ — imported office-hours doc; left other gstack
    artifacts alone.

Skipped:
  - GitHub remote (you said skip)
  - gbrain registration (you said skip)

Next:
  - Run `uv init` to initialize the Python project
  - Run `/project-setup` if you want any of items 2/3/4/8/10b (others are duplicates — see CLAUDE.md ## Project conventions)
  - Run `/office-hours` to backfill DESIGN.md if you didn't already
  - Run `/groot-project status` later for a re-audit
```

Collision-detected lines only appear if collisions were actually found. The point is to make the avoidance auditable.

## `--auto` mode

`--auto` skips all prompts and picks sensible defaults:

- **Language**: detect from existing files (`pyproject.toml` → Python, `package.json` → TypeScript, `Cargo.toml` → Rust, `go.mod` → Go). If ambiguous or none, skip language-specific scaffolding (no `.gitignore` patterns, Makefile bodies left as `# TODO`).
- **Terminal background**: invoke `/terminal-setup auto` (terminal-setup's auto mode picks the first unused color and uses project basename as the alias).
- **GitHub remote**: SKIPPED. Creating an external resource without explicit consent is too consequential for `--auto`.
- **gbrain**: SKIPPED. Same reason.
- **Office-hours import**: still imports if a doc is found (low risk, just file content).
- All `auto-default-Y` phases just happen.

End-of-run summary calls out skipped external integrations: _"Re-run without `--auto` to handle GitHub remote and gbrain registration."_

## `status` mode

`/groot-project status` is a read-only audit. Walk the same detection logic as Pre-flight, format as a checklist:

```
Project audit for myproject:

  [✓] Git initialized
  [✓] design/ subtree (DESIGN.md, helping-hands/, plans/, stories/, notes/)
  [⚠] design/ root has 2 unmigrated files (foo-plan.md, foo.md) — Phase 2 will offer to migrate
  [✓] CLAUDE.md
  [✓] DIARY.md
  [✓] TODO.md
  [⚠] Makefile (missing targets: dist, clean)
  [✓] .gitignore (Python)
  [✓] Terminal background (claude-config, Plum)
  [✓] .groot-project.toml ([iterm].color recorded)
  [ ] GitHub remote
  [ ] gbrain registered
  [✓] /office-hours doc imported

7/10 in place. Want to address the missing/drifted items? (Y/n)
```

If the user says Y, fall through into the regular interactive walkthrough, only running phases for missing/drifted items.

## Aggressive retrofit

Files **inside** `design/` are handled by the default Phase 2 migration step (see above) — no aggressive flag needed. Aggressive mode is for the **broader, project-root** moves the default step won't touch.

When the user invokes with aggressive/restructure language (_"be aggressive"_, _"restructure"_, _"reorganize"_, _"move things into design/"_, etc.), expand scope to:

- Offer to move top-level directories that semantically belong inside `design/` — e.g., a project-root `docs/` → `design/notes/`, `specs/` → `design/plans/`, `stories/` (at project root) → `design/stories/`.
- Offer to rename non-standard sibling directories that map to canonical names.
- Offer to consolidate scattered design-ish files from across the repo into `design/notes/`.

**Always confirm each structural move before acting**, and use git operations (`git mv`) so history is preserved. Never silently restructure files. Aggressive mode is opt-in by user phrasing — never the default.

## Helping-hands template

The embedded template below is the single source of truth for `design/helping-hands/README.md`. To evolve the convention, edit it here in `skills/groot-project/SKILL.md` and re-run `make install`.

```markdown
# Helping hands

Tasks that need Derek's hands, eyes, account credentials, paid subscription, or physical access.

## Format

- One markdown file per item, date-prefixed: `YYYY-MM-DD-<slug>.md`
- YAML frontmatter: `status` (open/in-progress/done/dropped), `created`, `priority`, `estimated_time`
- Body structure, **in this exact order** — TL;DR and the concrete steps must be readable without scrolling past the title. Background context lives below the fold.
  1. `# <Friendly title>` — phrased as a request, not a directive.
  2. `**TL;DR:** <one sentence>` — reader should know what to do from this line alone.
  3. `## Do this` — numbered concrete steps, paste-ready, one action per step. Second from top, never buried.
  4. `## Tell me when you're done` — what the user reports back (or what the LLM will detect) to unblock the next step.
  5. `---` separator.
  6. `## Background (optional reading)` containing:
     - `### Why this matters`
     - `### What I already did to make this easier`
     - `### Related`

  Snags, gotchas, future-state notes, and other detail are additional `###` sub-sections inside Background.

- The "what I already did" section is non-decorative — if it would be empty, the entry should not have been created. Do that work first instead.

## Surfacing in chat

Filed entries surface as a one-liner only: `Filed: <title> — see design/helping-hands/`. Not a paragraph. Not a recap. The artifact is the source of truth.

## Just-in-time, not session-start

When picking up work, check whether any open helping-hands item is referenced as a blocker by the current task, its parent story, or its plan. If so, name the specific blocker before pressing on. Do not auto-scan the directory at session start.
```

## Coexistence with `/project-setup` and gstack

`/groot-project` runs alongside Joe Walnes's `/project-setup` and the gstack skill family. None of them modifies the others' files. They cooperate via a single **shared memory**: the `## Project conventions` section in the project's `CLAUDE.md`.

### How the shared memory works

`/project-setup` already promises (in its own SKILL.md): _"read the project's existing `CLAUDE.md`, `README.md`, `CONTRIBUTING.md`, and any config files to understand what's already in place. Don't suggest things the project already does."_ This is the hook. `/groot-project` writes a `## Project conventions` section that explicitly names which `/project-setup` items are already covered globally and which would conflict with this project's design/ pattern.

Many gstack skills also read `CLAUDE.md` for project context. The conventions block tells them too.

### Order of invocation — both directions handled

- **`/groot-project` first, then `/project-setup`** (the recommended path): the conventions block is in place. `/project-setup` reads it and skips covered items (5/6/7/9/10a duplicates, item 1 conflict with design/ tracking). It still offers 2/3/4/8/10b — the user picks.
- **`/project-setup` first, then `/groot-project`**: pre-flight detects root-level `TODO.md` / `DIARY.md` / `CHANGELOG.md`. Phase 2 skips creating any equivalent under `design/`. Phase 3 inserts a `## Project conventions` block that _reflects what already exists_ (e.g., "Bug tracking — uses root `TODO.md` per `/project-setup`. Don't create `design/TODO.md`.") so subsequent `/groot-project` and `/project-setup` runs stay coherent.
- **Either run twice**: pre-flight detection makes both idempotent. No file is ever overwritten. The summary's "collision-detected" section makes the avoidance auditable.

### gstack collisions

- **`/office-hours`** writes to `~/.gstack/projects/<basename>/`. Phase 4 imports from there. No collision.
- **`/todo` and `/bug-bash`** (gstack) read/write root-level `TODO.md`. If `/project-setup` created one, gstack works on it natively. If this project uses the design/-centric pattern instead, the conventions block tells gstack skills that there's no `TODO.md` to read — they should fall back to `design/stories/` or ask.
- **`/sync-gbrain`** is invoked optionally in Phase 9; it manages its own state in `CLAUDE.md` under a `## GBrain Search Guidance` heading. Don't touch that section.
- **`/setup-deploy`** writes deploy config under its own heading in `CLAUDE.md`. Don't touch.
- **`/plan-*` gstack skills** write plan files to ad-hoc paths. They don't conflict with `design/plans/` — but they also don't integrate. If the user wants gstack plan output to land in `design/plans/`, that's a manual move (out of scope for this skill).

### Maintenance discipline

- **Never edit upstream skills** (`/project-setup`, gstack/\*). Behavior changes for them happen by changing what `CLAUDE.md` says, not by patching their SKILL.md.
- **Re-running `/groot-project` is safe** — it re-detects state and only fills gaps.
- **If the conventions block goes stale** (e.g., the project moves from design/-centric to root-level tracking), update it by hand or re-run `/groot-project status` followed by the interactive walkthrough; the skeleton offer in Phase 3 will surface the drift.

## What this skill does NOT do

- Doesn't run `/project-setup` (mention it as a final pointer; separate skill, separate concern).
- Doesn't write `pyproject.toml` / `package.json` / `Cargo.toml` directly — delegates to the language tool's own init flow (`uv init`, `npm init`, `cargo init`).
- Doesn't do detailed code architecture or design-system work — use `/design-consultation` or `/init` for that.
- Doesn't manage worktrees — separate concern.
- Doesn't push to GitHub aggressively or set up CI/CD — out of scope; use `/setup-deploy` and friends for that.
- Doesn't restructure files unless the user explicitly invokes aggressive/restructure mode.
- Doesn't maintain or update CLAUDE.md content beyond the initial skeleton — use `/claude-md-add` for ongoing additions.

## Reference

- All canonical templates (stories/, STORY_TEMPLATE, helping-hands, notes/, plans/, design/README) live in this SKILL.md itself — no external dependencies, portable across machines.
- terminal-setup: `~/.claude/skills/terminal-setup/terminal-setup.py`
- `gh` CLI for GitHub remote: https://cli.github.com/
- `/sync-gbrain` skill (gstack)
- `/project-setup` skill (Joe Walnes upstream): retrofits 10 conventions to existing projects (independent of this skill)
- `/office-hours` skill (gstack): produces a design doc at `~/.gstack/projects/<basename>/*.md` that this skill can import
