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

## Profile schema

A profile is a markdown file with **two H2 sections that have different access rules**:

- `## Visible to fresh observer` — structural information the Phase 3 fresh-observer subagent IS allowed to see (scope, corpus location, behavioral signal sources, etc.).
- `## Orchestrator only — do not include in fresh-observer subagent context` — rationale, design history, "known-weird-but-intentional" answers. The orchestrator uses this ONLY when answering questions the fresh subagent asks; it MUST NOT include this section in the subagent's input.

### How to parse a profile

1. Read the profile file with the `Read` tool.
2. Split on the H2 headers. Identify both sections by exact header match (case-sensitive). The two required headers, verbatim, are:
   - `## Visible to fresh observer`
   - `## Orchestrator only — do not include in fresh-observer subagent context`

   The full header text must match verbatim — punctuation, em-dash, and trailing phrase included for the second header. Substring matching is not sufficient.

3. If either section is missing, surface an error naming the exact required header text. Example: `Profile at /path/to/profile.md is missing required section: ## Visible to fresh observer`.
4. Return both sections as separate strings. The Phase 3 dispatcher uses ONLY the "Visible to fresh observer" section.

### Locating the profile

Priority order, first match wins:

1. Explicit path from `--profile <path>` argument.
2. `design/beginners-mind.md` relative to the current working directory.
3. `.beginners-mind.md` at the current working directory.
4. If none found, fall through to `--init` mode (Task 3).

## Mode: --init

Triggered explicitly via `/beginners-mind --init`, or auto-fires when no profile is found by the "Locating the profile" rules.

This is an interactive flow. Use `AskUserQuestion` (preferred) or plain prompts as appropriate. Walk the user through the eight steps below in order. Do not skip ahead or batch questions — the owner's input on each step informs the next.

### AskUserQuestion conventions

When using `AskUserQuestion`, mark the recommended option by ordering it first in the options list AND including " (Recommended)" in its `label`. The combination produces the expected UX (recommended badge + first position).

### Step 1 — Identify the project

Before asking, derive `{{project_name}}` automatically: try `git remote get-url origin` and extract the repo name; fall back to the basename of the current working directory. Show the derived name to the user so they can correct it if wrong.

Ask: _"What is this project, in one paragraph? Include what it does, who uses it, and roughly what stage it's at (new, mature, legacy, etc.)."_

Capture the response verbatim. This identity paragraph drives the meta-research pass in Step 5.

The identity paragraph is used as input to Step 5's meta-research pass and discarded after. It is **not** written to the profile. (If you want the paragraph preserved, either add a `{{project_description}}` placeholder to the template and the substitution table, or write the paragraph into the profile's _Orchestrator only_ `Decisions log` as a "project as of <init date>" entry. For now, adopt the "discarded after Step 5" framing — no template field.)

### Step 2 — Scope

Default scope = the current git repo's root. Show that to the user and ask via `AskUserQuestion`:

- **Just this repo (Recommended)** — `<cwd>` only.
- **Add sibling paths** — user provides additional dirs/repos to include (federation case).
- **Custom subset** — user provides a specific list of dirs inside this repo.

For "Add sibling paths" or "Custom subset", follow up with a free-form prompt asking the owner to list the paths (one per line). Validate each path exists with `Bash` (`test -d <path>`). Capture the result as `{{scope_paths_comma_separated}}`. For "Just this repo," the scope is the current git repo's root (use `git rev-parse --show-toplevel`).

Then ask what to exclude (out of scope). Defaults to suggest: `archived/`, `deprecated/`, `vendor/`, `node_modules/`, `.git/`, generated build outputs. Present the default exclusions in a free-form prompt: "I'll exclude these by default. Anything to add or remove? Reply 'looks good' to accept." Capture the final list as `{{exclude_paths_comma_separated}}`.

### Step 3 — Behavioral signal sources

Use `AskUserQuestion` with `multiSelect: true`. Options:

- **git** (recommended for any project) — commit history in scope.
- **CC transcripts** — if owner uses Claude Code; ask for a path glob (default `~/.claude/projects/*/`).
- **Diary** — if project has a diary/journal markdown convention; ask for the path.
- **Issue tracker** — if accessible via `gh issue list` or similar; capture the command.
- **PR history** — if applicable; default `gh pr list --state all`.

Capture user's selections + any path/command details as `{{signal_sources_comma_separated}}`.

If the user de-selects all options, surface a warning: "No behavioral signal sources selected; Phase 2 (behavioral observation) will run with no input. Are you sure?" If confirmed, capture `{{signal_sources_comma_separated}}` as `(none)`.

### Step 4 — Owner-seeded corpus

Ask in free-form: _"Before I do meta-research, what sources do you already trust for this project's domain? Anything that comes to mind — blogs, GitHub users, Substacks, Discord channels, podcasts, conference series, individual people. Don't worry about being exhaustive."_

Capture the seed list. If the user has nothing, that's fine — skip to Step 5.

### Step 5 — Meta-research pass

Derive 2–3 search queries from the identity paragraph (Step 1) — use the domain nouns and the tech stack mentioned. Example: a project description mentioning "distributed task queue in Go" yields searches like "distributed task queue Go community blogs", "distributed task queue Go GitHub trending", "Go concurrency Substack". For each query, run `WebSearch`; for top candidates, optionally `WebFetch` to confirm signal density.

Use the results to identify additional trusted sources for this project's domain. Look for: subject-matter blogs, GitHub users with active relevant work, Substacks, podcasts, conference talk series.

Combine with the user's seeds from Step 4. Present the combined candidate list using `AskUserQuestion` (or, if list is long, a numbered text list with bulk approve/reject). Each candidate gets a one-line "why this." User approves / rejects / edits.

Capture the approved list; it will be written to `corpus.md` in Step 8.

### Step 6 — Standing concerns, anti-recs, and design context

Four questions in sequence:

1. _"What do you want me to be especially watchful for? Anything you've been noticing yourself but haven't formalized?"_
   → Captures `{{owner_standing_concerns}}`.

2. _"Anything I should explicitly NOT recommend? E.g., 'don't suggest more tests, we know,' or 'we are deliberately not using TypeScript.'"_
   → Captures `{{owner_anti_recs}}`.

3. _"Are there design docs, ADRs, or prior planning notes I should know about? Provide paths or URLs — these go into the Orchestrator-only section so the fresh-observer subagent never sees them."_
   → Captures `{{design_doc_pointers}}`. If none, use `(none)`.

4. _"Any known-weird-but-intentional choices I should never flag as problems? E.g., 'the monorepo structure is deliberate,' or 'we use callbacks, not promises, on purpose.'"_
   → Captures `{{intentional_quirks}}`. If none, use `(none)`.

`{{decisions_log}}` is initialized to `(none yet)` — it accumulates as `/beginners-mind` runs over time.

### Step 7 — Token budget + cadence

Use `AskUserQuestion`. Defaults to recommend:

- **Token budget:** 500K per run (Recommended). Smaller projects: 250K. Federation-scale: 1M.
- **Cadence:** 30 days (Recommended). Tighter (21d) for active iteration. Looser (45d) for stable projects.

Capture as `{{token_budget}}` and `{{cadence_days}}`.

### Step 8 — Write the profile

Read `~/.claude/skills/beginners-mind/templates/profile.md`. If the template file is not found, surface an error: "Template missing at ~/.claude/skills/beginners-mind/templates/profile.md — re-run `make install` from ~/code/claude/skills." Then abort the init flow.

Substitute all `{{placeholders}}` from the prior steps:

| Placeholder                          | Source                                              |
| ------------------------------------ | --------------------------------------------------- |
| `{{project_name}}`                   | Derived in Step 1 (git remote name or cwd basename) |
| `{{scope_paths_comma_separated}}`    | Step 2                                              |
| `{{exclude_paths_comma_separated}}`  | Step 2                                              |
| `{{signal_sources_comma_separated}}` | Step 3                                              |
| `{{corpus_path}}`                    | Derived below (design/ detection)                   |
| `{{state_path}}`                     | Derived below (design/ detection)                   |
| `{{cadence_days}}`                   | Step 7                                              |
| `{{token_budget}}`                   | Step 7                                              |
| `{{owner_standing_concerns}}`        | Step 6, question 1                                  |
| `{{owner_anti_recs}}`                | Step 6, question 2                                  |
| `{{design_doc_pointers}}`            | Step 6, question 3                                  |
| `{{intentional_quirks}}`             | Step 6, question 4                                  |
| `{{decisions_log}}`                  | `(none yet)`                                        |

Determine output and state locations:

- If `design/` subtree exists in scope root → profile at `<scope_root>/design/beginners-mind.md`, state at `<scope_root>/design/beginners-mind/state/`
- Else → profile at `<scope_root>/.beginners-mind.md`, state at `<scope_root>/.beginners-mind/state/`

Use `Bash` to detect the `design/` subtree: `test -d <scope_root>/design && echo yes || echo no`.

Write the profile. Surface the path and present the file contents for the user's review/edit before committing.

After user approval:

1. Scaffold the state directory: create empty `corpus.md` (with tiered headers), empty `findings/` and `reports/` dirs (use `.gitkeep` placeholders), empty `ledger.md`, and a `last-run.json` with `null` timestamp. (Note: detailed scaffolding routine is added in Task 4; for now, just note "see State management section, Scaffolding routine" as a placeholder reference.)
2. Write the approved corpus to `corpus.md`.
3. Surface which repo the commit will land in.
4. Commit the profile + state scaffold.

## State management

### State directory layout

```
<state_path>/
├── corpus.md              # tiered source list (Tier 0–3 headers)
├── findings/              # per-run findings JSON (compressed; pointers, not raw content)
│   └── YYYY-MM-DD.json
├── reports/               # human-readable monthly reports
│   └── YYYY-MM-DD.md
├── ledger.md              # recommendation history (Markdown table)
├── last-run.json          # {timestamp, tokens_estimated, duration_seconds, partial: bool}
└── cache/                 # ETag/last-modified cache for external fetches
    └── <url-hash>.{json,body}
```

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
   ```

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

(Further sections to be added by subsequent plan tasks.)
