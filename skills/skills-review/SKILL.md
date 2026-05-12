---
name: skills-review
description: Audit installed Claude Code skills — enumerate, categorize, flag duplicates and conflicts, surface usefulness for this user. Default mode regenerates an HTML report at ~/.claude/design/skills-review.html and opens it. Use when asked to "review skills", "audit skills", "what skills do I have", "skills review", or "do recommended" / "apply skills-review recommendations" to act on a prior report's action items.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Skills Review

Audit the installed skill catalog and produce an actionable HTML report. Three modes, dispatched on invocation args.

## Modes

**(no args) — review.** Regenerate the catalog report. Default behavior.

**`research` — project-aware analysis.** Same report plus a "Suggested for this project" section that walks the *current* project's CLAUDE.md, README, package manifests, and recent git activity to recommend skills the user is leaving on the table.

**`do recommended` / `apply recommendations` / `apply <ID>` / `do <ID> and <ID>` — act.** Re-read the existing report, execute the requested actions. IDs use the form `A1`, `E1`, `D1` etc., taken from the action list in the prior report.

## Mode 1: Review (default)

### Step 1 — Enumerate skill sources

Walk the filesystem in parallel:

1. `ls -la ~/.claude/skills/` — directly-installed and symlinked skills.
2. `ls ~/.claude/plugins/cache/claude-plugins-official/` — installed plugins. For each plugin, find SKILL.md files: `find ~/.claude/plugins/cache/claude-plugins-official/<plugin>/<version>/skills/ -name SKILL.md`.
3. Local skills source repo (e.g., a fork of `joewalnes/skills` or any sibling repo whose skills are symlinked into `~/.claude/skills/`). **Discover the path at runtime**, don't hardcode: `readlink ~/.claude/skills/<any-symlinked-skill>` resolves to that skill's source location, and the parent's parent (`dirname $(dirname $(readlink ...))`) is the repo's `skills/` dir. Pick a skill you know is local (e.g., one listed in this repo's `MAINTAINERS.md`); skip this source entirely if no `~/.claude/skills/<name>` symlinks resolve to a non-plugin location.
4. Note built-in CLI skills (loop, schedule, claude-api, init, review, security-review, simplify, fewer-permission-prompts, update-config, keybindings-help). These aren't on disk — they're harness-resident. Use the session's system-reminder skill listing as the canonical source for these (their descriptions appear there).

For each skill found, capture: name, source (gstack / superpowers / plugin / local / built-in), one-line description (from frontmatter `description:` field, trimmed to a single sentence).

### Step 2 — Read user context

Read `~/.claude/CLAUDE.md`. Extract:
- Stated languages / stack (Python, TypeScript, etc.)
- Workflow preferences (TDD, plan-before-implement, evidence-over-claims, etc.)
- Safety / destructive-command preferences
- Any explicit framework preferences (gstack vs superpowers)

These drive the per-skill rating.

### Step 3 — Categorize and sort

Group skills into these buckets (skip empty ones):

1. Discovery & Planning — brainstorming, office-hours, prior-art, plan-*, writing-plans, autoplan
2. Design — design-*, frontend-design, devex-review
3. Implementation — TDD, executing-plans, subagent-driven-development, dispatching-parallel-agents, using-git-worktrees, claude-api, tool-web
4. Debugging & Quality — investigate, systematic-debugging, verification-before-completion, simplify, scorecard, health, learn, retro
5. Code & Plan Review — review (gstack + native), codex, requesting/receiving-code-review, finishing-a-development-branch, cso, security-review
6. Ship & Deploy — ship, land-and-deploy, canary, document-release, landing-report, benchmark*, release-setup
7. Browser & QA — browse, gstack, qa, qa-only, scrape, skillify, pair-agent, open-gstack-browser, setup-browser-cookies
8. Setup & Config — project-setup, iterm-setup, setup-deploy, setup-gbrain, sync-gbrain, gstack-upgrade, init, update-config, fewer-permission-prompts, keybindings-help
9. Safety — careful, freeze, unfreeze, guard
10. Context & Memory — context-save, context-restore, sitrep
11. Meta & Skill-Authoring — using-superpowers, writing-skills, loop, schedule, skills-review
12. Utilities & Misc — make-pdf, readme, todo, bug, bug-bash, hello-world

**Within each category, sort rows by:**

1. **Rating** (primary): green (High) → yellow (Situational) → orange (Niche) → red (Redundant/Removable) → gray (—/Required).
2. **Source** (secondary, alphabetical by class name): `built-in` → `gstack` → `local` → `plugin` → `super` (superpowers).
3. **Skill name** (tertiary, alphabetical).

This keeps the most useful skills at the top of every section and makes scanning predictable. If a skill's rating ties with another, source-then-name decides — never insertion order.

### Step 4 — Rate each skill

Four ratings, plus a "—" (gray) for required/unrateable framework skills:
- **High (green)** — fits the user's stack, preferences, and recent activity directly.
- **Situational (yellow)** — domain-specific (UI work, deploys, etc.). Useful when the situation arises.
- **Niche (orange)** — narrow application or rarely needed.
- **Redundant (red)** — duplicates another skill or has no production value.

Don't bake ratings into the skill — re-derive them each run from the user's current CLAUDE.md.

### Step 5 — Find duplicates and conflicts

Scan for:
- Identical or near-identical descriptions (e.g. `gstack` ≡ `browse`).
- Skills whose own description says "alias for" or "subset of" another.
- Workflow overlaps (two skills that fire on the same trigger).
- Stale directories — a SKILL.md whose `name:` field doesn't match its parent dir name.
- Composite skills (e.g. `guard` = `careful` + `freeze`) — flag but don't recommend removal unless unused.

### Step 6 — Build action list

Group recommendations into three tiers:
- **🟢 Safe to auto-apply** — concrete `rm` / `make install` commands that delete clear-no-value skills (test skills, stale dirs, alias skills the user explicitly opts to drop). Each gets an ID (`A1`, `A2`, ...).
- **🔵 Suggested edit** — drafts of CLAUDE.md additions or settings changes. Each gets an ID (`E1`, `E2`, ...).
- **🟡 Needs your call** — overlapping skills where the user has to choose. Each gets an ID (`D1`, `D2`, ...). No commands until decided.

**Be conservative on red ratings.** The user has explicitly said: don't object to skills that seem usable in other projects. Treat red as "candidate to consider", not "delete". Only A-tier (safe to auto-apply) gets concrete commands.

### Step 7 — Write the report

Write to `~/.claude/design/skills-review.html`. Use the structure from the existing report at that path as the template. Required sections, top to bottom:

1. **Header** — date, total skills count, source breakdown, current project + branch.
2. **Executive Summary** (top, before legend) — one-line verdict, then the three action tiers with IDs and inline commands. Footer: "say `do recommended` next session…".
3. **Legend** — color-coded usefulness key.
4. **Table of contents** — anchored links to each category.
5. **Per-category tables** — name, source pill (color-coded), description, rating.
6. **Redundancy & Conflicts** section — narrative explanation of each detected conflict.
7. **Probably underused** section — skills the model thinks fit the user but they may not be invoking.
8. **Sources walked** footer — what file paths were inspected, what was excluded.

Use the existing report's CSS verbatim. Don't add JS — the report is static HTML.

### Step 8 — Open it

`open ~/.claude/design/skills-review.html`. Skip the open if running headless (no GUI environment).

Print one line of text: `Wrote ~/.claude/design/skills-review.html (N skills, M actions). Opened.`

## Mode 2: Research (project-aware)

Run Mode 1's enumeration + categorization first (steps 1–5 — you need the catalog). **But don't write the global report yet.** Mode 2 produces a *project-specific* report at `<project-root>/design/skills-review.html`, not the global one.

The goal: find 3–5 skills that fit this project's stack and recent work but the user hasn't been invoking. Evidence-backed, not vibes.

### Step R1 — Identify the project

```bash
project_root=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
project_name=$(basename "$project_root")
```

If `$project_root` is `~/.claude` itself, this is the same project as Mode 1's global view — write to `~/.claude/design/skills-review.html` and label the panel "for ~/.claude" rather than duplicating.

### Step R2 — Detect stack

Read whichever of these exist in `$project_root`:

- `package.json` → JS/TS. Note dependencies that map to skills: `@anthropic-ai/sdk` / `anthropic` → claude-api signal; `react` / `next` / `vite` → frontend-design signal; `playwright` / `puppeteer` → browse signal.
- `pyproject.toml` / `requirements.txt` / `Pipfile` → Python. Note `anthropic` → claude-api signal.
- `Cargo.toml` → Rust. `go.mod` → Go (release-setup signal). `Gemfile` → Ruby.
- `Dockerfile` / `fly.toml` / `vercel.json` / `netlify.toml` / `.github/workflows/` → deploy targets (setup-deploy signal).
- `tsconfig.json`, `vitest.config.*`, `jest.config.*`, `pytest.ini`, `tox.ini` → test infra (TDD signal).

Capture stack as a short list: e.g. `["TypeScript", "Next.js", "Anthropic SDK", "Vercel"]`.

### Step R3 — Read project context

- `<project>/CLAUDE.md` (project-level, if present) → preferences specific to this repo.
- `<project>/README.md` → first 100 lines for purpose summary.
- `<project>/design/` → if it exists, list files for ongoing-work signals.

### Step R4 — Recent activity

```bash
git -C "$project_root" log --since="60 days ago" --pretty=format:"%h|%s" 2>/dev/null
git -C "$project_root" log --since="60 days ago" --pretty=format:"" --name-only 2>/dev/null | sort -u
git -C "$project_root" rev-parse --abbrev-ref HEAD
git -C "$project_root" worktree list 2>/dev/null
```

Extract patterns:
- Commit subject prefixes (`fix:`, `feat:`, `refactor:`, `test:`, `docs:`) — what kinds of work?
- Repeat fix subjects on the same area → debugging gap (signals `/investigate` or `/systematic-debugging`).
- Commits that look like deploys/releases without VERSION/CHANGELOG churn → `/ship` gap.
- Files touched: lots of `.tsx` / `.css` → design-* signal; lots of `_test.py` / `*.test.ts` → TDD already in flow; lots of `.md` doc churn → `/document-release` signal.

### Step R5 — Skill invocation history (the gold signal)

Compute the transcript directory and list recent skill invocations:

```bash
encoded=$(printf '%s' "$project_root" | sed 's|[^a-zA-Z0-9]|-|g')
transcripts="$HOME/.claude/projects/$encoded"

# What skills have ever been invoked in this project?
grep -h '"name":"Skill"' "$transcripts"/*.jsonl 2>/dev/null \
  | grep -oE '"skill":"[^"]+"' \
  | sort -u

# Invocation counts (last 60 days):
find "$transcripts" -name '*.jsonl' -mtime -60 -exec grep -h '"name":"Skill"' {} + 2>/dev/null \
  | grep -oE '"skill":"[^"]+"' \
  | sort | uniq -c | sort -rn
```

If `$transcripts` doesn't exist (fresh project, never opened in CC before), note that and rely entirely on stack + commit signals.

### Step R6 — Apply the recommendation rubric

Pick at most 5 skills. Each must have **at least one** of these signals:

1. **Stack-fit, never-invoked** — skill description matches stack from R2 but skill name absent from R5's history. (Strongest signal.)
2. **Workflow gap** — recent activity shows a pattern (e.g. ≥3 `fix:` commits) without the matching skill (e.g. `/investigate`, `/systematic-debugging`).
3. **CLAUDE.md alignment** — project's CLAUDE.md states a preference that a specific skill enforces.
4. **Cadence gap** — commits to a release branch without `/ship` ever firing → recommend `/ship`.
5. **Inferred from recent CC commits** — if recent commits mention skills, hooks, settings.json, suggest `/update-config` or `/writing-skills`.

**Disqualify a recommendation if:**
- The user's CLAUDE.md (global or project) explicitly opts out of this skill or its category.
- The skill is rated red in the global review (redundant).
- The user has invoked this skill ≥3 times in the last 60 days (they already know about it).

For each kept recommendation, write one line of evidence — citing a file, dependency, or commit count — not a generic description.

### Step R7 — Write the project-specific report

Write to `<project_root>/design/skills-review.html`. Create `design/` if missing.

Same structure as the global report, with the executive summary's first panel replaced by **"Suggested for this project"**:

```html
<section class="exec">
  <h2>Skills Suggestions for <project-name></h2>
  <p class="verdict">
    Stack: <stack chips>. Last 60 days: N commits, top kinds: feat/fix/refactor.
    Skills invoked here: M unique. <K> recommendations below, each with evidence.
  </p>
  <h3>⭐ Try these in this project</h3>
  <ul class="actions">
    <li class="draft">
      <span class="marker">R1</span>
      <div>
        <div class="what">Try /<skill-name>.</div>
        <div class="why"><evidence-line — file, dep, or commit count></div>
        <div class="cmd"># Invoke next session:
/<skill-name> [<args>]</div>
      </div>
    </li>
    ...
  </ul>
  <h3>📊 Skill usage in this project (60d)</h3>
  <!-- small bar list: skill name → invocation count -->
</section>
```

After the suggestions panel, include the *same* global catalog from Mode 1 (categorized tables, redundancy section) for reference — but mark which rows in the tables have been invoked in *this* project (e.g. a small badge `· used 4× here` next to the rating column).

### Step R8 — Open it

```bash
open "$project_root/design/skills-review.html"
```

Print one line: `Wrote $project_root/design/skills-review.html (K project recommendations from N skills, M unique invoked here in 60d). Opened.`

### Mode 2 edge cases

- **No git** → skip R4 and R5. Recommendations come from stack + project CLAUDE.md only. Note "no git history" in the verdict line.
- **No transcripts** → skip R5. Recommendations come from stack + commits. Note "no prior CC sessions in this project".
- **Project root is ~/.claude** → write to `~/.claude/design/skills-review.html` (the global location). Don't duplicate; merge the suggestions panel into the existing exec summary above the global recommendations.
- **Stack detection finds nothing** (e.g., a docs-only repo) → recommend `/make-pdf`, `/readme`, `/document-release`, etc. — workflow skills that don't depend on a code stack.

## Mode 3: Apply actions

Triggered when invocation args include `do recommended`, `apply recommendations`, `apply <ID>`, `do <ID> and <ID>`, etc.

### Step 1 — Locate the report

Read `~/.claude/design/skills-review.html`. If missing, run Mode 1 first.

### Step 2 — Parse action items

Extract each `<li class="actions ...">` block. Each has:
- An ID (A1, E1, D1, ...) in `<span class="marker">`.
- A "what" line.
- A "why" line.
- An optional `<div class="cmd">` block with the exact commands.

### Step 3 — Determine scope

- `do recommended` / `apply recommendations` → all 🟢 (safe) actions, plus offer 🔵 (edit) drafts, plus surface 🟡 (decide) for user input.
- `apply A1` → only A1.
- `do A1 and E1` → A1 and E1.

### Step 4 — Confirm and execute

Print the planned actions as a numbered list, with the exact commands that will run. Ask for a single confirmation: `Apply these N actions? (y/N)`.

On `y`:
- 🟢 actions: run the commands. Show output for each. If a `make install` or git commit is in the command, run those too.
- 🔵 actions: print the draft block, ask the user to paste it into the file (or offer to apply via Edit if the target file is unambiguous, e.g. `~/.claude/CLAUDE.md`).
- 🟡 actions: print the question for each, wait for user's choice, then act per their answer (which may itself become a new auto-apply step).

After execution, regenerate the report (Mode 1) so the action list reflects the new state.

### Step 5 — Verify

For each removed skill: confirm the directory no longer exists. For each Makefile-driven change: confirm `make install` succeeded. For CLAUDE.md edits: confirm the new section appears with `grep`.

## Rules

- **Never delete skills directly from `~/.claude/skills/<name>/`** unless they are real directories (not symlinks) and not from a plugin. For symlinked local skills: discover the source location via `readlink ~/.claude/skills/<name>` (resolves to the skill's actual source dir), delete that source, then run `make install` from the source repo's root to refresh the symlinks.
- **Never modify plugin skill content** — those are owned by the plugins and reset on update.
- **Don't propose removing safety skills** (careful, freeze, unfreeze, guard, verification-before-completion) even if rarely used. They're insurance.
- **Don't add JS to the report.** Static HTML, inline CSS, zero deps.
- **Re-derive ratings on every run.** Read CLAUDE.md fresh; don't cache.
- **Conservative on red.** Red = "consider", not "delete".
- **Open is best-effort.** Skip silently if headless.
- **Built-in skills are listed by name** — the harness owns their descriptions in the session reminder. Use what's in the active session's system reminder rather than guessing.

## Known limitations

- The session's skill listing (system reminder) is the only source for built-in skill descriptions. If the report is regenerated outside an active session, those descriptions will be missing. Note this in the report's footer.
- Plugin versions are pinned by directory name; multiple versions may exist in the cache. Use the symlink at `~/.claude/plugins/cache/claude-plugins-official/<plugin>/<version>` referenced from `~/.claude/plugins/installed_plugins.json` as the active version.
- The "Suggested for this project" panel depends on git history and project files; for a fresh project with no commits, it will produce thin output. Note this in the panel.
