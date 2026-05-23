---
name: claude-md-add
description: Use when adding a single entry to a CLAUDE.md file, typically via /claude-md-add <text>, or when the user says "add this to claude.md", "remember this in claude.md", or "put this in my claude.md". Acts as a copy editor on the draft before writing — flags vague triggers, redundancy with existing entries, and voice mismatches; preserves the user's voice rather than rewriting.
argument-hint: <text to add>
---

# /claude-md-add

Add a single new rule, preference, or note to a CLAUDE.md file with a copy-editor pass before writing. Sharpens vague triggers, flags redundancy, picks the right section — but does not rewrite the user's voice.

Companion to (not replacement for):

- `/claude-md-improver` — full audit across all CLAUDE.md files. For periodic cleanup, not single additions.
- `/revise-claude-md` — synthesize learnings from current session. For end-of-session rollups.

Use `/claude-md-add` when the user has _one explicit thing_ they want recorded, in their own words.

## How to Invoke

```
/claude-md-add <text>
```

If invoked with no argument, ask: "What do you want to add, and (if ambiguous) which CLAUDE.md — global or project?"

## Workflow

### 1. Pick the target file

Infer from the text's content:

- **Personal preference / how-we-work** ("I prefer X", "talk to me like Y", "always do Z when working with me") → `~/.claude/CLAUDE.md`
- **Project-specific rule** ("run `make test` before commits", "use Foo client for Bar in this repo") → nearest `./CLAUDE.md`
- **Ambiguous** → ask once: "Global (`~/.claude/CLAUDE.md`) or this project's `./CLAUDE.md`?"

If no project CLAUDE.md exists, the answer is global. Don't ask in that case.

### 2. Read existing content

Read the target file. Note:

- **Sections and headings** — for picking where the entry lands.
- **Voice** — terse imperatives ("Run X before Y") vs. flowing prose ("I tend to find...").
- **Entry shape** — bold-led (`**Plan before implementing.** For non-trivial work...`) vs. plain prose vs. bulleted.

The user's own writing in adjacent entries is the style guide. Match it.

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
**Target:** <path>
**Section:** <section heading + suggested insertion point>
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

On accept, use Edit to insert the entry at the chosen point. Don't restructure surrounding content. Don't fold the new entry into an existing one.

## Common Mistakes

- **Expanding scope.** One entry in, one entry out. Don't propose adjacent rules the user didn't ask for, even if you notice them.
- **Adding explanatory prose the user didn't write.** If a clause in the proposed version doesn't trace to a clause in the original (or a sharpening of one), delete it. Smaller and less obvious failure mode than wholesale rewriting, easier to rationalize ("just clarifying"), and just as wrong.
- **Inventing sections.** Use what's there unless nothing fits.
- **Folding into existing entries.** New addition stands on its own line/block.
- **Silent rewrites.** If voice is changed, say so explicitly in "Diff rationale".
- **Skipping the diff.** Always show original vs. proposed before writing, even if the edit feels obviously right.
- **Treating "proceed"-style approval as license to rewrite freely.** The user agreed to a copy-edit pass, not a paraphrase pass.

## Help

When invoked as `/claude-md-add help`, print the following block verbatim:

```
claude-md-add — Add a single rule to a CLAUDE.md file with a copy-editor pass.

Usage: /claude-md-add <text>

Acts as copy editor on the draft before writing — sharpens vague triggers,
flags redundancy with existing entries, picks the right section, preserves
the user's voice rather than rewriting.

Verbs:
  <text>            Propose adding <text> to the right CLAUDE.md.
  help              Show this message.

Target file picked by content:
  ~/.claude/CLAUDE.md   For "I prefer X" / "talk to me like Y" / global rules.
  ./CLAUDE.md           For project-specific rules.

Iron rule: copy editor, not rewriter. Every clause in the proposed version
must trace to a clause in the original (or be a sharpening of one).

Companion skills:
  /claude-md-improver   Full audit across all CLAUDE.md files.
  /revise-claude-md     End-of-session learnings rollup.

See SKILL.md for full reference.
```
