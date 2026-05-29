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

1. Scaffold the state directory following the **Scaffolding routine** in the **State management** section below: create empty `corpus.md` (with tiered headers), empty `findings/` and `reports/` dirs (use `.gitkeep` placeholders), empty `ledger.md`, and a `last-run.json` with `null` timestamp.
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

## Phase 1 — Introspect (parallel subagents)

Goal: capture "what lives in the project right now" from external (filesystem, git, tooling) signal only. Behavioral signal is Phase 2; fresh-observer questions are Phase 3.

**Cost estimate before running:** log "Phase 1 estimated: ~30K tokens" (rough — subagents do the heavy lifting).

Dispatch the four subagents below **in parallel** via a single message with multiple `Agent` tool calls. Each subagent returns a short markdown summary.

### Subagent 1.1 — File tree snapshot

Subagent type: `Explore`. Prompt:

> _"List the file tree at the following paths, depth 2 from each path root: {{scope_paths}}. Exclude: {{out_of_scope_paths}}. Return a short markdown summary: directory layout + any files whose name suggests configuration or convention (e.g., `.tool-versions`, `CODEOWNERS`, `Makefile`, `*.toml`, `*.yaml` at root). Do not read file contents. Cap response at 100 lines."_

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

Read the file with the `Read` tool and include verbatim in the report.

### Aggregation

Combine all four outputs into a single "Phase 1 introspection" markdown block. Store this block in memory for the synthesis phase; do not write to disk yet.

**Cost transparency:** log "Phase 1 actual: ~Y tokens" once subagents return.

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

**Verification before dispatch:** in your orchestrator state, explicitly check that none of the withheld inputs appear in the subagent's input. If you find yourself about to include README/CLAUDE.md/design rationale, the _Orchestrator only_ profile section, or any orchestrator conversation history, STOP — that's a bug in this implementation.

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

**Malformed or empty subagent return.** If the fresh-observer subagent returns an empty array, malformed JSON, or prose instead of the expected JSON array, log a warning ("Phase 3 subagent returned unusable output: <one-line description>") and proceed to Phase 4 with an empty Phase 3 table. Note this in the report's Phase 3 section so the run isn't silently weakened.

**Cost transparency:** log "Phase 3 actual: ~Y tokens."

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

Fetch the source using `Bash`:

```bash
ETAG=$(jq -r '.etag // empty' "<state>/cache/<key>.json" 2>/dev/null)
LAST_MOD=$(jq -r '.last_modified // empty' "<state>/cache/<key>.json" 2>/dev/null)
HEADERS=""
if [ -n "$ETAG" ]; then HEADERS="$HEADERS -H \"If-None-Match: $ETAG\""; fi
if [ -n "$LAST_MOD" ]; then HEADERS="$HEADERS -H \"If-Modified-Since: $LAST_MOD\""; fi
HTTP_STATUS=$(curl -s -o "<state>/cache/<key>.body" -D /tmp/bm-headers -w "%{http_code}" $HEADERS "$URL")
```

If response is 304 → log "cache hit: `<url>`"; skip subagent dispatch for this source.

If response is 200 → extract `ETag` and `Last-Modified` from `/tmp/bm-headers`; update `<key>.json`:

```bash
NEW_ETAG=$(grep -i '^etag:' /tmp/bm-headers | awk '{print $2}' | tr -d '\r')
NEW_LAST_MOD=$(grep -i '^last-modified:' /tmp/bm-headers | cut -d' ' -f2- | tr -d '\r')
jq -n --arg url "$URL" --arg etag "$NEW_ETAG" --arg lm "$NEW_LAST_MOD" --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  '{url: $url, etag: $etag, last_modified: $lm, fetched_at: $ts}' > "<state>/cache/<key>.json"
```

Then dispatch a subagent for this source.

### Project context for subagents

**Design note:** the identity paragraph written by the user in `--init` Step 1 is discarded after Step 5 and not persisted to the profile (per Task 3 design). Phase 4 therefore derives project context on the fly from the profile's _Visible to fresh observer_ section — specifically the `scope`, `standing_concerns`, and `what_to_watch_for` fields. This is option 2 (derive on the fly) rather than option 1 (add an identity field to the profile). Rationale: the profile's Visible section already captures the structured distillation of project identity (scope paths, concerns, what to watch for) — the prose identity paragraph adds warmth but not signal the subagent needs. If future runs reveal that subagent relevance filtering is weak, adding a persisted `{{project_description}}` field to the profile template (option 1) is the obvious upgrade path.

Construct a `{{visible_profile_summary}}` string before dispatching subagents:

> Extract from the profile's _Visible to fresh observer_ section: the `scope` field (what paths/repos), the `standing_concerns` field (what the owner is watchful for), and the `what_to_watch_for` field (explicit asks). Concatenate into two sentences: "This project covers: `<scope>`. Owner standing concerns: `<concerns>`. Watching for: `<watch_for>`." Use this as `{{visible_profile_summary}}`.

### Subagent per source

For each newly-fetched source, dispatch an `Explore` subagent in parallel:

> _"Read the content at `<state>/cache/<key>.body`. The source is `{{source_url}}`, last fetched on `{{prior_fetch_date}}` (or 'never' if first run). Project context: `{{visible_profile_summary}}`. Identify items dated AFTER the prior fetch date that are relevant to this project. For each, return: title, date, URL (if a different URL than the source), one-paragraph summary, why-this-matters for this project. Return at most 5 items per source. Return a JSON array with fields: `title`, `date`, `url`, `summary`, `why_relevant`, `source_url`."_

Dispatch all source subagents in a single message (parallel `Agent` tool calls).

### Aggregation

Combine all source outputs into a single "Phase 4 external findings" markdown block, ordered by date descending. Each item carries provenance: `source_url + item_url + date`. Format:

```
### <title> (<date>)
Source: <source_url> | Item: <item_url>
<summary>
**Why this matters:** <why_relevant>
```

**Cost transparency:** log "Phase 4 actual: ~Y tokens" + "N cache hits, M new fetches."

### Cache cleanup

After Phase 4 aggregation, identify cache files that meet both conditions:

1. Not touched in this run (i.e., not associated with any URL that was fetched or checked in this run).
2. Not associated with any URL currently in `corpus.md`.

Surface these as a "Stale cache candidates" list in the report (filename + URL + `fetched_at`). Do not delete automatically — let the user decide.

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

**Behavioral observations section.** Walk Phase 2's three sub-sections. Each pattern with frequency >= 3 across the run window is reported. Each gets a one-paragraph description + a proposed remediation (which may become a Recommendation with cross-reference).

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

(Further sections to be added by subsequent plan tasks.)
