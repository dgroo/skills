---
name: md-add
description: Use when adding a single entry to a CLAUDE.md file, typically via /md-add <text>, or when the user says "add this to claude.md", "remember this in claude.md", or "put this in my claude.md". Routes the entry to the right home — global CLAUDE.md, a project CLAUDE.md, or a path-scoped ~/.claude/rules/*.md for file-type/domain-specific rules so the always-loaded file doesn't bloat — then acts as a copy editor on the draft before writing: flags vague triggers, redundancy with existing entries, and voice mismatches; preserves the user's voice rather than rewriting.
argument-hint: <text to add>
---

# /md-add

Add a single new rule, preference, or note to a CLAUDE.md file with a copy-editor pass before writing. Sharpens vague triggers, flags redundancy, picks the right section — but does not rewrite the user's voice.

Companion to (not replacement for):

- `/claude-md-improver` — full audit across all CLAUDE.md files. For periodic cleanup, not single additions.
- `/revise-claude-md` — synthesize learnings from current session. For end-of-session rollups.

Use `/md-add` when the user has _one explicit thing_ they want recorded, in their own words.

## How to Invoke

```
/md-add <text>
```

If invoked with no argument, ask: "What do you want to add, and (if ambiguous) which CLAUDE.md — global or project?"

## Workflow

### 1. Pick the target file

Three homes, decided by two questions — **scope** (global vs this project), then **always-relevant vs domain-specific**:

1. **Project-specific** (applies only in this repo: "run `make test` before commits here", "use Foo client for Bar in this repo") → nearest `./CLAUDE.md`. A project file only loads in its own repo, so domain-specific _project_ rules stay here too — don't over-engineer a project rules dir (the `rules-loader` hook only reads `~/.claude/rules/`).
2. **Global + always-relevant** (a how-we-work preference that matters every session regardless of which files are open — comms style, workflow, safety, estimates, code philosophy: "talk to me like X", "always commit atomically") → `~/.claude/CLAUDE.md`. This file is a fixed attention tax on _every_ session, so the bar is the **noise test**: would this be noise in a session that never touches the thing it's about? If yes, it's not always-relevant — go to (3).
3. **Global + file-type/domain-specific** (only matters when working with a particular language, tool, file type, or domain — Python conventions, testing discipline, secrets handling, a framework, shell config) → a path-scoped rule under `~/.claude/rules/`, **not** the global CLAUDE.md. This is the anti-bloat route: rules load only when cwd has matching files, so they cost nothing in unrelated sessions. See §1a.

**Ambiguous between global and project** → ask once: "Global (`~/.claude/CLAUDE.md` or a `~/.claude/rules/` file) or this project's `./CLAUDE.md`?" If no project CLAUDE.md exists, the answer is global — don't ask.

**The re-bloat trap:** the lazy default is "it's a preference → global CLAUDE.md." Resist it for anything domain-specific — apply the noise test. (Example: "prefer pytest fixtures over setUp methods" is _not_ a how-we-work preference — it's Python/testing-specific → `rules/testing.md` or `rules/python.md`, never the always-loaded file.)

### 1a. Routing a domain-specific entry into `~/.claude/rules/`

When (3) fires:

- **Enumerate existing rules** — `ls ~/.claude/rules/` and read each file's `paths:` frontmatter + topic (typically `python.md`, `testing.md`, `secrets.md`, `database-entities.md`).
- **If an existing rule covers the topic** → that's the target; run the copy-edit pass (§2–5) against it exactly as for a CLAUDE.md. Sanity-check the entry's domain is actually in that rule's `paths:` — if the rule wouldn't load where the entry is relevant, flag the mismatch.
- **If no existing rule fits** → propose a **new** `~/.claude/rules/<topic>.md` (topic = short kebab-case noun: `docker`, `frontend`, `rust`). It needs `paths:` frontmatter — globs matching the files/contexts where the rule should fire. **Propose the globs explicitly and get approval**: wrong globs are the one failure mode that silently breaks a rule (too narrow → never loads; too broad → loads everywhere, re-bloating by another route). Model the format on existing rules (gitignore-style globs; brace-expansion `{ts,tsx,js}` supported). Show the proposed frontmatter in the review (§4).

### 2. Read existing content

Read the target file. Note:

- **Sections and headings** — for picking where the entry lands.
- **Voice** — terse imperatives ("Run X before Y") vs. flowing prose ("I tend to find...").
- **Entry shape** — bold-led (`**Plan before implementing.** For non-trivial work...`) vs. plain prose vs. bulleted.

The user's own writing in adjacent entries is the style guide. Match it. (For a **new** `~/.claude/rules/` file there's no existing content to match — write a minimal clean file: the `paths:` frontmatter plus the entry as the first bullet, in the terse bold-led style of the existing rule files.)

### 3. Copy-edit pass

Evaluate the draft against four criteria:

| Criterion            | What to check                                                                                                | Example fix                                                          |
| -------------------- | ------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------- |
| **Specific trigger** | Does it say _when_ the rule applies? Hedges like "when sensible", "as appropriate", "if relevant" are flags. | "when it seems sensible" → "when there are 2+ viable paths to weigh" |
| **No redundancy**    | Does an existing entry already cover this?                                                                   | Quote the overlap; ask whether to merge, replace, or skip.           |
| **Section fit**      | Which existing section does it belong in?                                                                    | Suggest one; don't invent new sections unless nothing fits.          |
| **Voice match**      | Bold-led? Imperative? Pronouns? Match the surrounding style.                                                 | Reshape phrasing minimally to match.                                 |

**Iron rule: copy editor, not rewriter.** The proposed version must be the user's own text with tightening — not a paraphrase, and **not the user's text plus new sentences**. Every clause in the proposed version should trace to a clause in the original (or be a sharpening of one). The user's draft is the spec; if they wanted more, they'd have written more.

**The trace test:** before showing the proposed version, walk through it clause by clause and ask "is this in the original, or a sharpening of something in the original?" If a clause is genuinely new — explanation, elaboration, justification — delete it.

Fix:

- Vague triggers (sharpen the _when_)
- Voice mismatch with surrounding entries
- Redundant or colloquial term + canonical name where one would do (e.g., "Interview/AskUserQuestion" → pick the canonical one)

Don't fix:

- "Better English" the user didn't ask for
- Stylistic phrasing that's theirs
- Things that aren't broken
- **Missing explanation.** If the user wrote a metaphor without unpacking it, leave it un-unpacked. They picked the level of detail. Common rationalization: "the metaphor needs context for the reader." Reality: the reader is the user themselves, and they don't need their own metaphor explained back to them.

### 4. Show the review

Output exactly this shape:

```
**Target:** <path>   (+ "NEW rule file" when creating one)
**Section:** <section heading + suggested insertion point>   (omit for a new rule file)
**Proposed `paths:`:** <globs>   (only when creating a new ~/.claude/rules/ file — the load-when-matched scope, for approval)
**Issues:**
- <bullet per issue, tied to a criterion>
- (or "None — entry is clean")

**Original:**
> <user's text, verbatim>

**Proposed:**
> <copy-edited version>

**Diff rationale:** <one line per change>
```

### 5. Get approval, then write

Ask: **accept proposed / use original verbatim / tweak further / cancel.**

On accept, insert the entry at the chosen point with Edit (don't restructure surrounding content; don't fold the new entry into an existing one). For a **new** `~/.claude/rules/` file, use Write to create it with the approved `paths:` frontmatter + the entry.

**Where the change lives:** `~/.claude/CLAUDE.md` and `~/.claude/rules/*.md` are tracked in the git repo backing `~/.claude` (a project `./CLAUDE.md` lives in its own repo). Surface that the write needs committing there to land on other machines — don't silently leave it uncommitted.

## Common Mistakes

- **Re-bloating the global file.** Routing a file-type/domain-specific entry to `~/.claude/CLAUDE.md` because "it's a preference." Apply the noise test (§1): if it'd be noise in a session that never touches its domain, it belongs in a `~/.claude/rules/` file. Defaulting to the always-loaded file is exactly what bloats it.
- **New rule file with wrong `paths:`.** Too-narrow globs → the rule never loads (silent dead rule); too-broad → it loads everywhere, re-bloating by another route. Always show the proposed globs for approval; never guess them silently.
- **Expanding scope.** One entry in, one entry out. Don't propose adjacent rules the user didn't ask for, even if you notice them.
- **Adding explanatory prose the user didn't write.** If a clause in the proposed version doesn't trace to a clause in the original (or a sharpening of one), delete it. Smaller and less obvious failure mode than wholesale rewriting, easier to rationalize ("just clarifying"), and just as wrong.
- **Inventing sections.** Use what's there unless nothing fits.
- **Folding into existing entries.** New addition stands on its own line/block.
- **Silent rewrites.** If voice is changed, say so explicitly in "Diff rationale".
- **Skipping the diff.** Always show original vs. proposed before writing, even if the edit feels obviously right.
- **Treating "proceed"-style approval as license to rewrite freely.** The user agreed to a copy-edit pass, not a paraphrase pass.

## Help

When invoked as `/md-add help`, print the following block verbatim:

```
md-add — Add a single rule to a CLAUDE.md file with a copy-editor pass.

Usage: /md-add <text>

Routes the entry to the right home, then acts as copy editor on the draft —
sharpens vague triggers, flags redundancy, picks the section, preserves the
user's voice rather than rewriting.

Verbs:
  <text>            Propose adding <text> to the right home.
  help              Show this message.

Target picked by scope, then always-relevant vs domain-specific:
  ./CLAUDE.md            Project-specific rules (this repo only).
  ~/.claude/CLAUDE.md    Global + always-relevant (comms/workflow/safety/etc).
  ~/.claude/rules/*.md   Global + file-type/domain-specific (Python, testing,
                         secrets, a framework) — path-scoped, loads only when
                         cwd has matching files, so the always-loaded CLAUDE.md
                         doesn't bloat. Routes into an existing rule or proposes
                         a new one with paths: globs (shown for approval).

Noise test: if an entry would be noise in a session that never touches its
domain, it belongs in ~/.claude/rules/, not the global CLAUDE.md.

Iron rule: copy editor, not rewriter. Every clause in the proposed version
must trace to a clause in the original (or be a sharpening of one).

Companion skills:
  /claude-md-improver   Full audit across all CLAUDE.md files.
  /revise-claude-md     End-of-session learnings rollup.

See SKILL.md for full reference.
```
