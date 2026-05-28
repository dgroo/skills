# /beginners-mind Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a general-purpose `/beginners-mind` skill that periodically audits any project with a fresh-eyes perspective, surfacing recommendations, behavioral patterns, novel-to-the-corpus practices, and "why is it like this?" cruft.

**Architecture:** Markdown-driven Claude Code skill (a single `SKILL.md` orchestrates everything; subagents do all heavy reading). State is per-project (location declared in a profile artifact the skill generates on first run via `--init`). The beginner's-mind perspective comes from a deliberately under-briefed fresh subagent in Phase 3 (code-only, docs-withheld, question-first) — the orchestrator answers the subagent's questions using full context, and the mismatches become report content.

**Tech Stack:** Markdown (SKILL.md prompts), Bash (file enumeration, git, WebFetch caching via curl with ETag), Claude Code Agent tool (subagent dispatch), Read/Write/Edit (state files), AskUserQuestion (cadence guardrail + `--init` flow). No Python helper scripts in v1 — keep everything in the prompt-driven skill surface.

**Spec:** `~/code/claude/skills/design/stories/ready/beginners-mind.md` (commit `597a202`).

**Where things live:**

- Skill code (source of truth): `~/code/claude/skills/skills/beginners-mind/` in the `dgroo/skills` repo.
- Installed: `~/.claude/skills/beginners-mind/` (symlink, created by `make install` from `dgroo/skills`).
- Plan + spec: in `dgroo/skills/design/`.
- Per-project profile + state: declared by the profile itself. Default `design/beginners-mind.md` + `design/beginners-mind/state/`; or `~/.claude/beginners-mind/` for the federation/global use case.

**Note on TDD rhythm for prompt-driven work:** Standard TDD ("write failing unit test, watch it fail, implement, watch it pass") doesn't apply to markdown prompt files. The adapted rhythm for each task is:

1. Write a **smoke-test specification** — a concrete invocation + expected observable behavior.
2. Run the smoke test against the current SKILL.md state — expected to fail (behavior not implemented).
3. Add/modify the SKILL.md section.
4. Run the smoke test again — expected to pass.
5. Commit.

Most smoke tests will be invocations of the partial skill against a small fixture project created in `/tmp`. Task 14 is the end-to-end smoke against the real federation use case.

**Commit hygiene:** All commits in this plan land in `dgroo/skills` unless noted otherwise. The final smoke-test task (Task 14) generates state artifacts that land in `dgroo/dot-claude` — that task explicitly flags both repos and commits to each separately.

Every commit message ends with the standard Claude Code Co-Authored-By trailer (see the global Bash-tool conventions). The commit commands below use `<COAUTHOR_EMAIL>` as a placeholder to satisfy this repo's PII linter; **at commit time, substitute the standard CC co-author email** (the same one used in every other commit in this repo — `git log -1 --format=%B` on any prior commit shows the exact form). Full trailer:

```
Co-Authored-By: Claude Opus 4.7 (1M context) <COAUTHOR_EMAIL>
```

---

## File Structure

Files created across this plan:

```
~/code/claude/skills/
├── skills/beginners-mind/
│   ├── SKILL.md                          # main orchestration (built up across tasks)
│   └── templates/
│       ├── profile.md                    # the profile artifact template
│       └── report.md                     # report structure template
├── design/
│   ├── plans/2026-05-28-beginners-mind.md   # this plan
│   └── stories/ready/beginners-mind.md       # the spec
└── MAINTAINERS.md                        # add /beginners-mind to Derek-authored table

/tmp/bm-fixture-project/                  # ephemeral fixture for smoke tests (gitignored, regenerated per task)
```

`SKILL.md` is the single big file; each task adds one well-bounded section. Templates are small standalone files copied verbatim by `--init` and the report writer.

---

## Task 1: Scaffold skill directory + minimal SKILL.md + Makefile install

**Files:**

- Create: `~/code/claude/skills/skills/beginners-mind/SKILL.md`
- Modify: `~/code/claude/skills/MAINTAINERS.md` (add entry to Derek-authored table)

- [ ] **Step 1: Write the smoke-test spec**

After this task, the smoke test is:

- `ls -la ~/.claude/skills/beginners-mind` shows a symlink resolving to `~/code/claude/skills/skills/beginners-mind/`.
- Starting a fresh CC session and typing `/` shows `beginners-mind` in the skill menu with the description from frontmatter.

- [ ] **Step 2: Run smoke test against current state**

Run:

```bash
ls -la ~/.claude/skills/beginners-mind 2>&1
```

Expected: "No such file or directory" — skill doesn't exist yet.

- [ ] **Step 3: Create the skill directory and minimal SKILL.md**

Create `~/code/claude/skills/skills/beginners-mind/SKILL.md`:

```markdown
---
name: beginners-mind
description: Periodic fresh-eyes audit of any project. Reads the project's profile, introspects current state, observes behavioral patterns, runs an under-briefed fresh-observer subagent (code-only, question-first), pulls from a curated external corpus, and produces a four-section report — Recommendations, Behavioral observations, Cool things, "Why is it like this?". Stateful (corpus + findings + ledger persist across runs). Use when asked to "review the setup", "fresh eyes on this project", "beginner's mind", "/beginners-mind", or to apply prior recommendations via "/beginners-mind apply <ID>".
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent, WebFetch, WebSearch, AskUserQuestion
---

# /beginners-mind — fresh-eyes audit for any project

(Implementation in progress — sections added task-by-task per the implementation plan at `~/code/claude/skills/design/plans/2026-05-28-beginners-mind.md`.)

## How to invoke

- `/beginners-mind` — full run.
- `/beginners-mind --init` — interactive profile setup (also auto-fires if no profile found).
- `/beginners-mind --force` — bypass cadence guardrail.
- `/beginners-mind --dry-run` — show planned phases and estimated token spend; no fetches, no writes.
- `/beginners-mind --skip-research` / `--skip-transcripts` / `--introspect-only` — phase-level cost control.
- `/beginners-mind --bootstrap-corpus` — re-seed the project corpus.
- `/beginners-mind apply <ID>` or `do recommended` — act on prior report's action items.

(Further sections to be added by subsequent plan tasks.)
```

- [ ] **Step 4: Add entry to MAINTAINERS.md**

Open `~/code/claude/skills/MAINTAINERS.md`. In the "Derek-authored" table, insert a new row alphabetically (between `bug-bash` row if any and `claude-md-add`):

```
| `beginners-mind`     | 2026-05-28  | Periodic fresh-eyes setup audit; general, profile-driven                                                                                                                                                                                                |
```

Verify the row is sorted alphabetically.

- [ ] **Step 5: Run `make install`**

Run:

```bash
cd ~/code/claude/skills && make install
```

Expected output includes a line indicating `beginners-mind` was symlinked into `~/.claude/skills/`.

- [ ] **Step 6: Run smoke test**

Run:

```bash
ls -la ~/.claude/skills/beginners-mind
```

Expected: a symlink line resolving to `~/code/claude/skills/skills/beginners-mind`.

- [ ] **Step 7: Commit**

```bash
cd ~/code/claude/skills && git add skills/beginners-mind/SKILL.md MAINTAINERS.md && git commit -m "$(cat <<'EOF'
beginners-mind: scaffold skill + add to MAINTAINERS

Empty skill body with frontmatter and invocation surface only;
phases get added per the implementation plan.

Co-Authored-By: Claude Opus 4.7 (1M context) <COAUTHOR_EMAIL>
EOF
)"
```

---

## Task 2: Profile template + parser instructions

**Files:**

- Create: `~/code/claude/skills/skills/beginners-mind/templates/profile.md`
- Modify: `~/code/claude/skills/skills/beginners-mind/SKILL.md` (add "Profile schema" section)

- [ ] **Step 1: Write the smoke-test spec**

After this task, given a fake profile written to `/tmp/test-profile.md`, asking Claude (with SKILL.md instructions) to "parse this profile and tell me what's in the _Visible to fresh observer_ section vs the _Orchestrator only_ section" should return both sections distinctly, with the orchestrator-only content clearly flagged as not-for-subagent.

- [ ] **Step 2: Run smoke test against current state**

Write a fake profile:

```bash
cat > /tmp/test-profile.md <<'EOF'
# Test Project — /beginners-mind profile

## Visible to fresh observer

- **Scope:** `/tmp/test-project/src/`
- **Out of scope:** `/tmp/test-project/vendor/`
- **Behavioral signal sources:** git
- **Corpus location:** `/tmp/test-project/design/beginners-mind/state/corpus.md`
- **State location:** `/tmp/test-project/design/beginners-mind/state/`
- **Cadence:** 30
- **Token budget:** 500000
- **What to watch for:** "we keep re-inventing config patterns"
- **What to skip:** "don't recommend more tests"

## Orchestrator only — do not include in fresh-observer subagent context

- Design history pointers: `design/DESIGN.md`
- Known-weird-but-intentional choices:
  - `vendor/` is a frozen snapshot of legacy code; pending migration sprint 2026-Q3.
EOF
```

Expected: skill has no profile-parsing instructions yet; can't pass smoke test.

- [ ] **Step 3: Create the profile template**

Create `~/code/claude/skills/skills/beginners-mind/templates/profile.md`:

```markdown
# {{project_name}} — /beginners-mind profile

> **About this file.** This profile is the project's pact with the `/beginners-mind` skill. The two H2 sections below are read with _different access rules_: the **Visible to fresh observer** section is shared with the Phase 3 fresh-observer subagent; the **Orchestrator only** section is _never_ passed to that subagent. The skill enforces this split.

## Visible to fresh observer

- **Scope:** {{scope_paths_comma_separated}}
- **Out of scope:** {{exclude_paths_comma_separated}}
- **Behavioral signal sources:** {{signal_sources_comma_separated}}
- **Corpus location:** {{corpus_path}}
- **State location:** {{state_path}}
- **Cadence:** {{cadence_days}}
- **Token budget:** {{token_budget}}
- **What to watch for:** {{owner_standing_concerns}}
- **What to skip:** {{owner_anti_recs}}

## Orchestrator only — do not include in fresh-observer subagent context

- **Design history pointers:** {{design_doc_pointers}}
- **Known-weird-but-intentional choices:** {{intentional_quirks}}
- **Decisions log:** {{decisions_log}}
```

The `{{placeholder}}` tokens are filled in by the `--init` flow (Task 3).

- [ ] **Step 4: Add "Profile schema" section to SKILL.md**

Append to `~/code/claude/skills/skills/beginners-mind/SKILL.md` (above the closing parenthetical, replacing the "(Further sections to be added…)" line):

```markdown
## Profile schema

A profile is a markdown file with **two H2 sections that have different access rules**:

- `## Visible to fresh observer` — structural information the Phase 3 fresh-observer subagent IS allowed to see (scope, corpus location, behavioral signal sources, etc.).
- `## Orchestrator only — do not include in fresh-observer subagent context` — rationale, design history, "known-weird-but-intentional" answers. The orchestrator uses this ONLY when answering questions the fresh subagent asks; it MUST NOT include this section in the subagent's input.

### How to parse a profile

1. Read the profile file with the `Read` tool.
2. Split on the H2 headers. Identify both sections by exact header match (case-sensitive on the first phrase: "Visible to fresh observer" and "Orchestrator only").
3. If either section is missing, surface an error: "Profile at <path> is missing required section: <name>."
4. Return both sections as separate strings. The Phase 3 dispatcher uses ONLY the "Visible to fresh observer" section.

### Locating the profile

Priority order, first match wins:

1. Explicit path from `--profile <path>` argument.
2. `design/beginners-mind.md` relative to the current working directory.
3. `.beginners-mind.md` at the current working directory.
4. If none found, fall through to `--init` mode (Task 3).
```

- [ ] **Step 5: Run smoke test**

Start a fresh CC session and prompt:

> Using the `/beginners-mind` SKILL.md's profile-parsing instructions, parse `/tmp/test-profile.md` and report back the two sections separately. Confirm the orchestrator-only section is flagged as not-for-subagent.

Expected: Claude reads SKILL.md, follows the parse instructions, returns both sections with the orchestrator-only one clearly flagged.

- [ ] **Step 6: Commit**

```bash
cd ~/code/claude/skills && git add skills/beginners-mind/templates/profile.md skills/beginners-mind/SKILL.md && git commit -m "$(cat <<'EOF'
beginners-mind: profile template + schema/parser section

Two-section profile (Visible to fresh observer / Orchestrator
only) is the access-control primitive for the Phase 3 meta-
cognitive split. Parser instructions live in SKILL.md; template
gets copied verbatim by --init.

Co-Authored-By: Claude Opus 4.7 (1M context) <COAUTHOR_EMAIL>
EOF
)"
```

---

## Task 3: `--init` interactive flow

**Files:**

- Modify: `~/code/claude/skills/skills/beginners-mind/SKILL.md` (add "Mode: --init" section)

- [ ] **Step 1: Write the smoke-test spec**

After this task, running `/beginners-mind --init` against a fresh `/tmp/bm-fixture-project/` (a small dummy repo with no profile) should:

1. Walk the 8 questions in order (project identity, scope, signal sources, owner-seeded corpus, meta-research, standing concerns + anti-recs, token budget + cadence, write).
2. Produce a profile at `/tmp/bm-fixture-project/design/beginners-mind.md` with both sections populated.
3. Commit announcement message names the right repo.

- [ ] **Step 2: Create the fixture project**

Run:

```bash
rm -rf /tmp/bm-fixture-project && mkdir -p /tmp/bm-fixture-project/{src,design} && cd /tmp/bm-fixture-project && git init -q && echo "# Test Project" > README.md && echo "def hello(): print('hi')" > src/main.py && git add . && git commit -q -m "initial" && echo "Fixture ready at /tmp/bm-fixture-project"
```

- [ ] **Step 3: Run smoke test against current state**

Start a fresh CC session in `/tmp/bm-fixture-project` and invoke `/beginners-mind --init`. Expected: no `--init` instructions in SKILL.md yet, so behavior is undefined. Test fails.

- [ ] **Step 4: Add "Mode: --init" section to SKILL.md**

Append to `~/code/claude/skills/skills/beginners-mind/SKILL.md`:

```markdown
## Mode: --init

Triggered explicitly via `/beginners-mind --init`, or auto-fires when no profile is found by the "Locating the profile" rules.

This is an interactive flow. Use `AskUserQuestion` (preferred) or plain prompts as appropriate. Walk the user through the eight steps below in order. Do not skip ahead or batch questions — the owner's input on each step informs the next.

### Step 1 — Identify the project

Ask: _"What is this project, in one paragraph? Include what it does, who uses it, and roughly what stage it's at (new, mature, legacy, etc.)."_

Capture the response verbatim. This identity paragraph drives the meta-research pass in Step 5.

### Step 2 — Scope

Default scope = the current git repo's root. Show that to the user and ask via `AskUserQuestion`:

- **Just this repo (Recommended)** — `<cwd>` only.
- **Add sibling paths** — user provides additional dirs/repos to include (federation case).
- **Custom subset** — user provides a specific list of dirs inside this repo.

Then ask what to exclude (out of scope). Defaults to suggest: `archived/`, `deprecated/`, `vendor/`, `node_modules/`, `.git/`, generated build outputs. Confirm with user.

### Step 3 — Behavioral signal sources

Use `AskUserQuestion` with `multiSelect: true`. Options:

- **git** (recommended for any project) — commit history in scope.
- **CC transcripts** — if owner uses Claude Code; ask for a path glob (default `~/.claude/projects/*/`).
- **Diary** — if project has a diary/journal markdown convention; ask for the path.
- **Issue tracker** — if accessible via `gh issue list` or similar; capture the command.
- **PR history** — if applicable; default `gh pr list --state all`.

Capture user's selections + any path/command details.

### Step 4 — Owner-seeded corpus

Ask in free-form: _"Before I do meta-research, what sources do you already trust for this project's domain? Anything that comes to mind — blogs, GitHub users, Substacks, Discord channels, podcasts, conference series, individual people. Don't worry about being exhaustive."_

Capture the seed list. If the user has nothing, that's fine — skip to Step 5.

### Step 5 — Meta-research pass

Use `WebSearch` and `WebFetch` to identify additional trusted sources for this project's domain (informed by the identity paragraph from Step 1). Look for: subject-matter blogs, GitHub users with active relevant work, Substacks, podcasts, conference talk series.

Combine with the user's seeds from Step 4. Present the combined candidate list using `AskUserQuestion` (or, if list is long, a numbered text list with bulk approve/reject). Each candidate gets a one-line "why this." User approves / rejects / edits.

### Step 6 — Standing concerns + anti-recs

Two questions in sequence:

1. _"What do you want me to be especially watchful for? Anything you've been noticing yourself but haven't formalized?"_
2. _"Anything I should explicitly NOT recommend? E.g., 'don't suggest more tests, we know,' or 'we are deliberately not using TypeScript.'"_

Capture both as free-form text.

### Step 7 — Token budget + cadence

Use `AskUserQuestion`. Defaults to recommend:

- **Token budget:** 500K per run (Recommended). Smaller projects: 250K. Federation-scale: 1M.
- **Cadence:** 30 days (Recommended). Tighter (21d) for active iteration. Looser (45d) for stable projects.

### Step 8 — Write the profile

Read `~/.claude/skills/beginners-mind/templates/profile.md`. Substitute all `{{placeholders}}` from the prior steps.

Determine output location:

- If `design/` subtree exists in scope root → `<scope_root>/design/beginners-mind.md`
- Else → `<scope_root>/.beginners-mind.md`

Determine state location:

- If `design/` subtree → `<scope_root>/design/beginners-mind/state/`
- Else → `<scope_root>/.beginners-mind/state/`

Write the profile. Surface the path and present the file contents for the user's review/edit before committing.

After user approval:

1. Scaffold the state directory: create empty `corpus.md` (with tiered headers), empty `findings/` and `reports/` dirs (use `.gitkeep` placeholders), empty `ledger.md`, and a `last-run.json` with `null` timestamp.
2. Write the approved corpus to `corpus.md`.
3. Surface which repo the commit will land in.
4. Commit the profile + state scaffold.
```

- [ ] **Step 5: Run smoke test**

Start a fresh CC session in `/tmp/bm-fixture-project` and invoke `/beginners-mind --init`. Walk through the eight questions (use minimal answers — this is a smoke test, not a real configuration).

Expected:

- All 8 steps execute in order.
- A profile lands at `/tmp/bm-fixture-project/design/beginners-mind.md` with both H2 sections.
- A state directory scaffold lands at `/tmp/bm-fixture-project/design/beginners-mind/state/`.
- Commit announcement names `/tmp/bm-fixture-project`.

If any step is skipped or batched, fix SKILL.md and re-run.

- [ ] **Step 6: Commit**

```bash
cd ~/code/claude/skills && git add skills/beginners-mind/SKILL.md && git commit -m "$(cat <<'EOF'
beginners-mind: --init flow (8-step profile creation)

Owner-first corpus seeding (step 4) before meta-research (step 5)
is intentional: gives the owner visibility into what assumptions
get baked in. Profile location + state location both detect the
project's design/ subtree and adapt.

Co-Authored-By: Claude Opus 4.7 (1M context) <COAUTHOR_EMAIL>
EOF
)"
```

---

## Task 4: State directory scaffolding helper

**Files:**

- Modify: `~/code/claude/skills/skills/beginners-mind/SKILL.md` (add "State management" section)

- [ ] **Step 1: Write the smoke-test spec**

After this task, calling out to the "Scaffold state directory" routine from SKILL.md (when invoked from `--init` Step 8) produces this exact layout:

```
<state_path>/
├── corpus.md           # contains tiered headers (Tier 0, Tier 1, Tier 2, Tier 3) with empty sections
├── findings/
│   └── .gitkeep
├── reports/
│   └── .gitkeep
├── ledger.md           # contains header "# Recommendation ledger" and empty body
└── last-run.json       # contains {"timestamp": null, "tokens_estimated": null, "duration_seconds": null}
```

- [ ] **Step 2: Run smoke test against current state**

`--init` Step 8 currently says "Scaffold the state directory" abstractly without specifying the layout. Verify by re-running `--init` in a fresh fixture and inspecting the produced state dir. Expected: layout is incomplete or inconsistent.

- [ ] **Step 3: Add "State management" section to SKILL.md**

Append to SKILL.md:

```markdown
## State management

### State directory layout
```

<state_path>/
├── corpus.md # tiered source list (Tier 0–3 headers)
├── findings/ # per-run findings JSON (compressed; pointers, not raw content)
│ └── YYYY-MM-DD.json
├── reports/ # human-readable monthly reports
│ └── YYYY-MM-DD.md
├── ledger.md # recommendation history (Markdown table)
├── last-run.json # {timestamp, tokens_estimated, duration_seconds, partial: bool}
└── cache/ # ETag/last-modified cache for external fetches
└── <url-hash>.{json,body}

````

### Scaffolding routine (used by --init Step 8)

Given a target `<state_path>`:

1. `mkdir -p <state_path>/{findings,reports,cache}`
2. Write `<state_path>/corpus.md`:
   ```markdown
   # Corpus

   Sources the `/beginners-mind` skill pulls from for external research.
   Tiered by trust + signal-to-noise.

   ## Tier 0 — authoritative primary sources

   (always pulled; near-zero false-positive rate)

   ## Tier 1 — curated individuals

   (trusted bloggers, GitHub users, Substacks, podcasts; grown over time)

   ## Tier 2 — community surfaces

   (aggregators; filtered hard)

   ## Tier 3 — peer reports

   (v2 only — AI discussion group archive)
````

3. Write `<state_path>/ledger.md`:

   ```markdown
   # Recommendation ledger

   | ID  | First seen | Status | Recommendation | Last update |
   | --- | ---------- | ------ | -------------- | ----------- |
   ```

4. Write `<state_path>/last-run.json`:
   ```json
   {
     "timestamp": null,
     "tokens_estimated": null,
     "duration_seconds": null,
     "partial": false
   }
   ```
5. Write `<state_path>/findings/.gitkeep` and `<state_path>/reports/.gitkeep` (empty files).

### Reading last-run.json

Use `Read` tool. If file is missing or `timestamp` is `null`, treat as "never run" — skip Phase 0 (cadence guardrail).

### Writing last-run.json

After Phase 6 completes, overwrite with:

```json
{
  "timestamp": "<ISO 8601 UTC>",
  "tokens_estimated": <number>,
  "duration_seconds": <number>,
  "partial": false
}
```

If a phase aborted under fail-safe, set `partial: true`.

````

- [ ] **Step 4: Update --init Step 8 to reference the scaffolding routine**

Edit the `## Mode: --init` → Step 8 section in SKILL.md. Replace the existing "Scaffold the state directory" sentence with:

```markdown
1. Scaffold the state directory using the **Scaffolding routine** in the **State management** section below.
````

(Adjust numbering as needed.)

- [ ] **Step 5: Run smoke test**

Re-run `/beginners-mind --init` against a freshly-created `/tmp/bm-fixture-project/`. After the flow completes:

```bash
ls -la /tmp/bm-fixture-project/design/beginners-mind/state/
cat /tmp/bm-fixture-project/design/beginners-mind/state/last-run.json
head -20 /tmp/bm-fixture-project/design/beginners-mind/state/corpus.md
cat /tmp/bm-fixture-project/design/beginners-mind/state/ledger.md
```

Expected: all four files present with the exact contents specified above (corpus has all four tier headers; ledger has the table header; last-run has `null` values).

- [ ] **Step 6: Commit**

```bash
cd ~/code/claude/skills && git add skills/beginners-mind/SKILL.md && git commit -m "$(cat <<'EOF'
beginners-mind: state management + scaffolding routine

Exact layout for corpus.md, ledger.md, last-run.json, findings/,
reports/, cache/. Scaffolding routine called by --init Step 8.

Co-Authored-By: Claude Opus 4.7 (1M context) <COAUTHOR_EMAIL>
EOF
)"
```

---

## Task 5: Phase 0 — Cadence guardrail

**Files:**

- Modify: `~/code/claude/skills/skills/beginners-mind/SKILL.md` (add "## Phase 0" section)

- [ ] **Step 1: Write the smoke-test spec**

After this task:

- If `last-run.json` has `timestamp: null` → Phase 0 is skipped silently (no AskUserQuestion).
- If `timestamp` is within `cadence_days` of now → AskUserQuestion fires with options [proceed / defer / abort], showing days-since-last and tokens from last run.
- `--force` flag bypasses Phase 0 unconditionally.
- If user picks "abort" → skill exits cleanly with a one-line message.
- If user picks "defer" → skill exits with "Will revisit in N days."

- [ ] **Step 2: Run smoke test against current state**

Manually set `last-run.json` in the fixture to a recent timestamp:

```bash
cat > /tmp/bm-fixture-project/design/beginners-mind/state/last-run.json <<'EOF'
{
  "timestamp": "2026-05-25T12:00:00Z",
  "tokens_estimated": 350000,
  "duration_seconds": 480,
  "partial": false
}
EOF
```

Run `/beginners-mind` in the fixture. Expected: no guardrail behavior yet; test fails.

- [ ] **Step 3: Add "## Phase 0" section to SKILL.md**

Append to SKILL.md:

```markdown
## Phase 0 — Cadence guardrail

**Skip this phase entirely if:**

- `--force` flag is present.
- `last-run.json` is missing or has `timestamp: null` (first run).

**Otherwise:**

1. Read `last-run.json`. Compute `days_since_last = floor((now - timestamp_utc) / 86400)`.
2. Read `cadence_days` from the profile's _Visible to fresh observer_ section.
3. If `days_since_last >= cadence_days` → proceed to Phase 1 silently.
4. If `days_since_last < cadence_days` → fire `AskUserQuestion`:

   Question: _"Last run was {{days_since_last}} days ago (cadence is {{cadence_days}}), used ~{{tokens_estimated}} tokens. Run anyway?"_

   Options:
   - **Proceed (Recommended if you have a reason)** — full run, ignore the guardrail this time.
   - **Defer** — exit cleanly; skill prints "Will revisit when cadence reached (~{{cadence_days - days_since_last}} days from now)."
   - **Abort** — exit cleanly; skill prints "Aborted by user at Phase 0."

5. Act on the choice. Defer/Abort exit. Proceed continues to Phase 1.
```

- [ ] **Step 4: Run smoke test (case A: within cadence)**

With `last-run.json` set to 3 days ago and `cadence: 30` in the profile, run `/beginners-mind` in the fixture.

Expected: AskUserQuestion fires with options [Proceed / Defer / Abort]. Pick "Defer" — skill exits with the expected message.

- [ ] **Step 5: Run smoke test (case B: outside cadence)**

Update `last-run.json` to a date 60 days ago. Re-run `/beginners-mind`.

Expected: No guardrail prompt; skill proceeds silently to Phase 1 (which doesn't exist yet, so output is partial — that's expected at this stage).

- [ ] **Step 6: Run smoke test (case C: --force)**

With `last-run.json` set to 3 days ago, run `/beginners-mind --force`.

Expected: No guardrail prompt; bypass.

- [ ] **Step 7: Commit**

```bash
cd ~/code/claude/skills && git add skills/beginners-mind/SKILL.md && git commit -m "$(cat <<'EOF'
beginners-mind: Phase 0 cadence guardrail

Fires AskUserQuestion if days-since-last < cadence_days. Three
exits: proceed, defer, abort. --force bypasses. First run (no
last-run.json) skipped silently.

Co-Authored-By: Claude Opus 4.7 (1M context) <COAUTHOR_EMAIL>
EOF
)"
```

---

## Task 6: Phase 1 — Introspection (parallel subagents)

**Files:**

- Modify: `~/code/claude/skills/skills/beginners-mind/SKILL.md` (add "## Phase 1" section)

- [ ] **Step 1: Write the smoke-test spec**

After this task, running `/beginners-mind --introspect-only` against the fixture produces a single-section report containing:

- Current file tree of in-scope paths (top-level depth = 2).
- Skills/tooling catalog (skipped or stubbed if `/skills-review` not present).
- Diff of config-shaped files vs `findings/<last_run>.json` (empty on first run — "no prior findings").
- Tooling snapshot (`brew list | head`, `pipx list`, etc.).

Each section authored by a separate subagent dispatch.

- [ ] **Step 2: Run smoke test against current state**

Run `/beginners-mind --introspect-only` in fixture. Expected: no Phase 1 instructions, undefined output. Fails.

- [ ] **Step 3: Add "## Phase 1" section to SKILL.md**

Append:

````markdown
## Phase 1 — Introspect (parallel subagents)

Goal: capture "what lives in the project right now" from external (filesystem, git, tooling) signal only. Behavioral signal is Phase 2; fresh-observer questions are Phase 3.

**Cost estimate before running:** log "Phase 1 estimated: ~30K tokens" (rough — subagents do the heavy lifting).

Dispatch the four subagents below **in parallel** via a single message with multiple `Agent` tool calls. Each subagent returns a short markdown summary.

### Subagent 1.1 — File tree snapshot

Subagent type: `Explore`. Prompt:

> _"List the file tree at the following paths, depth 2 from each path root: {{scope_paths}}. Exclude: {{out_of_scope_paths}}. Return a short markdown summary: directory layout + any files whose name suggests configuration or convention (e.g., `.tool-versions`, `CODEOWNERS`, `Makefile`, `_.toml`, `_.yaml` at root). Do not read file contents. Cap response at 100 lines."_

### Subagent 1.2 — Skills/tooling catalog

Subagent type: `general-purpose`. Prompt:

> _"If `/skills-review research` is available as a skill, invoke it via the Skill tool and return its 'Suggested for this project' section. Otherwise, return a short summary of: installed Claude Code skills (`ls ~/.claude/skills/`), MCP servers (`cat ~/.claude/settings.json | jq '.mcpServers'`), and any project-local tooling (`Makefile` targets, `package.json` scripts, etc.). Cap response at 80 lines."_

### Subagent 1.3 — Config diff since last run

Subagent type: `Explore`. Prompt:

> _"Compare current config-shaped files to those captured in {{prior_findings_path}}. Config-shaped means: files at the project root with extensions `.toml`, `.yaml`, `.yml`, `.json`, `.ini`, or named `Makefile`, `CLAUDE.md`, `README.md`, `.envrc`. If no prior findings exist, list current config-shaped files with their sizes. Return a short markdown summary highlighting additions, deletions, and notable size changes. Cap response at 60 lines."_

### Subagent 1.4 — Tooling snapshot

Run via `Bash`, not subagent (cheap + bounded):

```bash
{
  echo "## Brew (top 30):"; brew list 2>/dev/null | head -30
  echo "## Pipx:"; pipx list 2>/dev/null | grep package
  echo "## MCP servers:"; jq -r '.mcpServers | keys[]' ~/.claude/settings.json 2>/dev/null
} > /tmp/bm-tooling-snapshot.md
```
````

Read the file with the `Read` tool and include verbatim in the report.

### Aggregation

Combine all four outputs into a single "Phase 1 introspection" markdown block. Store this block in memory for the synthesis phase; do not write to disk yet.

**Cost transparency:** log "Phase 1 actual: ~Y tokens" once subagents return.

````

- [ ] **Step 4: Run smoke test**

Run `/beginners-mind --introspect-only` in the fixture. Expected:
- Four subagent dispatches happen (visible in tool-call output).
- Output contains all four sub-sections.
- Each section is bounded (no runaway content).
- Cost log lines present.

- [ ] **Step 5: Commit**

```bash
cd ~/code/claude/skills && git add skills/beginners-mind/SKILL.md && git commit -m "$(cat <<'EOF'
beginners-mind: Phase 1 introspection (parallel subagents)

Four subagent dispatches (file tree, skills/tooling, config diff,
tooling snapshot) running in parallel via Agent tool. Returns
bounded summaries; main context never sees raw file contents.

Co-Authored-By: Claude Opus 4.7 (1M context) <COAUTHOR_EMAIL>
EOF
)"
````

---

## Task 7: Phase 2 — Behavioral observation

**Files:**

- Modify: `~/code/claude/skills/skills/beginners-mind/SKILL.md` (add "## Phase 2" section)

- [ ] **Step 1: Write the smoke-test spec**

After this task, running `/beginners-mind --skip-research --introspect-only=false` (i.e., include Phase 2 but skip everything past Phase 2) against the fixture produces a "Behavioral observation" section with three sub-sections:

- Transcript patterns (if profile's signal sources include CC transcripts).
- Diary themes (if profile points to a diary).
- Git activity trends.

Sub-sections that aren't configured by the profile are explicitly noted as "skipped — not configured in profile."

- [ ] **Step 2: Run smoke test against current state**

Expected to fail — no Phase 2 instructions yet.

- [ ] **Step 3: Add "## Phase 2" section to SKILL.md**

Append:

```markdown
## Phase 2 — Behavioral observation (parallel subagents)

Goal: observe what the project owner actually does. Three subagents in parallel, each conditional on profile config. Each returns a short summary.

**Cost estimate before running:** log "Phase 2 estimated: ~50K tokens (varies with transcript volume)."

**Run window:** all subagents scope their reads to "since `last-run.json.timestamp`" if present, else "last 30 days."

### Subagent 2.1 — Transcript patterns

**Skip if** profile's signal sources do not include `CC transcripts`.

Subagent type: `general-purpose`. Prompt:

> _"Read Claude Code transcripts matching the path glob {{transcript_glob}}, filtering to those modified since {{since_timestamp}}. Summarize patterns visible across sessions: (a) prompts the user typed multiple times in similar form (candidates for aliasing/templating), (b) common frustrations or re-explanations (where the user re-stated the same context), (c) things the user did manually that a skill or alias would simplify. Return a markdown bullet list with NO raw transcript quotes — only summarized patterns with file pointers (e.g., '5 sessions in `~/.claude/projects/foo/`'). Cap response at 60 lines."_

**Token budget guard:** before dispatching, estimate transcript volume via `du -sh <transcript_glob>`. If total > 50MB, prepend to the prompt: "Sample by recency: process the 20 most recently-modified transcripts only. Note this in your summary."

### Subagent 2.2 — Diary themes

**Skip if** profile's signal sources do not include `Diary`.

Subagent type: `Explore`. Prompt:

> _"Read entries from {{diary_path}} dated since {{since_timestamp}}. Identify recurring themes, frustrations, or decisions. Return a markdown bullet list of themes with one-sentence summary each. Cap response at 40 lines."_

### Subagent 2.3 — Git activity trends

Subagent type: `Explore`. Prompt:

> _"Run `git log --since='{{since_date}}' --pretty=format:'%h %an %s' -- {{scope_paths}}` and analyze for behavioral trends: which areas of the codebase saw concentrated activity, which files changed repeatedly, which sessions touched config vs feature code. Return a markdown bullet list with concrete observations (e.g., 'shell config touched 7 times this month; no commits to skills repo despite many sessions'). Cap response at 40 lines."_

### Aggregation

Combine into a single "Phase 2 behavioral observation" markdown block. Each sub-section is either filled or marked `*skipped — not configured in profile*`.

**Cost transparency:** log "Phase 2 actual: ~Y tokens."
```

- [ ] **Step 4: Run smoke test**

Configure the fixture profile to include `git` only (skip transcripts/diary). Run `/beginners-mind` and inspect Phase 2 output.

Expected: 2.1 and 2.2 marked "skipped — not configured"; 2.3 returns git trends summary.

Then update profile to add `Diary` pointing to a non-existent path. Re-run.

Expected: 2.2 dispatches subagent, which returns "no entries found at path" or similar (gracefully handled).

- [ ] **Step 5: Commit**

```bash
cd ~/code/claude/skills && git add skills/beginners-mind/SKILL.md && git commit -m "$(cat <<'EOF'
beginners-mind: Phase 2 behavioral observation

Three subagents (transcripts, diary, git activity), each
conditional on profile signal-source config. Transcript volume
guard samples by recency if over 50MB.

Co-Authored-By: Claude Opus 4.7 (1M context) <COAUTHOR_EMAIL>
EOF
)"
```

---

## Task 8: Phase 3 — Fresh-observer questions (architectural core)

**Files:**

- Modify: `~/code/claude/skills/skills/beginners-mind/SKILL.md` (add "## Phase 3" section)

- [ ] **Step 1: Write the smoke-test spec**

After this task, running `/beginners-mind` against the fixture (with Phase 0 bypassed) produces a Phase 3 output containing:

- A list of beginner questions tagged by file/path (from the fresh-observer subagent).
- Each question with an answer attempt by the orchestrator, bucketed into clean / awkward-history / unanswerable.

Critical: the subagent dispatch in Step 3 of this task explicitly enumerates withheld inputs (README, CLAUDE.md, design/, the _Orchestrator only_ profile section) and the prompt confirms only "Visible to fresh observer" section + file tree + code is passed.

- [ ] **Step 2: Run smoke test against current state**

Expected to fail — no Phase 3 instructions.

- [ ] **Step 3: Add "## Phase 3" section to SKILL.md**

Append:

```markdown
## Phase 3 — Fresh-observer questions (architectural core)

Goal: surface questions a beginner would ask after reading the code with no other briefing. The mismatch between those questions and the answers the orchestrator can construct from full context is the report's most valuable signal.

**Cost estimate before running:** log "Phase 3 estimated: ~80K tokens."

### Sub-phase 3a — Dispatch the fresh-observer subagent

Use the `Agent` tool with `subagent_type: general-purpose`.

**CRITICAL: Inputs that MUST be passed to the subagent:**

- The _Visible to fresh observer_ section of the profile (structural info only).
- The file tree of the in-scope paths (you already have this from Phase 1).
- The persona prompt below.
- The list of code files the subagent may `Read` — derived from the in-scope paths, excluding out-of-scope items.

**CRITICAL: Inputs that MUST NOT be passed:**

- The project's `README.md`.
- Any `CLAUDE.md` file (project or global).
- Any file under `design/` or equivalent design-docs path.
- The diary or any rationale-shaped narrative file.
- The _Orchestrator only_ section of the profile.
- Anything from the orchestrator's conversation history.

Persona prompt (use verbatim):

> _"You are a senior engineer joining this team on day one. You've been told the team is well-regarded but this is your first look at the code. You have the file tree and you may read any file you choose from the in-scope list below. You DO NOT have the README, design docs, or any project rationale — only the code and structural info._
>
> _Your task: generate a list of QUESTIONS a beginner would honestly ask after reading the code. Not conclusions. Not 'fixes.' Questions, of the form 'Why is X like this?', 'What's this directory for?', 'These two functions look almost identical — should they be merged?', 'Why is this file 800 lines?', 'What's the relationship between A and B?', 'Is `archived/` still relevant?'._
>
> _Be honest. If something looks weird, say so. If you can't tell what something does, ask. Don't be polite about cruft._
>
> _Return a JSON array, each element: `{\"file_or_path\": \"<relative path>\", \"question\": \"<the question>\"}`. Cap at 30 questions."_

Pass to the subagent:

- `## Visible to fresh observer` profile section
- File tree from Phase 1
- List of in-scope file paths

**Verification before dispatch:** in your orchestrator state, explicitly check that none of the withheld inputs appear in the subagent's input. If you find yourself about to include README/CLAUDE.md/design rationale, STOP — that's a bug in this implementation.

### Sub-phase 3b — Answer each question from full context

For each question returned, the orchestrator (which has full context) attempts to answer using:

- The withheld inputs (README, CLAUDE.md, design docs, diary).
- The _Orchestrator only_ profile section.
- `git blame` on the referenced file/path for historical context.
- Commit messages that touched the referenced file recently.

Bucket each question into:

- **clean** — Answer is in the docs/code clearly. No action.
- **awkward-history** — Answer requires backstory not captured anywhere obvious. Candidate for "Why is it like this?" report section; may also warrant adding an inline comment.
- **unanswerable** — Even with full context, no good answer. Top-priority finding for cleanup or investigation.

Optional bucket:

- **surprisingly-clever** — Answer reveals an intentional, non-obvious-good design choice. Candidate for "Cool things" report section.

Output: a markdown table with columns `Path | Question | Bucket | Answer/Note`.

**Cost transparency:** log "Phase 3 actual: ~Y tokens."
```

- [ ] **Step 4: Run smoke test**

Configure fixture: ensure `/tmp/bm-fixture-project/src/main.py` exists, add a deliberately weird file:

```bash
mkdir -p /tmp/bm-fixture-project/src/archived && echo "def legacy_thing(): pass" > /tmp/bm-fixture-project/src/archived/old.py && cd /tmp/bm-fixture-project && git add . && git commit -q -m "add archived legacy_thing"
```

Run `/beginners-mind --force --skip-research` in the fixture. Inspect Phase 3 output.

Expected:

- Fresh-observer subagent returns ≥ 1 question (likely about `src/archived/`).
- Verify by inspecting the subagent invocation: README and design/ contents are NOT in the prompt.
- Orchestrator buckets the question(s) and produces the table.

- [ ] **Step 5: Verify the access-rule split (anti-leakage check)**

This is the most important verification in the whole plan. Re-run Phase 3 with a profile whose _Orchestrator only_ section contains a distinctive sentinel string, e.g., `SENTINEL_DO_NOT_LEAK_42`. Inspect the subagent dispatch's actual prompt content (visible in tool-call args).

Expected: the sentinel string is NOT in the subagent prompt. If it IS, the implementation has leaked rationale into the subagent's context — fix SKILL.md to enforce the split before proceeding.

- [ ] **Step 6: Commit**

```bash
cd ~/code/claude/skills && git add skills/beginners-mind/SKILL.md && git commit -m "$(cat <<'EOF'
beginners-mind: Phase 3 fresh-observer questions (core)

The architectural heart of the skill. Fresh subagent gets code +
Visible-to-fresh-observer profile section + persona; explicitly
withholds README/CLAUDE.md/design docs/Orchestrator-only profile
section. Returns beginner questions; orchestrator answers with
full context; bucketing into clean / awkward-history /
unanswerable / surprisingly-clever drives the report.

Co-Authored-By: Claude Opus 4.7 (1M context) <COAUTHOR_EMAIL>
EOF
)"
```

---

## Task 9: Phase 4 — External research with ETag caching

**Files:**

- Modify: `~/code/claude/skills/skills/beginners-mind/SKILL.md` (add "## Phase 4" section)

- [ ] **Step 1: Write the smoke-test spec**

After this task, running `/beginners-mind --force` against the fixture (with corpus.md populated with two test sources) produces a Phase 4 output containing:

- Per-source: list of new findings since last run, each with URL + date + short excerpt.
- Cache directory populated under `<state>/cache/` with ETag-keyed entries.
- Re-running immediately: second run uses cached entries for unchanged sources (visible via "cache hit" log line).

- [ ] **Step 2: Run smoke test against current state**

Expected to fail — no Phase 4.

- [ ] **Step 3: Populate the fixture corpus with two test sources**

```bash
cat > /tmp/bm-fixture-project/design/beginners-mind/state/corpus.md <<'EOF'
# Corpus

## Tier 0 — authoritative primary sources

- https://www.anthropic.com/news

## Tier 1 — curated individuals

- https://simonwillison.net/atom/everything/

## Tier 2 — community surfaces

## Tier 3 — peer reports
EOF
```

(These are real public URLs; the smoke test will do live fetches but they are read-only and bounded.)

- [ ] **Step 4: Add "## Phase 4" section to SKILL.md**

Append:

````markdown
## Phase 4 — External research (parallel subagents per source)

Goal: pull what's new since the last run from corpus sources.

**Cost estimate before running:** log "Phase 4 estimated: ~30K tokens × N sources."

### Source list

Read `corpus.md` from the profile's corpus location. For each non-blank line under each tier that looks like a URL (starts with `http`), treat as a source.

### Per-source fetch with ETag caching

For each source URL, derive a cache key: `sha256(url)[:16]`. Check `<state>/cache/<key>.json` for an existing entry:

```json
{
  "url": "<url>",
  "etag": "<etag from prior fetch>",
  "last_modified": "<RFC date from prior fetch>",
  "fetched_at": "<ISO timestamp>"
}
```
````

Fetch the source using `Bash`:

```bash
HEADERS=""
if [ -n "$ETAG" ]; then HEADERS="$HEADERS -H 'If-None-Match: $ETAG'"; fi
if [ -n "$LAST_MOD" ]; then HEADERS="$HEADERS -H 'If-Modified-Since: $LAST_MOD'"; fi
curl -s -D /tmp/bm-headers -o "<state>/cache/<key>.body" $HEADERS "$URL"
```

If response is 304 → log "cache hit: <url>"; skip subagent dispatch for this source.
If response is 200 → update `<key>.json` with new ETag/Last-Modified headers; dispatch subagent.

### Subagent per source

For each newly-fetched source, dispatch an `Explore` subagent in parallel:

> _"Read the content at <state>/cache/<key>.body. The source is {{source_url}}, last fetched on {{prior_fetch_date}} (or 'never' if first run). Identify items dated AFTER the prior fetch date that are relevant to this project (project identity: {{project_identity_from_profile_step_1}}). For each, return: title, date, URL (if a different URL than the source), one-paragraph summary, why-this-matters for this project. Return at most 5 items per source. JSON array."_

### Aggregation

Combine all source outputs into a single "Phase 4 external findings" markdown block, ordered by date desc. Each item carries provenance: `source_url + item_url + date`.

**Cost transparency:** log "Phase 4 actual: ~Y tokens" + "N cache hits, M new fetches."

**Cache cleanup (run after Phase 4):** any cache file not touched in this run AND not associated with any URL in the current corpus is candidate for cleanup. Surface in the report (don't delete automatically).

````

- [ ] **Step 5: Run smoke test (first run — live fetch)**

Run `/beginners-mind --force --skip-transcripts` in the fixture. Inspect:
- Two live fetches happen (one per source).
- `<state>/cache/` populated with two `.json` + two `.body` files.
- Phase 4 output includes items from both sources.

- [ ] **Step 6: Run smoke test (second run — cache hit)**

Immediately re-run `/beginners-mind --force --skip-transcripts`. Inspect:
- Log shows "cache hit" for both sources (since neither will have updated content in seconds).
- No subagent dispatches for these sources.
- Phase 4 output notes "no new items since last run."

- [ ] **Step 7: Commit**

```bash
cd ~/code/claude/skills && git add skills/beginners-mind/SKILL.md && git commit -m "$(cat <<'EOF'
beginners-mind: Phase 4 external research with ETag caching

Per-source ETag / Last-Modified caching via curl conditional
GETs. Cache hits skip subagent dispatch entirely. Provenance
recorded per finding.

Co-Authored-By: Claude Opus 4.7 (1M context) <COAUTHOR_EMAIL>
EOF
)"
````

---

## Task 10: Phase 5 — Synthesis (four report sections)

**Files:**

- Create: `~/code/claude/skills/skills/beginners-mind/templates/report.md`
- Modify: `~/code/claude/skills/skills/beginners-mind/SKILL.md` (add "## Phase 5" section)

- [ ] **Step 1: Write the smoke-test spec**

After this task, running `/beginners-mind --force` against the fixture produces a complete report with all four sections (Recommendations, Behavioral observations, Cool things, "Why is it like this?"). Each recommendation has a stable ID (`R1`, `R2`, …) and the four required attributes (motivation, source, effort estimate, action ID).

- [ ] **Step 2: Run smoke test against current state**

Expected: no synthesis logic; output is just the raw per-phase blocks. Fails.

- [ ] **Step 3: Create the report template**

Create `~/code/claude/skills/skills/beginners-mind/templates/report.md`:

```markdown
# /beginners-mind report — {{date}}

**Project:** {{project_identity_one_liner}}
**Run cost:** ~{{tokens_actual}} tokens / {{duration_seconds}}s
**Cadence:** {{cadence_days}}-day target; this was day {{days_since_last}} since last run
{{partial_warning_if_applicable}}

---

## Recommendations

{{recommendations_list}}

## Behavioral observations

{{behavioral_observations}}

## Cool things callout

{{cool_things}}

## "Why is it like this?"

{{why_is_it_like_this}}

---

**Findings archive:** `findings/{{date}}.json`
**Ledger update:** see `ledger.md` for accept/reject/defer actions on these recommendations.
**Corpus proposals:** {{corpus_changes_summary_or_none}}
```

- [ ] **Step 4: Add "## Phase 5" section to SKILL.md**

Append:

```markdown
## Phase 5 — Synthesize (four-section report)

Goal: cross-reference all prior phases into a single coherent report.

**Cost estimate before running:** log "Phase 5 estimated: ~40K tokens."

### Step 5.1 — Construct each section

**Recommendations section.** Walk Phase 1 (introspection), Phase 2 (behavior), and Phase 4 (external research) for actionable proposals. Each recommendation gets:

- **ID:** `R<N>`, sequential within this report.
- **Motivation:** which observation triggered this (Phase + sub-section).
- **Source:** corpus item supporting this, if any (URL).
- **Effort:** time estimate per the global "1/1000 calibration" rule (small / medium / large with explicit reasoning).
- **Body:** the recommendation itself, 1–3 sentences.

Anti-rec filter: if any rec matches the profile's _What to skip_ section, drop it.

**Behavioral observations section.** Walk Phase 2's three sub-sections. Each pattern with frequency ≥ 3 across the run window is reported. Each gets a one-paragraph description + a proposed remediation (which may become a Recommendation with cross-reference).

**Cool things callout section.** Walk:

- Phase 1 introspection items that don't appear in Phase 4's external corpus (project doing something the wider world isn't).
- Phase 3 questions bucketed as `surprisingly-clever`.

Each item: what it is + why it stands out.

**"Why is it like this?" section.** Walk Phase 3 questions bucketed as `awkward-history` or `unanswerable`. Each item: the question + the answer (with awkward backstory or "no answer found") + suggested remediation (add a comment / clean up / investigate further).

### Step 5.2 — Apply the report template

Read `~/.claude/skills/beginners-mind/templates/report.md`. Substitute all placeholders. The four section bodies come from Step 5.1.

If any section is empty after filtering, write "_No items this run._" rather than omitting the section.

### Step 5.3 — Cross-references

Where a Behavioral observation has a matching Recommendation, link by ID: "(see R<N>)". Where a "Why is it like this?" answer suggests a fix, link the same way.

**Cost transparency:** log "Phase 5 actual: ~Y tokens."
```

- [ ] **Step 5: Run smoke test**

Run `/beginners-mind --force` in the fixture (full run, all phases). Inspect the in-memory report structure.

Expected:

- All four sections present.
- Recommendations have IDs `R1`, `R2`, ... and the four required attributes.
- Cross-references between sections where applicable.

- [ ] **Step 6: Commit**

```bash
cd ~/code/claude/skills && git add skills/beginners-mind/templates/report.md skills/beginners-mind/SKILL.md && git commit -m "$(cat <<'EOF'
beginners-mind: Phase 5 synthesis (four-section report)

Cross-references Phase 1/2/3/4 outputs into the report template.
Anti-rec filter respects profile's What-to-skip. Each
recommendation gets ID, motivation, source, effort, body.

Co-Authored-By: Claude Opus 4.7 (1M context) <COAUTHOR_EMAIL>
EOF
)"
```

---

## Task 11: Phase 6 — Output + state update + corpus self-management

**Files:**

- Modify: `~/code/claude/skills/skills/beginners-mind/SKILL.md` (add "## Phase 6" section)

- [ ] **Step 1: Write the smoke-test spec**

After this task, running `/beginners-mind --force` against the fixture produces:

- A report file at `<state>/reports/<YYYY-MM-DD>.md`.
- A compressed findings file at `<state>/findings/<YYYY-MM-DD>.json` (patterns + pointers, no raw content).
- Updated `ledger.md` with new recommendations as `pending`.
- A `corpus.md` proposal (printed to terminal, not auto-applied) listing new sources to add + dead sources to consider pruning.
- Updated `last-run.json` with the new timestamp + token estimate.
- Terminal output ends with the report path + one-line summary.

- [ ] **Step 2: Run smoke test against current state**

Expected: report is generated in memory by Phase 5 but never written to disk. Fails.

- [ ] **Step 3: Add "## Phase 6" section to SKILL.md**

Append:

````markdown
## Phase 6 — Output + state update

Goal: persist this run's results, propose corpus changes, surface report to user.

**Cost estimate before running:** log "Phase 6 estimated: ~5K tokens (mostly file I/O)."

### Step 6.1 — Write report

Write the synthesized report from Phase 5 to `<state>/reports/<YYYY-MM-DD>.md` using the `Write` tool.

If a report for today's date already exists, append a `-<HHMM>` suffix to disambiguate.

### Step 6.2 — Write findings (compressed)

Create the findings JSON at `<state>/findings/<YYYY-MM-DD>.json`. Schema:

```json
{
  "run_date": "YYYY-MM-DD",
  "run_window": {"since": "<ISO ts of prior run>", "until": "<ISO ts now>"},
  "introspection_pointers": [{"phase": "1.1", "summary_hash": "<sha>", "key_findings": ["..."]}],
  "behavioral_pointers": [{"phase": "2.1", "pattern_label": "...", "frequency": N, "file_pointers": ["..."]}],
  "fresh_observer_questions": [{"id": "Q1", "path": "...", "bucket": "awkward-history"}],
  "external_findings": [{"source": "<url>", "items": [{"title": "...", "date": "...", "url": "..."}]}],
  "recommendations": [{"id": "R1", "motivation": "...", "source_url": "...", "effort": "small"}]
}
```
````

**CRITICAL:** Do NOT include raw transcript content, raw file content, or raw fetched body content in this JSON. Pointers only. The findings file is consumed by the next run; bloat compounds across runs.

### Step 6.3 — Update ledger.md

Read `<state>/ledger.md`. For each new recommendation from this run:

- Add a row to the table: `| R<N> | <today> | pending | <one-line rec> | <today> |`.

For each existing `pending` recommendation in ledger that is also present in this run's recommendations (matched by recommendation body similarity):

- Update its "Last update" column to today; status remains `pending` but add ` (still-relevant)` annotation.

Write back with `Write` (overwrite).

### Step 6.4 — Propose corpus changes (do not auto-apply)

Two lists:

- **Adds:** any source URL cited in Phase 4 findings that is NOT in the current `corpus.md`. Suggest tier based on signal density.
- **Prunes:** any source in `corpus.md` whose Phase 4 subagent returned zero usable items in the last 3 runs (look at the last 3 `findings/*.json`). Suggest removal.

Print these proposals to the terminal at the end of the run. Do NOT modify `corpus.md` automatically.

### Step 6.5 — Update last-run.json

Overwrite `<state>/last-run.json`:

```json
{
  "timestamp": "<now ISO 8601 UTC>",
  "tokens_estimated": <sum of all phase actual costs>,
  "duration_seconds": <wall clock>,
  "partial": false
}
```

If any phase aborted under fail-safe (Task 13), set `partial: true`.

### Step 6.6 — Terminal summary

Print:

```
/beginners-mind run complete.
Report: <state>/reports/<YYYY-MM-DD>.md
Findings: <state>/findings/<YYYY-MM-DD>.json
Ledger updated with N new recommendations.
Corpus proposals: <A adds, P prunes — see above>
Next run cadence: <date>
```

### Step 6.7 — Commit (cross-repo surfacing)

If the state directory is inside the current repo: commit `reports/`, `findings/`, `ledger.md`, `last-run.json` changes (NOT `cache/`). Surface the commit message + which repo it lands in.

If the state directory is outside the current repo (federation case — state at `~/.claude/beginners-mind/`): commit in the dot-claude repo per the federation hub-use-case rule. Surface "committing to dgroo/dot-claude" before doing it.

If `--dry-run` was used: skip all commits and writes.

````

- [ ] **Step 4: Run smoke test**

Run `/beginners-mind --force` in the fixture. Inspect:
- `ls /tmp/bm-fixture-project/design/beginners-mind/state/reports/` — one file.
- `ls /tmp/bm-fixture-project/design/beginners-mind/state/findings/` — one file.
- `cat ../ledger.md` — has new rows.
- `cat ../last-run.json` — has new timestamp.
- Terminal output ends with the summary block.

Verify findings JSON has no raw transcript/file/body content (check size — should be small, KB not MB).

- [ ] **Step 5: Commit**

```bash
cd ~/code/claude/skills && git add skills/beginners-mind/SKILL.md && git commit -m "$(cat <<'EOF'
beginners-mind: Phase 6 output + state update

Writes report + compressed findings + ledger update + corpus
proposals (not auto-applied) + last-run.json. Cross-repo
commits surface their target repo per the federation hub rule.

Co-Authored-By: Claude Opus 4.7 (1M context) <COAUTHOR_EMAIL>
EOF
)"
````

---

## Task 12: `apply <ID>` mode

**Files:**

- Modify: `~/code/claude/skills/skills/beginners-mind/SKILL.md` (add "## Mode: apply" section)

- [ ] **Step 1: Write the smoke-test spec**

After this task, running `/beginners-mind apply R1` (where R1 is a recommendation from the most recent report) does:

1. Reads the most recent report.
2. Locates R1.
3. Asks user to confirm the proposed action via `AskUserQuestion` [accept / decline / defer].
4. If accept: attempts the action (may dispatch a subagent for non-trivial changes), reports outcome, updates ledger row to `accepted`.
5. If decline: updates ledger row to `rejected`.
6. If defer: updates ledger row to `deferred`.

`do recommended` walks all `pending` IDs from the most recent report, repeating the flow for each.

- [ ] **Step 2: Run smoke test against current state**

Expected: no apply-mode instructions; behavior undefined. Fails.

- [ ] **Step 3: Add "## Mode: apply" section to SKILL.md**

Append:

```markdown
## Mode: apply

Triggered by `/beginners-mind apply <ID>` or `/beginners-mind do recommended`.

### apply <ID>

1. Find the most recent report by date in `<state>/reports/`.
2. Parse the Recommendations section. Locate the row with matching ID.
3. Display the recommendation body + motivation + source + effort. Ask via `AskUserQuestion`:
   - **Accept** — attempt the action now.
   - **Decline** — mark rejected in ledger; don't act.
   - **Defer** — mark deferred in ledger; will resurface next run as `still-relevant` if conditions persist.
4. On Accept:
   - If the action is small/mechanical (rename a file, add a line to config, etc.), execute directly with the appropriate tool (`Edit`, `Bash`, `Write`).
   - If the action is non-trivial (build a feature, refactor a module), dispatch a `general-purpose` subagent with a focused prompt derived from the recommendation body.
   - Surface what was done. Surface which repo each commit lands in.
   - Update ledger row: status `accepted`, add a "completed" note with commit SHA(s).
5. On Decline:
   - Update ledger row: status `rejected`, add the user's reason if provided.
6. On Defer:
   - Update ledger row: status `deferred`, add today's date.

### do recommended

Walk all `pending` IDs from the most recent report in ID order. For each, run the `apply <ID>` flow above. Allow the user to bulk-defer remaining (`AskUserQuestion: "Continue / Stop / Defer all remaining"` after each completion).
```

- [ ] **Step 4: Run smoke test**

Use a fixture where the most recent report has a known-easy recommendation (e.g., "Add `.gitkeep` to empty dir X"). Run `/beginners-mind apply R1`. Walk through Accept.

Expected:

- The action is taken.
- Ledger row updates to `accepted`.
- Commit announcement names the right repo.

Then run again: `/beginners-mind apply R2` and pick Decline. Verify ledger updates.

- [ ] **Step 5: Commit**

```bash
cd ~/code/claude/skills && git add skills/beginners-mind/SKILL.md && git commit -m "$(cat <<'EOF'
beginners-mind: apply mode + do recommended

User-driven follow-up on report recommendations. Small/mechanical
actions executed directly; non-trivial actions dispatched to a
subagent. Ledger reflects accept/reject/defer with completion
metadata.

Co-Authored-By: Claude Opus 4.7 (1M context) <COAUTHOR_EMAIL>
EOF
)"
```

---

## Task 13: Token cost primitives integration + verification

**Files:**

- Modify: `~/code/claude/skills/skills/beginners-mind/SKILL.md` (add "## Cost primitives" section and verify per-phase logs are wired)

- [ ] **Step 1: Write the smoke-test spec**

After this task:

- Every phase logs "Phase N estimated: ~X tokens" before running and "Phase N actual: ~Y tokens" after.
- `--dry-run` produces a plan-only output listing all phases with their estimates, no fetches, no writes.
- Phase-skip flags (`--skip-research`, `--skip-transcripts`, `--introspect-only`) actually skip the named phases (log lines confirm).
- Fail-safe: if any phase's actual cost exceeds `(phase_estimate × 1.5)` AND the cumulative run cost exceeds `(profile.token_budget × 1.5)`, the skill aborts the current phase, writes a partial report, and surfaces "ABORT: budget overrun. Partial report written."

- [ ] **Step 2: Run smoke test against current state**

Run `/beginners-mind --dry-run` in the fixture.

Expected: log lines for estimate exist (from prior tasks), but `--dry-run` may not yet plan-only. Verify and identify gaps.

- [ ] **Step 3: Add "## Cost primitives" section to SKILL.md**

Append:

```markdown
## Cost primitives

### Per-phase cost transparency

Every phase logs:

- Before dispatch: `Phase N estimated: ~X tokens`.
- After completion: `Phase N actual: ~Y tokens`.

The actual is approximated from the tool-call response sizes returned by subagents (or by `len(response_text) // 4` as a rough proxy if a more accurate count is not available).

### Cumulative tracking

Maintain a running counter `cumulative_cost` across phases. After each phase, compare:

- `cumulative_cost > profile.token_budget × 1.5` AND
- `phase_actual > phase_estimate × 1.5`

If BOTH are true, trigger fail-safe.

### Fail-safe

1. Abort the current phase (do not dispatch further subagents within it).
2. Skip remaining phases.
3. Jump to Phase 6 with whatever partial state exists.
4. In the report, prepend: "**⚠ Partial run — budget overrun in Phase N.**"
5. Set `last-run.json.partial = true`.
6. Surface to terminal: "ABORT: budget overrun in Phase N. Partial report at <path>."

### Phase-skip flag handling

Parse args at run start:

- `--introspect-only` → run Phase 0 + 1, skip 2/3/4/5/6 (other than partial report write).
- `--skip-transcripts` → run all phases, but in Phase 2 skip subagent 2.1 (transcript reading) regardless of profile config.
- `--skip-research` → run all phases except Phase 4.
- `--dry-run` → for each phase, log "Phase N estimated: ~X tokens (DRY RUN — not executed)". No subagent dispatches. No fetches. No writes. Print summary at end: "DRY RUN. Estimated total: ~Z tokens."

### Estimation table (initial values; refine over time)

| Phase | Default estimate (tokens) | Drivers                                                         |
| ----- | ------------------------- | --------------------------------------------------------------- |
| 0     | 1K                        | Read 1 small file + 1 AskUserQuestion                           |
| 1     | 30K                       | 4 subagents, bounded                                            |
| 2     | 50K                       | Transcript subagent dominates; subsampled if needed             |
| 3     | 80K                       | Fresh-observer reads code; question count × answer construction |
| 4     | 30K × N sources           | Subagent per source after cache check                           |
| 5     | 40K                       | Cross-reference + template substitution                         |
| 6     | 5K                        | File I/O                                                        |

Sum these for `--dry-run` projection (Phase 4 scales with source count).
```

- [ ] **Step 4: Verify per-phase logs are wired in prior tasks**

Walk back through Tasks 5–11 and confirm each `## Phase N` section has both log lines (estimate before, actual after). If any are missing, add inline now.

- [ ] **Step 5: Run smoke test (case A: --dry-run)**

Run `/beginners-mind --dry-run` in the fixture.

Expected:

- All phase estimate lines print.
- No subagent dispatches happen.
- No files written.
- Final summary line: "DRY RUN. Estimated total: ~Z tokens."

- [ ] **Step 6: Run smoke test (case B: phase-skip)**

Run `/beginners-mind --introspect-only` in the fixture.

Expected: Phase 1 runs, Phases 2–5 skipped (visible in log), Phase 6 writes a partial report containing only the introspection block.

- [ ] **Step 7: Run smoke test (case C: fail-safe simulation)**

This is harder to trigger naturally. Manually force-fail-safe by setting `profile.token_budget` to a very low value (e.g., 1000) and running `/beginners-mind --force`.

Expected: Phase 1 (or 2) abort triggers; partial report written; `last-run.json.partial = true`.

Reset budget after smoke test.

- [ ] **Step 8: Commit**

```bash
cd ~/code/claude/skills && git add skills/beginners-mind/SKILL.md && git commit -m "$(cat <<'EOF'
beginners-mind: cost primitives — dry-run, skip flags, fail-safe

Cumulative cost tracker. Per-phase estimate/actual logs. Hard
fail-safe at budget × 1.5 with partial-report fallback. Dry-run
mode for projection without execution. Three phase-skip flags
for cheap iterative dev runs.

Co-Authored-By: Claude Opus 4.7 (1M context) <COAUTHOR_EMAIL>
EOF
)"
```

---

## Task 14: End-to-end smoke against the federation use case

**Files:**

- This task touches `dgroo/dot-claude` (state output) and `~/code/0.llm/remote-coding-setup/` (profile location). NO changes to `dgroo/skills` itself.

- [ ] **Step 1: Write the smoke-test spec**

The end-to-end test:

1. Run `/beginners-mind --init` from `~/code/0.llm/remote-coding-setup/`. Configure the federation profile per the worked example in the spec.
2. Run `/beginners-mind --dry-run` to confirm the planned run is sane.
3. Run `/beginners-mind` for real.
4. Inspect: report has all four sections, none empty; behavioral observations cite real transcripts; recommendations are concrete; "Why is it like this?" surfaces at least one real awkward-history item.
5. Commit profile to `remote-coding-setup`. Commit state (corpus, ledger, findings, reports) to `dgroo/dot-claude`. Two separate commits surfacing their respective repos.

- [ ] **Step 2: Pre-flight check**

Verify:

- `~/.claude/skills/beginners-mind/SKILL.md` resolves (symlink works).
- No existing `~/.claude/beginners-mind/` directory (would conflict — back up if so).
- No existing `~/code/0.llm/remote-coding-setup/design/beginners-mind.md` (would conflict — back up if so).

If either conflicts: back up, then proceed.

- [ ] **Step 3: Run `--init`**

```bash
cd ~/code/0.llm/remote-coding-setup
```

Invoke `/beginners-mind --init`. Answer the 8 questions per the federation worked example in the spec:

- Step 1 (identity): "Derek's federated coding environment — five interrelated repos managing the always-on host + workstation + Claude Code setup + dotfiles + shared coordination primitives."
- Step 2 (scope): Add sibling paths — all five federated repos + `~/.claude/` + `~/bin/`.
- Step 3 (signal sources): git, CC transcripts (`~/.claude/projects/*/`), diary (federation diary shards).
- Step 4 (owner-seeded corpus): whatever sources Derek lists.
- Step 5 (meta-research): combined list, approved.
- Step 6 (standing concerns + anti-recs): whatever Derek provides.
- Step 7 (budget + cadence): 1M tokens, 21 days (federation case is bigger + more frequent than default).
- Step 8 (write): profile at `~/code/0.llm/remote-coding-setup/design/beginners-mind.md`, state at `~/.claude/beginners-mind/`.

- [ ] **Step 4: Run `--dry-run`**

Invoke `/beginners-mind --dry-run`. Verify the projected total token spend is within reason (target: under 800K for the first full run; subsequent runs much less due to incremental + caching).

If projection is way over, surface to Derek and decide whether to tighten scope before the real run.

- [ ] **Step 5: Run `/beginners-mind` for real**

Invoke `/beginners-mind`. This may take several minutes due to subagent dispatches and external fetches.

Watch for:

- Per-phase cost logs land within estimate × 1.5.
- No fail-safe trigger.
- Phase 3 fresh-observer subagent dispatch's prompt does NOT contain README, CLAUDE.md, design docs, or _Orchestrator only_ profile content (anti-leakage spot-check).

- [ ] **Step 6: Inspect the report**

```bash
cat ~/.claude/beginners-mind/reports/<today>.md | less
```

Verify:

- All four sections present, none empty.
- Recommendations are concrete (not generic platitudes like "consider adding more tests").
- Behavioral observations cite real patterns from real transcripts.
- "Why is it like this?" surfaces at least one real awkward-history item from the federation's accumulated complexity.

If the report is thin, low-quality, or generic: this is the moment to iterate on the skill — the smoke test is the truth, not the unit tests.

- [ ] **Step 7: Commit profile to remote-coding-setup**

```bash
cd ~/code/0.llm/remote-coding-setup && git add design/beginners-mind.md && git commit -m "$(cat <<'EOF'
beginners-mind: federation profile + initial state pact

Configures /beginners-mind for the federation use case: scope
covers all five federated repos + ~/.claude/ + ~/bin/. State
lives outside this repo (~/.claude/beginners-mind/) since no
single repo owns the meta-review.

Co-Authored-By: Claude Opus 4.7 (1M context) <COAUTHOR_EMAIL>
EOF
)"
```

- [ ] **Step 8: Commit state to dot-claude**

The state files (`~/.claude/beginners-mind/`) are versioned via the `dgroo/dot-claude` repo. Locate that repo's working tree (per Derek's setup convention).

```bash
cd ~/code/dot-claude  # or wherever dot-claude is checked out
git add beginners-mind/  # adjust path to match dot-claude's layout for ~/.claude/ contents
git commit -m "$(cat <<'EOF'
beginners-mind: state for federation use case (corpus, ledger, first report)

First run output from /beginners-mind against the federation
profile in remote-coding-setup. Corpus seeded interactively;
recommendations in ledger as pending; first report in reports/.

Co-Authored-By: Claude Opus 4.7 (1M context) <COAUTHOR_EMAIL>
EOF
)"
```

- [ ] **Step 9: Add a diary entry**

Append to `~/code/0.llm/remote-coding-setup/diary/serenity26.md` (or whichever host the session ran on) — a short narrative entry about the first real `/beginners-mind` run: what was useful, what was noise, what should be tuned for v2.

Commit the diary entry separately (atomic).

---

## Self-review checklist

Run after the plan is fully drafted:

- **Spec coverage.** Each design-doc requirement should map to at least one task above. Walk the spec's acceptance criteria — every checkbox should be addressable by these 14 tasks. Gaps: none identified during initial pass; verify by re-reading both documents side-by-side.
- **Placeholder scan.** No "TBD", "TODO", "implement later", or "fill in details" should appear in any task body. Each step contains the actual prompt/code/command an engineer would run.
- **Type consistency.** Subagent dispatch verbs, profile section names ("Visible to fresh observer", "Orchestrator only"), state directory names (`corpus.md`, `ledger.md`, `findings/`, `reports/`, `cache/`, `last-run.json`), invocation flag names (`--force`, `--dry-run`, `--init`, `--skip-research`, `--skip-transcripts`, `--introspect-only`, `--bootstrap-corpus`, `apply <ID>`, `do recommended`) must all be used identically across tasks.
- **Anti-leakage verification (Task 8 Step 5).** The single most important verification in this plan. If Phase 3 leaks orchestrator-only content into the fresh-observer subagent, the entire architectural premise collapses. Do not mark Task 8 complete until the sentinel-string test passes.
